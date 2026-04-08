# Frontend - Stock Ranking Dashboard

Vue 3 (Composition API) + TypeScript + Tailwind CSS + Pinia

## Setup

npm install

Copy .env.example to .env and set VITE_API_BASE_URL for your environment.

Example:

VITE_API_BASE_URL=http://127.0.0.1:8000/api/rankings

## Run

npm run dev

## Build

npm run build

## Key Features

- Top N ranking query (parameterized, default 100)
- ETF switch filter
- Ranking change display:
	- Up: red arrow
	- Down: green arrow
	- New entry: New badge
