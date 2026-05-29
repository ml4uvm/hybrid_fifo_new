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

            curr.write_en = int(
                str(self.dut.write_en.value)
            )

            curr.read_en = int(
                str(self.dut.read_en.value)
            )

            curr.data_in = int(
                str(self.dut.data_in.value)
            )

            # =====================================
            # Capture status signals
            # =====================================

            curr.full = int(
                str(self.dut.full.value)
            )

            curr.empty = int(
                str(self.dut.empty.value)
            )

            # =====================================
            # Capture output
            # =====================================

            curr.data_out = int(
                str(self.dut.data_out.value)
            )

            # =====================================
            # FIFO alignment
            #
            # Send previous transaction and
            # attach current cycle data_out
            # =====================================

            if self.prev_item is not None:

                self.prev_item.data_out = (
                    curr.data_out
                )

                # Hybrid mode tracking
                self.prev_item.mode = getattr(
                    self,
                    "last_mode",
                    "random"
                )

                self.ap.write(
                    self.prev_item
                )

            self.prev_item = curr