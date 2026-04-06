from __future__ import annotations

import os
import json
from datetime import date, timedelta
from collections.abc import Iterable
from typing import Protocol

import httpx
from dotenv import load_dotenv

from app.schemas.stock import RankedStock
from app.services.theme_mapping import load_theme_mapping, map_stock_theme

load_dotenv()

TWSE_INDUSTRY_CODE_MAP: dict[str, str] = {
    "01": "水泥工業",
    "02": "食品工業",
    "03": "塑膠工業",
    "04": "紡織纖維",
    "05": "電機機械",
    "06": "電器電纜",
    "07": "化學生技醫療",
    "08": "玻璃陶瓷",
    "09": "造紙工業",
    "10": "鋼鐵工業",
    "11": "橡膠工業",
    "12": "汽車工業",
    "13": "電子工業",
    "14": "建材營造",
    "15": "航運業",
    "16": "觀光餐旅",
    "17": "金融保險",
    "18": "貿易百貨",
    "19": "綜合",
    "20": "其他",
    "21": "化學工業",
    "22": "生技醫療業",
    "23": "油電燃氣業",
    "24": "半導體業",
    "25": "電腦及週邊設備業",
    "26": "光電業",
    "27": "通信網路業",
    "28": "電子零組件業",
    "29": "電子通路業",
    "30": "資訊服務業",
    "31": "其他電子業",
    "32": "文化創意業",
    "33": "農業科技業",
    "34": "電子商務",
    "35": "綠能環保",
    "36": "數位雲端",
    "37": "運動休閒",
    "38": "居家生活",
    "39": "存託憑證",
    "40": "創新板",
}


class StockDataSource(Protocol):
    def get_today(self) -> list[RankedStock]: ...

    def get_yesterday(self) -> list[RankedStock]: ...


class HttpJsonStockDataSource:
    def __init__(self, today_url: str, yesterday_url: str, timeout: float = 8.0) -> None:
        self.today_url = today_url
        self.yesterday_url = yesterday_url
        self.timeout = timeout
        self.verify_ssl = _verify_ssl_enabled()

    def _fetch(self, url: str) -> list[RankedStock]:
        response = httpx.get(url, timeout=self.timeout, verify=self.verify_ssl)
        response.raise_for_status()
        payload = _load_json_payload(response)

        if not isinstance(payload, list):
            raise ValueError("Data source must return a JSON list")

        return [RankedStock(**item) for item in payload]

    def get_today(self) -> list[RankedStock]:
        return self._fetch(self.today_url)

    def get_yesterday(self) -> list[RankedStock]:
        return self._fetch(self.yesterday_url)


class TwseDelayedDataSource:
    MI_INDEX_URL = "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX"
    COMPANY_INFO_URL = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"

    def __init__(self, timeout: float = 10.0, max_lookback_days: int = 14) -> None:
        self.timeout = timeout
        self.max_lookback_days = max_lookback_days
        self.verify_ssl = _verify_ssl_enabled()
        self._industry_cache: dict[str, tuple[str, str]] | None = None

    def get_today(self) -> list[RankedStock]:
        return self._fetch_nearest_ranked(start_date=date.today(), skip_found=0)

    def get_yesterday(self) -> list[RankedStock]:
        return self._fetch_nearest_ranked(start_date=date.today(), skip_found=1)

    def _fetch_nearest_ranked(self, start_date: date, skip_found: int) -> list[RankedStock]:
        found = 0
        for day_offset in range(self.max_lookback_days):
            target_day = start_date - timedelta(days=day_offset)
            rows = self._fetch_daily_rows(target_day)
            if not rows:
                continue

            if found == skip_found:
                return self._rows_to_ranked(rows)

            found += 1

        raise ValueError("Unable to find enough TWSE trading days in lookback window")

    def _fetch_daily_rows(self, trading_day: date) -> list[dict[str, str]]:
        response = httpx.get(
            self.MI_INDEX_URL,
            params={
                "date": trading_day.strftime("%Y%m%d"),
                "type": "ALLBUT0999",
                "response": "json",
            },
            timeout=self.timeout,
            headers={"User-Agent": "stock-ranking-dashboard/1.0"},
            verify=self.verify_ssl,
        )
        response.raise_for_status()
        payload = _load_json_payload(response)

        tables = payload.get("tables")
        if not isinstance(tables, list):
            return []

        for table in tables:
            fields = table.get("fields")
            data = table.get("data")

            if not isinstance(fields, list) or not isinstance(data, list):
                continue

            if not _is_target_stock_table(fields):
                continue

            rows: list[dict[str, str]] = []
            for row in data:
                if not isinstance(row, list) or len(row) != len(fields):
                    continue
                rows.append(dict(zip(fields, row)))

            return rows

        return []

    def _rows_to_ranked(self, rows: Iterable[dict[str, str]]) -> list[RankedStock]:
        industry_map = self._get_industry_map()
        theme_mapping = load_theme_mapping()
        parsed_rows: list[dict[str, str | int | float]] = []

        for row in rows:
            symbol = _clean_text(row.get("證券代號", ""))
            if not (symbol.isdigit() and len(symbol) == 4):
                continue

            turnover_value = _parse_tw_number(row.get("成交金額", "0"))
            if turnover_value <= 0:
                continue

            industry_l1, industry_l2 = industry_map.get(symbol, ("Unknown", "Unknown"))
            mapping_item = map_stock_theme(symbol, theme_mapping)
            if mapping_item is not None:
                industry_l1 = mapping_item["industry"]

            group_tags = mapping_item["tags"] if mapping_item is not None else ["未分類族群"]
            primary_group_tag = group_tags[0]

            parsed_rows.append(
                {
                    "symbol": symbol,
                    "name": _clean_text(row.get("證券名稱", symbol)),
                    "industry_level_1": industry_l1,
                    "industry_level_2": industry_l2,
                    "custom_group_tag": primary_group_tag,
                    "custom_group_tags": group_tags,
                    "volume": int(_parse_tw_number(row.get("成交股數", "0"))),
                    "turnover_value": float(turnover_value),
                }
            )

        return _make_ranked(parsed_rows)

    def _get_industry_map(self) -> dict[str, tuple[str, str]]:
        if self._industry_cache is not None:
            return self._industry_cache

        response = httpx.get(
            self.COMPANY_INFO_URL,
            timeout=self.timeout,
            headers={"User-Agent": "stock-ranking-dashboard/1.0"},
            verify=self.verify_ssl,
        )
        response.raise_for_status()
        payload = _load_json_payload(response)

        industry_map: dict[str, tuple[str, str]] = {}
        if isinstance(payload, list):
            for item in payload:
                if not isinstance(item, dict):
                    continue

                symbol = _clean_text(
                    item.get("公司代號")
                    or item.get("證券代號")
                    or item.get("stock_id")
                    or ""
                )
                if not (symbol.isdigit() and len(symbol) == 4):
                    continue

                industry = _normalize_tw_industry_name(
                    item.get("產業別")
                    or item.get("industry")
                    or item.get("industry_category")
                    or "Unknown"
                )
                sub_industry = _clean_text(
                    item.get("子產業")
                    or item.get("sub_industry")
                    or "Unknown"
                )
                industry_map[symbol] = (industry, sub_industry)

        self._industry_cache = industry_map
        return industry_map


class SampleStockDataSource:
    def __init__(self) -> None:
        theme_mapping = load_theme_mapping()

        self._today = _make_ranked([
            {
                "symbol": "2330",
                "name": "TSMC",
                "industry_level_1": "Semiconductor",
                "industry_level_2": "Foundry",
                "custom_group_tag": _sample_primary_tag("2330", theme_mapping),
                "custom_group_tags": _sample_tags("2330", theme_mapping),
                "volume": 95000,
                "turnover_value": 82000000000,
            },
            {
                "symbol": "0050",
                "name": "ETF50",
                "industry_level_1": "Fund",
                "industry_level_2": "ETF",
                "custom_group_tag": _sample_primary_tag("0050", theme_mapping),
                "custom_group_tags": _sample_tags("0050", theme_mapping),
                "volume": 87000,
                "turnover_value": 7500000000,
            },
            {
                "symbol": "2317",
                "name": "Hon Hai",
                "industry_level_1": "Electronics",
                "industry_level_2": "EMS",
                "custom_group_tag": _sample_primary_tag("2317", theme_mapping),
                "custom_group_tags": _sample_tags("2317", theme_mapping),
                "volume": 76000,
                "turnover_value": 16500000000,
            },
            {
                "symbol": "2603",
                "name": "Evergreen",
                "industry_level_1": "Shipping",
                "industry_level_2": "Container",
                "custom_group_tag": _sample_primary_tag("2603", theme_mapping),
                "custom_group_tags": _sample_tags("2603", theme_mapping),
                "volume": 55000,
                "turnover_value": 5100000000,
            },
        ])
        self._yesterday = _make_ranked([
            {
                "symbol": "0050",
                "name": "ETF50",
                "industry_level_1": "Fund",
                "industry_level_2": "ETF",
                "custom_group_tag": _sample_primary_tag("0050", theme_mapping),
                "custom_group_tags": _sample_tags("0050", theme_mapping),
                "volume": 91000,
                "turnover_value": 8100000000,
            },
            {
                "symbol": "2330",
                "name": "TSMC",
                "industry_level_1": "Semiconductor",
                "industry_level_2": "Foundry",
                "custom_group_tag": _sample_primary_tag("2330", theme_mapping),
                "custom_group_tags": _sample_tags("2330", theme_mapping),
                "volume": 86000,
                "turnover_value": 70000000000,
            },
            {
                "symbol": "2303",
                "name": "UMC",
                "industry_level_1": "Semiconductor",
                "industry_level_2": "Foundry",
                "custom_group_tag": _sample_primary_tag("2303", theme_mapping),
                "custom_group_tags": _sample_tags("2303", theme_mapping),
                "volume": 63000,
                "turnover_value": 3000000000,
            },
            {
                "symbol": "2317",
                "name": "Hon Hai",
                "industry_level_1": "Electronics",
                "industry_level_2": "EMS",
                "custom_group_tag": _sample_primary_tag("2317", theme_mapping),
                "custom_group_tags": _sample_tags("2317", theme_mapping),
                "volume": 54000,
                "turnover_value": 12200000000,
            },
        ])

    def get_today(self) -> list[RankedStock]:
        return list(self._today)

    def get_yesterday(self) -> list[RankedStock]:
        return list(self._yesterday)


def _make_ranked(rows: Iterable[dict]) -> list[RankedStock]:
    sorted_rows = sorted(rows, key=lambda row: row["turnover_value"], reverse=True)
    return [RankedStock(**row, rank=index) for index, row in enumerate(sorted_rows, start=1)]


def _clean_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _parse_tw_number(value: str) -> float:
    cleaned = _clean_text(value).replace(",", "")
    if cleaned in {"", "--", "-"}:
        return 0.0
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _is_target_stock_table(fields: list[str]) -> bool:
    field_set = set(fields)
    required_fields = {"證券代號", "證券名稱", "成交股數", "成交金額"}
    return required_fields.issubset(field_set)


def _verify_ssl_enabled() -> bool:
    raw = os.getenv("STOCK_HTTP_VERIFY_SSL", "true").strip().lower()
    return raw not in {"0", "false", "no", "off"}


def _normalize_tw_industry_name(value: object) -> str:
    raw = _clean_text(value)
    if raw in {"", "Unknown", "未分類"}:
        return "Unknown"

    code = raw.zfill(2) if raw.isdigit() else raw
    return TWSE_INDUSTRY_CODE_MAP.get(code, raw)


def _load_json_payload(response: httpx.Response) -> object:
    # TWSE endpoints may return JSON without reliable charset hints.
    for encoding in ("utf-8-sig", "utf-8", "cp950", "big5"):
        try:
            return json.loads(response.content.decode(encoding))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue

    return response.json()


def _sample_primary_tag(symbol: str, theme_mapping: dict[str, dict[str, str | list[str]]]) -> str:
    item = theme_mapping.get(symbol)
    if item is None:
        return "未分類族群"
    tag = item.get("tag")
    if isinstance(tag, str) and tag.strip():
        return tag
    return "未分類族群"


def _sample_tags(symbol: str, theme_mapping: dict[str, dict[str, str | list[str]]]) -> list[str]:
    item = theme_mapping.get(symbol)
    if item is None:
        return ["未分類族群"]

    tags = item.get("tags")
    if isinstance(tags, list):
        normalized = [str(tag).strip() for tag in tags if str(tag).strip()]
        if normalized:
            return normalized

    return [_sample_primary_tag(symbol, theme_mapping)]


def get_data_source() -> StockDataSource:
    source_type = os.getenv("STOCK_DATA_SOURCE", "").lower().strip()
    today_url = os.getenv("STOCK_TODAY_API_URL")
    yesterday_url = os.getenv("STOCK_YESTERDAY_API_URL")

    if source_type == "twse_delayed":
        return TwseDelayedDataSource()

    if today_url and yesterday_url:
        return HttpJsonStockDataSource(today_url=today_url, yesterday_url=yesterday_url)

    return SampleStockDataSource()
