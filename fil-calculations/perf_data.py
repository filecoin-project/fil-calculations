from proofs import Machine, Instance, ZigZag
import proofs

porcuquine_prover_machine = Machine(clock_speed_ghz=3.1, cores=14, ram_gb=64)
ec2_x1e32_xlarge_machine = Machine(clock_speed_ghz=2.3, cores=64, ram_gb=3904)

# ➜  rust-proofs git:(zigzag-example-taper) ✗ ./target/release/examples/zigzag --m 5 --expansion 8 --layers 10 --challenges 5 --size 262144 --groth
# Feb 22 22:47:42.385 INFO replication_time/GiB: 2588.454166843s, target: stats, place: filecoin-proofs/examples/zigzag.rs:176 zigzag, root: filecoin-proofs
# Feb 22 22:49:03.378 INFO vanilla_proving_time: 80.99321579 seconds, target: stats, place: filecoin-proofs/examples/zigzag.rs:208 zigzag, root: filecoin-proofs
# Feb 22 22:51:34.656 INFO circuit_num_constraints: 31490555, target: stats, place: filecoin-proofs/examples/zigzag.rs:255 zigzag, root: filecoin-proofs
# Feb 22 22:55:23.362 INFO groth_parameter_bytes: 13777652280, target: stats, place: storage-proofs/src/parameter_cache.rs:131 storage_proofs::parameter_cache, root: storage-proofs
# Feb 22 22:57:57.967 INFO groth_proving_time: 310.895328636s seconds, target: stats, place: filecoin-proofs/examples/zigzag.rs:272 zigzag, root: filecoin-proofs
# real wall clock proving time = 22:57:57 - 22:55:23 = 2:34 = 154s
# core-seconds = 154s * 14 cores = 2156
# FIXME: replication_time here and below is only serial time. It ignores parallel merkle-tree-generation time. Assumes (safely) that was the bottleneck in measured time.
porcuquine_prover = Instance(description="Porcuquine Prover (64GiB, 14 cores)",
                             encoding_replication_time_per_GiB=2588,
                             sector_size=268435456,
                             constraints=31490555,
                             groth_proving_time=2156,
                             vanilla_proving_time=80.99,
                             layers=10,
                             machine=porcuquine_prover_machine)

# From DIZK vs Bellman table. In core-seconds
# 2.785 minutes for 16M constraints on 6 cores
# TODO/FIXME: Account for clock speed.
def projected_proving_time(constraints):
    optimization_discount = 4/5 # measured on 4GHz machine
    return constraints * (2.785 * 60 * 6) * optimization_discount / 16000000


# [ec2-user@ip-172-31-47-121 rust-fil-proofs]$ ./target/release/examples/zigzag --m 5 --expansion 8 --layers 10 --challenges 333 --taper-layers 7 --taper 0.3 --size 262144 --groth --no-bench --partitions 8
# Feb 28 09:58:40.228 INFO replication_time/GiB: 3197.191021367s, target: stats, place: filecoin-proofs/examples/zigzag.rs:178 zigzag, root: filecoin-proofs
# Feb 28 10:53:37.132 INFO vanilla_proving_time: 3296.904225516 seconds, target: stats, place: filecoin-proofs/examples/zigzag.rs:210 zigzag, root: filecoin-proofs
# Feb 28 13:06:22.781 INFO groth_parameter_bytes: 336470126136, target: stats, place: storage-proofs/src/parameter_cache.rs:164 storage_proofs::parameter_cache, root: storage-proofs
# Feb 28 20:48:29.006 INFO groth_proving_time: 34734.387995685s seconds, target: stats, place: filecoin-proofs/examples/zigzag.rs:274 zigzag, root: filecoin-proofs
# real wall clock proving time = 20:48:29 - 13:06:22 = 7:42:07 = 27727s
# core-seconds = 27727s * 64 cores = 1774528
# Recalculated with --bench-only
# Mar 09 20:26:00.146 INFO circuit_num_constraints: 696224603, target: stats, place: filecoin-proofs/examples/zigzag.rs:326 zigzag, root: filecoin-proofs
ec2_x1e32_xlarge = Instance(description='x1e32.xlarge',
                            encoding_replication_time_per_GiB=3197,
                            constraints=696224603,
                            sector_size = 268435456,
                            groth_proving_time=1774528,
                            vanilla_proving_time=3297,
                            layers=10,
                            machine=ec2_x1e32_xlarge_machine)

old_projected_instance = Instance(description='x1e32.xlarge projected',
                              encoding_replication_time_per_GiB=3197,
                              constraints=696224603,
                              sector_size = 268435456,
                              groth_proving_time= projected_proving_time(696224603),
                              vanilla_proving_time=3297,
                              layers=10,
                              machine=ec2_x1e32_xlarge_machine)

# x1e32.xlarge 64GiB (8 partitions)
# [ec2-user@ip-172-31-35-148 rust-fil-proofs]$ MAXIMIZE_CACHING=1 /usr/bin/time ./target/release/examples/zigzag --m 5 --expansion 8 --layers 10 --challenges 333 --taper-layers 7 --taper 0.3 --size 67108864 --groth --no-bench --dump --no-tmp --partitions 8 > zigzag-333-64GiB.txt 2>&1 &
# Mar 17 13:34:46.698 INFO replication_time: 129225.694359253s, target: stats, place: filecoin-proofs/examples/zigzag.rs:243 zigzag, root: filecoin-proofs
# Mar 17 13:34:46 17 13:34:46.701 INFO replication_time/GiB: 2018.63462912s, target: stats, place: filecoin-proofs/examples/zigzag.rs:262 zigzag, root: filecoin-proofs
# Mar 18 22:18:19.128 INFO circuit_num_constraints: 879643632, target: stats, place: filecoin-proofs/examples/zigzag.rs:325 zigzag, root: filecoin-proofs
# Mar 17 21:49:57.881 INFO groth_parameter_bytes: 393715971000, id: zigzag-proof-of-replication-b8711acf1ed1b26f4ed8694d6cef198e3cf6b05411e9d65605f794d8d1c420a6, target: stats, place: storage-proofs/src/parameter_cache.rs:150 storage_proofs::parameter_cache, root: storage-proofs
# Mar 18 05:58:25.047 INFO groth_proving_time: 29307.162513139s seconds, target: stats, place: filecoin-proofs/examples/zigzag.rs:361 zigzag, root: filecoin-proofs
# Sector size = 67108864 * 1024 = 68719476736
# Real wall clock proving time: 05:58:25 - 21:49:47 = 8:11 = 29460
# core-seconds = 29460 * 64 = 1885440
# vanilla proving time = .497 * 64 = 31.808 seconds
x1e32_xlarge_64 = Instance(description='x1e32.xlarge',
                           encoding_replication_time_per_GiB=2018,
                           constraints=879643632,
                           sector_size = 68719476736,
                           groth_proving_time=1885440,
                           vanilla_proving_time=31.808,
                           layers=10,
                           machine=ec2_x1e32_xlarge_machine)

projected_instance = Instance(description='x1e32.xlarge projected',
                              encoding_replication_time_per_GiB=2018,
                              constraints=879643632,
                              sector_size = 68719476736,
                              groth_proving_time= projected_proving_time(879643632),
                              vanilla_proving_time=31.808,
                              layers=10,
                              machine=ec2_x1e32_xlarge_machine)

filecoin_zigzag = ZigZag(security=proofs.filecoin_security_requirements, instance=projected_instance, partitions=8)

