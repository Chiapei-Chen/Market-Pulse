# Backend - Stock Ranking API

## Setup

1. Create venv (optional):

   python -m venv .venv
   .venv\\Scripts\\activate

2. Install dependencies:

   python -m pip install -r requirements.txt

3. Data source settings

   Copy .env.example to .env.

   Phase 1 delayed-real (recommended):
   - STOCK_DATA_SOURCE=twse_delayed

   Custom API mode (optional):
   - STOCK_TODAY_API_URL
   - STOCK_YESTERDAY_API_URL

4. Upstream API response format (only for custom API mode)

   Both URLs must return a JSON array, each item with fields below:
   - symbol (string)
   - name (string)
   - industry_level_1 (string)
   - industry_level_2 (string)
   - volume (number)
   - turnover_value (number)
   - rank (number)

   Note: rank can come from your upstream. This service may rerank after ETF filtering/top_n.

## Run

python -m uvicorn main:app --reload --port 8000

Mode selection behavior:
- If STOCK_DATA_SOURCE=twse_delayed, backend uses delayed-real TWSE data.
- Else, if both STOCK_TODAY_API_URL and STOCK_YESTERDAY_API_URL are set, backend uses your custom API.
- Otherwise, backend falls back to built-in sample data.

SSL note:
- If your local machine cannot validate external certificates, set STOCK_HTTP_VERIFY_SSL=false in .env for development.

Theme mapping:
- Custom group labels are configured in app/config/stock_theme_map.json
- Format: symbol -> { code, industry, tags[] }
- `tags[0]` is treated as primary display tag

Unclassified maintenance helper:
- Export top N symbols still marked as 未分類族群
- Command (run in backend folder):
   - python scripts/export_unclassified.py --top-n 100 --metric turnover_value
   - python scripts/export_unclassified.py --top-n 100 --metric volume --include-etf

## Test

python -m pytest -q

## API Endpoints

- GET /health
- GET /api/rankings/today?top_n=100&include_etf=true
- GET /api/rankings/yesterday?top_n=100&include_etf=true
- GET /api/rankings/compared?top_n=100&include_etf=true
- GET /api/rankings/momentum?top_n=100&include_etf=true
