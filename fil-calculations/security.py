from dataclasses import dataclass
from perf_data import filecoin_zigzag
from proofs import ZigZag

@dataclass
class Security:
    zigzag: ZigZag
    encoding_speedup: float
    drg_cheat: float
    late_submission_overhead: int
    proof_count: int

    def polling_time(self):
        encoding_time = self.zigzag.performance().total_seal_time * self.drg_cheat / self.encoding_speedup
        vdf_time = 0
        return encoding_time + vdf_time

    def proving_period(self):
        return self.proof_count * self.polling_time()

    def total_proof_size(self):
        return self.zigzag.performance().proof_size * self.proof_count




filsec = Security(zigzag = filecoin_zigzag,
                  encoding_speedup = 100,
                  drg_cheat = 1/4,
                  late_submission_overhead = 4,
                  proof_count = 10
                  )
