from app.schemas.stock import RankedStock
from app.services.ranking import (
    aggregate_group_frequency,
    compare_rankings,
    detect_group_collective_strengthening,
    filter_etf,
    is_etf_symbol,
    rerank,
)


def _stock(symbol: str, rank: int) -> RankedStock:
    return RankedStock(
        symbol=symbol,
        name=symbol,
        industry_level_1="Tech",
        industry_level_2="SubTech",
        volume=100,
        turnover_value=1000,
        rank=rank,
    )


def test_compare_rankings_rank_up_down_and_new_entry() -> None:
    yesterday = [_stock("2330", 2), _stock("2317", 1)]
    today = [_stock("2330", 1), _stock("2603", 2)]

    result = compare_rankings(yesterday=yesterday, today=today, top_n=100)

    assert result[0].symbol == "2330"
    assert result[0].rank_change == 1
    assert result[0].is_new_entry is False

    assert result[1].symbol == "2603"
    assert result[1].rank_change == 0
    assert result[1].is_new_entry is True


def test_compare_rankings_respects_top_n() -> None:
    yesterday = [_stock("2330", 1), _stock("2317", 2), _stock("2603", 3)]
    today = [_stock("2330", 1), _stock("2317", 2), _stock("2603", 3)]

    result = compare_rankings(yesterday=yesterday, today=today, top_n=2)

    assert len(result) == 2
    assert [item.symbol for item in result] == ["2330", "2317"]


def test_etf_filter_and_symbol_rule() -> None:
    rows = [_stock("0050", 1), _stock("2330", 2)]

    assert is_etf_symbol("0056") is True
    assert is_etf_symbol("2330") is False

    filtered = filter_etf(rows, include_etf=False)
    assert [item.symbol for item in filtered] == ["2330"]


def test_rerank_assigns_compact_rank_order() -> None:
    rows = [_stock("2330", 2), _stock("2317", 4), _stock("2603", 8)]

    reranked = rerank(rows, top_n=2)

    assert [item.symbol for item in reranked] == ["2330", "2317"]
    assert [item.rank for item in reranked] == [1, 2]


def test_aggregate_group_frequency_counts_tags() -> None:
    rows = [_stock("2330", 1), _stock("2317", 2), _stock("2603", 3)]
    rows[0].custom_group_tag = "AI晶片"
    rows[1].custom_group_tag = "AI晶片"
    rows[2].custom_group_tag = "重電"

    frequencies = aggregate_group_frequency(rows, top_n=100)

    assert frequencies[0].tag == "AI晶片"
    assert frequencies[0].count == 2


def test_detect_collective_strengthening_marks_jump() -> None:
    yesterday = [_stock("2330", 1), _stock("2317", 2), _stock("2603", 3)]
    today = [_stock("2330", 1), _stock("2317", 2), _stock("2603", 3), _stock("2303", 4), _stock("2382", 5)]

    yesterday[0].custom_group_tag = "重電"
    yesterday[1].custom_group_tag = "重電"
    yesterday[2].custom_group_tag = "AI晶片"

    today[0].custom_group_tag = "重電"
    today[1].custom_group_tag = "重電"
    today[2].custom_group_tag = "重電"
    today[3].custom_group_tag = "重電"
    today[4].custom_group_tag = "重電"

    signals = detect_group_collective_strengthening(
        yesterday=yesterday,
        today=today,
        top_n=100,
        min_today_count=5,
        min_delta_count=3,
    )

    heavy_power = next(item for item in signals if item.tag == "重電")
    assert heavy_power.yesterday_count == 2
    assert heavy_power.today_count == 5
    assert heavy_power.is_collective_strengthening is True
