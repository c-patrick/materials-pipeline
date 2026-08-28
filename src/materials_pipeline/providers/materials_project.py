from datetime import UTC, datetime
from typing import Any

from pymatgen.core import Composition, Structure

from materials_pipeline.models import (
    CompositionRecord,
    CrystalStructureRecord,
    MaterialRecord,
    ProviderName,
    SourceReference,
)
from materials_pipeline.providers.base import MaterialProvider, RawRecord


class MaterialsProjectProvider(MaterialProvider):
    """Transform Materials Project records into the common data model"""

    provider_name = ProviderName.MATERIALS_PROJECT

    def transform(self, raw: RawRecord) -> MaterialRecord:
        """Transform one Materials Project record"""

        # Check the provider requirements before domain-model construction
        # (An absent or blank materials project ID is an adapter error)
        source_id = self._require_string(raw, "material_id")
        formula = self._require_string(raw, "formula_pretty")

        composition = self._build_composition(
            formula=formula,
            supplied_chemical_system=raw.get("chemsys"),
        )

        structure = self._build_structure(raw.get("structure"))

        # Create provenance
        source = SourceReference(
            provider=self.provider_name,
            source_id=source_id,
            retrieved_at=datetime.now(UTC),
            source_url=(f"https://materialsproject.org/materials/{source_id}"),
        )

        return MaterialRecord(
            composition=composition,
            structure=structure,
            sources=[source],
        )

    @staticmethod
    def _require_string(raw: RawRecord, field_name: str) -> str:
        """Read and validate a required non-empty string field"""

        value = raw.get(field_name)

        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f'Required field "{field_name}" must be a non-empty string.'
            )

        return value.strip()

    @staticmethod
    def _build_composition(
        formula: str,
        supplied_chemical_system: Any,
    ) -> CompositionRecord:
        """Create a normalised composition using pymatgen"""

        # Normalise the composition (instead of tusting the provider's formula formatting)
        pymatgen_composition = Composition(formula)

        # Reduce the composition
        reduced_composition = pymatgen_composition.reduced_composition

        derived_chemical_system = "-".join(
            sorted(element.symbol for element in pymatgen_composition.elements)
        )

        if (
            isinstance(supplied_chemical_system, str)
            and supplied_chemical_system.strip()
        ):
            chemical_system = "-".join(
                sorted(supplied_chemical_system.strip().split("-"))
            )
        else:
            chemical_system = derived_chemical_system

        return CompositionRecord(
            reduced_formula=pymatgen_composition.reduced_formula,
            chemical_system=chemical_system,
            element_amounts={
                element: float(amount)
                for element, amount in reduced_composition.get_el_amt_dict().items()
            },
        )

    @staticmethod
    def _build_structure(
        raw_structure: Any,
    ) -> CrystalStructureRecord | None:
        """Convert supported structure representations to serialisable data"""

        if raw_structure is None:
            return None

        if isinstance(raw_structure, Structure):
            return CrystalStructureRecord(pymatgen_data=raw_structure.as_dict())

        if isinstance(raw_structure, dict):
            structure = Structure.from_dict(raw_structure)

            return CrystalStructureRecord(pymatgen_data=structure.as_dict())

        raise TypeError(
            "The Materials Project structure must be a pymatgen Structure, "
            "a serialized structure dictionary, or None."
        )
