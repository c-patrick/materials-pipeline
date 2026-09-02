def test_nomad_adapter_maps_response_correctly():
    fake_material = {
        "chemical_formula_reduced": "CuH3NiO4",
        "elements": ["Cu", "H", "Ni", "O"],
        "topology": [
            {"material_id": "WsEZCY3Sm28KVRMaDzOZyBIavcqY", "cell": {"a": 1.0}}
        ],
    }

    fake_response = {
        "entry_id": "w5hdgY4N38hhf6LMdQxy0niDxBMh",
        "data": {"results": {"material": fake_material}},
    }

    class FakeClient:
        def get_entry(self, entry_id):
            assert entry_id == "w5hdgY4N38hhf6LMdQxy0niDxBMh"
            return fake_response

    from materials_pipeline.providers.nomad_api import NOMADAPIAdapter

    adapter = NOMADAPIAdapter(client=FakeClient())

    raw = adapter.fetch_entry("w5hdgY4N38hhf6LMdQxy0niDxBMh")

    assert raw["material_id"] == "w5hdgY4N38hhf6LMdQxy0niDxBMh"
    assert raw["formula_pretty"] == "CuH3NiO4"
    assert raw["chemsys"] == "Cu-H-Ni-O"
    assert isinstance(raw["structure"], dict)
