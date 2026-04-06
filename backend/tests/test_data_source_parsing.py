from app.services.data_source import (
    _is_target_stock_table,
    _normalize_tw_industry_name,
    _parse_tw_number,
)


def test_parse_tw_number_handles_comma_and_placeholder() -> None:
    assert _parse_tw_number("1,234,567") == 1234567.0
    assert _parse_tw_number("--") == 0.0
    assert _parse_tw_number("-") == 0.0


def test_is_target_stock_table_requires_key_fields() -> None:
    valid_fields = ["證券代號", "證券名稱", "成交股數", "成交金額", "成交筆數"]
    invalid_fields = ["證券代號", "證券名稱", "收盤價"]

    assert _is_target_stock_table(valid_fields) is True
    assert _is_target_stock_table(invalid_fields) is False


def test_normalize_tw_industry_name_maps_code_to_label() -> None:
    assert _normalize_tw_industry_name("24") == "半導體業"
    assert _normalize_tw_industry_name("28") == "電子零組件業"


def test_normalize_tw_industry_name_keeps_unknown_and_label() -> None:
    assert _normalize_tw_industry_name("Unknown") == "Unknown"
    assert _normalize_tw_industry_name("航運業") == "航運業"
