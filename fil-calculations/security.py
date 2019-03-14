from perf_data import filecoin_zigzag

class Security(object):
    def __init__(self, *, encoding_speedup, drg_cheat, late_submission_overhead, zigzag, proof_count):
        self.zigzag = zigzag
        self.encoding_speedup = encoding_speedup
        self.drg_cheat = drg_cheat
        self.late_submission_overhead = late_submission_overhead
        self.proof_count = proof_count

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
