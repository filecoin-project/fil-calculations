from proofs import Instance
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
