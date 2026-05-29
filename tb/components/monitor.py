import cocotb
from pyuvm import uvm_monitor, uvm_analysis_port
from cocotb.triggers import RisingEdge
from tb.sequences.sequence_item import FIFOSeqItem


class FIFOMonitor(uvm_monitor):

    def build_phase(self):

        self.ap = uvm_analysis_port(
            "ap",
            self
        )

        self.dut = cocotb.top

        # For FIFO data_out alignment
        self.prev_item = None

        # Hybrid support
        self.last_mode = "random"

    async def run_phase(self):

        # =====================================
        # Wait for reset/initialization
        # =====================================

        for _ in range(3):
            await RisingEdge(
                self.dut.clk
            )

        while True:

            await RisingEdge(
                self.dut.clk
            )

            curr = FIFOSeqItem(
                "curr"
            )

            # =====================================
            # Capture inputs
            # =====================================

            curr.write_en = (
                self.dut.write_en.value.integer
            )

            curr.read_en = (
                self.dut.read_en.value.integer
            )

            curr.data_in = (
                self.dut.data_in.value.integer
            )

            # =====================================
            # Capture status signals
            # =====================================

            curr.full = (
                self.dut.full.value.integer
            )

            curr.empty = (
                self.dut.empty.value.integer
            )

            # =====================================
            # Capture output
            # =====================================

            curr.data_out = (
                self.dut.data_out.value.integer
            )

            # =====================================
            # FIFO alignment
            # =====================================

            if self.prev_item is not None:

                self.prev_item.data_out = (
                    curr.data_out
                )

                self.prev_item.mode = getattr(
                    self,
                    "last_mode",
                    "random"
                )

                self.ap.write(
                    self.prev_item
                )

            self.prev_item = curr