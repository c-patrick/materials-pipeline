import pytest

from materials_pipeline.models import ProviderName
from materials_pipeline.providers.materials_project import (
    MaterialsProjectProvider,
)


def test_transform_minimal_materials_project_record() -> None:
    provider = MaterialsProjectProvider()

    raw = {
        "material_id": "mp-149",
        "formula_pretty": "Si",
        "chemsys": "Si",
        "structure": None,
    }

    result = provider.transform(raw)

    assert result.composition.reduced_formula == "Si"
    assert result.composition.chemical_system == "Si"
    assert result.composition.element_amounts == {"Si": 1.0}
    assert result.structure is None

    assert len(result.sources) == 1
    assert result.sources[0].provider == ProviderName.MATERIALS_PROJECT
    assert result.sources[0].source_id == "mp-149"


def test_transform_reduces_composition() -> None:
    provider = MaterialsProjectProvider()

    raw = {
        "material_id": "example-001",
        "formula_pretty": "Si2O4",
        "chemsys": "Si-O",
        "structure": None,
    }

    result = provider.transform(raw)

    assert result.composition.reduced_formula == "SiO2"
    assert result.composition.element_amounts == {
        "Si": 1.0,
        "O": 2.0,
    }


def test_transform_rejects_missing_material_id() -> None:
    provider = MaterialsProjectProvider()

    raw = {
        "formula_pretty": "Si",
        "chemsys": "Si",
        "structure": None,
    }

    with pytest.raises(
        ValueError,
        match="material_id",
    ):
        provider.transform(raw)


def test_transform_rejects_unsupported_structure_type() -> None:
    provider = MaterialsProjectProvider()

    raw = {
        "material_id": "mp-149",
        "formula_pretty": "Si",
        "chemsys": "Si",
        "structure": "not a structure",
    }

    with pytest.raises(
        TypeError,
        match="pymatgen Structure",
    ):
        provider.transform(raw)
