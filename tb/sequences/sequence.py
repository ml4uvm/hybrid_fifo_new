import os
import random
from pyuvm import uvm_sequence

from tb.sequences.sequence_item import FIFOSeqItem
from tb.components import env as env_mod          # covered_bins / get_bin / is_coverage_complete
from hybrid.ml_pool import MLTestPool


# Must match env.py's classify_data() / get_fifo_state() category ordering
STATES = ["EMPTY", "MID", "FULL"]
DATA_TYPES = ["ZERO", "SMALL", "LARGE"]
WR_RD_COMBOS = [(0, 0), (0, 1), (1, 0), (1, 1)]


class FIFOSequence(uvm_sequence):
    """
    Hybrid FIFO sequence — software-tracked state model.

    Phase 1 - ML pool:      replay offline RF+KMeans clustered testcases once
    Phase 2/3/4 - Gap fill: greedily target uncovered bins, generating a
                             preamble FROM THE CURRENT TRACKED STATE (no
                             reset between gaps) to reach each bin's
                             required fifo_state, cheapest-available first.

    self.count mirrors fifo.sv's `count` register exactly (same
    write/read/full/empty guard logic), so preamble cost is always
    computed relative to where the FIFO actually is, not assumed EMPTY.
    """

    def __init__(self, name="FIFOSequence", total_budget=36,
                 use_hybrid=True, depth=8):
        super().__init__(name)
        self.total_budget = total_budget
        self.use_hybrid = use_hybrid
        self.depth = depth
        self.executed = 0
        self.count = 0  # software-tracked FIFO occupancy; FIFO is reset to 0 before sequence starts

    # -----------------------------------------------------------------
    # Stimulus value generation
    # -----------------------------------------------------------------
    def generate_value(self, data_type):
        if data_type == "ZERO":
            return 0
        elif data_type == "SMALL":
            return random.randint(1, 9)
        elif data_type == "LARGE":
            return random.randint(10, 255)
        raise ValueError(f"Unknown data_type: {data_type}")

    # -----------------------------------------------------------------
    # Software state model — mirrors fifo.sv count-update logic exactly
    # -----------------------------------------------------------------
    def apply_count(self, write_en, read_en):
        full = (self.count == self.depth)
        empty = (self.count == 0)
        do_write = write_en and not full
        do_read = read_en and not empty
        if do_write and not do_read:
            self.count += 1
        elif do_read and not do_write:
            self.count -= 1
        # simultaneous or neither -> unchanged (matches RTL case stmt)

    def state_of(self, count):
        if count == 0:
            return "EMPTY"
        elif count == self.depth:
            return "FULL"
        return "MID"

    # -----------------------------------------------------------------
    # Preamble: transactions to move from self.count to target_state,
    # relative to CURRENT tracked state (no reset assumed)
    # -----------------------------------------------------------------
    def transactions_to_reach(self, target_state):
        c = self.count
        d = self.depth

        if target_state == "EMPTY":
            n_reads = c
            return [(0, 1, "SMALL")] * n_reads

        elif target_state == "FULL":
            n_writes = d - c
            return [(1, 0, "SMALL")] * n_writes

        elif target_state == "MID":
            if 1 <= c <= d - 1:
                return []
            elif c == 0:
                target_count = max(1, d // 2)
                return [(1, 0, "SMALL")] * target_count
            else:  # c == d (FULL)
                target_count = d // 2
                n_reads = d - target_count
                return [(0, 1, "SMALL")] * n_reads

        raise ValueError(f"Unknown state: {target_state}")

    def bin_cost(self, target_state):
        """Preamble length + 1 target transaction, from CURRENT self.count."""
        return len(self.transactions_to_reach(target_state)) + 1

    # -----------------------------------------------------------------
    # Drive a single transaction and keep the software model in sync
    # -----------------------------------------------------------------
    async def drive_item(self, write_en, read_en, data_type, mode):
        item = FIFOSeqItem("item")
        item.write_en = write_en
        item.read_en = read_en
        item.data_type = data_type
        item.data_in = self.generate_value(data_type)
        item.mode = mode
        await self.start_item(item)
        await self.finish_item(item)

        self.apply_count(write_en, read_en)
        self.executed += 1

    # -----------------------------------------------------------------
    # Phase 1: ML pool (run once, not cycled)
    # -----------------------------------------------------------------
    async def run_ml_pool(self):
        base_dir = os.path.dirname(__file__)
        csv_path = os.path.join(base_dir, "../../ml/clustered_tests.csv")
        pool = MLTestPool(csv_path)

        reverse_map = {0: "ZERO", 1: "SMALL", 2: "LARGE"}
        print(f"[HYBRID] Phase 1: running {len(pool)} ML-prioritized testcases")

        for tc in pool.get_all():
            if self.executed >= self.total_budget:
                return
            if env_mod.is_coverage_complete():
                return
            data_type = reverse_map[tc["data_type"]]
            await self.drive_item(tc["write_en"], tc["read_en"], data_type, mode="ml")

        print(f"[HYBRID] Phase 1 done. executed={self.executed}, "
              f"tracked_count={self.count}, state={self.state_of(self.count)}")

    # -----------------------------------------------------------------
    # Phase 2/3/4 combined: greedy dynamic gap filling
    # -----------------------------------------------------------------
    def pick_cheapest_gap(self):
        """
        Scan all uncovered bins, cost each one relative to self.count
        (NOT precomputed), return the cheapest as
        (write_en, read_en, state, data_type, preamble, cost) or None.
        """
        covered = env_mod.covered_bins
        best = None
        for write_en, read_en in WR_RD_COMBOS:
            for state in STATES:
                for data_type in DATA_TYPES:
                    bin_key = env_mod.get_bin(write_en, read_en, state, data_type)
                    if bin_key in covered:
                        continue
                    cost = self.bin_cost(state)
                    if best is None or cost < best[-1]:
                        preamble = self.transactions_to_reach(state)
                        best = (write_en, read_en, state, data_type, preamble, cost)
        return best

    async def run_gap_filling(self):
        remaining = self.total_budget - self.executed
        print(f"[HYBRID] Phase 2/3/4: {remaining} testcases remaining in budget, "
              f"starting from tracked_count={self.count} "
              f"({self.state_of(self.count)})")

        while remaining > 0 and not env_mod.is_coverage_complete():
            gap = self.pick_cheapest_gap()
            if gap is None:
                print("[HYBRID] No uncovered bins remain.")
                break

            write_en, read_en, state, data_type, preamble, cost = gap
            if cost > remaining:
                print(f"[HYBRID] Cheapest remaining gap costs {cost}, "
                      f"only {remaining} left in budget. Stopping.")
                break

            for (p_we, p_re, p_dt) in preamble:
                await self.drive_item(p_we, p_re, p_dt, mode="preamble")

            await self.drive_item(write_en, read_en, data_type, mode="gapfill")

            remaining = self.total_budget - self.executed

        print(f"[HYBRID] Gap filling complete. Total executed: "
              f"{self.executed}/{self.total_budget}")

    # -----------------------------------------------------------------
    # Baseline mode, preserved for CRV/CDV comparison runs
    # -----------------------------------------------------------------
    async def run_baseline(self):
        print(f"[BASELINE MODE] Running {self.total_budget} random tests")
        for _ in range(self.total_budget):
            item = FIFOSeqItem("item")
            item.randomize()
            item.mode = "random"
            await self.start_item(item)
            await self.finish_item(item)
            self.apply_count(item.write_en, item.read_en)
            self.executed += 1

    # -----------------------------------------------------------------
    # Entry point
    # -----------------------------------------------------------------
    async def body(self):
        if not self.use_hybrid:
            await self.run_baseline()
            return

        await self.run_ml_pool()
        await self.run_gap_filling()