from datetime import datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ProviderName(StrEnum):
    """Data providers supported by the ingestion pipeline"""

    MATERIALS_PROJECT = "materials_project"
    NOMAD = "nomad"
    CSD = "csd"


class SourceReference(BaseModel):
    """Identified the provider record from which the data originated"""

    provider: ProviderName
    source_id: str
    retrieved_at: datetime
    source_url: str | None = None


class CompositionRecord(BaseModel):
    """Provider-agnostic representation of a material composition"""

    reduced_formula: str
    chemical_system: str
    element_amounts: dict[str, float]


class CrystalStructureRecord(BaseModel):
    """Serialisable representation of a periodic crystal structure"""

    pymatgen_data: dict[str, Any]


class MaterialRecord(BaseModel):  # This represents the normalised scientific data
    """A normalised material record produced by this pipeline"""

    record_id: UUID = Field(default_factory=uuid4)
    composition: CompositionRecord
    structure: CrystalStructureRecord | None = None
    sources: list[SourceReference] = Field(default_factory=list)
    # default_factory is used to create a new UUID for each MaterialRecord (similarly for sources, which creates a new list for each model isntance)


class RawEnvelope(BaseModel):  # This represents what entered the pipeline
    """Immutable metadata and payload captured from a provider"""

    provider: ProviderName
    source_id: str
    retrieved_at: datetime
    adapter_version: str
    payload_sha256: str
    payload: dict[str, Any]


class IngestionIssue(BaseModel):
    """A warning or error encountered during ingestion"""

    code: str
    severity: Literal["warning", "error"]
    message: str
    field: str | None = None


class IngestionResult(BaseModel):  # This represents what happened during processing
    """Summary of one completed ingestion attempt"""

    status: Literal[
        "accepted",
        "accepted_with_warnings",
        "rejected",
    ]
    provider: ProviderName
    source_id: str
    raw_path: str | None = None
    normalised_path: str | None = None
    material: MaterialRecord | None = None
    issues: list[IngestionIssue] = Field(default_factory=list)
