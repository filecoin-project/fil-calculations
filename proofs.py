import math
from util import humanize_bytes

GiB = 1024 * 1024 * 1024

class Performance(object):
    """Performance model, defining time and proof size to securely seal 1GiB."""
    def __init__(self, seal_seconds, proof_bytes, sector_size=GiB):
        scale = sector_size/GiB
        self.total_seal_time = seal_seconds/scale # vcpu-seconds per gigabyte; 1 core = 2 hyperthreads = 2 vcpus
        self.proof_size = proof_bytes / scale # per gigabyte

    # Proof size per sector size. Defaults to standard 1 GiB
    def proof_size(self, sector_size=GiB):
        return self.proof_size_per_gigabyte * (sector_size/GiB)
    #
    # # Total seal time per sector size. Defaults to standard 1 GiB
    # def total_seal_time(self, sector_size=GiB):
    #     return self.total_seal_time_per_GiB * (sector_size/GiB)

    # Does other have performance greater than or equal to self in all dimensions?
    def satisfied_by(self, other):
        return (other.total_seal_time <= self.total_seal_time) and (other.proof_size <= self.proof_size)

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
filecoin_security_requirements = Security(base_degree=5, expansion_degree=8, layers=10, sloth_iter=0,
                                          total_challenges=8848)

class HashFunction(object):
    ## For now, assume 64 byte input, 32 byte output
    def __init__(self, time, constraints):
        self.hash_time = time # seconds
        self.constraints = constraints

    def time(self):
        return self.hash_time

    def div_time(self, other_hash):
        return self.hash_time / other_hash.hash_time

    def div_constraints(self, other_hash):
        return self.constraints / other_hash.constraints

def hybrid_hash(leaf_hash, root_hash, root_fraction):
    leaf_fraction = 1 - root_fraction
    hash_time = (root_hash.hash_time * root_fraction) + (leaf_hash.hash_time * leaf_fraction)
    constraints = (root_hash.constraints * root_fraction) + (leaf_hash.constraints * leaf_fraction)
    return HashFunction(hash_time, constraints)

pedersen = HashFunction(0.000017993, 1324)
blake2s = HashFunction(1.0428e-7, 10324)

pb50 = hybrid_hash(pedersen, blake2s, 0.5)

class MerkleTree(object):
    def __init__(self, nodes, hash_function):
        self.nodes = nodes
        self.hash_function = hash_function
        self.height = math.ceil(math.log2(nodes)) + 1

    def hash_count(self):
        return self.nodes - 1

    # Assuming no parallelism
    def time(self):
        return self.hash_function.time() * self.hash_count()

    def constraints(self):
        return self.hash_function.constraints() * self.hash_count()

    def proof_hashes(self):
        return self.height

    def proof_constraints(self):
        return self.proof_hashes() * self.hash_function.constraints


# TODO: Make it so this can be extracted directly (and correctly) from the JSON results of the zigzag example.
class Instance(object):
    """Concrete implementations with known benchmarks of fixed parameters on a specific machine."""
    def __init__(self, merkle_tree_hash=pedersen, **kwargs):
        self.init_args = kwargs
        self.description = kwargs.get('description')
        self.security = kwargs.get('security', filecoin_security_requirements) # Assume we are using secure params if not otherwise specified.
        self.encoding_replication_time_per_GiB = kwargs.get('encoding_replication_time_per_GiB') # vcpu-seconds
        # Q: Is reported vanilla proving time serial, or do we have to account for parallelism? A: It's parallel
        self.sector_size = kwargs.get('sector_size')
        self.vanilla_proving_time = kwargs.get('vanilla_proving_time') # vcpu-seconds
        self.constraints = kwargs.get('constraints')
        self.groth_proving_time = kwargs.get('groth_proving_time') # vcpu-seconds
        self.proving_time_per_constraint = self.groth_proving_time / self.constraints
        #self.merkle_tree_hash = kwargs.get('merkle_tree_hash', pedersen)
        self.merkle_tree_hash = merkle_tree_hash
        assert self.constraints, "constraints required"

    def merkle_tree_replication_time_per_GiB(self):
        # For now, assume merkle tree uses pedersen hashes.
        return MerkleTree(GiB / 32, self.merkle_tree_hash).time() * 11  # Grrr... hard-coding layers, needs to move to ZigZag in refactor.

    def replication_time_per_GiB(self):
        return self.encoding_replication_time_per_GiB + self.merkle_tree_replication_time_per_GiB()

    def scale(self, constraints, new_hash):
        new_init_args = dict(self.init_args)
        # TODO: mirror more sophisticated constraint calculation for replication time.
        new_init_args['encoding_replication_time_per_GiB'] = new_hash.div_time(self.merkle_tree_hash) * self.encoding_replication_time_per_GiB
        new_init_args['constraints'] = constraints
        new_init_args['groth_proving_time'] = self.proving_time_per_constraint * constraints
        return Instance(**new_init_args)
        
# ➜  rust-proofs git:(zigzag-example-taper) ✗ ./target/release/examples/zigzag --m 5 --expansion 8 --layers 10 --challenges 5 --size 262144 --groth
# Feb 22 22:47:42.385 INFO replication_time/GiB: 2588.454166843s, target: stats, place: filecoin-proofs/examples/zigzag.rs:176 zigzag, root: filecoin-proofs
# Feb 22 22:49:03.378 INFO vanilla_proving_time: 80.99321579 seconds, target: stats, place: filecoin-proofs/examples/zigzag.rs:208 zigzag, root: filecoin-proofs
# Feb 22 22:51:34.656 INFO circuit_num_constraints: 31490555, target: stats, place: filecoin-proofs/examples/zigzag.rs:255 zigzag, root: filecoin-proofs
# Feb 22 22:55:23.362 INFO groth_parameter_bytes: 13777652280, target: stats, place: storage-proofs/src/parameter_cache.rs:131 storage_proofs::parameter_cache, root: storage-proofs
# Feb 22 22:57:57.967 INFO groth_proving_time: 310.895328636s seconds, target: stats, place: filecoin-proofs/examples/zigzag.rs:272 zigzag, root: filecoin-proofs
# real wall clock proving time = 22:57:57 - 22:55:23 = 2:34 = 154s
# vcpu-seconds = 154s * 28 vcpus = 4312
# FIXME: replication_time here and below is only serial time. It ignores parallel merkle-tree-generation time. Assumes (safely) that was the bottleneck in measured time.
porcuquine_prover = Instance(description="Porcuquine Prover (64GiB, 14 cores)",
                             encoding_replication_time_per_GiB=2588,
                             sector_size=268435456,
                             constraints=31490555,
                             groth_proving_time=4312,
                             vanilla_proving_time=80.99)

# From DIZK vs Bellman table. In vcpu seconds
def projected_proving_time(constraints):
    return constraints * (2.785 * 60 * 6) / 16000000

# [ec2-user@ip-172-31-47-121 rust-fil-proofs]$ ./target/release/examples/zigzag --m 5 --expansion 8 --layers 10 --challenges 333 --taper-layers 7 --taper 0.3 --size 262144 --groth --no-bench --partitions 8
# Feb 28 09:58:40.228 INFO replication_time/GiB: 3197.191021367s, target: stats, place: filecoin-proofs/examples/zigzag.rs:178 zigzag, root: filecoin-proofs
# Feb 28 10:53:37.132 INFO vanilla_proving_time: 3296.904225516 seconds, target: stats, place: filecoin-proofs/examples/zigzag.rs:210 zigzag, root: filecoin-proofs
# Feb 28 13:06:22.781 INFO groth_parameter_bytes: 336470126136, target: stats, place: storage-proofs/src/parameter_cache.rs:164 storage_proofs::parameter_cache, root: storage-proofs
# Feb 28 20:48:29.006 INFO groth_proving_time: 34734.387995685s seconds, target: stats, place: filecoin-proofs/examples/zigzag.rs:274 zigzag, root: filecoin-proofs
# real wall clock proving time = 20:48:29 - 13:06:22 = 7:42:07 = 27727s
# vcpu-seconds = 27727s * 128 vcpus = 3549056
# vcpu-seconds = 27227
# Recalculated withn --bench-only
# Mar 09 20:26:00.146 INFO circuit_num_constraints: 696224603, target: stats, place: filecoin-proofs/examples/zigzag.rs:326 zigzag, root: filecoin-proofs
# Previous projection for constraints was high: 5572568613 (by 2771789)
ec2_x1e32_xlarge = Instance(description='EC2 x1e32.xlarge pedersen',
                            encoding_replication_time_per_GiB=3197,
                            constraints=696224603,
                            sector_size = 268435456,
                            groth_proving_time=3549056,
                            vanilla_proving_time=3297)

projected_instance = Instance(description='EC2 x1e32.xlarge pedersen with projected proof times',
                              encoding_replication_time_per_GiB=3197,
                              constraints=696224603,
                              sector_size = 268435456,
                              groth_proving_time= projected_proving_time(696224603),
                              vanilla_proving_time=3297)



class ZigZag(object):
    """ZigZag Model"""

    def __init__(self, **kwargs):
        self.init_args = kwargs
        self.security = kwargs.get('security', filecoin_security_requirements) # Assume we are using secure params if not otherwise specified.
        self.instance = kwargs.get('instance') # Optional Instance.
        self.circuit_proof_size = kwargs.get('circuit_proof_size', 192) # bytes
        self.hash_size = kwargs.get('hash_size', 32) # bytes
        self.node_size = kwargs.get('hash_size', 32) # bytes
        # TODO: Should we just remove sector_size from this model, since it's
        #  always being varied? Having it here confuses expectations.
        self.size = kwargs.get('size', GiB) # Bytes, default to 1GiB
        # Sector size must be a power of 2.
        assert math.log2(self.size) % 1 == 0
        self.partitions = kwargs.get('partitions', 1)
        self.merkle_hash = kwargs.get('merkle_hash', pedersen)
        self.kdf_hash = kwargs.get('kdf_hash', blake2s)
        assert (self.node_size == self.hash_size)

    def description(self):
        return self.instance and self.instance.description or "undescribed"


    def sector_size(self):
        if self.instance:
            return self.instance.sector_size
        else:
            return self.size

    def merkle_tree(self, size=GiB):
        return MerkleTree(self.nodes(size), self.merkle_hash)

    def comm_d_size(self): return self.hash_size

    def comm_r_size(self): return self.hash_size

    def comm_r_star_size(self): return self.hash_size

    def proof_size(self): return (self.circuit_proof_size * self.partitions) \
                                 + self.comm_d_size() + self.comm_r_size() + self.comm_r_star_size()

    # This can be calculated from taper, etc. later.
    def total_challenges(self): return self.challenges

    def degree(self): return self.base_degree + self.expansion_degree

    def nodes(self, size):
        nodes = size / self.node_size
        assert (nodes % 1) == 0
        return math.floor(nodes)

    def merkle_time(self, n_trees, size=GiB):
        tree_time = self.merkle_tree.time()
        return n_trees * tree_time

    def all_merkle_time(self): return self.merkle_time(self.layers + 1)

    # Per GiB
    def replication_time(self, size=GiB):
        if self.instance:
            # Assumes replication time scales linearly with size.
            return self.instance.replication_time_per_GiB() * (size / GiB)
        else:
            # Calculate a projection, as in the calculator.
            assert false, "unimplemented"

    def vanilla_proving_time(self, size=GiB):
        if self.instance:
            return self.instance.vanilla_proving_time
        else:
            # Calculate a projection, as in the calculator.
            assert false, "unimplemented"

    def groth_proving_time(self, size=GiB):
        if self.instance:
            # FIXME: Calculate ratio of constraints for self.sector_size and
            #  size. Use to calculate groth proving time for size.
            return self.instance.groth_proving_time
        else:
            # Calculate a projection, as in the calculator.
            assert false, "unimplemented"

    def total_proving_time(self, size=GiB):
        return self.vanilla_proving_time(size) + self.groth_proving_time(size)

    def encoding_operations(self):
        return self.nodes(self.sector_size()) * self.security.layers

    def hashing_constraints(self, size):
        # FIXME: This doesn't account for size of kdf vs merkle hash. Set kdf_hash_factor correctly.
        kdf_hash_factor = 1
        merkle_tree = self.merkle_tree(size)
        return merkle_tree.proof_constraints() + (self.kdf_hash.constraints * kdf_hash_factor ) * \
               self.security.total_challenges

    def non_hashing_contraints(self, size):
        return self.instance.constraints - self.hashing_constraints(size)


    def performance(self, size=GiB):
        scale = GiB / size
        seal_time =  scale * (self.replication_time(size) + self.total_proving_time(size))
        proof_size_per_GiB = scale * self.proof_size()
        return Performance(seal_time, proof_size_per_GiB)

    # TODO: This doesn't yet account for the changes to seal time introduced by changing sector size.
    def sector_size_required_to_justify_seal_time(self, required_performance):
        # This works because proof_size is per 1GiB.
        return GiB* self.performance().total_seal_time / required_performance.total_seal_time

    def justifies_seal_time(self, sector_size, required_performance):
        return required_performance.satisfied_by(self.performance(size=sector_size))

    def scaled_for_new_hash(self, new_hash):
        new_init_args = dict(self.init_args)
        # NOTE: This assumes proof size does not change when changing hash, but depending on number of constraints,
        # that may not be accurate — since we may need to add partitions as parameter and memory requirements grow.
        if self.instance:
            constraint_scale = new_hash.constraints / self.merkle_hash.constraints
            instance_size = self.instance.sector_size
            new_hashing_constraints = self.hashing_constraints(instance_size) * constraint_scale
            new_constraints = self.non_hashing_contraints(instance_size) + new_hashing_constraints

            scaled_instance = self.instance.scale(new_constraints, new_hash)

            new_init_args['instance'] = scaled_instance
            new_init_args['merkle_hash'] = new_hash
            return ZigZag(**new_init_args)
        else:
            assert false, "unimplemented"

def minimum_viable_sector_size(performance_requirements, zigzag, guess=GiB, iterations_so_far=0, max_iterations=20):
    if guess < 1: return 0
    #TODO: if guess < minimum sector size for proof size: return the minimum. Need to calculate.
    if iterations_so_far >= max_iterations: return 0

    is_viable = zigzag.justifies_seal_time(guess, performance_requirements)
    if is_viable:
        recur = minimum_viable_sector_size(performance_requirements, zigzag, guess / 2,
                                           iterations_so_far=iterations_so_far + 1,
                                           max_iterations=max_iterations)
        return guess if recur == 0 else recur
    else:
        return minimum_viable_sector_size(performance_requirements, zigzag, guess * 2,
                                          iterations_so_far = iterations_so_far + 1,
                                          max_iterations=max_iterations)

def minimum_viable_sector_size_for_hybrids(performance_requirements, zigzag):
    f = lambda r, n : r *(1/n)

    return [(f(r, 10), humanize_bytes(minimum_viable_sector_size(performance_requirements,
                                                  zigzag.scaled_for_new_hash(hybrid_hash(pedersen, blake2s, f(r,10))))))
            for r in range(0, 11)]

################################################################################
#### Unused so far

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

################################################################################

z = ZigZag(security=filecoin_security_requirements, instance=porcuquine_prover)
print(f"ZigZag nodes: {z.nodes(z.sector_size())}")
