from proofs import *
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from dataclasses import replace

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
    xs = range(1, 1024, 16)
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
    ax3.legend()

    ax4.set_xlabel('Sector Size (GiB')

    cross = find_approximate_simple_crossing(xs, pedersen_seal_times, blake2s_seal_times)
    plt.show()
    print(f"Seal rates cross at about {humanize_bytes(cross)}")


def plot_performance(zigzag, requirements, axis):
    xs = range(1, 512, 64) # unit GiB

    axis.set_title(zigzag.description())
    max_cycles = [requirements.total_seal_cycles() * size for size in xs]
    seal_cycles = [zigzag.performance(size * GiB).total_seal_cycles() * size for size in xs]

    mvs = zigzag.minimum_viable_sector_size(requirements)

    if mvs > 0:
        axis.plot([mvs/GiB], [zigzag.performance(mvs).total_seal_cycles() * mvs/GiB], 'g.',
                  label=f'min size {humanize_bytes(mvs)}' )
    axis.plot(xs, max_cycles, label='max cycles')
    axis.plot(xs, seal_cycles, label='seal cycles')
    axis.set_title(zigzag.description())
    axis.set_ylabel('total cycles')
    axis.legend(loc='best')

    return mvs


# zigzag should use pedersen
def plot_cycle_graphs(zigzag, requirements, axes):
    (ax1, ax2) = axes
    xs = range(1, 2*1024, 64)

    plot_performance(zigzag, requirements, ax1)
    scaled = zigzag.scaled_for_new_hash(blake2s)
    scaled.instance.description += ' blake2s'
    plot_performance(zigzag.scaled_for_new_hash(blake2s), requirements, ax2)

def compare_zigzags(alternatives, *, requirements=filecoin_scaling_requirements):
    cols = 2
    rows = len(alternatives)
    f, axes = plt.subplots(rows, cols)
    f.set_size_inches(8, 10)

    for (alternative, axis) in zip(alternatives, axes):
        plot_cycle_graphs(alternative, requirements, axis)

    plt.subplots_adjust(hspace = 0.3)
    plt.show()

def plot_relaxed_requirements(zigzag, requirements, target_sector_size):
    f, ax = plt.subplots()
    ax.set_xlabel('total seal time')
    ax.set_ylabel('minimum sector size (GiB)')
    req = requirements
    done = 10
    xs, ys = [], []

    while done > 0:
        mvs = zigzag.minimum_viable_sector_size(req)
        xs.append(req.total_seal_time / (60 * 60))
        ys.append(mvs/GiB)
        if zigzag.meets_performance_requirements(target_sector_size, req):
            done -= 1
        new_seal_time = req.total_seal_time * 1.1
        req = replace(req, total_seal_time=new_seal_time)

    plt.plot(xs, ys, 'gs')
    plt.show()

def plot_accelerated_proving(zigzag, requirements, target_sector_size):
    f, ax = plt.subplots()
    ax.set_xlabel('groth proving time')
    ax.set_ylabel('minimum sector size (GiB)')
    z = zigzag
    done = 10
    xs, ys = [], []

    while done > 0:
        mvs = z.minimum_viable_sector_size(requirements)
        xs.append(z.instance.groth_proving_time)
        ys.append(mvs/GiB)
        if z.meets_performance_requirements(target_sector_size, requirements):
            done -= 1
        new_proving_time = z.instance.groth_proving_time * 0.5
        new_inst = replace(z.instance, groth_proving_time=new_proving_time)
        z = replace(z, instance=new_inst)

    plt.plot(xs, ys, 'gs')
    plt.show()

def plot_accelerated_hashing(zigzag, requirements, target_sector_size):
    f, ax = plt.subplots()
    ax.set_xlabel('hash time')
    ax.set_ylabel('minimum sector size (GiB)')
    z = zigzag
    done = 10
    xs, ys = [], []

    scale = 1
    while done > 0:
        mvs = z.minimum_viable_sector_size(requirements)
        xs.append(scale)
        ys.append(mvs/GiB)
        if z.meets_performance_requirements(target_sector_size, requirements):
            done -= 1
        scale *= 0.9
        new_hash = replace(z.merkle_hash, hash_time=(zigzag.merkle_hash.time() * scale))
        z = zigzag.scaled_for_new_hash(new_hash)

    plt.xlim(1, 0)
    plt.plot(xs, ys, 'gs')
    plt.show()