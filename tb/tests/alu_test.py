import cocotb
from pyuvm import uvm_test, uvm_root
from tb.components.env import ALUEnv
from tb.sequences.sequence import ALUSequence


class ALUTest(uvm_test):

    def build_phase(self):
        self.env = ALUEnv("env", self)

    async def run_phase(self):
        self.raise_objection()

        # =====================================================
        # BASELINE MODE (random)
        # =====================================================
        #seq = ALUSequence("seq", num_tests=300, use_ml=False)

        # =====================================================
        # ML MODE (clustered testcases)
        # =====================================================
        seq = ALUSequence("seq", use_ml=True)

        await seq.start(self.env.agent.seqr)

        self.drop_objection()


@cocotb.test()
async def run_test(dut):
    await uvm_root().run_test("ALUTest")