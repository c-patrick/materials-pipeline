"""NOMAD API adapter.

Client-agnostic adapter that can fetch a NOMAD entry by `entry_id` or accept
an injected client (for testing). The adapter maps NOMAD responses into a
`RawRecord` dict with keys: `material_id` (entry_id), `formula_pretty`,
`chemsys`, and `structure` (if available).
"""

from __future__ import annotations

from typing import Any

from materials_pipeline.providers.base import RawRecord
from materials_pipeline.tools import compute_chemsys


class NOMADAPIAdapter:
    """Adapter for NOMAD entries.

    The adapter expects either a `client` object with a `get_entry(entry_id)`
    method that returns the NOMAD JSON-like response structure, or it will
    lazily import `requests` and perform an HTTP GET against the public NOMAD
    API when `base_url` is provided.
    """

    def __init__(self, client: Any | None = None, base_url: str | None = None) -> None:
        self.client = client
        self.base_url = base_url or "https://nomad-lab.eu/prod/v1/api/v1"

    def fetch_entry(self, entry_id: str) -> RawRecord:
        """Fetch an entry by id and return a provider-native mapping.

        The returned mapping contains the keys expected by the pipeline's
        normalisers: `material_id`, `formula_pretty`, `chemsys`, `structure`.
        """

        if self.client is not None:
            data = self.client.get_entry(entry_id)
        else:
            # Lazy import to avoid network dependency in tests
            import requests

            url = f"{self.base_url}/entries/{entry_id}"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()

        # Nomad returns envelope with top-level keys like 'entry_id' and 'data'
        entry_id_value = data.get("entry_id") or data.get("calc_id") or entry_id

        # Prefer processed results material fields when present
        results = (
            data.get("data", {}).get("results")
            if data.get("data")
            else data.get("results")
        )

        material = None
        if isinstance(results, dict):
            material = results.get("material")

        # Extract formula: look for descriptive/reduced/hill fields
        formula = None
        if isinstance(material, dict):
            formula = (
                material.get("chemical_formula_reduced")
                or material.get("chemical_formula_descriptive")
                or material.get("chemical_formula_hill")
            )

        # Extract elements list if available
        elements = None
        if isinstance(material, dict):
            elements = material.get("elements") or material.get("elements_exclusive")

        # Structure may be present under topology or other fields; keep raw dict
        # but only return it when it contains plausible structure data (positions,
        # lattice vectors or atoms) to avoid downstream parsing errors.
        structure = None
        if isinstance(material, dict):
            topology = material.get("topology")
            if isinstance(topology, list) and topology:
                # pick the first topology system representative if available
                system = topology[0]
                # Detect presence of structure-like fields
                if any(
                    key in system
                    for key in ("positions", "lattice_vectors", "atoms", "cell")
                ):
                    structure = system

        chemsys = compute_chemsys(formula=formula, elements=elements)

        return {
            "material_id": entry_id_value,
            "formula_pretty": formula or "",
            "chemsys": chemsys,
            "structure": structure,
        }
