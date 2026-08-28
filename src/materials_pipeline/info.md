# `pipeline.py`

The processing order is intentional.

First, the raw input must be preserved
```python
raw_path = self.storage.write_raw(...)
```
This measn that if transformation fails, the source record is still available (e.g. for debugging, reprocessing, audit, adapter development)

The we transform the material. Here, the provider-specific adapter controls the mapping into the common model.
```python
material = provider.transform(raw)
```

Finally, the normalised record is preserved. This is only created if transformation is successful.
```python
normalised_path = self.storage.write_normalised(...)
```

We also use `unknown-source` as a means of preserving the raw record, even if it is not valid for the adapter. These will be placed in a provisional folder before provider validation completes:
```text
data/raw/materials_project/unknown-source/
```