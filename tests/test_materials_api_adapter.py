from types import SimpleNamespace


def test_fetch_material_with_mp_api_monkeypatched(monkeypatch):
    class FakeStructure:
        def as_dict(self):
            return {"fake": "structure"}

    # Create a fake entry object similar to what mp_api returns
    fake_entry = SimpleNamespace(
        formula_pretty="Si",
        chemsys="Si",
        structure=FakeStructure(),
    )

    class FakeMPRester:
        def __init__(self, api_key=None):
            self.api_key = api_key

        def __enter__(self):
            # client.materials.summary.search(...) should be callable
            materials = SimpleNamespace(
                summary=SimpleNamespace(
                    search=lambda material_ids, fields: [fake_entry]
                )
            )

            return SimpleNamespace(materials=materials)

        def __exit__(self, exc_type, exc, tb):
            return False

    # Patch the MPRester imported in the adapter module
    monkeypatch.setattr(
        "materials_pipeline.providers.materials_project_api.MPRester",
        FakeMPRester,
    )

    from materials_pipeline.providers.materials_project_api import (
        MaterialsProjectAPIAdapter,
    )

    adapter = MaterialsProjectAPIAdapter(api_key=None)

    raw = adapter.fetch_material("mp-149")

    assert raw["material_id"] == "mp-149"
    assert raw["formula_pretty"] == "Si"
    assert raw["chemsys"] == "Si"
    assert hasattr(raw["structure"], "as_dict")
