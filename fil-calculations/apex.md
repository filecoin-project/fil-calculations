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
humanize_seconds(z.groth_proving_time())
```

```python
humanize_seconds(a.groth_proving_time())
```

```python
humanize_seconds(z.groth_proving_time()-a.groth_proving_time())
```

```python
a.groth_proving_time()/z.groth_proving_time()
```

```python
humanize_seconds(z.total_seal_time())
```

```python
humanize_seconds(a.total_seal_time())
```

```python
1 - (a.total_seal_time() / z.total_seal_time())
```

```python
humanize_seconds(a.replication_time())
```

```python
aa.merkle_hash
```

```python

```
