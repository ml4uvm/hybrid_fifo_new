from pyuvm import uvm_sequence_item
import random


class FIFOSeqItem(uvm_sequence_item):

    def __init__(self, name="fifo_seq_item"):
        super().__init__(name)

        # Control
        self.write_en = 0
        self.read_en  = 0

        # Data
        self.data_in  = 0

        # Observed outputs
        self.data_out = 0
        self.full     = 0
        self.empty    = 0

        # ML feature
        self.data_type = "ZERO"

        # Hybrid support
        self.mode = "random"

    def randomize(self):

        # Random control signals
        self.write_en = random.randint(0, 1)
        self.read_en  = random.randint(0, 1)

        # Coverage-aligned data categories
        choice = random.choice(
            ["ZERO", "SMALL", "LARGE"]
        )

        self.data_type = choice

        if choice == "ZERO":

            self.data_in = 0

        elif choice == "SMALL":

            self.data_in = random.randint(
                1,
                9
            )

        elif choice == "LARGE":

            self.data_in = random.randint(
                10,
                255
            )

        self.mode = "random"

        return True

    def __str__(self):

        return (
            f"FIFOSeqItem("
            f"write_en={self.write_en}, "
            f"read_en={self.read_en}, "
            f"data_in={self.data_in}, "
            f"data_out={self.data_out}, "
            f"full={self.full}, "
            f"empty={self.empty}, "
            f"data_type={self.data_type}, "
            f"mode={self.mode})"
        )