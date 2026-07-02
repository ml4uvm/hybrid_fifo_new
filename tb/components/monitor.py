import cocotb
from pyuvm import uvm_monitor, uvm_analysis_port
from cocotb.triggers import RisingEdge
from tb.sequences.sequence_item import FIFOSeqItem


class FIFOMonitor(uvm_monitor):
    def build_phase(self):
        self.ap = uvm_analysis_port("ap", self)
        self.dut = cocotb.top
        self.prev_item = None
        self.prev_mode = "random"  # mode captured alongside prev_item, from the driver

    async def run_phase(self):
        for _ in range(3):
            await RisingEdge(self.dut.clk)

        while True:
            await RisingEdge(self.dut.clk)

            curr = FIFOSeqItem("curr")
            curr.write_en = int(str(self.dut.write_en.value))
            curr.read_en = int(str(self.dut.read_en.value))
            curr.data_in = int(str(self.dut.data_in.value))
            curr.full = int(str(self.dut.full.value))
            curr.empty = int(str(self.dut.empty.value))
            curr.data_out = int(str(self.dut.data_out.value))

            # Capture the mode of the transaction that is CURRENTLY being
            # applied (this cycle), to be attached to it once it becomes
            # prev_item and is published next cycle.
            current_mode = getattr(self.driver, "last_mode", "random")

            if self.prev_item is not None:
                self.prev_item.data_out = curr.data_out
                self.prev_item.mode = self.prev_mode  # correct mode, from driver, not a guess
                self.ap.write(self.prev_item)

            self.prev_item = curr
            self.prev_mode = current_mode