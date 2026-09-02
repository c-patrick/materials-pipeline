from pathlib import Path

from materials_pipeline.ingestion import calculate_sha256
from materials_pipeline.pipeline import IngestionPipeline
from materials_pipeline.providers.nomad import NomadProvider


def test_end_to_end_nomad_ingest(tmp_path):
    fake_material = {
        "chemical_formula_reduced": "CuH3NiO4",
        "elements": ["Cu", "H", "Ni", "O"],
        "topology": [{"material_id": "WsEZCY3Sm28KVRMaDzOZyBIavcqY"}],
    }

    fake_response = {
        "entry_id": "w5hdgY4N38hhf6LMdQxy0niDxBMh",
        "data": {"results": {"material": fake_material}},
    }

    class FakeClient:
        def get_entry(self, entry_id):
            return fake_response

    from materials_pipeline.providers.nomad_api import NOMADAPIAdapter

    adapter = NOMADAPIAdapter(client=FakeClient())

    raw = adapter.fetch_entry("w5hdgY4N38hhf6LMdQxy0niDxBMh")

    pipeline = IngestionPipeline(project_root=tmp_path)
    provider = NomadProvider()

    result = pipeline.ingest(provider=provider, raw=raw)

    assert result.status == "accepted"

    raw_path = Path(result.raw_path)
    normalised_path = Path(result.normalised_path)

    assert raw_path.exists()
    assert normalised_path.exists()

    saved_envelope = __import__("json").loads(raw_path.read_text(encoding="utf-8"))

    assert saved_envelope["payload"]["material_id"] == "w5hdgY4N38hhf6LMdQxy0niDxBMh"
    assert (
        calculate_sha256(saved_envelope["payload"]) == saved_envelope["payload_sha256"]
    )
