from pyuvm import uvm_component
from pyuvm.s12_uvm_tlm_interfaces import uvm_analysis_export

class ALUScoreboard(uvm_component):

    def build_phase(self):
        self.analysis_export = uvm_analysis_export("analysis_export", self)
        self.analysis_export.write = self.write

    def write(self, item):
        expected = self.alu_model(item.a, item.b, item.opcode)
        actual   = item.result

        assert actual == expected, (
            f"Mismatch! opcode={item.opcode}, "
            f"A={item.a:#010x}, B={item.b:#010x}, "
            f"expected={expected:#010x}, got={actual:#010x}"
        )

        assert (actual == 0) == (item.zero == 1), "Zero flag mismatch"

    def alu_model(self, a, b, opcode):
        shamt = b & 0x1F

        if opcode == 0:
            return (a + b) & 0xFFFFFFFF
        elif opcode == 1:
            return (a - b) & 0xFFFFFFFF
        elif opcode == 2:
            return a & b
        elif opcode == 3:
            return a | b
        elif opcode == 4:
            return a ^ b
        elif opcode == 5:
            return (a << shamt) & 0xFFFFFFFF
        elif opcode == 6:
            return (a >> shamt) & 0xFFFFFFFF
        elif opcode == 7:
            a_signed = a if a < (1 << 31) else a - (1 << 32)
            b_signed = b if b < (1 << 31) else b - (1 << 32)
            return 1 if (a_signed < b_signed) else 0
        else:
            return 0