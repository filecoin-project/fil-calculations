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
(lx, _, _, _) = optimize(projected_blake); lx
```

```python
apex_projected_blake = apex(projected_blake, lx)
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
(ly, _, savings, best) = optimize(projected_blake); (l, savings, best)
```

```python
apex_projected_blake = apex(projected_blake, ly)
```

```python
apex_projected_blake.meets_performance_requirements(64*GiB, filecoin_scaling_requirements)
```

```python
apex_projected_blake.constraints() / apex_projected_blake.partitions # how many constraints in each partition
```

```python
ZigZag(partitions=16).proof_size() <= filecoin_scaling_requirements.proof_size * 128 * GiB
```

Let's work through this again with 128 GiB sectors:

```python
simulated128 = ZigZag(security=proofs.filecoin_security_requirements, partitions=8, size=128*GiB, merkle_hash=blake2s)
```

```python
projected.constraints(), projected.constraints(), simulated128.constraints()
```

```python
optimize(projected)
```

```python
humanize_bytes(apex_projected.groth_proving_memory())
```

```python
apex_projected.meets_performance_requirements(128*GiB, filecoin_scaling_requirements)
```

```python
apex_projected_blake.meets_performance_requirements(128*GiB, filecoin_scaling_requirements)
```

```python
apex_projected_blake.meets_performance_requirements(64*GiB, filecoin_scaling_requirements)
```

Still good.

```python
humanize_bytes(apex_projected.minimum_viable_sector_size(filecoin_scaling_requirements))
```

```python
humanize_bytes(apex_projected_blake.minimum_viable_sector_size(filecoin_scaling_requirements))
```

```python
apex_projected.constraints(),  apex_projected_blake.constraints()
```

```python
apex_projected.total_seal_time() / apex_projected_blake.total_seal_time()
```

```python
apex_projected.show_times()
```

```python
apex_projected_blake.show_times()
```

```python
apex_projected.apex_constraints_avoided()/ apex_projected.apex_constraints()
```

```python
apex_projected_blake.apex_constraints_avoided() / apex_projected_blake.apex_constraints()
```

```python
apex_projected.total_seal_time() / projected.total_seal_time()
```

```python
apex_projected.groth_proving_time(), projected.groth_proving_time()
```

```python
projected.show_times()
```

```python
aa.apex_constraints_avoided()
```

```python
(aa.apex_height - 1) * (aa.degree() + 2) * aa.total_challenges() * aa.merkle_hash.constraints **aa.constraint_proving_time
```

```python
aa.constraints()
```

### NOTE

Here is the point at which I realize that we need a distinct apex (and the cost of commiting to it) per layer. Then also, that because parent selection is pseudorandom, we cannot use the trick of bucketing challenges evenly within apex leaves except for the data and replica nodes. Sadness descends on the late night.

```python

```
