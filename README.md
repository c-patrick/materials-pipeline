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

## New features

Since the initial commit, the pipeline has gained several practical features useful for ingestion and provenance tracking:
- Preserve and persist the original source material (raw JSON) alongside any normalised output.
- Write both raw and normalised data files to disk under the `data/` directory so ingestion runs are auditable and reproducible.
- Generate a SHA256 checksum for each ingested source and include it with the normalised record to help detect duplicates and verify integrity.
- Produce a typed `MaterialRecord` (Pydantic) as the canonical, provider-agnostic representation returned by provider adapters.

These behaviors are implemented in the pipeline and storage helpers; see the implementation in [src/materials_pipeline/pipeline.py](src/materials_pipeline/pipeline.py#L1), [src/materials_pipeline/storage.py](src/materials_pipeline/storage.py#L1), and the canonical models in [src/materials_pipeline/models.py](src/materials_pipeline/models.py#L1).

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
from pathlib import Path
from materials_pipeline.providers.materials_project import MaterialsProjectProvider
from materials_pipeline.pipeline import IngestionPipeline

# Set the project root (where `data/` will be created)
project_root = Path(".")

# Create the ingestion pipeline and provider adapter
pipeline = IngestionPipeline(project_root)
provider = MaterialsProjectProvider()

# Example raw provider record (this is preserved to `data/raw/...`)
raw = {
    "material_id": "mp-149",
    "formula_pretty": "Si",
    "chemsys": "Si",
    "structure": None,
}

# Ingest the raw record. This will:
# - compute a SHA256 of the provider payload
# - write the raw envelope to `data/raw/<provider>/<source_id>/<timestamp>.json`
# - transform to a `MaterialRecord`
# - write the normalised record to `data/normalised/<record_id>.json`
result = pipeline.ingest(provider, raw)

print(result.status)
print("raw ->", result.raw_path)
print("normalised ->", result.normalised_path)

# Inspect the canonical MaterialRecord
if result.material is not None:
    print(result.material.record_id, result.material.composition.reduced_formula)

# Read the preserved raw envelope to view the computed checksum
if result.raw_path:
    import json

    envelope = json.loads(Path(result.raw_path).read_text(encoding="utf-8"))
    print("payload_sha256:", envelope.get("payload_sha256"))
```

This returns a normalised material record with a reduced formula, chemical system, and source metadata.

## Repository layout

```text
materials-pipeline/
├── data/
│   ├── raw/           # preserved original provider JSON files
    │   ├── materials_project/
│   ├── normalised/    # returned canonical MaterialRecord JSON files
│   └── rejected/      # invalid or unparseable inputs
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

## Demo Notebooks
### Materials Project API

This project includes a small API adapter and a demo notebook that shows how to fetch
provider-native records from the Materials Project and ingest them through the
pipeline.

- **Provide an API key:** set your Materials Project API key in the `MP_API_KEY`
    environment variable. Example (Linux/macOS):

    ```bash
    export MP_API_KEY=your_materials_project_api_key_here
    ```

- **Interactive demo:** open the notebook `notebooks/02_demo_materials_project_ingest.ipynb`
    in Jupyter Lab / Notebook and run the cells. The notebook will fetch `mp-149` by
    default, preserve the raw payload under `data/raw/...`, and write a normalised
    record to `data/normalised/`.

- **Notes:** the demo uses the `mp_api` client (the `mp_api` Python package).
    If you prefer, the adapter can be run against mocked responses (see the tests
    under `tests/` for examples of how the client is monkeypatched during testing).

## Next ideas

- Add another provider such as CSD or NOMAD
- Add validation for missing or inconsistent fields
- Unify structure serialisation across providers
- Write a simple ingestion pipeline over raw JSON files
- Explore graph-style linking between materials, formulas, and source records