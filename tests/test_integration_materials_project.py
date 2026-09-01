from pathlib import Path
from types import SimpleNamespace

from materials_pipeline.ingestion import calculate_sha256
from materials_pipeline.pipeline import IngestionPipeline
from materials_pipeline.providers.materials_project import MaterialsProjectProvider


def test_end_to_end_ingest_with_mocked_mp_api(monkeypatch, tmp_path):
    """Integration-style test: mock mp_api client, fetch raw, ingest, assert files."""

    # Prepare a fake entry returned from the mp_api search
    fake_entry = SimpleNamespace(
        formula_pretty="Si",
        chemsys="Si",
        structure=None,
    )

    class FakeMPRester:
        def __init__(self, api_key=None):
            self.api_key = api_key

        def __enter__(self):
            materials = SimpleNamespace(
                summary=SimpleNamespace(
                    search=lambda material_ids, fields: [fake_entry]
                )
            )

            return SimpleNamespace(materials=materials)

        def __exit__(self, exc_type, exc, tb):
            return False

    # Patch the adapter's MPRester
    monkeypatch.setattr(
        "materials_pipeline.providers.materials_project_api.MPRester",
        FakeMPRester,
    )

    # Now perform a live-ish fetch + ingest using temporary project root
    adapter_mod = __import__(
        "materials_pipeline.providers.materials_project_api",
        fromlist=["MaterialsProjectAPIAdapter"],
    )

    MaterialsProjectAPIAdapter = adapter_mod.MaterialsProjectAPIAdapter

    adapter = MaterialsProjectAPIAdapter(api_key=None)

    raw = adapter.fetch_material("mp-149")

    pipeline = IngestionPipeline(project_root=tmp_path)
    provider = MaterialsProjectProvider()

    result = pipeline.ingest(provider=provider, raw=raw)

    assert result.status == "accepted"
    assert result.raw_path is not None
    assert result.normalised_path is not None

    # Check files exist
    raw_path = tmp_path / result.raw_path
    normalised_path = tmp_path / result.normalised_path

    # result.raw_path/normalised_path are strings; ensure correct Path join
    # If paths are absolute they will still exist; otherwise, join with tmp_path
    if not raw_path.exists():
        raw_path = Path(result.raw_path)
    if not normalised_path.exists():
        normalised_path = Path(result.normalised_path)

    assert raw_path.exists()
    assert normalised_path.exists()

    saved_envelope = __import__("json").loads(raw_path.read_text(encoding="utf-8"))

    assert saved_envelope["payload"]["material_id"] == "mp-149"
    assert (
        calculate_sha256(saved_envelope["payload"]) == saved_envelope["payload_sha256"]
    )
