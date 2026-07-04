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
*(Note: Adding or updating an item triggers an automatic AI-powered security check to prevent tracking malicious URLs)*
- `POST /item/add` - Adds a new product URL and size to the watchlist.
  ```json
  {
    "url": "https://example.com/shoes",
    "size": "42",
    "interval_value": 5,
    "interval_unit": "minutes"
  }
  ```
- `POST /item/update` - Updates the URL and check interval for a specific product ID.
  ```json
  {
    "id": "1",
    "url": "https://example.com/new-shoes",
    "interval_value": 30,
    "interval_unit": "seconds"
  }
  ```
- `POST /item/delete` - Removes a specific size from a product. If it's the last size, the product is removed.
  ```json
  {
    "url": "https://example.com/shoes",
    "size": "42"
  }
  ```
- `GET /item/list` - Returns all observed items.

### Documentation
- `GET /docs` - Interactive Swagger UI for the API (requires Basic Auth).
