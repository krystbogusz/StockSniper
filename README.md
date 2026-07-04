# StockSniper

StockSniper is a smart, automated e-commerce monitoring system. It combines a RESTful API (FastAPI) for managing watchlists and an independent background script (Selenium Headless) to monitor specific products for availability. When a product is available, it notifies the user via email. It leverages Google's Gemini GenAI to check for phishing/unsafe links and intelligently parse page contents to locate available sizes.

## Features

- **FastAPI Backend:** Secure REST API for managing monitored items and the background worker process.
- **Headless Browser Scraping:** Uses `Playwright` with Firefox to effectively bypass CDNs and bot-protections, rendering JavaScript and extracting XHR APIs.
- **AI-Powered Analysis:** Uses `google-genai` to parse text and check for exact requested sizes, bypassing complex DOM structures and ignoring cross-sells.
- **URL Security Checks:** Automatically assesses URLs via LLM to reject phishing or malicious links before they are stored.
- **Dynamic Logging System:** Toggable logging mechanism for debugging, logging API access and script operations without a restart.
- **Automated Health Checks:** Includes a scheduled health checker endpoint and background task to ensure the scraping monitor never hangs.
- **Email Notifications:** Instant alerts using SMTP for both product availability and automated script error monitoring.
- **Comprehensive Test Suite:** Unit testing with `pytest` using mocked AI responses and mocked network calls.

## Prerequisites

- Python 3.13+
- A Google Gemini API Key
- SMTP credentials (e.g., Gmail App Password)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd StockSniper
   ```

2. **Set up a virtual environment and install dependencies:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory based on the following template:

   ```env
   # API Settings
   API_HOST=0.0.0.0
   API_PORT=8000
   API_USERNAME=admin
   API_PASSWORD=secret
   API_TOKEN=your_secure_bearer_token

   # Background Script Settings
   SCRIPT_PATH=./scripts/monitor.py

   # GenAI Settings
   LLM_API_KEY=your_gemini_api_key_here

   # Email Settings
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   EMAIL_TO=recipient_email@gmail.com
   ```

## Running the Application

### 1. Start the API Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
You can access the Swagger UI documentation securely via Basic Auth at `http://localhost:8000/docs`.

### 2. Manage the Monitor Process

You can start or stop the background scraping process using the API (or via the provided Postman collection):

- **Start:** `POST /process/start` (Requires Bearer Token)
- **Stop:** `POST /process/stop` (Requires Bearer Token)
- **Restart:** `POST /process/restart` (Requires Bearer Token)
- **Status:** `GET /process/status` (Requires Bearer Token)
- **Health Check:** `GET /process/health` (Requires Bearer Token)

## API Endpoints

All functional endpoints require `Authorization: Bearer <API_TOKEN>`.

### Item Watchlist (`/item`)

- `GET /item/list`: Returns all monitored items.
- `POST /item/add`: Add a new product to monitor.
  ```json
  {
    "url": "https://example.com/shoes",
    "size": "42",
    "interval_value": 5,
    "interval_unit": "minutes"
  }
  ```
- `POST /item/update`: Update the monitoring interval of an existing item by its ID.
- `POST /item/delete`: Remove an item from the watchlist.

### Settings (`/settings`)

- `POST /settings/logging`: Dynamically toggle disk logging on or off for both the API and the monitor script.
  ```json
  {
    "enabled": true
  }
  ```
  *Logs are saved in the `logs/` directory.*

## Postman Collection

A ready-to-use Postman collection is included in the root directory (`postman_collection.json`). Import it into Postman to easily interact with all endpoints. Make sure to set the `bearer_token` collection variable to match your `API_TOKEN`.

## Testing

The project uses `pytest` for unit testing. Tests include mock models for Google GenAI to prevent real API calls and charges.

To run the test suite:
```bash
pytest
```

## Architecture Notes

- **Process Isolation:** The monitoring script runs as an isolated subprocess. State changes (like turning logging on/off) are communicated via a shared `data/settings.json` configuration file.
- **Smart Parsing & Error Recovery:** The script uses `Playwright` to intercept background XHR/JSON requests and hidden SEO data (JSON-LD). It condenses massive HTML blobs using regex before sending payloads to Gemini AI to ensure fast and cheap API usage. All unhandled exceptions trigger immediate email alerts to the administrator.
- **Clean Codebase:** Fully formatted following strict PEP8 guidelines. All internal and external logs/outputs are in English for maximum maintainability.
