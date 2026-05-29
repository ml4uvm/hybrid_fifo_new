import csv
from itertools import cycle


class MLTestPool:
    """
    Handles ML-prioritized / clustered FIFO testcases
    """

    def __init__(self, file_path):

        self.testcases = self._load_testcases(
            file_path
        )

        if not self.testcases:
            raise ValueError(
                "ML pool is empty!"
            )

        self.iterator = cycle(
            self.testcases
        )

    # =====================================================
    # Load clustered FIFO testcases
    # =====================================================

    def _load_testcases(self, file_path):

        testcases = []

        with open(file_path, "r") as f:

            reader = csv.DictReader(f)

            for row in reader:

                testcase = {

                    "write_en": int(
                        row["write_en"]
                    ),

                    "read_en": int(
                        row["read_en"]
                    ),

                    "data_type": int(
                        row["data_type"]
                    ),

                    "predicted_gain": float(
                        row["predicted_gain"]
                    ),

                    "cluster": int(
                        row["cluster"]
                    )
                }

                testcases.append(
                    testcase
                )

        return testcases

    # =====================================================
    # Get next ML testcase
    # =====================================================

    def get_next(self):

        return next(
            self.iterator
        )