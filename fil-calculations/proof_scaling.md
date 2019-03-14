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
from util import humanize_bytes
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
ec2_x1e32_xlarge.proving_time_per_constraint / porcuquine_prover.proving_time_per_constraint
```

```python
porcuquine = ZigZag(security=filecoin_security_requirements, instance=porcuquine_prover)
```

```python
x1e32 = ZigZag(security=filecoin_security_requirements, instance=ec2_x1e32_xlarge, partitions=8)
```

```python
p = porcuquine.performance()
```

```python
pp = x1e32.performance()
```

```python
p.total_seal_time
```

```python
pp.total_seal_time
```

`pp.total_seal_time` is much higher than `p.total_seal_time` because of 8 partitions and sufficient challenges.

```python
humanize_bytes(p.proof_size)
```

```python
humanize_bytes(pp.proof_size)
```

```python
porcuquine_blake = porcuquine.scaled_for_new_hash(blake2s)
```

```python
porcuquine_blake.performance().total_seal_time
```

```python
porcuquine.meets_performance_requirements(512 * GiB, filecoin_scaling_requirements)
```

```python
x1e32.meets_performance_requirements(512 * GiB, filecoin_scaling_requirements)
```

```python
porcuquine_blake.meets_performance_requirements(512 * GiB, filecoin_scaling_requirements)
```

*TODO*
  - [x] check all against a range of seal times;
  - [x] make graphs
  - [x] try with pedersen/blake hybrid, varying `root_height`
  - [x] search space for a combination of `root_height` and sector size which meets performance requirements


```python
porcuquine_pb50 = porcuquine.scaled_for_new_hash(pb50)
```

```python
porcuquine_pb50.meets_performance_requirements(GiB, filecoin_scaling_requirements)
```

```python
porcuquine_pb50.meets_performance_requirements(512 * GiB, filecoin_scaling_requirements)
```

```python
porcuquine_pb50.meets_performance_requirements(2048 * GiB, filecoin_scaling_requirements)
```

```python
porcuquine_pb50.performance().total_seal_time
```

```python
porcuquine_pb50.performance(2048 * GiB).total_seal_time
```

```python
porcuquine.performance(2048 * GiB).total_seal_time
```

```python
porcuquine.performance().total_seal_time
```

```python
filecoin_scaling_requirements.total_seal_time
```

```python
filecoin_scaling_requirements.proof_size
```

```python
porcuquine.performance().proof_size
```

```python
x1e32.performance(64 * GiB).proof_size
```

```python
x1e32.performance(66 * GiB).proof_size
```

```python
x1e32.performance(66 * GiB).total_seal_time
```

```python
x1e32.performance(2048 * GiB).total_seal_time
```

```python
x1_pb50 = x1e32.scaled_for_new_hash(pb50)
```

```python
x1_pb50.performance(66 * GiB).total_seal_time
```

```python
x1_pb50.performance(2048 * 4 * GiB).total_seal_time
```

```python
x1_blake2s = x1e32.scaled_for_new_hash(blake2s)
```

```python
x1_blake2s.performance(66 * GiB).total_seal_time
```

```python
x1_pb50.meets_performance_requirements(2048 * 4 * GiB, filecoin_scaling_requirements)
```

~~**We have a first firing solution!**~~ [Not anymore…]

```python
x1_blake2s.meets_performance_requirements(2048 * 4 * GiB, filecoin_scaling_requirements)
```

And another. Which has a better (lower) seal time? [**This one is still good, though — with better below.**]

```python
x1_blake2s.performance(8 * 1024 * GiB).total_seal_time < x1_pb50.performance(8 * 1024 * GiB).total_seal_time
```

We have a winner, and by how much?

```python
x1_pb50.performance(8 * 1024 * GiB).total_seal_time / x1_blake2s.performance(8 * 1024 * GiB).total_seal_time
```

Just about double, at that size. Let's try a range, to be sure. TODO: Graph this — but instead of ratio, just include both points and pedersen. Actually just graph a spread of 10 hybrids to make the relationship clear.

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
projected_pedersen.total_proving_time(128 * GiB)
```

Hmmmmm, something is not right with the constraint projection.

```python

```