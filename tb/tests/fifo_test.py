import cocotb
from pyuvm import uvm_test, uvm_root
from tb.components.env import FIFOEnv
from tb.sequences.sequence import FIFOSequence
from cocotb.clock import Clock


class FIFOTest(uvm_test):
    def build_phase(self):
        self.env = FIFOEnv("env", self)

    async def run_phase(self):
        self.raise_objection()

        # =====================================================
        # BASELINE MODE (CRV/CDV comparison)
        # =====================================================
        seq = FIFOSequence("seq", total_budget=36, use_hybrid=False)

        # =====================================================
        # HYBRID MODE (ML pool -> software-tracked-state gap filling)
        # Budget matches the CRV/CDV baseline exactly, per paper's
        # Table II testcase counts: 36, 54, 72, 108, 144
        # =====================================================
        #seq = FIFOSequence("seq", total_budget=36, use_hybrid=True)

        await seq.start(self.env.agent.seqr)
        self.drop_objection()


@cocotb.test()
async def run_test(dut):
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())
    await uvm_root().run_test("FIFOTest")