import hashlib
import json
from collections.abc import Mapping
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID

from pymatgen.core import Structure


def to_json_compatible(value: Any) -> Any:
    """Recursively convert supported values into JSON-compatible data"""

    if value is None or isinstance(value, str | int | float | bool):
        return value

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, UUID):
        return str(value)

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, Structure):
        return value.as_dict()

    if isinstance(value, Mapping):
        return {str(key): to_json_compatible(item) for key, item in value.items()}

    if isinstance(value, list | tuple):
        return [to_json_compatible(item) for item in value]

    raise TypeError(
        f"Cannot convert value to JSON-compatible data: {type(value).__name__}"
    )


# Ordinary JSON serialisation may preserve their different insertion orders and produce different byte sequences and will in turn result in different hashes. So here, we need to use `sort_keys = True` and separatos to create a deterministic representation before calculating the checksum.
def canonical_json(data: Any) -> str:
    """Serialise data deterministically for hashing"""

    compatible_data = to_json_compatible(data)

    return json.dumps(
        compatible_data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def calculate_sha256(data: Any) -> str:
    """Calculate a SHA-256 checksum from canonical JSON"""

    serialised = canonical_json(data)

    return hashlib.sha256(serialised.encode("utf-8")).hexdigest()
