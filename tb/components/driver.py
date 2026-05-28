import cocotb
from pyuvm import uvm_driver
from cocotb.triggers import Timer

class ALUDriver(uvm_driver):
    def build_phase(self):
        self.dut = cocotb.top

    async def run_phase(self):
        while True:
            item = await self.seq_item_port.get_next_item()

            self.dut.opcode.value = item.opcode
            self.dut.a.value      = item.a
            self.dut.b.value      = item.b

            await Timer(1, unit="ns")

            self.seq_item_port.item_done()