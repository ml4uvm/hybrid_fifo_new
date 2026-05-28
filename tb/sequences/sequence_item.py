import random
from pyuvm import uvm_sequence_item


#  Balanced operand generator
def random_operand():
    choice = random.choice(["ZERO", "SMALL", "LARGE", "NEG"])

    if choice == "ZERO":
        return 0
    elif choice == "SMALL":
        return random.randint(1, 9)
    elif choice == "LARGE":
        return random.randint(10, 100)
    else:
        return random.randint(-20, -1)


class ALUSeqItem(uvm_sequence_item):

    def __init__(self, name="ALUSeqItem"):
        super().__init__(name)
        self.opcode = 0
        self.a      = 0
        self.b      = 0
        self.result = 0
        self.zero   = 0

    def randomize(self):
        self.opcode = random.randint(0, 7)
        self.a      = random_operand()
        self.b      = random_operand()