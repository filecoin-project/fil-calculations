---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.0'
      jupytext_version: 1.0.3
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

```python
from apex import *
from proofs import *
from perf_data import *
```

```python
z = ZigZag(security=proofs.filecoin_security_requirements, partitions=8, size=64*GiB, merkle_hash=pedersen)
```

```python
(l1, savings, savings_, best_) = optimize(z); (l, savings, savings_, best_)
```

```python
a = apex(z, l); a
```

```python
zz = ZigZag(security=proofs.filecoin_security_requirements, partitions=8, size=64*GiB, merkle_hash=blake2s)
```

```python
(ll, savings, savings_, best_) = optimize(zz); (ll, savings, savings_, best_)
```

```python
aa = apex(zz, ll); aa
```

```python
z.show_times()
```

```python
a.show_times()
```

```python
a.groth_proving_time()/z.groth_proving_time()
```

```python
zz.show_times()
```

```python
aa.show_times()
```

```python
aa.groth_proving_time()/zz.groth_proving_time()
```

```python
zz.constraints()
```

```python
aa.constraints()
```

```python
zz.constraints() - aa.constraints()
```

```python
aa.constraints() / zz.constraints()
```

```python
projected = ZigZag(security=proofs.filecoin_security_requirements, instance=projected_instance, partitions=8)
```

```python
optimize(projected)
```

```python
apex_projected = apex(projected, 13)
```

```python
apex_projected.show_times(64*GiB)
```

```python
apex_projected.meets_performance_requirements(64*GiB, filecoin_scaling_requirements)
```

```python
projected_blake = projected.scaled_for_new_hash(blake2s)
```

```python
optimize(projected_blake)
```

```python
apex_projected_blake = apex(projected_blake, 17)
```

```python
apex_projected_blake.show_times(64 * GiB)
```

```python
projected_blake.show_times(64 * GiB)
```

```python
projected_blake.meets_performance_requirements(64*GiB, filecoin_scaling_requirements)
```

```python
(l, _, savings, best) = optimize(projected_blake); (l, savings, best)
```

```python
apex_projected_blake = apex(projected_blake, 17)
```

```python
apex_projected_blake.meets_performance_requirements(64*GiB, filecoin_scaling_requirements)
```

### OUTDATED
**Yes!** This will meet scaling requirements. We need to consider how large the circuits are. We also need to repartition so the first layer of challenges is a power of 2.

```python
apex_projected_blake.constraints() / apex_projected_blake.partitions # how many constraints in each partition
```

This is huge. So we will need to go 128-GiB sectors. However, that means we can go up to 16 partitions. Verify that: (TODO — should be a simpler way to ask for only this.)~

Actually I failed to divide by partitions the first time, so the below is unncessary.

```python
ZigZag(partitions=16).proof_size() <= filecoin_scaling_requirements.proof_size * 128 * GiB
```

Let's work through this again with 128 GiB sectors:

```python
projected128 = ZigZag(security=proofs.filecoin_security_requirements, instance=projected_instance, partitions=8)
```

```python
simulated128 = ZigZag(security=proofs.filecoin_security_requirements, partitions=8, size=128*GiB, merkle_hash=blake2s)
```

```python
projected.constraints(), projected128.constraints(), simulated128.constraints()
```

```python
optimize(projected128)
```

```python
apex_projected128 = apex(projected128, 13)
```

```python
apex_projected128
```

```python
humanize_bytes(apex_projected128.groth_proving_memory())
```

```python
apex_projected128.meets_performance_requirements(128*GiB, filecoin_scaling_requirements)
```

```python

```

```python
projected_blake128 = projected128.scaled_for_new_hash(blake2s)
```

```python
optimize(projected_blake128)
```

```python
apex_projected_blake128 = apex(projected_blake128, 17)
```

```python
apex_projected_blake128.meets_performance_requirements(128*GiB, filecoin_scaling_requirements)
```

Still good.

```python
(apex_projected_blake128.constraints(), apex_projected_blake.constraints())
```

```python
apex_projected_blake128.merkle_time(100)
```

```python
apex_projected_blake128.replication_time()
```

```python
apex_projected_blake128.merkle_pessimization=100
```

```python
apex_projected_blake128.meets_performance_requirements(128*GiB, filecoin_scaling_requirements)
```

```python
apex_projected_blake128.replication_time()
```

```python
apex_projected_blake128.show_times()
```

```python
apex_projected_blake128.constraints() * constraint_ram
```

```python
apex_projected_blake128.partition_constraints()
```

```python
humanize_bytes(apex_projected_blake128.partition_constraints() * constraint_ram)
```

```python
humanize_bytes((apex_projected_blake128.constraints() / 32) * constraint_ram)
```

```python

```

```python

```
