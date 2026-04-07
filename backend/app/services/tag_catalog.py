from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import TypedDict

from app.schemas.stock import RankedStock, TagEditorCatalogResponse, TagEditorStock
from app.services.theme_mapping import load_theme_mapping


class CatalogStock(TypedDict):
    symbol: str
    name: str
    industry_level_1: str
    industry_level_2: str
    first_seen_date: str
    last_seen_date: str
    seen_days_count: int
    last_rank: int


class CatalogFilePayload(TypedDict):
    last_sync_date: str
    tracked_top_n: int
    new_symbols_today: list[str]
    stocks: dict[str, CatalogStock]


def get_tag_catalog_path() -> Path:
    return Path(__file__).resolve().parents[1] / "config" / "stock_tag_catalog.json"


def _default_payload() -> CatalogFilePayload:
    return {
        "last_sync_date": "",
        "tracked_top_n": 100,
        "new_symbols_today": [],
        "stocks": {},
    }


def _load_catalog_payload() -> CatalogFilePayload:
    path = get_tag_catalog_path()
    if not path.exists():
        return _default_payload()

    with path.open("r", encoding="utf-8") as file:
        raw = json.load(file)

    if not isinstance(raw, dict):
        return _default_payload()

    payload = _default_payload()
    payload["last_sync_date"] = str(raw.get("last_sync_date", "")).strip()
    payload["tracked_top_n"] = int(raw.get("tracked_top_n", 100) or 100)
    payload["new_symbols_today"] = [str(item).strip() for item in raw.get("new_symbols_today", []) if str(item).strip()]

    raw_stocks = raw.get("stocks", {})
    if isinstance(raw_stocks, dict):
        normalized_stocks: dict[str, CatalogStock] = {}
        for symbol, item in raw_stocks.items():
            if not isinstance(item, dict):
                continue
            cleaned_symbol = str(symbol).strip()
            if not cleaned_symbol:
                continue

            normalized_stocks[cleaned_symbol] = {
                "symbol": cleaned_symbol,
                "name": str(item.get("name", cleaned_symbol)).strip() or cleaned_symbol,
                "industry_level_1": str(item.get("industry_level_1", "Unknown")).strip() or "Unknown",
                "industry_level_2": str(item.get("industry_level_2", "Unknown")).strip() or "Unknown",
                "first_seen_date": str(item.get("first_seen_date", "")).strip() or payload["last_sync_date"],
                "last_seen_date": str(item.get("last_seen_date", "")).strip() or payload["last_sync_date"],
                "seen_days_count": max(1, int(item.get("seen_days_count", 1) or 1)),
                "last_rank": max(1, int(item.get("last_rank", 1) or 1)),
            }
        payload["stocks"] = normalized_stocks

    return payload


def _write_catalog_payload(payload: CatalogFilePayload) -> None:
    path = get_tag_catalog_path()
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def sync_and_build_catalog(rows: list[RankedStock], tracked_top_n: int = 100) -> TagEditorCatalogResponse:
    today_str = date.today().isoformat()
    payload = _load_catalog_payload()
    stocks = payload["stocks"]

    prior_symbols = set(stocks.keys())
    today_symbols = {row.symbol for row in rows}

    if payload["last_sync_date"] != today_str:
        payload["new_symbols_today"] = sorted(today_symbols - prior_symbols)
    else:
        existing_new = set(payload["new_symbols_today"])
        payload["new_symbols_today"] = sorted(existing_new | (today_symbols - prior_symbols))

    for row in rows:
        existing = stocks.get(row.symbol)
        if existing is None:
            stocks[row.symbol] = {
                "symbol": row.symbol,
                "name": row.name,
                "industry_level_1": row.industry_level_1,
                "industry_level_2": row.industry_level_2,
                "first_seen_date": today_str,
                "last_seen_date": today_str,
                "seen_days_count": 1,
                "last_rank": row.rank,
            }
            continue

        next_seen_days_count = existing["seen_days_count"]
        if existing["last_seen_date"] != today_str:
            next_seen_days_count += 1

        stocks[row.symbol] = {
            "symbol": row.symbol,
            "name": row.name,
            "industry_level_1": row.industry_level_1,
            "industry_level_2": row.industry_level_2,
            "first_seen_date": existing["first_seen_date"],
            "last_seen_date": today_str,
            "seen_days_count": next_seen_days_count,
            "last_rank": row.rank,
        }

    payload["last_sync_date"] = today_str
    payload["tracked_top_n"] = tracked_top_n
    payload["stocks"] = stocks
    _write_catalog_payload(payload)

    theme_mapping = load_theme_mapping()
    new_symbols_today = set(payload["new_symbols_today"])

    sorted_stocks = sorted(
        stocks.values(),
        key=lambda item: (
            item["last_seen_date"],
            -item["seen_days_count"],
            item["last_rank"],
            item["symbol"],
        ),
        reverse=True,
    )

    result_rows: list[TagEditorStock] = []
    for item in sorted_stocks:
        mapping_item = theme_mapping.get(item["symbol"])
        tags = mapping_item["tags"] if mapping_item is not None else ["未分類族群"]
        primary_tag = mapping_item["tag"] if mapping_item is not None else tags[0]
        result_rows.append(
            TagEditorStock(
                symbol=item["symbol"],
                name=item["name"],
                industry_level_1=item["industry_level_1"],
                industry_level_2=item["industry_level_2"],
                custom_group_tag=primary_tag,
                custom_group_tags=tags,
                first_seen_date=item["first_seen_date"],
                last_seen_date=item["last_seen_date"],
                seen_days_count=item["seen_days_count"],
                last_rank=item["last_rank"],
                is_new_today=item["symbol"] in new_symbols_today,
            )
        )

    return TagEditorCatalogResponse(
        generated_date=today_str,
        tracked_top_n=tracked_top_n,
        total_symbols=len(result_rows),
        new_symbols_today=sorted(new_symbols_today),
        rows=result_rows,
    )
