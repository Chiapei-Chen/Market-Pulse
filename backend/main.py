from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.api.rankings import router as rankings_router

app = FastAPI(title="Stock Ranking API", version="0.1.0")


@app.middleware("http")
async def no_cache_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "https://market-pulse-web.zeabur.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rankings_router, prefix="/api/rankings", tags=["rankings"])


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/debug/env")
def debug_env() -> dict[str, str]:
    import os
    return {
        "STOCK_DATA_SOURCE": os.getenv("STOCK_DATA_SOURCE", "(not set)"),
        "STOCK_HTTP_VERIFY_SSL": os.getenv("STOCK_HTTP_VERIFY_SSL", "(not set)"),
    }
