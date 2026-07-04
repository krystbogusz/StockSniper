# StockSniper API

Simple FastAPI application to manage background processes for tracking observed items (watchlist).

## Setup

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Setup configuration:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` and set your preferred usernames, passwords, and tokens.*

## Running the API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Authentication

The API uses two types of authentication:
1. **HTTP Basic Auth**: Secures the Swagger Documentation (`/docs` and `/openapi.json`). Your browser will prompt for a username and password (configured via `API_USERNAME` and `API_PASSWORD`).
2. **HTTP Bearer Token**: Secures all operational endpoints (`/process` and `/item`). Include the token in the `Authorization: Bearer <TOKEN>` header (configured via `API_TOKEN`).

## API Endpoints

### Process Management
- `POST /process/start` - Starts the background script.
- `POST /process/stop` - Stops the background script.
- `GET /process/status` - Checks if the background script is running.

### Watchlist (Items)
- `POST /item/add` - Adds a new product URL to the watchlist (JSON body: `{"url": "http..."}`).
- `POST /item/delete` - Removes a product URL from the watchlist (JSON body: `{"url": "http..."}`).
- `GET /item/list` - Returns all observed items.

### Documentation
- `GET /docs` - Interactive Swagger UI for the API (requires Basic Auth).
