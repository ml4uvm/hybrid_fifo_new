import cocotb
from pyuvm import uvm_monitor, uvm_analysis_port
from cocotb.triggers import RisingEdge, ReadOnly
from tb.sequences.sequence_item import FIFOSeqItem


class FIFOMonitor(uvm_monitor):
    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)
        self.dut = cocotb.top
        self.pending_item = None
        self.pending_mode = "random"

    async def run_phase(self):
        # Let reset settle
        for _ in range(3):
            await RisingEdge(self.dut.clk)
        await ReadOnly()

        # State BEFORE the next edge's transaction is processed
        full_before = int(str(self.dut.full.value))
        empty_before = int(str(self.dut.empty.value))

        while True:
            await RisingEdge(self.dut.clk)
            await ReadOnly()  # guarantee NBA + combinational logic has settled

            # Signals driven for THIS edge's transaction (stable since the
            # driver set them before the edge; ReadOnly just confirms settle)
            we = int(str(self.dut.write_en.value))
            re = int(str(self.dut.read_en.value))
            din = int(str(self.dut.data_in.value))
            data_out_now = int(str(self.dut.data_out.value))
            full_after = int(str(self.dut.full.value))
            empty_after = int(str(self.dut.empty.value))
            
            we = int(str(self.dut.write_en.value))
            re = int(str(self.dut.read_en.value))
            print(f"[MON DEBUG] t={cocotb.utils.get_sim_time('ns')} we={we} re={re} full_before={full_before} empty_before={empty_before}")

            current_mode = getattr(self.driver, "last_mode", "random")

            # Publish the item from the PREVIOUS edge now that its
            # data_out (valid one cycle after a read) is settled.
            if self.pending_item is not None:
                self.pending_item.data_out = data_out_now
                self.pending_item.mode = self.pending_mode
                self.ap.write(self.pending_item)

            # Build this edge's item using full/empty as they stood
            # BEFORE this edge's write/read was processed — i.e. the
            # state that actually gated whether this transaction was legal.
            item = FIFOSeqItem("curr")
            item.write_en = we
            item.read_en = re
            item.data_in = din
            item.full = full_before
            item.empty = empty_before

            self.pending_item = item
            self.pending_mode = current_mode

            # This edge's post-transaction state becomes "before" for the next edge
            full_before = full_after
            empty_before = empty_after

    def final_phase(self):
        if self.pending_item is not None:
            self.pending_item.mode = self.pending_mode
            self.ap.write(self.pending_item)
            self.pending_item = None