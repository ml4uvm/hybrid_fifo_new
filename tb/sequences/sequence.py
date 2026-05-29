import pandas as pd
import os
import random

from pyuvm import uvm_sequence
from tb.sequences.sequence_item import FIFOSeqItem


class FIFOSequence(uvm_sequence):

    def __init__(self, name="FIFOSequence", num_tests=300, use_ml=False):
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

        # =====================================================
        # ML MODE
        # =====================================================

        if self.use_ml:

            base_dir = os.path.dirname(__file__)

            csv_path = os.path.join(
                base_dir,
                "../../ml/clustered_tests.csv"
            )

            df = pd.read_csv(csv_path)

            print(
                f"[ML MODE] Running {len(df)} testcases"
            )

            reverse_map = {
                0: "ZERO",
                1: "SMALL",
                2: "LARGE"
            }

            for _, row in df.iterrows():

                item = FIFOSeqItem("item")

                item.write_en = int(
                    row["write_en"]
                )

                item.read_en = int(
                    row["read_en"]
                )

                data_type = reverse_map[
                    int(row["data_type"])
                ]

                item.data_type = data_type

                item.data_in = self.generate_value(
                    data_type
                )

                item.mode = "ml"

                await self.start_item(item)
                await self.finish_item(item)

        # =====================================================
        # BASELINE MODE
        # =====================================================

        else:

            print(
                f"[BASELINE MODE] Running "
                f"{self.num_tests} tests"
            )

            data_types = [
                "ZERO",
                "SMALL",
                "LARGE"
            ]

            dt_idx = 0

            # ---------------------------------------------
            # PHASE 1 : FILL FIFO
            # ---------------------------------------------

            for _ in range(20):

                item = FIFOSeqItem("item")

                item.write_en = 1
                item.read_en = 0

                dt = data_types[
                    dt_idx % len(data_types)
                ]

                dt_idx += 1

                item.data_type = dt

                item.data_in = self.generate_value(
                    dt
                )

                item.mode = "random"

                await self.start_item(item)
                await self.finish_item(item)

            # ---------------------------------------------
            # PHASE 2 : DRAIN FIFO
            # ---------------------------------------------

            for _ in range(20):

                item = FIFOSeqItem("item")

                item.write_en = 0
                item.read_en = 1

                dt = data_types[
                    dt_idx % len(data_types)
                ]

                dt_idx += 1

                item.data_type = dt

                item.data_in = self.generate_value(
                    dt
                )

                item.mode = "random"

                await self.start_item(item)
                await self.finish_item(item)

            # ---------------------------------------------
            # PHASE 3 : MIXED OPERATIONS
            # ---------------------------------------------

            for _ in range(self.num_tests - 40):

                item = FIFOSeqItem("item")

                item.write_en = random.randint(
                    0,
                    1
                )

                item.read_en = random.randint(
                    0,
                    1
                )

                dt = data_types[
                    dt_idx % len(data_types)
                ]

                dt_idx += 1

                item.data_type = dt

                item.data_in = self.generate_value(
                    dt
                )

                item.mode = "random"

                await self.start_item(item)
                await self.finish_item(item)