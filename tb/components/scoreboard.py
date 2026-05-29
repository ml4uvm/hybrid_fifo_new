from pyuvm import uvm_component
from pyuvm.s12_uvm_tlm_interfaces import uvm_analysis_export


class FIFOScoreboard(uvm_component):

    def build_phase(self):
        self.analysis_export = uvm_analysis_export("analysis_export", self)
        self.analysis_export.write = self.write

        # FIFO reference model
        self.queue = []

    def write(self, item):

        write_en = item.write_en
        read_en  = item.read_en
        data_in  = item.data_in
        data_out = item.data_out
        full     = item.full
        empty    = item.empty

        # ----------------------------
        # UNDERFLOW check (informational)
        # ----------------------------
        if read_en and empty:
            print("[WARNING] FIFO UNDERFLOW attempted")

        # ----------------------------
        # OVERFLOW check (informational)
        # ----------------------------
        if write_en and full:
            print("[WARNING] FIFO OVERFLOW attempted")

        # ----------------------------
        # READ FIRST (CRITICAL FIX)
        # ----------------------------
        if read_en and not empty:
            assert len(self.queue) > 0, "Queue underflow in model!"

            expected = self.queue.pop(0)
            actual   = data_out

            assert actual == expected, (
                f"FIFO Mismatch! expected={expected}, got={actual}"
            )

        # ----------------------------
        # THEN WRITE
        # ----------------------------
        if write_en and not full:
            self.queue.append(data_in)