from fastapi import APIRouter, Depends, HTTPException, Query

from app.schemas.stock import (
    MomentumComparedResponse,
    RankedStock,
    RankedStockWithChange,
    TagEditorCatalogResponse,
    ThemeMappingItemResponse,
    ThemeTagMutationRequest,
)
from app.services.data_source import StockDataSource, get_data_source
from app.services.ranking import (
    RankingMetric,
    aggregate_group_frequency,
    compare_rankings,
    detect_group_collective_strengthening,
    filter_etf,
    rerank,
)
from app.services.theme_mapping import add_theme_tag, remove_theme_tag
from app.services.tag_catalog import sync_and_build_catalog

router = APIRouter()


def get_ranking_data_source() -> StockDataSource:
    return get_data_source()


@router.get("/today", response_model=list[RankedStock])
def get_today_rankings(
    top_n: int = Query(default=100, ge=1, le=500),
    include_etf: bool = Query(default=True),
    ranking_metric: RankingMetric = Query(default="turnover_value"),
    source: StockDataSource = Depends(get_ranking_data_source),
) -> list[RankedStock]:
    today = source.get_today()
    today = filter_etf(today, include_etf=include_etf)
    return rerank(today, top_n=top_n, ranking_metric=ranking_metric)


@router.get("/yesterday", response_model=list[RankedStock])
def get_yesterday_rankings(
    top_n: int = Query(default=100, ge=1, le=500),
    include_etf: bool = Query(default=True),
    ranking_metric: RankingMetric = Query(default="turnover_value"),
    source: StockDataSource = Depends(get_ranking_data_source),
) -> list[RankedStock]:
    yesterday = source.get_yesterday()
    yesterday = filter_etf(yesterday, include_etf=include_etf)
    return rerank(yesterday, top_n=top_n, ranking_metric=ranking_metric)


@router.get("/compared", response_model=list[RankedStockWithChange])
def get_compared_rankings(
    top_n: int = Query(default=100, ge=1, le=500),
    include_etf: bool = Query(default=True),
    ranking_metric: RankingMetric = Query(default="turnover_value"),
    source: StockDataSource = Depends(get_ranking_data_source),
) -> list[RankedStockWithChange]:
    today = rerank(
        filter_etf(source.get_today(), include_etf=include_etf),
        top_n=top_n,
        ranking_metric=ranking_metric,
    )
    yesterday = rerank(
        filter_etf(source.get_yesterday(), include_etf=include_etf),
        top_n=top_n,
        ranking_metric=ranking_metric,
    )
    return compare_rankings(yesterday=yesterday, today=today, top_n=top_n)


@router.get("/momentum", response_model=MomentumComparedResponse)
def get_momentum_snapshot(
    top_n: int = Query(default=100, ge=1, le=500),
    include_etf: bool = Query(default=True),
    ranking_metric: RankingMetric = Query(default="turnover_value"),
    source: StockDataSource = Depends(get_ranking_data_source),
) -> MomentumComparedResponse:
    today = rerank(
        filter_etf(source.get_today(), include_etf=include_etf),
        top_n=top_n,
        ranking_metric=ranking_metric,
    )
    yesterday = rerank(
        filter_etf(source.get_yesterday(), include_etf=include_etf),
        top_n=top_n,
        ranking_metric=ranking_metric,
    )

    return MomentumComparedResponse(
        ranking_metric=ranking_metric,
        rows=compare_rankings(yesterday=yesterday, today=today, top_n=top_n),
        today_group_frequency=aggregate_group_frequency(today, top_n=top_n),
        group_strengthening=detect_group_collective_strengthening(
            yesterday=yesterday,
            today=today,
            top_n=top_n,
        ),
    )


@router.post("/themes/{symbol}/tags", response_model=ThemeMappingItemResponse)
def add_custom_theme_tag(symbol: str, payload: ThemeTagMutationRequest) -> ThemeMappingItemResponse:
    try:
        item = add_theme_tag(symbol=symbol, tag=payload.tag, industry=payload.industry)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ThemeMappingItemResponse(symbol=symbol, **item)


@router.delete("/themes/{symbol}/tags", response_model=ThemeMappingItemResponse)
def remove_custom_theme_tag(symbol: str, payload: ThemeTagMutationRequest) -> ThemeMappingItemResponse:
    try:
        item = remove_theme_tag(symbol=symbol, tag=payload.tag)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ThemeMappingItemResponse(symbol=symbol, **item)


@router.get("/themes/catalog", response_model=TagEditorCatalogResponse)
def get_tag_editor_catalog(
    include_etf: bool = Query(default=True),
    ranking_metric: RankingMetric = Query(default="turnover_value"),
    source: StockDataSource = Depends(get_ranking_data_source),
) -> TagEditorCatalogResponse:
    tracked_top_n = 100
    today_rows = rerank(
        filter_etf(source.get_today(), include_etf=include_etf),
        top_n=tracked_top_n,
        ranking_metric=ranking_metric,
    )
    return sync_and_build_catalog(rows=today_rows, tracked_top_n=tracked_top_n)
