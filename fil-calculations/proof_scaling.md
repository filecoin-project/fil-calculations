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
from util import *
from proofs import *
from proofs_analysis import *
from perf_data import *
import matplotlib.pyplot as plt
import numpy as np
```

```python
filecoin_scaling_requirements.satisfied_by(bad_performance)
```

```python
porcuquine = ZigZag(security=filecoin_security_requirements, instance=porcuquine_prover)
```

```python
x1e32 = ZigZag(security=filecoin_security_requirements, instance=ec2_x1e32_xlarge, partitions=8)
```

```python
x1e32.meets_performance_requirements(512 * GiB, filecoin_scaling_requirements)
```

```python
x1_pb50 = x1e32.scaled_for_new_hash(pb50)
```

```python
x1_blake2s = x1e32.scaled_for_new_hash(blake2s)
```

```python
graph_hash_seal_times(x1e32, filecoin_scaling_requirements)
```

```python
projected_pedersen = ZigZag(security=filecoin_security_requirements, instance=projected_instance, partitions=8)
projected_blake2s = projected_pedersen.scaled_for_new_hash(blake2s)
graph_hash_seal_times(projected_pedersen, filecoin_scaling_requirements)
```

What's the minimum viable sector size for a 50/50 pedersen/blake2s hybrid on x1e32?

```python
humanize_bytes(x1_pb50.minimum_viable_sector_size(filecoin_scaling_requirements))
```

Blake?

```python
humanize_bytes(x1_blake2s.minimum_viable_sector_size(filecoin_scaling_requirements))
```

Pedersen?

```python
humanize_bytes(x1e32.minimum_viable_sector_size(filecoin_scaling_requirements))
```

```python
projected_pedersen = ZigZag(security=filecoin_security_requirements, instance=projected_instance, partitions=8)
projected_blake2s = projected_pedersen.scaled_for_new_hash(blake2s)
```

```python
humanize_bytes(projected_pedersen.minimum_viable_sector_size(filecoin_scaling_requirements))
```

```python
humanize_bytes(projected_blake2s.minimum_viable_sector_size(filecoin_scaling_requirements))
```

```python
projected_blake2s.total_proving_time(128 * GiB)
```

```python
projected_pedersen.total_proving_time(64 * GiB)
```

```python
projected_pedersen.performance(64 * GiB).total_seal_cycles() - filecoin_scaling_requirements.total_seal_cycles()
```

```python
humanize_seconds(filecoin_scaling_requirements.total_seal_time)
```

```python
humanize_seconds(projected_pedersen.performance(512 * GiB).total_seal_time)
```

```python
humanize_seconds(projected_blake2s.performance(512 * GiB).total_seal_time)
```

```python
humanize_seconds(x1e32.performance(256 * GiB).total_seal_time)
```

```python
humanize_seconds(x1_blake2s.performance(256 * GiB).total_seal_time)
```

```python
projected_blake2s.meets_performance_requirements(512*GiB, filecoin_scaling_requirements)
```

```python
filecoin_scaling_requirements
```

```python
projected_blake2s.performance(512*GiB)
```

```python
projected_pedersen.performance(512*GiB)
```

```python

```
