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
alternatives = [x1e32_8GiB, x1e32_64GiB]
```

```python
compare_zigzags(alternatives, requirements=filecoin_scaling_requirements)
```

```python

```
