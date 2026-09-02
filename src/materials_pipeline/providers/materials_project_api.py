"""Materials Project API adapter.

This module provides a small adapter that uses pymatgen's `MPRester`
to fetch provider-native records and return them as `RawRecord`-style
dicts suitable for the existing `MaterialsProjectProvider` to
transform and normalise.
"""

from mp_api.client import MPRester

from materials_pipeline.providers.base import RawRecord


class MaterialsProjectAPIAdapter:
    """Fetch raw materials data from the Materials Project API.

    The adapter returns a mapping with the same keys the existing
    `MaterialsProjectProvider` expects: `material_id`,
    `formula_pretty`, `chemsys` and `structure`.
    """

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key

    def fetch_material(self, material_id: str) -> RawRecord:
        """Fetch a single material by Materials Project id.

        Returns a mapping that can be passed directly to
        `MaterialsProjectProvider.transform`.
        """

        # Use the context-manager style MPRester where available
        if self.api_key:
            mpr = MPRester(self.api_key)
        else:
            mpr = MPRester()

        # MPRester implements the context manager protocol.
        with mpr as client:
            # Attempt to pull metadata (may be empty)
            data = client.materials.summary.search(
                material_ids=[material_id],
                fields=["formula_pretty", "chemsys", "structure"],
            )

            formula = None
            chemsys = None

            if data:
                entry = data[0]
                formula = entry.formula_pretty
                chemsys = entry.chemsys # Chemsys should be native to Materials Project, so no need to import compute_chemsys here

                # Try to obtain a structure when available
                try:
                    structure = entry.structure
                except (AttributeError, TypeError):
                    # entry.structure may not exist or may be an unexpected type
                    structure = None

        return {
            "material_id": material_id,
            "formula_pretty": formula or "",
            "chemsys": chemsys,
            "structure": structure,
        }
