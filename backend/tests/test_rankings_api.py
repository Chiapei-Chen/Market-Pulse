from fastapi.testclient import TestClient

from app.api.rankings import get_ranking_data_source
from app.schemas.stock import RankedStock
from app.services.data_source import StockDataSource
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
