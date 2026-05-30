import os
import random

from pyuvm import uvm_sequence

from tb.sequences.sequence_item import FIFOSeqItem

from hybrid.ml_pool import MLTestPool

from tb.components.env import (
    is_coverage_complete
)

from hybrid.hybrid_config import (
    ENABLE_EARLY_STOP
)


class FIFOSequence(uvm_sequence):

    def __init__(
        self,
        name="FIFOSequence",
        num_tests=36,
        use_ml=False
    ):
        super().__init__(name)

        self.num_tests = num_tests
        self.use_ml = use_ml

    def generate_value(self, t):

        if t == "ZERO":
            return 0

        elif t == "SMALL":
            return random.randint(1, 9)

        elif t == "LARGE":
            return random.randint(200, 255)

    async def body(self):

        executed_tests = 0

        # =====================================================
        # BASELINE MODE
        # =====================================================

        if not self.use_ml:

            print(
                f"[BASELINE MODE] "
                f"Running {self.num_tests} tests"
            )

        # =====================================================
        # HYBRID MODE
        # =====================================================

        else:

            print(
                f"[HYBRID MODE] "
                f"Running {self.num_tests} tests"
            )

            base_dir = os.path.dirname(__file__)

            csv_path = os.path.join(
                base_dir,
                "../../ml/clustered_tests.csv"
            )

            ml_pool = MLTestPool(
                csv_path
            )

            reverse_map = {
                0: "ZERO",
                1: "SMALL",
                2: "LARGE"
            }

        # =====================================================
        # Fixed testcase budget
        # =====================================================

        total_tests = self.num_tests

        for _ in range(total_tests):

            # ==========================================
            # Stop if all bins covered
            # ==========================================

            if self.use_ml and ENABLE_EARLY_STOP:

                if is_coverage_complete():

                    print(
                        "[HYBRID] Coverage complete. "
                        "Stopping."
                    )

                    break

            # ==========================================
            # BASELINE
            # ==========================================

            if not self.use_ml:

                mode = "random"

            # ==========================================
            # TRUE HYBRID
            # 80% ML
            # 20% RANDOM
            # ==========================================

            else:

                if random.random() < 0.2:

                    mode = "random"

                else:

                    mode = "ml"

            item = FIFOSeqItem(
                "item"
            )

            # ==========================================
            # ML testcase
            # ==========================================

            if self.use_ml and mode == "ml":

                tc = ml_pool.get_next()

                item.write_en = tc[
                    "write_en"
                ]

                item.read_en = tc[
                    "read_en"
                ]

                data_type = reverse_map[
                    tc["data_type"]
                ]

                item.data_type = data_type

                item.data_in = self.generate_value(
                    data_type
                )

            # ==========================================
            # RANDOM testcase
            # ==========================================

            else:

                item.randomize()

            item.mode = mode

            await self.start_item(
                item
            )

            await self.finish_item(
                item
            )

            executed_tests += 1

        # =====================================================
        # Final statistics
        # =====================================================

        if self.use_ml:

            print(
                f"[HYBRID] Executed "
                f"{executed_tests} testcases"
            )

        else:

            print(
                f"[BASELINE] Executed "
                f"{executed_tests} testcases"
            )