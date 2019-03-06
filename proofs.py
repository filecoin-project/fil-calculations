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

class HashFunction(object):
    ## For now, assume 64 byte input, 32 byte output
    def __init__(self, time, constraints):
        self.hash_time = time # seconds
        self.constraints = constraints

    def time(self):
        return self.hash_time

pedersen = HashFunction(0.000017993, 1324)
blake2s = HashFunction(1.0428e-7, 10324)

class ImplementationConfig(object):
    """Concrete implementations with known benchmarks of fixed parameters on a specific machine."""
    def __init__(self, **kwargs):
        self.replication_time_per_GiB = kwargs.get('replication_time') # seconds
        self.proving_time_per_constraint('constraint_time') # seconds


# ➜  rust-proofs git:(zigzag-example-taper) ✗ ./target/release/examples/zigzag --m 5 --expansion 8 --layers 10 --challenges 5 --size 262144 --groth
# Feb 22 22:47:42.385 INFO replication_time/GiB: 2588.454166843s, target: stats, place: filecoin-proofs/examples/zigzag.rs:176 zigzag, root: filecoin-proofs

porcuquine_256MiB = ImplementationConfig(replication_time=2488.454)

z

current_implementation = Implementation()


class ZigZag(object):
    """ZigZag Model"""

    def __init__(self, **kwargs):
        self.circuit_proof_size = kwargs.get('circuit_proof_size', 192) # bytes
        self.hash_size = kwargs.get('hash_size', 32) # bytes
        self.node_size = kwargs.get('hash_size', 32) # bytes
        self.sector_size = kwargs.get('size', 1024 * 1024 * 1024) # bytes
        # Sector size must be a power of 2.
        assert math.log2(self.sector_size) % 1 == 0

        self.partitions = kwargs.get('partitions', 1)
        self.challenges = kwargs.get('challenges', 8000)
        self.layers = kwargs.get('layers', 10)
        self.base_degree = kwargs.get('base_degree', 5)
        self.expansion_degree = kwargs.get('expansion_degree', 8)
        self.merkle_hash = kwargs.get('merkle_hash', pedersen)


        self.merkle_tree = MerkleTree(self.nodes(), self.merkle_hash)

        assert (self.node_size == self.hash_size)

    def comm_d_size(self):
        return self.hash_size

    def comm_r_size(self):
        return self.hash_size

    def comm_r_star_size(self):
        return self.hash_size

    def proof_size(self):
        return (self.size * self.partitions) + self.comm_d_size() + self.comm_r_size() + self.comm_r_star_size()

    # This can be calculated from taper, etc. later.
    def total_challenges(self):
        return self.challenges

    def degree(self):
        return self.base_degree + self.expansion_degree

    def nodes(self):
        nodes = self.sector_size / self.node_size
        assert (nodes % 1) == 0
        return math.floor(nodes)

    def merkle_time(self, n_trees):
        tree_time = self.merkle_tree.time()
        return n_trees * tree_time

    def all_merkle_time(self):
        return self.merkle_time(self.layers + 1)


    def replication_time(self):
        12345




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
        self.core_hyperthreads = kwargs.get('core_hyperthreads', 2)
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

z = ZigZag()
m = Machine()
c = Config(z, m)

print(f"ZigZag nodes: {z.nodes()}")
