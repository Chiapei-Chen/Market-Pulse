from typing import Literal

from pydantic import BaseModel, Field


class StockBase(BaseModel):
    symbol: str = Field(..., description="Stock code")
    name: str = Field(..., description="Stock name")
    industry_level_1: str = Field(..., description="Primary industry")
    industry_level_2: str = Field(..., description="Secondary industry")
    custom_group_tag: str = Field(default="未分類族群", description="Custom momentum group tag")
    custom_group_tags: list[str] = Field(
        default_factory=lambda: ["未分類族群"],
        description="Custom momentum group tags (multi-label)",
    )
    volume: int = Field(..., ge=0, description="Trade volume")
    turnover_value: float = Field(..., ge=0, description="Trade value")


class RankedStock(StockBase):
    rank: int = Field(..., ge=1, description="Current rank")


class RankedStockWithChange(RankedStock):
    rank_change: int = Field(..., description="Positive means rank up")
    is_new_entry: bool = Field(..., description="True if stock was outside yesterday top N")


class GroupFrequency(BaseModel):
    tag: str = Field(..., description="Custom group tag")
    count: int = Field(..., ge=0, description="Number of stocks in top N")


class GroupStrengtheningSignal(BaseModel):
    tag: str = Field(..., description="Custom group tag")
    yesterday_count: int = Field(..., ge=0)
    today_count: int = Field(..., ge=0)
    delta_count: int = Field(..., description="today_count - yesterday_count")
    is_collective_strengthening: bool = Field(
        ..., description="True when group count jumps significantly day-over-day"
    )


class MomentumComparedResponse(BaseModel):
    ranking_metric: Literal["turnover_value", "volume"]
    rows: list[RankedStockWithChange]
    today_group_frequency: list[GroupFrequency]
    group_strengthening: list[GroupStrengtheningSignal]


class ThemeTagMutationRequest(BaseModel):
    tag: str = Field(..., min_length=1, description="Tag to add or remove")
    industry: str | None = Field(default=None, description="Optional industry when creating new symbol mapping")


class ThemeMappingItemResponse(BaseModel):
    symbol: str = Field(..., description="Stock code")
    code: str = Field(..., description="Stock code in mapping file")
    industry: str = Field(..., description="Industry label")
    tag: str = Field(..., description="Primary tag")
    tags: list[str] = Field(..., description="All custom tags")


class TagEditorStock(BaseModel):
    symbol: str = Field(..., description="Stock code")
    name: str = Field(..., description="Stock name")
    industry_level_1: str = Field(..., description="Primary industry")
    industry_level_2: str = Field(..., description="Secondary industry")
    custom_group_tag: str = Field(..., description="Primary custom tag")
    custom_group_tags: list[str] = Field(..., description="All custom tags")
    first_seen_date: str = Field(..., description="First date appeared in daily top 100")
    last_seen_date: str = Field(..., description="Last date appeared in daily top 100")
    seen_days_count: int = Field(..., ge=1, description="How many trading days appeared")
    last_rank: int = Field(..., ge=1, description="Latest rank in tracked top 100")
    is_new_today: bool = Field(..., description="True if symbol is newly added today")


class TagEditorCatalogResponse(BaseModel):
    generated_date: str = Field(..., description="Date of this sync snapshot")
    tracked_top_n: int = Field(..., ge=1)
    total_symbols: int = Field(..., ge=0)
    new_symbols_today: list[str] = Field(default_factory=list)
    rows: list[TagEditorStock] = Field(default_factory=list)
