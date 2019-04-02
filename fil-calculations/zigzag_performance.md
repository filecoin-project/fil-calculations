---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.0'
      jupytext_version: 0.8.6
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

```python
from util import *
from proofs import *
from perf_data import *
from proofs_analysis import *
from dataclasses import replace
```

```python
x1e32_8GiB = ZigZag(security=filecoin_security_requirements, instance=ec2_x1e32_xlarge, partitions=8)
```

```python
x1e32_64GiB = ZigZag(security=filecoin_security_requirements, instance=x1e32_xlarge_64, partitions=8)
```

```python
x1e32_projected = ZigZag(security=filecoin_security_requirements, instance=projected_instance, partitions=8)
x1e32_projected_relaxed = ZigZag(security=filecoin_security_requirements, instance=projected_instance, partitions=8, relax_time=1.25)
```

```python
alternatives = [x1e32_8GiB, x1e32_64GiB, x1e32_projected, x1e32_projected_relaxed]
```

```python
compare_zigzags(alternatives, requirements=filecoin_scaling_requirements)
```

```python
target_sector_size=64*GiB
```

```python
plot_relaxed_requirements(x1e32_projected, filecoin_scaling_requirements, target_sector_size)
```

```python
# Doesn't terminate.
# plot_accelerated_proving(x1e32_projected, filecoin_scaling_requirements, target_sector_size)
```

```python
plot_accelerated_hashing(x1e32_projected, filecoin_scaling_requirements, target_sector_size)
```

```python
x1e32_projected.meets_performance_requirements(64 * GiB, filecoin_scaling_requirements)
```

```python
x1e32_projected_relaxed.meets_performance_requirements(64 * GiB, filecoin_scaling_requirements)
```

```python
pb = x1e32_projected.scaled_for_new_hash(blake2s)
prb = x1e32_projected_relaxed.scaled_for_new_hash(blake2s)
```

```python
humanize_bytes(x1e32_projected.minimum_viable_sector_size(filecoin_scaling_requirements))
```

```python
humanize_bytes(x1e32_projected_relaxed.minimum_viable_sector_size(filecoin_scaling_requirements))
```

```python
humanize_bytes(prb.minimum_viable_sector_size(filecoin_scaling_requirements))
```

```python
humanize_bytes(pb.minimum_viable_sector_size(filecoin_scaling_requirements))
```

```python
accelerated_instance = replace(projected_instance, groth_acceleration=8)
x1e32_accelerated = ZigZag(security=filecoin_security_requirements, instance=accelerated_instance, partitions=8)
x1e32_accelerated_blake2s = x1e32_accelerated.scaled_for_new_hash(blake2s)
```

```python
humanize_bytes(x1e32_accelerated.minimum_viable_sector_size(filecoin_scaling_requirements))
```

```python
humanize_seconds(x1e32_projected.total_seal_time()), humanize_seconds(x1e32_projected.replication_time()), humanize_seconds(x1e32_projected.groth_proving_time())
```

```python
humanize_seconds(x1e32_accelerated.total_seal_time()), humanize_seconds(x1e32_accelerated.replication_time()), humanize_seconds(x1e32_accelerated.groth_proving_time())
```

```python
humanize_seconds(x1e32_accelerated.vanilla_proving_time()), humanize_seconds(x1e32_accelerated.total_proving_time())
```

```python
humanize_seconds(x1e32_accelerated.replication_time(64*GiB) + x1e32_accelerated.total_proving_time())
```

```python
accelerated_instance.replication_time_per_GiB()
```

```python
humanize_seconds(x1e32_accelerated_blake2s.replication_time())
```

```python
humanize_bytes(x1e32_accelerated_blake2s.minimum_viable_sector_size(filecoin_scaling_requirements))
```

Need 8x groth acceleration for 64 GiB.

```python

```
