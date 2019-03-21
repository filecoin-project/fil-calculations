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
projected = ZigZag(security=proofs.filecoin_security_requirements, instance=projected_instance, partitions=8, size=64*GiB)
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

```
