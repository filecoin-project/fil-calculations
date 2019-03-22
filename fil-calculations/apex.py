import copy

import proofs
from proofs import ZigZag, MerkleTree, GiB
from util import *
from perf_data import *

from dataclasses import dataclass, replace

def optimize_zigzag(zigzag, apex_height):
    123

def total_cost(zigzag, apex_height, replication_hash_fn, proof_constraints_fn):
    optimized = optimize_zigzag(zigzag, apex_height)
    return optimized.total_seal_time()

def tree_height(sector_size):
    MerkleTree.tree_height(sector_size / 32)
    
def apex_savings(zigzag, apex_height, optimization_fn):
    base_cost = zigzag.total_seal_time()
    optimized = optimization_fn(zigzag, apex_height)
    optimized_cost = optimized.total_seal_time()

    savings = base_cost - optimized_cost
    return (savings, optimized_cost)

def optimal_apex(zigzag, optimization_fn):
    best_savings = 0
    best_l = 0
    actual_best = zigzag.total_seal_time()
    savings = 0
    # apex height 1 is undefined
    for l in range(2, zigzag.merkle_tree().height):
        (savings, actual) = apex_savings(zigzag, l, optimization_fn)
        if savings > best_savings:
            best_savings = savings
            actual_best = actual
            best_l = l

    return (best_l, best_savings, humanize_seconds(best_savings), humanize_seconds(actual_best))


def optimize(zigzag):
    return optimal_apex(zigzag, apex)

#######################################################
# Optimization Functions

def identity(zigzag, _apex_height): return zigzag

def apex(zigzag, apex_height):
    optimized = copy.deepcopy(zigzag)
    optimized.apex_height = apex_height

    return optimized

#######################################################

z = ZigZag(security=proofs.filecoin_security_requirements, partitions=8, size=64*GiB)
(l, _, _, _) = optimize(z)
a = apex(z, l)


zz = ZigZag(security=proofs.filecoin_security_requirements, partitions=8, size=64*GiB, merkle_hash=proofs.blake2s)
(l, _, _, _) = optimize(zz)
aa = apex(zz, l)

x = ZigZag(security=proofs.filecoin_security_requirements, instance=projected_instance, partitions=8)
(l, _, _, _) = optimize(x)
y = apex(x, l)
#y = apex(x, 17)

xx = x.scaled_for_new_hash(proofs.blake2s)
(l, _, _, _) = optimize(xx)
yy = apex(xx, l)
#yy = apex(xx,17)
