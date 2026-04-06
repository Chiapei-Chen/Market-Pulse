from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import TypedDict


class ThemeMappingItem(TypedDict):
    code: str
    industry: str
    tag: str
    tags: list[str]


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

        raw_tags = item.get("tags")
        tags: list[str] = []
        if isinstance(raw_tags, list):
            tags = [str(tag).strip() for tag in raw_tags if str(tag).strip()]

        single_tag = str(item.get("tag", "")).strip()
        if single_tag:
            tags = [single_tag, *[tag for tag in tags if tag != single_tag]]

        if not tags:
            tags = ["未分類族群"]

        tag = tags[0]
        normalized[str(symbol).strip()] = {
            "code": code,
            "industry": industry,
            "tag": tag,
            "tags": tags,
        }

    return normalized


def map_stock_theme(symbol: str, mapping: ThemeMappingDict) -> ThemeMappingItem | None:
    return mapping.get(symbol)
