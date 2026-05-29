import os
import random

from pyuvm import uvm_sequence

from tb.sequences.sequence_item import FIFOSeqItem

from hybrid.ml_pool import MLTestPool
from hybrid.hybrid_selector import select_mode

from tb.components.env import (
    get_last_gain_label,
    is_coverage_complete
)

from hybrid.hybrid_config import (
    STAGNATION_THRESHOLD,
    ENABLE_EARLY_STOP,
    MAX_TESTS
)


class FIFOSequence(uvm_sequence):

    def __init__(
        self,
        name="FIFOSequence",
        num_tests=36,
        use_ml=False
    ):
        super().__init__(name)

        self.num_tests = num_tests
        self.use_ml = use_ml

    def generate_value(self, t):

        if t == "ZERO":
            return 0

        elif t == "SMALL":
            return random.randint(1, 9)

        elif t == "LARGE":
            return random.randint(200, 255)

    async def body(self):

        # =====================================================
        # BASELINE MODE
        # =====================================================

        if not self.use_ml:

            print(
                f"[BASELINE MODE] "
                f"Running {self.num_tests} tests"
            )

        # =====================================================
        # HYBRID MODE
        # =====================================================

        else:

            print(
                "[HYBRID MODE] "
                "Running adaptive hybrid execution"
            )

            base_dir = os.path.dirname(__file__)

            csv_path = os.path.join(
                base_dir,
                "../../ml/clustered_tests.csv"
            )

            ml_pool = MLTestPool(
                csv_path
            )

            reverse_map = {
                0: "ZERO",
                1: "SMALL",
                2: "LARGE"
            }

            consecutive_no_gain = 0

        # =====================================================
        # Main execution loop
        # =====================================================

        total_tests = (
            self.num_tests
            if not self.use_ml
            else MAX_TESTS
        )

        for _ in range(total_tests):

            # ==========================================
            # Early stop on full coverage
            # ==========================================

            if self.use_ml and ENABLE_EARLY_STOP:

                if is_coverage_complete():

                    print(
                        "[HYBRID] Coverage complete. "
                        "Stopping."
                    )

                    break

            # ==========================================
            # BASELINE
            # ==========================================

            if not self.use_ml:

                mode = "random"

            # ==========================================
            # HYBRID
            # ==========================================

            else:

                stagnated = (
                    consecutive_no_gain >=
                    STAGNATION_THRESHOLD
                )

                mode = select_mode(
                    stagnated=stagnated
                )

            item = FIFOSeqItem(
                "item"
            )

            # ==========================================
            # ML testcase
            # ==========================================

            if self.use_ml and mode == "ml":

                tc = ml_pool.get_next()

                item.write_en = tc[
                    "write_en"
                ]

                item.read_en = tc[
                    "read_en"
                ]

                data_type = reverse_map[
                    tc["data_type"]
                ]

                item.data_type = data_type

                item.data_in = self.generate_value(
                    data_type
                )

            # ==========================================
            # RANDOM testcase
            # ==========================================

            else:

                item.randomize()

            item.mode = mode

            await self.start_item(
                item
            )

            await self.finish_item(
                item
            )

            # ==========================================
            # Stagnation tracking
            # ==========================================

            if self.use_ml:

                gain = get_last_gain_label()

                if gain == 0:

                    consecutive_no_gain += 1

                else:

                    consecutive_no_gain = 0