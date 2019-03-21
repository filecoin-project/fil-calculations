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
from perf_data import *
from proofs_analysis import *
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
humanize_bytes(x1e32_projected.minimum_viable_sector_size(filecoin_scaling_requirements))
```

```python
humanize_bytes(x1e32_projected_relaxed.minimum_viable_sector_size(filecoin_scaling_requirements))
```

```python

```
