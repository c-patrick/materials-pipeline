# Materials Pipeline

A small Python project for learning how to normalise heterogeneous materials data into a single, provider-agnostic schema.

The goal is to take records from multiple sources such as the Materials Project and other crystallographic or materials databases, map each source into a common Pydantic model, and preserve provenance along the way. The project is intentionally lightweight and educational so that I can focus on data modeling, schema design, provider adapters, and the early steps of ontology-aware materials knowledge engineering.

## Why this project exists

This repository is a practical sandbox for exploring:
* Ontology and knowledge graph concepts in a materials context
* Data normalisation across inconsistent provider schemas
* Pydantic models as a typed, serialisable domain layer
* Provenance tracking for source attribution
* Architecture patterns for multi-provider ingestion pipelines

It is also useful preparation for discussions around materials informatics, data architecture, and knowledge representation.

## Current scope

The project currently includes a simple provider adapter for Materials Project records and a canonical material model that standardises:
* Composition
* Chemical system
* Source provenance
* Optional crystal structure payloads

The pipeline design is intentionally extensible so additional providers can be added in the same pattern.

## Getting started

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install the package in editable mode

```bash
pip install --upgrade pip
pip install -e '.[dev]'
```

### 3. Run the test suite

```bash
pytest -q
```

### 4. Try a minimal transform

```python
from materials_pipeline.providers.materials_project import MaterialsProjectProvider

raw = {
    'material_id': 'mp-149',
    'formula_pretty': 'Si',
    'chemsys': 'Si',
    'structure': None,
}

record = MaterialsProjectProvider().transform(raw)
print(record.model_dump())
```

This returns a normalised material record with a reduced formula, chemical system, and source metadata.

## Repository layout

```text
materials-pipeline/
├── data/
│   ├── raw/
│   ├── normalised/
│   └── rejected/
├── notebooks/
│   └── 01_basic_pipeline.ipynb
├── src/
│   └── materials_pipeline/
│       ├── __init__.py
│       ├── models.py
│       └── providers/
│           ├── __init__.py
│           ├── base.py
│           └── materials_project.py
├── tests/
├── pyproject.toml
├── project-overview.md
├── README.md
└── .gitignore
```

## Next ideas

- Add another provider such as CSD or NOMAD
- Add validation for missing or inconsistent fields
- Unify structure serialisation across providers
- Write a simple ingestion pipeline over raw JSON files
- Explore graph-style linking between materials, formulas, and source records