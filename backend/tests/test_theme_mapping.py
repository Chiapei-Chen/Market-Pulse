from app.services.theme_mapping import load_theme_mapping, map_stock_theme


def test_theme_mapping_supports_multi_tags() -> None:
    mapping = load_theme_mapping()

    item = map_stock_theme("2317", mapping)
    assert item is not None
    assert item["tag"] == "AI伺服器"
    assert "電動車" in item["tags"]


def test_theme_mapping_single_tag_fallback() -> None:
    mapping = load_theme_mapping()

    item = map_stock_theme("2330", mapping)
    assert item is not None
    assert item["tag"] == item["tags"][0]
