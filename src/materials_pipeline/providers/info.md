# `__init__.py`

The `__all__` variable documents the public objects intentionally exposed by this module. We can therefore do:
```python
from materials_pipeline.providers import MaterialProvider
```
rather than
```python
from materials_pipeline.providers.base import MaterialProvider
```


# `base.py`

`RawRecord` is a type alias (it represents a dictionary-like provider record containing arbitrary values):
```python
RawRecord = Mapping[str, Any]
```

The abstract class establishes a contract
```python
transform(raw) -> MaterialRecord
```

Where every future provider adapter must accept the provider-native data and return the same internal model
```text
Materials Project dictionary → MaterialRecord
NOMAD dictionary             → MaterialRecord
CSD object                   → MaterialRecord
```