import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class JsonStorage:
    """Write raw and normalised pipeline records to JSON files"""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.raw_directory = project_root / "data" / "raw"
        self.normalised_directory = project_root / "data" / "normalised"
        self.rejected_directory = project_root / "data" / "rejected"

        self._create_directories()

    def _create_directories(self) -> None:
        """Ensure that all pipeline output directories exist"""

        self.raw_directory.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.normalised_directory.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.rejected_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    @staticmethod
    def _write_json(
        path: Path,
        data: dict[str, Any],
    ) -> Path:
        """Write data to JSON without silently overwriting a file"""

        if path.exists():
            raise FileExistsError(f"Refusing to overwrite existing file: {path}")

        path.write_text(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
                allow_nan=False,
            )
            + "\n",
            encoding="utf-8",
        )

        return path

    def write_raw(
        self,
        provider: str,
        source_id: str,
        timestamp_token: str,
        envelope: BaseModel,
    ) -> Path:
        """Write a raw provider envelope"""

        output_directory = self.raw_directory / provider / self._safe_name(source_id)

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = output_directory / (f"{timestamp_token}.json")

        return self._write_json(
            output_path,
            envelope.model_dump(mode="json"),
        )

    def write_normalised(
        self,
        record_id: str,
        material: BaseModel,
    ) -> Path:
        """Write a normalised material record"""

        output_path = self.normalised_directory / f"{self._safe_name(record_id)}.json"

        return self._write_json(
            output_path,
            material.model_dump(mode="json"),
        )

    @staticmethod
    def _safe_name(value: str) -> str:
        """Convert an identifier into a conservative file name."""

        safe_value = "".join(
            character
            for character in value
            if character.isalnum() or character in {"-", "_", "."}
        )

        if not safe_value:
            raise ValueError("The identifier cannot form a safe file name.")

        return safe_value
