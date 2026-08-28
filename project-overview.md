# Materials Pipeline

This repository is a learning project for building a materials ingestion pipeline that normalizes data from multiple providers into a common, typed data model. The core idea is to take provider-specific representations (for example from the Materials Project or other materials databases), convert them into a consistent Pydantic schema, and preserve source provenance so the data can later be linked into a broader knowledge graph or ontology.

The project is intended as a practical exploration of materials informatics, schema design, data normalization, and knowledge representation, with a focus on the kinds of architectural questions that arise in a Materials Knowledge Architect role.

## Structure
```text
materials-pipeline/
├── notebooks/
│   └── 01_basic_pipeline.ipynb
├── src/
│   └── materials_pipeline/
│       ├── __init__.py
│       ├── models.py
│       ├── providers/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── materials_project.py
│       └── pipeline.py
├── data/
│   ├── raw/
│   ├── normalised/
│   └── rejected/
├── tests/
├── .gitignore
└── pyproject.toml
```
