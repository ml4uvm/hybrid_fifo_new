import cocotb

from pyuvm import (
    uvm_test,
    uvm_root
)

from tb.components.env import FIFOEnv
from tb.sequences.sequence import FIFOSequence

from cocotb.clock import Clock


class FIFOTest(uvm_test):

    def build_phase(self):

        self.env = FIFOEnv(
            "env",
            self
        )

    async def run_phase(self):

        self.raise_objection()

        # =====================================================
        # BASELINE MODE (guided/random)
        # =====================================================
        seq = FIFOSequence(
            "seq",
            num_tests=144,
            use_ml=False
        )

        # =====================================================
        # ML MODE (clustered testcases)
        # =====================================================
        #seq = FIFOSequence(
        #    "seq",
        #    use_ml=True
        #)

        await seq.start(
            self.env.agent.seqr
        )

        self.drop_objection()


@cocotb.test()
async def run_test(dut):

    # Start FIFO clock
    clock = Clock(
        dut.clk,
        10,
        unit="ns"
    )

    cocotb.start_soon(
        clock.start()
    )

    await uvm_root().run_test(
        "FIFOTest"
    )