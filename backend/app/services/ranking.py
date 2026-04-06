from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from typing import Literal

from app.schemas.stock import (
    GroupFrequency,
    GroupStrengtheningSignal,
    RankedStock,
    RankedStockWithChange,
)

RankingMetric = Literal["turnover_value", "volume"]


def is_etf_symbol(symbol: str) -> bool:
    return symbol.startswith("00")


def compare_rankings(
    yesterday: Iterable[RankedStock],
    today: Iterable[RankedStock],
    top_n: int = 100,
) -> list[RankedStockWithChange]:
    yesterday_top = [item for item in yesterday if item.rank <= top_n]
    today_top = [item for item in today if item.rank <= top_n]

    yesterday_rank_map = {item.symbol: item.rank for item in yesterday_top}

    compared: list[RankedStockWithChange] = []
    for current in sorted(today_top, key=lambda item: item.rank):
        previous_rank = yesterday_rank_map.get(current.symbol)
        is_new_entry = previous_rank is None
        rank_change = 0 if is_new_entry else previous_rank - current.rank

        compared.append(
            RankedStockWithChange(
                **current.model_dump(),
                rank_change=rank_change,
                is_new_entry=is_new_entry,
            )
        )

    return compared


def filter_etf(rows: Iterable[RankedStock], include_etf: bool) -> list[RankedStock]:
    if include_etf:
        return list(rows)
    return [row for row in rows if not is_etf_symbol(row.symbol)]


def rerank(
    rows: Iterable[RankedStock],
    top_n: int,
    ranking_metric: RankingMetric = "turnover_value",
) -> list[RankedStock]:
    if ranking_metric not in {"turnover_value", "volume"}:
        raise ValueError(f"Unsupported ranking metric: {ranking_metric}")

    def metric_value(row: RankedStock) -> float:
        if ranking_metric == "volume":
            return float(row.volume)
        return float(row.turnover_value)

    ranked: list[RankedStock] = []
    sorted_rows = sorted(
        rows,
        key=lambda row: (metric_value(row), row.turnover_value, row.volume),
        reverse=True,
    )
    for index, item in enumerate(sorted_rows[:top_n], start=1):
        ranked.append(RankedStock(**item.model_dump(exclude={"rank"}), rank=index))
    return ranked


def aggregate_group_frequency(rows: Iterable[RankedStock], top_n: int) -> list[GroupFrequency]:
    top_rows = [row for row in rows if row.rank <= top_n]
    counter: Counter[str] = Counter()
    for row in top_rows:
        tags = row.custom_group_tags or [row.custom_group_tag]
        for tag in set(tags):
            counter[tag] += 1

    frequencies = [
        GroupFrequency(tag=tag, count=count)
        for tag, count in sorted(counter.items(), key=lambda item: item[1], reverse=True)
    ]
    return frequencies


def detect_group_collective_strengthening(
    yesterday: Iterable[RankedStock],
    today: Iterable[RankedStock],
    top_n: int,
    min_today_count: int = 5,
    min_delta_count: int = 3,
) -> list[GroupStrengtheningSignal]:
    yesterday_counts: Counter[str] = Counter()
    for row in yesterday:
        if row.rank > top_n:
            continue
        tags = row.custom_group_tags or [row.custom_group_tag]
        for tag in set(tags):
            yesterday_counts[tag] += 1

    today_counts: Counter[str] = Counter()
    for row in today:
        if row.rank > top_n:
            continue
        tags = row.custom_group_tags or [row.custom_group_tag]
        for tag in set(tags):
            today_counts[tag] += 1

    all_tags = set(yesterday_counts.keys()) | set(today_counts.keys())
    signals: list[GroupStrengtheningSignal] = []

    for tag in sorted(all_tags):
        yesterday_count = yesterday_counts.get(tag, 0)
        today_count = today_counts.get(tag, 0)
        delta_count = today_count - yesterday_count

        ratio_ok = today_count >= (2 * yesterday_count) if yesterday_count > 0 else today_count >= min_today_count
        is_strengthening = (
            today_count >= min_today_count
            and delta_count >= min_delta_count
            and ratio_ok
            and tag != "未分類族群"
        )

        signals.append(
            GroupStrengtheningSignal(
                tag=tag,
                yesterday_count=yesterday_count,
                today_count=today_count,
                delta_count=delta_count,
                is_collective_strengthening=is_strengthening,
            )
        )

    signals.sort(key=lambda item: item.delta_count, reverse=True)
    return signals
