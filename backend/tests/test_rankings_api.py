from fastapi.testclient import TestClient
import json

from app.api.rankings import get_ranking_data_source
from app.schemas.stock import RankedStock
from app.services.data_source import StockDataSource
from app.services import theme_mapping
from app.services import tag_catalog
from main import app


class FakeDataSource(StockDataSource):
    def get_today(self) -> list[RankedStock]:
        return [
            RankedStock(
                symbol="2330",
                name="TSMC",
                industry_level_1="Semiconductor",
                industry_level_2="Foundry",
                custom_group_tag="AI晶片",
                custom_group_tags=["AI晶片", "晶圓代工"],
                volume=10,
                turnover_value=500,
                rank=1,
            ),
            RankedStock(
                symbol="0050",
                name="ETF50",
                industry_level_1="Fund",
                industry_level_2="ETF",
                custom_group_tag="ETF",
                custom_group_tags=["ETF"],
                volume=9,
                turnover_value=400,
                rank=2,
            ),
        ]

    def get_yesterday(self) -> list[RankedStock]:
        return [
            RankedStock(
                symbol="0050",
                name="ETF50",
                industry_level_1="Fund",
                industry_level_2="ETF",
                custom_group_tag="ETF",
                custom_group_tags=["ETF"],
                volume=11,
                turnover_value=600,
                rank=1,
            ),
            RankedStock(
                symbol="2330",
                name="TSMC",
                industry_level_1="Semiconductor",
                industry_level_2="Foundry",
                custom_group_tag="AI晶片",
                custom_group_tags=["AI晶片", "晶圓代工"],
                volume=8,
                turnover_value=300,
                rank=2,
            ),
        ]


def _override_source() -> StockDataSource:
    return FakeDataSource()


def _override_empty_source() -> StockDataSource:
    class EmptyDataSource(StockDataSource):
        def get_today(self) -> list[RankedStock]:
            return []

        def get_yesterday(self) -> list[RankedStock]:
            return []

    return EmptyDataSource()


def test_today_endpoint_filters_etf() -> None:
    app.dependency_overrides[get_ranking_data_source] = _override_source
    client = TestClient(app)

    response = client.get("/api/rankings/today", params={"include_etf": "false", "top_n": 100})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["symbol"] == "2330"

    app.dependency_overrides.clear()


def test_compared_endpoint_returns_rank_change() -> None:
    app.dependency_overrides[get_ranking_data_source] = _override_source
    client = TestClient(app)

    response = client.get("/api/rankings/compared", params={"top_n": 100, "include_etf": "true"})

    assert response.status_code == 200
    payload = response.json()

    assert payload[0]["symbol"] == "2330"
    assert payload[0]["rank_change"] == 1
    assert payload[0]["is_new_entry"] is False

    app.dependency_overrides.clear()


def test_momentum_endpoint_returns_group_frequency() -> None:
    app.dependency_overrides[get_ranking_data_source] = _override_source
    client = TestClient(app)

    response = client.get("/api/rankings/momentum", params={"top_n": 100, "include_etf": "true"})

    assert response.status_code == 200
    payload = response.json()

    assert isinstance(payload["rows"], list)
    assert isinstance(payload["today_group_frequency"], list)
    tags = {item["tag"] for item in payload["today_group_frequency"]}
    assert "AI晶片" in tags
    assert "ETF" in tags
    assert payload["ranking_metric"] == "turnover_value"
    assert "group_strengthening" in payload

    app.dependency_overrides.clear()


def test_momentum_endpoint_returns_empty_rows_array_when_no_data() -> None:
    app.dependency_overrides[get_ranking_data_source] = _override_empty_source
    client = TestClient(app)

    response = client.get("/api/rankings/momentum", params={"top_n": 100, "include_etf": "true"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["rows"] == []

    app.dependency_overrides.clear()


def test_today_endpoint_supports_volume_metric() -> None:
    app.dependency_overrides[get_ranking_data_source] = _override_source
    client = TestClient(app)

    response = client.get(
        "/api/rankings/today",
        params={"include_etf": "true", "top_n": 100, "ranking_metric": "volume"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["symbol"] == "2330"
    assert payload[0]["rank"] == 1

    app.dependency_overrides.clear()


def test_add_custom_theme_tag_endpoint(tmp_path) -> None:
    mapping_path = tmp_path / "stock_theme_map.json"
    mapping_path.write_text("{}", encoding="utf-8")

    original_get_path = theme_mapping.get_theme_mapping_path
    theme_mapping.get_theme_mapping_path = lambda: mapping_path
    theme_mapping.load_theme_mapping.cache_clear()

    client = TestClient(app)
    response = client.post(
        "/api/rankings/themes/2330/tags",
        json={"tag": "AI晶片", "industry": "半導體業"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["symbol"] == "2330"
    assert payload["tags"][0] == "AI晶片"

    file_payload = json.loads(mapping_path.read_text(encoding="utf-8"))
    assert file_payload["2330"]["tags"][0] == "AI晶片"

    theme_mapping.get_theme_mapping_path = original_get_path
    theme_mapping.load_theme_mapping.cache_clear()


def test_remove_custom_theme_tag_endpoint(tmp_path) -> None:
    mapping_path = tmp_path / "stock_theme_map.json"
    mapping_path.write_text(
        json.dumps(
            {
                "2330": {
                    "code": "2330",
                    "industry": "半導體業",
                    "tag": "AI晶片",
                    "tags": ["AI晶片", "晶圓代工"],
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    original_get_path = theme_mapping.get_theme_mapping_path
    theme_mapping.get_theme_mapping_path = lambda: mapping_path
    theme_mapping.load_theme_mapping.cache_clear()

    client = TestClient(app)
    response = client.request(
        "DELETE",
        "/api/rankings/themes/2330/tags",
        json={"tag": "AI晶片"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["tags"] == ["晶圓代工"]
    assert payload["tag"] == "晶圓代工"

    file_payload = json.loads(mapping_path.read_text(encoding="utf-8"))
    assert file_payload["2330"]["tags"] == ["晶圓代工"]

    theme_mapping.get_theme_mapping_path = original_get_path
    theme_mapping.load_theme_mapping.cache_clear()


def test_tag_catalog_endpoint_accumulates_and_marks_new_symbols(tmp_path) -> None:
    mapping_path = tmp_path / "stock_theme_map.json"
    mapping_path.write_text(
        json.dumps(
            {
                "2330": {
                    "code": "2330",
                    "industry": "半導體業",
                    "tag": "AI晶片",
                    "tags": ["AI晶片", "晶圓代工"],
                },
                "2317": {
                    "code": "2317",
                    "industry": "電子零組件業",
                    "tag": "AI伺服器",
                    "tags": ["AI伺服器", "電動車"],
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    catalog_path = tmp_path / "stock_tag_catalog.json"

    class MutableSource(StockDataSource):
        def __init__(self) -> None:
            self.today_rows = [
                RankedStock(
                    symbol="2330",
                    name="TSMC",
                    industry_level_1="半導體業",
                    industry_level_2="Foundry",
                    custom_group_tag="AI晶片",
                    custom_group_tags=["AI晶片", "晶圓代工"],
                    volume=10,
                    turnover_value=500,
                    rank=1,
                )
            ]

        def get_today(self) -> list[RankedStock]:
            return list(self.today_rows)

        def get_yesterday(self) -> list[RankedStock]:
            return list(self.today_rows)

    source = MutableSource()

    original_get_mapping_path = theme_mapping.get_theme_mapping_path
    original_get_catalog_path = tag_catalog.get_tag_catalog_path
    theme_mapping.get_theme_mapping_path = lambda: mapping_path
    tag_catalog.get_tag_catalog_path = lambda: catalog_path
    theme_mapping.load_theme_mapping.cache_clear()

    app.dependency_overrides[get_ranking_data_source] = lambda: source
    client = TestClient(app)

    first = client.get("/api/rankings/themes/catalog")
    assert first.status_code == 200
    first_payload = first.json()
    assert first_payload["total_symbols"] == 1
    assert first_payload["new_symbols_today"] == ["2330"]
    assert first_payload["rows"][0]["is_new_today"] is True

    source.today_rows = [
        source.today_rows[0],
        RankedStock(
            symbol="2317",
            name="Hon Hai",
            industry_level_1="電子零組件業",
            industry_level_2="EMS",
            custom_group_tag="AI伺服器",
            custom_group_tags=["AI伺服器", "電動車"],
            volume=9,
            turnover_value=300,
            rank=2,
        ),
    ]

    second = client.get("/api/rankings/themes/catalog")
    assert second.status_code == 200
    second_payload = second.json()
    assert second_payload["total_symbols"] == 2
    assert set(second_payload["new_symbols_today"]) == {"2330", "2317"}
    symbols = {item["symbol"]: item for item in second_payload["rows"]}
    assert symbols["2317"]["is_new_today"] is True

    app.dependency_overrides.clear()
    theme_mapping.get_theme_mapping_path = original_get_mapping_path
    tag_catalog.get_tag_catalog_path = original_get_catalog_path
    theme_mapping.load_theme_mapping.cache_clear()
