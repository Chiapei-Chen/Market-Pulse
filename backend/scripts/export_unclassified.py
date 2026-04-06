from __future__ import annotations

import argparse
import csv
from pathlib import Path

from app.services.data_source import get_data_source
from app.services.ranking import filter_etf, rerank


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export unclassified symbols from top N ranking")
    parser.add_argument("--top-n", type=int, default=100)
    parser.add_argument("--metric", choices=["turnover_value", "volume"], default="turnover_value")
    parser.add_argument("--include-etf", action="store_true", default=False)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("scripts") / "unclassified_symbols.csv",
        help="CSV output path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = get_data_source()

    today = source.get_today()
    ranked = rerank(
        filter_etf(today, include_etf=args.include_etf),
        top_n=args.top_n,
        ranking_metric=args.metric,
    )

    rows = [
        row
        for row in ranked
        if not row.custom_group_tags
        or row.custom_group_tag == "未分類族群"
        or set(row.custom_group_tags) == {"未分類族群"}
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(["rank", "symbol", "name", "industry_level_1", "volume", "turnover_value"])
        for row in rows:
            writer.writerow(
                [row.rank, row.symbol, row.name, row.industry_level_1, row.volume, int(row.turnover_value)]
            )

    print(f"Exported {len(rows)} unclassified symbols to {args.output}")


if __name__ == "__main__":
    main()
