from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import TypedDict


class ThemeMappingItem(TypedDict):
    code: str
    industry: str
    tag: str


ThemeMappingDict = dict[str, ThemeMappingItem]


@lru_cache(maxsize=1)
def load_theme_mapping() -> ThemeMappingDict:
    config_path = Path(__file__).resolve().parents[1] / "config" / "stock_theme_map.json"
    with config_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)

    if not isinstance(payload, dict):
        raise ValueError("stock_theme_map.json must be a JSON object keyed by symbol")

    normalized: ThemeMappingDict = {}
    for symbol, item in payload.items():
        if not isinstance(item, dict):
            continue

        code = str(item.get("code", symbol)).strip()
        industry = str(item.get("industry", "Unknown")).strip() or "Unknown"
        tag = str(item.get("tag", "未分類族群")).strip() or "未分類族群"
        normalized[str(symbol).strip()] = {
            "code": code,
            "industry": industry,
            "tag": tag,
        }

    return normalized


def map_stock_theme(symbol: str, mapping: ThemeMappingDict) -> ThemeMappingItem | None:
    return mapping.get(symbol)
