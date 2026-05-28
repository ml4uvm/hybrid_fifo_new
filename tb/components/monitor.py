import cocotb
from pyuvm import uvm_monitor, uvm_analysis_port
from cocotb.triggers import Timer
from tb.sequences.sequence_item import ALUSeqItem

class ALUMonitor(uvm_monitor):
    def build_phase(self):
        self.ap  = uvm_analysis_port("ap", self)
        self.dut = cocotb.top

    async def run_phase(self):
        while True:
            await Timer(1, unit="ns")
            item        = ALUSeqItem("observed")
            item.opcode = int(self.dut.opcode.value)
            item.a      = int(self.dut.a.value)
            item.b      = int(self.dut.b.value)
            item.result = int(self.dut.result.value)
            item.zero   = int(self.dut.zero.value)
            self.ap.write(item)