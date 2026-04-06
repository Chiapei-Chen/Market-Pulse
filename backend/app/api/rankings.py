from fastapi import APIRouter, Depends, Query

from app.schemas.stock import MomentumComparedResponse, RankedStock, RankedStockWithChange
from app.services.data_source import StockDataSource, get_data_source
from app.services.ranking import (
    aggregate_group_frequency,
    compare_rankings,
    detect_group_collective_strengthening,
    filter_etf,
    rerank,
)

router = APIRouter()


def get_ranking_data_source() -> StockDataSource:
    return get_data_source()


@router.get("/today", response_model=list[RankedStock])
def get_today_rankings(
    top_n: int = Query(default=100, ge=1, le=500),
    include_etf: bool = Query(default=True),
    source: StockDataSource = Depends(get_ranking_data_source),
) -> list[RankedStock]:
    today = source.get_today()
    today = filter_etf(today, include_etf=include_etf)
    return rerank(today, top_n=top_n)


@router.get("/yesterday", response_model=list[RankedStock])
def get_yesterday_rankings(
    top_n: int = Query(default=100, ge=1, le=500),
    include_etf: bool = Query(default=True),
    source: StockDataSource = Depends(get_ranking_data_source),
) -> list[RankedStock]:
    yesterday = source.get_yesterday()
    yesterday = filter_etf(yesterday, include_etf=include_etf)
    return rerank(yesterday, top_n=top_n)


@router.get("/compared", response_model=list[RankedStockWithChange])
def get_compared_rankings(
    top_n: int = Query(default=100, ge=1, le=500),
    include_etf: bool = Query(default=True),
    source: StockDataSource = Depends(get_ranking_data_source),
) -> list[RankedStockWithChange]:
    today = rerank(filter_etf(source.get_today(), include_etf=include_etf), top_n=top_n)
    yesterday = rerank(filter_etf(source.get_yesterday(), include_etf=include_etf), top_n=top_n)
    return compare_rankings(yesterday=yesterday, today=today, top_n=top_n)


@router.get("/momentum", response_model=MomentumComparedResponse)
def get_momentum_snapshot(
    top_n: int = Query(default=100, ge=1, le=500),
    include_etf: bool = Query(default=True),
    source: StockDataSource = Depends(get_ranking_data_source),
) -> MomentumComparedResponse:
    today = rerank(filter_etf(source.get_today(), include_etf=include_etf), top_n=top_n)
    yesterday = rerank(filter_etf(source.get_yesterday(), include_etf=include_etf), top_n=top_n)

    return MomentumComparedResponse(
        rows=compare_rankings(yesterday=yesterday, today=today, top_n=top_n),
        today_group_frequency=aggregate_group_frequency(today, top_n=top_n),
        group_strengthening=detect_group_collective_strengthening(
            yesterday=yesterday,
            today=today,
            top_n=top_n,
        ),
    )
