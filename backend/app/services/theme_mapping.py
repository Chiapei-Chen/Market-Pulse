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


def get_theme_mapping_path() -> Path:
    return Path(__file__).resolve().parents[1] / "config" / "stock_theme_map.json"


def _normalize_mapping(payload: object) -> ThemeMappingDict:
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


@lru_cache(maxsize=1)
def load_theme_mapping() -> ThemeMappingDict:
    config_path = get_theme_mapping_path()
    with config_path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    return _normalize_mapping(payload)


def map_stock_theme(symbol: str, mapping: ThemeMappingDict) -> ThemeMappingItem | None:
    return mapping.get(symbol)


def _write_theme_mapping(mapping: ThemeMappingDict) -> None:
    config_path = get_theme_mapping_path()
    with config_path.open("w", encoding="utf-8") as file:
        json.dump(mapping, file, ensure_ascii=False, indent=2)
    load_theme_mapping.cache_clear()


def add_theme_tag(symbol: str, tag: str, industry: str | None = None) -> ThemeMappingItem:
    cleaned_symbol = symbol.strip()
    cleaned_tag = tag.strip()
    if not cleaned_symbol:
        raise ValueError("symbol is required")
    if not cleaned_tag:
        raise ValueError("tag is required")

    mapping = dict(load_theme_mapping())
    existing = mapping.get(cleaned_symbol)
    base_tags = list(existing["tags"]) if existing is not None else []

    next_tags = [cleaned_tag, *[item for item in base_tags if item != cleaned_tag]]
    if not next_tags:
        next_tags = ["未分類族群"]

    next_item: ThemeMappingItem = {
        "code": existing["code"] if existing is not None else cleaned_symbol,
        "industry": (
            existing["industry"]
            if existing is not None
            else (industry.strip() if isinstance(industry, str) and industry.strip() else "Unknown")
        ),
        "tag": next_tags[0],
        "tags": next_tags,
    }
    mapping[cleaned_symbol] = next_item
    _write_theme_mapping(mapping)
    return next_item


def remove_theme_tag(symbol: str, tag: str) -> ThemeMappingItem:
    cleaned_symbol = symbol.strip()
    cleaned_tag = tag.strip()
    if not cleaned_symbol:
        raise ValueError("symbol is required")
    if not cleaned_tag:
        raise ValueError("tag is required")

    mapping = dict(load_theme_mapping())
    existing = mapping.get(cleaned_symbol)
    if existing is None:
        raise KeyError(f"symbol not found: {cleaned_symbol}")

    next_tags = [item for item in existing["tags"] if item != cleaned_tag]
    if not next_tags:
        next_tags = ["未分類族群"]

    next_item: ThemeMappingItem = {
        "code": existing["code"],
        "industry": existing["industry"],
        "tag": next_tags[0],
        "tags": next_tags,
    }
    mapping[cleaned_symbol] = next_item
    _write_theme_mapping(mapping)
    return next_item
