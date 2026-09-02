"""
Various tools for the materials pipeline.
"""    
import re


def compute_chemsys(formula: str | None, elements: list | None) -> str:
    """Compute the chemical system (chemsys) from a chemical formula or list of elements."""
    chemsys = None
    if elements:
        if isinstance(elements, list):
            chemsys = "-".join(sorted(set(elements)))
        elif isinstance(elements, str):
            # sometimes returned as space-separated string
            parts = elements.split()
            chemsys = "-".join(sorted(set(parts)))

    if not chemsys and isinstance(formula, str) and formula.strip():
        elems = re.findall(r"[A-Z][a-z]*", formula)
        unique = sorted({el for el in elems})
        chemsys = "-".join(unique) if unique else None

    return chemsys