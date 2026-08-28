import json
from pathlib import Path

from materials_pipeline.ingestion import (
    calculate_sha256,
)
from materials_pipeline.pipeline import IngestionPipeline
from materials_pipeline.providers.materials_project import (
    MaterialsProjectProvider,
)


def test_pipeline_preserves_and_normalises_record(
    tmp_path: Path,
) -> None:
    pipeline = IngestionPipeline(project_root=tmp_path)

    provider = MaterialsProjectProvider()

    raw = {
        "material_id": "mp-149",
        "formula_pretty": "Si",
        "chemsys": "Si",
        "structure": None,
    }

    result = pipeline.ingest(
        provider=provider,
        raw=raw,
    )

    assert result.status == "accepted"
    assert result.material is not None
    assert result.raw_path is not None
    assert result.normalised_path is not None
    assert result.issues == []

    raw_path = Path(result.raw_path)
    normalised_path = Path(result.normalised_path)

    assert raw_path.exists()
    assert normalised_path.exists()

    saved_envelope = json.loads(raw_path.read_text(encoding="utf-8"))

    assert saved_envelope["payload"]["material_id"] == "mp-149"

    assert (
        calculate_sha256(saved_envelope["payload"]) == saved_envelope["payload_sha256"]
    )

    saved_material = json.loads(normalised_path.read_text(encoding="utf-8"))

    assert saved_material["composition"]["reduced_formula"] == "Si"


def test_pipeline_preserves_rejected_record(
    tmp_path: Path,
) -> None:
    pipeline = IngestionPipeline(project_root=tmp_path)

    provider = MaterialsProjectProvider()

    raw = {
        "formula_pretty": "Si",
        "chemsys": "Si",
        "structure": None,
    }

    result = pipeline.ingest(
        provider=provider,
        raw=raw,
    )

    assert result.status == "rejected"
    assert result.material is None
    assert result.raw_path is not None
    assert result.normalised_path is None

    assert len(result.issues) == 1
    assert result.issues[0].code == "TRANSFORMATION_FAILED"

    assert Path(result.raw_path).exists()

    normalised_files = list((tmp_path / "data" / "normalised").glob("*.json"))

    assert normalised_files == []
