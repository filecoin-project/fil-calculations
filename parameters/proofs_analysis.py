from proofs import *
import matplotlib.pyplot as plt


def find_approximate_simple_crossing(xs, points_a, points_b):
    last_diff = None
    last_x = None
    cross = -1
    for (x, blake, pedersen) in zip(xs, points_a, points_b):
        diff = abs(blake - pedersen)
        if last_diff and last_diff < diff:
            cross = last_x * GiB
            break
        last_diff = diff
        last_x = x

    return cross

def graph_hash_seal_times(pedersen_zigzag, required_performance):
    xs = range(1, 8*1024, 64)
    blake2s_zigzag = pedersen_zigzag.scaled_for_new_hash(blake2s)
    pb50_zigzag = pedersen_zigzag.scaled_for_new_hash(pb50)
    pedersen_seal_times = [pedersen_zigzag.performance(size * GiB).total_seal_time for size in xs]
    pb50_seal_times = [pb50_zigzag.performance(size * GiB).total_seal_time for size in xs]
    blake2s_seal_times = [blake2s_zigzag.performance(size * GiB).total_seal_time for size in xs]
    blake_advantage_pb50 = list(map(lambda pb50, blake: pb50/blake, pb50_seal_times, blake2s_seal_times))
    blake_advantage_pedersen = list(map(lambda pedersen, blake: pedersen/blake, pedersen_seal_times, blake2s_seal_times))

    proof_size_xs = range(1, 200, 10)
    pedersen_proof_size = [pedersen_zigzag.performance(size).proof_size for size in proof_size_xs]
    blake2s_proof_size = [blake2s_zigzag.performance(size).proof_size for size in proof_size_xs]
    required_proof_size = [required_performance.proof_size for size in proof_size_xs]

    f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    f.suptitle(f"Seal Time Analysis for {pedersen_zigzag.description()}")
    f.set_size_inches(12, 8)
    ax1.axis([0, xs[-1], 3000, 20000])
    ax1.plot(xs, pb50_seal_times, label='50/50 pedersen/blake2s hybrid')
    ax1.plot(xs, blake2s_seal_times, label='blake2s')
    ax1.plot(xs, pedersen_seal_times, label='pedersen')
    ax1.plot(xs,[required_performance.total_seal_time for size in xs], label='required')
    ax1.set_xlabel('Sector Size (GiB)')
    ax1.set_ylabel('seal time per GiB (smaller is better)')
    ax1.legend()
    ax2.plot(xs, blake_advantage_pb50, label='blake advantage over hybrid')
    ax2.plot(xs, blake_advantage_pedersen, label='blake advantage over pedersen')

    ax2.set_xlabel('Sector Size (GiB)')
    ax2.set_ylabel('blake2s advantage seal time')
    ax2.legend()

    ax3.plot(proof_size_xs, blake2s_proof_size, label='blake2s')
    ax3.plot(proof_size_xs, pedersen_proof_size, label='pedersen')
    ax3.plot(proof_size_xs, required_proof_size, label='required')
    ax3.set_xlabel('Sector Size (GiB')
    ax3.set_ylabel('proof size (smaller is better)')

    ax4.set_xlabel('Sector Size (GiB')

    cross = find_approximate_simple_crossing(xs, pedersen_seal_times, blake2s_seal_times)
    plt.show()
    print(f"Seal rates cross at about {humanize_bytes(cross)}")

