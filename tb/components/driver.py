import cocotb
from pyuvm import uvm_driver
from cocotb.triggers import RisingEdge, ReadOnly, NextTimeStep


class FIFODriver(uvm_driver):
    def build_phase(self):
        self.dut = cocotb.top
        self.ap = None  # set by env.py

    async def run_phase(self):
        # ----------------------------
        # Reset sequence
        # ----------------------------
        self.dut.rst.value = 1
        self.dut.write_en.value = 0
        self.dut.read_en.value = 0
        self.dut.data_in.value = 0
        for _ in range(2):
            await RisingEdge(self.dut.clk)
        self.dut.rst.value = 0
        await RisingEdge(self.dut.clk)

        await ReadOnly()
        full_before = int(str(self.dut.full.value))
        empty_before = int(str(self.dut.empty.value))
        await NextTimeStep()  # exit ReadOnly -> writes are legal again

        # ----------------------------
        # Main driver loop
        # ----------------------------
        while True:
            item = await self.seq_item_port.get_next_item()

            item.full = full_before
            item.empty = empty_before

            self.dut.write_en.value = item.write_en
            self.dut.read_en.value = item.read_en
            self.dut.data_in.value = item.data_in & 0xFF

            await RisingEdge(self.dut.clk)
            await ReadOnly()

            item.data_out = int(str(self.dut.data_out.value))
            full_before = int(str(self.dut.full.value))
            empty_before = int(str(self.dut.empty.value))

            await NextTimeStep()  # exit ReadOnly before next loop's writes

            if self.ap is not None:
                self.ap.write(item)

            self.seq_item_port.item_done()