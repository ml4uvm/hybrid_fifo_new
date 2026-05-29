import cocotb
from pyuvm import uvm_driver
from cocotb.triggers import RisingEdge


class FIFODriver(uvm_driver):

    def build_phase(self):
        self.dut = cocotb.top

    async def run_phase(self):

        # ====================================================
        # Reset sequence
        # ====================================================

        self.dut.rst.value = 1

        self.dut.write_en.value = 0
        self.dut.read_en.value  = 0
        self.dut.data_in.value  = 0

        for _ in range(2):
            await RisingEdge(self.dut.clk)

        self.dut.rst.value = 0

        await RisingEdge(self.dut.clk)

        # ====================================================
        # Main driver loop
        # ====================================================

        while True:

            item = await self.seq_item_port.get_next_item()

            # Apply transaction
            await RisingEdge(self.dut.clk)

            self.dut.write_en.value = item.write_en
            self.dut.read_en.value  = item.read_en
            self.dut.data_in.value  = item.data_in & 0xFF

            # Hold for one cycle
            await RisingEdge(self.dut.clk)

            # Return interface to idle state
            self.dut.write_en.value = 0
            self.dut.read_en.value  = 0

            self.seq_item_port.item_done()