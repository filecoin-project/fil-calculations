"""

Created on Mon Mar 11, 2019
Based on @nicola's ZigZag calculator: https://observablehq.com/d/51563fc39810b60d
@author: @redransil
"""


import math
import copy
from dataclasses import dataclass, replace

from util import humanize_bytes, humanize_seconds

KiB = 1024
MiB = 1024 * KiB
GiB = 1024 * MiB
TiB = 1024 * GiB



# https://docs.google.com/spreadsheets/d/14aqrRyQFTEpxPb5P9quiDW5gUwyS7ShMwgLG-_LihrU/edit#gid=0
# Row 24
# seconds per constraint
constraint_proving_time = ((2.785 * 60 * 6) / 16e6) * 4/5 # 4/5 because 4GHz benchmarks — TODO: move to cycles

# Row 24
# bytes required to prove: bytes per constraint
constraint_ram = 23.1 * GiB / 16e6

@dataclass
class Performance:
    """Performance model, defining time and proof size to securely seal 1GiB."""
    # TODO: rename total_seal_time in notebooks, to disambiguate from ZigZag.total_seal_time and make clear that this
    #  is scaled.
    total_seal_time: float # core-seconds per gigabyte
    proof_bytes: int # per gigabyte
    clock_speed_ghz: float

    def __post_init__(self):
        self.proof_size = self.proof_bytes # per gigabyte

    def total_seal_cycles(self):
        return self.total_seal_time * self.clock_speed_ghz * (10**9)

    # Proof size per sector size. Defaults to standard 1 GiB
    def proof_size(self, sector_size=GiB):
        return self.proof_bytes * (sector_size/GiB)

    # Does other have performance greater than or equal to self in all dimensions?
    def satisfied_by(self, other):
        return (other.total_seal_cycles() <= self.total_seal_cycles()) and (other.proof_size <= self.proof_size)


# Factor by which to relax the CPU time requirement for experiments.
global_time_relaxation = 1
filecoin_scaling_requirements = Performance(60*60*global_time_relaxation, 26, 5.0)
good_performance = Performance(100, 10, 6.6)
bad_performance = Performance(100000000000, 99999999, 1.1)

assert filecoin_scaling_requirements.satisfied_by(good_performance)
assert not filecoin_scaling_requirements.satisfied_by(bad_performance)

@dataclass
class Security:
    base_degree: int
    expansion_degree: int
    layers: int
    total_challenges: int
    sloth_iter: int=0

    def satisfied_by(self, other):
        return (other.base_degree >= self.base_degree) and (other.expansion_degree >= self.expansion_degree) \
            and (other.layers >= self.layers) and (other.sloth_iter >= self.sloth_iter) \
            and (other.total_challenges >= self.total_challenges)

# FIXME: What is the exact real number of challenges?
filecoin_security_requirements = Security(base_degree=5, expansion_degree=8, layers=10, sloth_iter=0,
                                          total_challenges=8848)

@dataclass
class HashFunction:
    ## For now, assume 64 byte input, 32 byte output
    hash_time: float
    constraints: int

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

#pedersen = HashFunction(0.000017993, 1324)
# Based on Merklepor, size 1024 (path length 6), 1 challenge = 6914 constraints; 2 challenges = 13827


#pedersen = HashFunction(.000022074, 1152)
pedersen = HashFunction(0.000017993, 1152)

blake2s = HashFunction(1.0428e-7, 10324)

pb50 = hybrid_hash(pedersen, blake2s, 0.5)

@dataclass
class MerkleTree:
    nodes: int
    hash_function: HashFunction
    apex_height: int=0

    def __post_init__(self):
        assert self.apex_height != 1, "apex_height of 1 is undefined"
        self.height = self.tree_height(self.nodes)

    def apex_leaves(self):
        return 2 ** (self.apex_height - 1)

    # Hashes required to build tree.
    def hash_count(self):
        apex_count = self.apex_leaves() - 1
        return (self.nodes - 1) - apex_count

    # Assuming no parallelism
    def time(self):
        return self.hash_function.time() * self.hash_count()

    # FIXME: This probably never makes sense to calculate. Probably remove.
    def constraints(self):
        return self.hash_function.constraints * self.hash_count()

    def proof_hashes(self):
        # excludes root, which is never hashed.
        path_length = self.height - 1
        return path_length - (self.apex_height - 1)

    def proof_constraints(self):
        return self.proof_hashes() * self.hash_function.constraints

    @staticmethod
    def tree_height(leaves):
        return math.ceil(math.log2(leaves)) + 1

@dataclass
class Machine:
    """Machine Model"""
    clock_speed_ghz: float
    ram_gb: float=None # Gib
    cores: int=None
    hourly_cost: float=None

# TODO: Make it so this can be extracted directly (and correctly) from the JSON results of the zigzag example.
@dataclass
class Instance:
    encoding_replication_time_per_GiB: int
    sector_size: int
    constraints: int
    groth_proving_time: float
    machine: Machine
    description: str="undescribed"
    merkle_tree_hash: HashFunction=pedersen
    layers: int=11 # FIXME: require this parameter.
    vanilla_proving_time: float=0
    security: Security=filecoin_security_requirements
    """Concrete implementations with known benchmarks of fixed parameters on a specific machine."""

    def __post_init__(self):
        self.proving_time_per_constraint = self.groth_proving_time / self.constraints
        assert self.constraints, "constraints required"
        return self

    def merkle_tree_replication_time_per_GiB(self):
        # FIXME: Don't hard-code 32.
        return MerkleTree(GiB / 32, self.merkle_tree_hash).time() * (self.layers + 1)  # Grrr... layers doesn't really
        # belong in Instance, but we need it here. Move to ZigZag in refactor.

    def replication_time_per_GiB(self):
        return self.encoding_replication_time_per_GiB + self.merkle_tree_replication_time_per_GiB()

    def scale(self, constraints, new_merkle_hash):
        # TODO: mirror more sophisticated constraint calculation for replication time.
        return replace(self,
                       merkle_tree_hash=new_merkle_hash,
                       constraints=constraints,
                       groth_proving_time=self.proving_time_per_constraint * constraints)

@dataclass
class ZigZag:
    """ZigZag Model"""

    instance: Instance=None
    circuit_proof_size: int=192 # bytes
    hash_size: int=32
    size: int=None # bytes
    partitions: int=1
    merkle_hash: HashFunction=pedersen
    kdf_hash: HashFunction=blake2s
    security: Security=filecoin_security_requirements
    merkle_pessimization: float=1.5 # Factor to make merkle tree generation more realistic than assuming raw hash speed.
    # FIXME: I added this here in order to merge @redransil's energy work in simply.
    # However, this really should live in the Machine model.
    processor_power: float=165 # watts
    relax_time: int=1
     # FIXME: since we're forced to hard-code performance, should we instead just default to a baseline instance?
    constraint_proving_time: int=constraint_proving_time # seconds per constraint
    apex_height: int=0
    def __post_init__(self):
        self.node_size = self.hash_size
        assert (self.node_size == self.hash_size)
        if self.instance:
            # size is only intended for when no instance is present. This should be refactored somehow over time.
            assert not self.size, "size may not be specified when instance is provided."
            self.size = self.instance.sector_size
        elif not self.size:
            self.size = GiB

        assert math.log2(self.size) % 1 == 0
        return self

    def description(self):
        return  (self.instance.description if self.instance else "undescribed") + f" ({humanize_bytes(self.instance.sector_size)})"

    def sector_size(self):
        return self.instance.sector_size if self.instance else self.size

    def merkle_tree(self, size=GiB):
        return MerkleTree(self.nodes(size), self.merkle_hash, apex_height=self.apex_height)

    def comm_d_size(self): return self.hash_size
    def comm_r_size(self): return self.hash_size
    def comm_r_star_size(self): return self.hash_size

    def proof_size(self): return (self.circuit_proof_size * self.partitions) \
                                 + self.comm_d_size() + self.comm_r_size() + self.comm_r_star_size()

    # This can be calculated from taper, etc. later.
    def total_challenges(self): return self.security.total_challenges

    def degree(self): return self.security.base_degree + self.security.expansion_degree

    def nodes(self, size):
        nodes = (size or self.sector_size()) / self.node_size
        assert (nodes % 1) == 0
        return math.floor(nodes)

    def merkle_time(self, n_trees):
        tree_time = self.merkle_tree().time() * self.merkle_pessimization
        return n_trees * tree_time

    def all_merkle_time(self): return self.merkle_time(self.security.layers + 1)


    # How many encoding operations does it take to replicate?
    def encoding_operations(self):
        return self.nodes(self.sector_size()) * self.security.layers

    # replicate_min is calculated minimum replication speed i.e. wall clock time.
    def replicate_min(self, size=None):
        nodes = self.nodes(size or self.sector_size())
        parents = self.security.base_degree + self.security.expansion_degree
        parents_hashing = ((parents + 1) / 2) * self.kdf_hash.time()
        kdf_time = parents_hashing * nodes * self.security.layers
        sloth = self.security.sloth_iter * nodes * self.security.layers
        return kdf_time + sloth

    # replicate_max is calculated total replication cpu time.
    def replicate_max(self, size = None):
        return self.replicate_min(size) + self.merkle_tree(size).time() * (self.security.layers + 1) * \
               self.merkle_pessimization # FIXME: unify with merkle_time

    # CPU time
    def replication_time(self, size=GiB):
        size = size or self.sector_size() # In case None is passed explicitly, which is a pattern used here.
        if self.instance:
            # TODO: This is horrible, but okay since hash time is so small (tiny negative time when no apex at all).
            apex_merkle_time = ((self.merkle_tree().apex_leaves() - 1) * self.merkle_hash.hash_time) * (self.security.layers + 1)
            # Assumes replication time scales linearly with size.
            return (self.instance.replication_time_per_GiB() - (apex_merkle_time * self.merkle_tree().nodes
                                                                * self.node_size )) * (size / GiB)
        else:
            return self.replicate_max(size)

    ############################################################################
    # Energy requirements include processor but not the rest of system
    # (cooling, memory, disk, etc)

    def replicate_energy(self):
        # returns in Wh
        # Use replicate_max time: even if you parallelize, you're still running
        # for this amount of cumulative time across all processors
        # for reference, one BTC transaction uses ~430 kWh
        # one household uses ~10 kWh/year
        replicate_time_hours = self.replicate_max()/3600
        return replicate_time_hours*self.processor_power # TODO: processor power belongs im machine. So?

    def snark_energy(self):
        # returns in Wh
        # Using the non-parallelizable version of constraint estimates
        # This has to be wrong; is giving GWh/GB
        snark_time_hours = self.groth_proving_time()/3600
        return snark_time_hours * self.processor_power
    ############################################################################

    # Calculate vanilla proving time for data of size.p
    def vanilla_proving_time(self, size=None):
        if self.instance:
            return self.instance.vanilla_proving_time
        else:
            # TODO: Calculate a projection, as in the calculator.
            return 0 # Vanilla proving time is cheap enough now that we can use 0 as an approximation when we need to.

    # Calculate groth proving time for data of size.
    def groth_proving_time(self, size=None):
        size = size or self.sector_size()
        if self.instance:
            # assert (not size) or  (size == self.sector_size()),\
            #     "cannot specify a size to groth_proving_time when Instance is present."
            # FIXME: Calculate ratio of constraints for self.sector_size and
            #  size. Use to calculate groth proving time for size.
            base_time = self.instance.groth_proving_time
            total_apex_constraints = (self.net_apex_constraints() * self.partitions)
            return base_time + total_apex_constraints * self.constraint_proving_time
        else:
            return self.constraints(size) * (0.01469 / 1000)  # FIXME: don't hard code this.


    # Calculate total_proving_time for data of `size`
    def total_proving_time(self, size=None):
        size = size or self.sector_size()
        return self.vanilla_proving_time(size) + self.groth_proving_time(size)

    # Constraints used to verify the commitment to the apex leaves.
    def apex_constraints(self):
        if self.apex_height > 0:
            # divide by two if we can avoid merkle-damgard TODO: how actually calculate this?
            return ((self.merkle_tree().apex_leaves() - 1) * self.merkle_hash.constraints) / 2
        else:
            return 0

    def apex_constraints_avoided(self):
        if self.apex_height > 0:
            return (self.apex_height - 1) * (self.degree() + 2) * self.total_challenges() * self.merkle_hash.constraints \
                   * self.constraint_proving_time
        else:
            return 0

    def net_apex_constraints(self):
        return self.apex_constraints() - self.apex_constraints_avoided()

    def constraints(self, size=None):
        if self.instance:
            non_apex_constraints = self.instance.constraints # * self.partitions
            return non_apex_constraints + self.net_apex_constraints()
        else:
            # NOTE: when no instance, return ONLY hashing constraints — for use in relative calculations.
            return self.hashing_constraints(size)

    # (Approximately) how many bytes of RAM are needed to run one partition's circuit?
    def groth_proving_memory(self):
        return self.constraints() * constraint_ram

    # How many hashing constraints due to hashing does the instance's circuit proof have?
    # NOTE: This is not the number of hashes required to build the merkle trees — which happens outside of circuits.
    def hashing_constraints(self, size=None):
        parents = self.degree()
        kdf_hashes = (parents + 1) / 2 # From ZigZag calculator.
        merkle_tree = self.merkle_tree(size or self.sector_size())
        return ((merkle_tree.proof_constraints() * (parents + 2)) + (self.kdf_hash.constraints * kdf_hashes)) * \
               (self.security.total_challenges / self.partitions)

    # How many hashing constraints not due to hashing does the instance's circuit proof have?
    def non_hashing_contraints(self):
        return self.constraints() - self.hashing_constraints()

    def total_seal_time(self, size=None):
        effective_size  = size or self.sector_size()
        return (self.replication_time(effective_size) + self.total_proving_time(effective_size))

    # Create a Performance object based on this ZigZag's calculated stats.
    def performance(self, size=GiB):
        scale = GiB / size
        seal_time =  scale * self.total_seal_time(size) / self.relax_time
        proof_size_per_GiB = scale * self.proof_size()
        clock_speed_ghz = self.instance.machine.clock_speed_ghz
        return Performance(seal_time, proof_size_per_GiB, clock_speed_ghz)

    # Does this ZigZag's performance with the given sector_size satisfy the required_performance requirements?
    def meets_performance_requirements(self, sector_size, required_performance):
        return required_performance.satisfied_by(self.performance(size=sector_size))

    def scaled_for_new_hash(self, new_hash):
        # NOTE: This assumes proof size does not change when changing hash, but depending on number of constraints,
        # that may not be accurate — since we may need to add partitions as parameter and memory requirements grow.
        if self.instance:
            constraint_scale = new_hash.constraints / self.merkle_hash.constraints
            old_hashing_constraints = self.hashing_constraints()
            new_hashing_constraints = old_hashing_constraints * constraint_scale
            new_constraints = self.non_hashing_contraints() + new_hashing_constraints

            scaled_instance = self.instance.scale(new_constraints, new_hash)

        # Set size None so it defaults. Illegal to pass since it might conflict with instance.
            return replace(self, instance=scaled_instance, merkle_hash=new_hash, size=None)
        else:
            assert False, "unimplemented"

    # Find the minimum viable sector size, which must be a power of 2 (assuming the initial guess is).
    def minimum_viable_sector_size(self, performance_requirements, guess=GiB, iterations_so_far=0,
                                   max_iterations=20):
        if guess < 1: return None
        #TODO: if guess < minimum sector size for proof size: return the minimum. Need to calculate.
        if iterations_so_far >= max_iterations: return 0

        # If guess is viable, search for a smaller solution, starting with 1/2 the current guess.
        if self.meets_performance_requirements(guess, performance_requirements):
            smaller_solution = self.minimum_viable_sector_size(performance_requirements, guess / 2,
                                               iterations_so_far=iterations_so_far + 1,
                                               max_iterations=max_iterations)
            return smaller_solution or guess
        # Otherwise, a larger one, starting with twice the current guess.
        else:
            return self.minimum_viable_sector_size(performance_requirements, guess * 2,
                                              iterations_so_far = iterations_so_far + 1,
                                              max_iterations=max_iterations)

    def minimum_viable_sector_size_for_hybrids(self, performance_requirements):
        f = lambda r, n : r *(1/n)
        scaled = zigzag.scaled_for_new_hash(hybrid_hash(pedersen, blake2s, f(r,10)))

        return [(f(r, 10), humanize_bytes(scaled.minimum_viable_sector_size(performance_requirements)))
                for r in range(0, 11)]

    def show_times(self, time=None):
        print(f"groth: {humanize_seconds(self.groth_proving_time(time))}; replication: {humanize_seconds(self.replication_time(time))}; seal: {humanize_seconds(self.total_seal_time(time))}")


################################################################################
#### Unused so far

@dataclass
class Config:
    """Configuration Model"""
    replication_machine: Machine
    proving_machine: Machine
    zigzag: ZigZag



################################################################################

z = ZigZag(security=filecoin_security_requirements, partitions=8)
print(f"ZigZag nodes: {z.nodes(z.sector_size())}")

constraint_test = ZigZag(security=Security(base_degree=5, expansion_degree=2, layers=2, total_challenges=2),
                         merkle_hash=pedersen,
                         instance=Instance(constraints=301624, groth_proving_time=2.1, sector_size=1024,
                                           encoding_replication_time_per_GiB=72858, layers=2,
                                           machine=Machine(clock_speed_ghz=3.1)))
