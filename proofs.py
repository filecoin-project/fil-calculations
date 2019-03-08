# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.3'
#       jupytext_version: 0.8.6
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

import math

class Performance(object):
    """Performance model, defining time and proof size to securely seal 1GiB."""
    def __init__(self, proof_seconds, proof_bytes):
        self.total_seal_time = proof_seconds # vcpu-seconds per gigabyte; 1 core = 2 hyperthreads = 2 vcpus
        self.total_proof_size = proof_bytes # per gigabyte

    def satisfied_by(self, other):
        return (other.total_seal_time <= self.total_seal_time) and (other.total_proof_size <= self.total_proof_size)

GiB = 1024 * 1024 * 1024

filecoin_scaling_requirements = Performance(2*60*60, 25) # time = 2 vcpu-hrs
good_performance = Performance(100, 10)
bad_performance = Performance(100000000000, 99999999)

assert filecoin_scaling_requirements.satisfied_by(good_performance)
assert not filecoin_scaling_requirements.satisfied_by(bad_performance)

class Security(object):
    def __init__(self, **kwargs):
        self.base_degree = kwargs.get('base_degree')
        self.expansion_degree = kwargs.get('expansion_degree')
        self.layers = kwargs.get('layers')
        self.sloth_iter = kwargs.get('sloth_iter')
        self.total_challenges = kwargs.get('total_challenges')

    def satisfied_by(self, other):
        return (other.base_degree >= self.base_degree) and (other.expansion_degree >= self.expansion_degree) \
            and (other.layers >= self.layers) and (other.sloth_iter >= self.sloth_iter) \
            and (other.total_challenges >= self.total_challenges)

# FIXME: What is the exact real number of challenges?
filecoin_security_requirements = Security(base_degree=5, expansion_degree=8, layers=10, sloth_iter=0, total_challenges=8848)

# TODO: Make it so this can be extracted directly (and correctly) from the JSON results of the zigzag example.
class Instance(object):
    """Concrete implementations with known benchmarks of fixed parameters on a specific machine."""
    def __init__(self, **kwargs):
        self.security = kwargs.get('security', filecoin_security_requirements) # Assume we are using secure params if not otherwise specified.
        self.replication_time_per_GiB = kwargs.get('replication_time') # vcpu-seconds
        # Is reported vanilla proving time serial, or do we have to account for parallelism?
        self.vanilla_proving_time = kwargs.get('vanilla_proving_time') # vcpu-seconds
        self.constraints = kwargs.get('constraints')
        self.groth_proving_time = kwargs.get('groth_proving_time') # vcpu-seconds
        self.proving_time_per_constraint = self.groth_proving_time / self.constraints

# ➜  rust-proofs git:(zigzag-example-taper) ✗ ./target/release/examples/zigzag --m 5 --expansion 8 --layers 10 --challenges 5 --size 262144 --groth
# Feb 22 22:47:42.385 INFO replication_time/GiB: 2588.454166843s, target: stats, place: filecoin-proofs/examples/zigzag.rs:176 zigzag, root: filecoin-proofs
# Feb 22 22:49:03.378 INFO vanilla_proving_time: 80.99321579 seconds, target: stats, place: filecoin-proofs/examples/zigzag.rs:208 zigzag, root: filecoin-proofs
# Feb 22 22:51:34.656 INFO circuit_num_constraints: 31490555, target: stats, place: filecoin-proofs/examples/zigzag.rs:255 zigzag, root: filecoin-proofs
# Feb 22 22:55:23.362 INFO groth_parameter_bytes: 13777652280, target: stats, place: storage-proofs/src/parameter_cache.rs:131 storage_proofs::parameter_cache, root: storage-proofs
# Feb 22 22:57:57.967 INFO groth_proving_time: 310.895328636s seconds, target: stats, place: filecoin-proofs/examples/zigzag.rs:272 zigzag, root: filecoin-proofs
# real wall clock proving time = 22:57:57 - 22:55:23 = 2:34 = 154s
# vcpu-seconds = 154s * 28 vcpus = 4312
# FIXME: replication_time here and below is only serial time. It ignores parallel merkle-tree-generation time.
porcuquine_prover = Instance(replication_time=2588, constraints=31490555, groth_proving_time=4312, vanilla_proving_time=80.99)

# [ec2-user@ip-172-31-47-121 rust-fil-proofs]$ ./target/release/examples/zigzag --m 5 --expansion 8 --layers 10 --challenges 333 --taper-layers 7 --taper 0.3 --size 262144 --groth --no-bench --partitions 8
# Feb 28 09:58:40.228 INFO replication_time/GiB: 3197.191021367s, target: stats, place: filecoin-proofs/examples/zigzag.rs:178 zigzag, root: filecoin-proofs
# Feb 28 10:53:37.132 INFO vanilla_proving_time: 3296.904225516 seconds, target: stats, place: filecoin-proofs/examples/zigzag.rs:210 zigzag, root: filecoin-proofs
# Feb 28 13:06:22.781 INFO groth_parameter_bytes: 336470126136, target: stats, place: storage-proofs/src/parameter_cache.rs:164 storage_proofs::parameter_cache, root: storage-proofs
# Feb 28 20:48:29.006 INFO groth_proving_time: 34734.387995685s seconds, target: stats, place: filecoin-proofs/examples/zigzag.rs:274 zigzag, root: filecoin-proofs
# real wall clock proving time = 20:48:29 - 13:06:22 = 7:42:07 = 27727s
# vcpu-seconds = 27727s * 128 vcpus = 3549056
ec2_x1e32_xlarge = Instance(replication_time=3197, constraints=5572568613, # FIXME: constraints is a projection -- bench the real value.
                            groth_proving_time=3549056,
                            vanilla_proving_time=3297)

class HashFunction(object):
    ## For now, assume 64 byte input, 32 byte output
    def __init__(self, time, constraints):
        self.hash_time = time # seconds
        self.constraints = constraints

    def time(self):
        return self.hash_time

pedersen = HashFunction(0.000017993, 1324)
blake2s = HashFunction(1.0428e-7, 10324)


class ZigZag(object):
    """ZigZag Model"""

    def __init__(self, **kwargs):
        self.security = kwargs.get('security', filecoin_security_requirements) # Assume we are using secure params if not otherwise specified.
        self.instance = kwargs.get('instance') # Optional Instance.
        self.circuit_proof_size = kwargs.get('circuit_proof_size', 192) # bytes
        self.hash_size = kwargs.get('hash_size', 32) # bytes
        self.node_size = kwargs.get('hash_size', 32) # bytes
        self.sector_size = kwargs.get('size', GiB) # Bytes, default to 1GiB
        # Sector size must be a power of 2.
        assert math.log2(self.sector_size) % 1 == 0

        self.partitions = kwargs.get('partitions', 1)

        self.merkle_hash = kwargs.get('merkle_hash', pedersen)
        self.merkle_tree = MerkleTree(self.nodes(), self.merkle_hash)

        assert (self.node_size == self.hash_size)

    def comm_d_size(self): return self.hash_size

    def comm_r_size(self): return self.hash_size

    def comm_r_star_size(self): return self.hash_size

    def proof_size(self): return (self.circuit_proof_size * self.partitions) + self.comm_d_size() + self.comm_r_size() + self.comm_r_star_size()

    # This can be calculated from taper, etc. later.
    def total_challenges(self): return self.challenges

    def degree(self): return self.base_degree + self.expansion_degree

    def nodes(self):
        nodes = self.sector_size / self.node_size
        assert (nodes % 1) == 0
        return math.floor(nodes)

    def merkle_time(self, n_trees):
        tree_time = self.merkle_tree.time()
        return n_trees * tree_time

    def all_merkle_time(self): return self.merkle_time(self.layers + 1)

    def total_replication_time(self):
        if self.instance:
            return self.instance.replication_time_per_GiB * (self.sector_size / GiB)
        else:
            # Calculate a projection, as in the calculator.
            assert false, unimplemented

    def vanilla_proving_time(self):
        if self.instance:
            return self.instance.vanilla_proving_time
        else:
            # Calculate a projection, as in the calculator.
            assert false, "unimplemented"

    def groth_proving_time(self):
        if self.instance:
            return self.instance.groth_proving_time
        else:
            # Calculate a projection, as in the calculator.
            assert false, "unimplemented"

    def total_proving_time(self):
        return self.vanilla_proving_time() + self.groth_proving_time()

    def performance(self):
        seal_time = self.total_replication_time() + self.total_proving_time()
        return Performance(seal_time, self.proof_size())

    def sector_size_required_to_justify_proof_size(self, required_performance):
        # This works because total_proof_size is per 1GiB.
        return GiB * self.performance().total_proof_size / required_performance.total_proof_size


    # TODO: This doesn't yet account for the changes to seal time introduced by changing sector time.
    def sector_size_required_to_justify_seal_time(self, required_performance):
        # This works because total_proof_size is per 1GiB.
        return GiB* self.performance().total_seal_time / required_performance.total_seal_time

#    def seal_time_for_sector_size(self, sector_size):



#    def replication_time(self, machine):

class MerkleTree(object):
    def __init__(self, nodes, hash_function):
        self.nodes = nodes
        self.hash_function = hash_function
        self.height = math.ceil(math.log2(nodes)) + 1

    # Assuming no parallelism
    def time(self):
        return self.hash_function.time() * (self.nodes - 1)

class Machine(object):
    """Machine Model"""

    def __init__(self, **kwargs):
        self.ram_gb = kwargs.get('ram_gb', 64)
        self.cores = kwargs.get('cores', 14)
        self.core_vcpus = kwargs.get('core_vcpus', 2)
        self.clock_speed = kwargs.get('clock_speed', 3.1) # GhZ
        # For now, assume a fixed operating cost.
        # Account for variable energy consumption later.
        self.hourly_cost = kwargs.get('hourly_cost') # dollars per hour

class Config(object):
    """Configuration Model"""

    def __init__(self, zigzag, machine):
        # For now, assume same machine for replication and proving.
        self.replication_machine = machine
        self.proving_machine = machine
        self.zigzag = zigzag

# ###############################################################################

z = ZigZag(security=filecoin_security_requirements, instance=porcuquine_prover)

m = Machine()
c = Config(z, m)
p = z.performance()

print(f"ZigZag nodes: {z.nodes()}")


