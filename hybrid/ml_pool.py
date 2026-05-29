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

        # Prevent exhaustion
        self.iterator = cycle(
            self.testcases
        )

    # =====================================================
    # Load clustered FIFO testcases
    # =====================================================

    def _load_testcases(self, file_path):

        testcases = []

        with open(file_path, 'r') as f:

            reader = csv.DictReader(f)

            for row in reader:

                testcase = {

                    # FIFO operation signals
                    "wr_en": int(row["wr_en"]),
                    "rd_en": int(row["rd_en"]),

                    # FIFO stimulus features
                    "data_type": int(
                        row["data_type"]
                    ),

                    # FIFO state-related features
                    "fifo_state": int(
                        row["fifo_state"]
                    ),

                    "occupancy_level": int(
                        row["occupancy_level"]
                    ),

                    # ML metadata
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