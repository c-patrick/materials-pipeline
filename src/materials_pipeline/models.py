from datetime import datetime
from enum import StrEnum
from typing import Any
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


class MaterialRecord(BaseModel):
    """A normalised material record produced by this pipeline"""

    record_id: UUID = Field(default_factory=uuid4)
    composition: CompositionRecord
    structure: CrystalStructureRecord | None = None
    sources: list[SourceReference] = Field(default_factory=list)
    # default_factory is used to create a new UUID for each MaterialRecord (similarly for sources, which creates a new list for each model isntance)
