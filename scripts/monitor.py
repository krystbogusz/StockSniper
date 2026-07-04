import os
import json
import time
import sys
from playwright.sync_api import sync_playwright

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app.core.config import settings
from app.core.email_client import send_email
from app.core.llm_client import check_availability
from app.core.logger import monitor_logger

ITEMS_FILE = "data/items.json"
TICK_SECONDS = 5


def fetch_page_text(url: str) -> str:
    api_payloads = []

    def handle_response(response):
        try:
            if "application/json" in response.headers.get("content-type", ""):
                text = response.text()
                if len(text) < 100000:
                    if any(
                        k in text.lower()
                        for k in [
                            "size",
                            "variant",
                            "stock",
                            "availability",
                            "sku",
                            "rozmiar",
                        ]
                    ):
                        try:
                            data = response.json()
                            api_payloads.append(json.dumps(data, indent=2))
                        except:
                            api_payloads.append(text)
        except Exception:
            pass

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            viewport={"width": 1920, "height": 1080},
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
            },
        )
        page = context.new_page()
        page.on("response", handle_response)

        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(1000)
        except Exception as e:
            monitor_logger.warning(
                f"Timeout or error while loading {url}, attempting to extract current text: {e}"
            )

        html = page.content()
        browser.close()

    import re

    scripts = re.findall(
        r"<script[^>]*>(.*?)</script>", html, flags=re.IGNORECASE | re.DOTALL
    )
    useful_scripts = []
    for s in scripts:
        s_lower = s.lower()
        if "schema.org" in s_lower or any(
            k in s_lower for k in ["size", "variant", "availability", "sku", "stock"]
        ):
            if not any(
                bad in s_lower
                for bad in [
                    "translations",
                    "locales",
                    "i18n",
                    "google_tag_manager",
                    "gtm-",
                    "analytics",
                ]
            ):
                if len(s) < 80000:
                    try:
                        parsed_json = json.loads(s)
                        useful_scripts.append(json.dumps(parsed_json, indent=2))
                    except:
                        useful_scripts.append(s.strip())

    html_clean = re.sub(
        r"<(script|noscript|style|svg|path|symbol)[^>]*>.*?</\1>",
        " ",
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    html_clean = re.sub(
        r"<(meta|link|img|picture|source|br|hr|video|iframe)[^>]*>",
        " ",
        html_clean,
        flags=re.IGNORECASE,
    )
    html_clean = re.sub(
        r'\s+(href|src|srcset|sizes|style|content)=["\'][^"\']*["\']',
        "",
        html_clean,
        flags=re.IGNORECASE,
    )
    html_clean = re.sub(
        r"data:image/[a-zA-Z0-9\-\+]+;base64,[a-zA-Z0-9\+\/=\s]+", "", html_clean
    )

    html_lines = html_clean.replace(">", ">\n").replace("<", "\n<").split("\n")

    pattern_str = r"\b(?:size|sizes|variant|variants|stock|availability|sku|inventory|rozmiar|rozmiary|talla|wymiar|wymiary|koszyk|cart|dodaj|add|wariant|warianty|dost[eę]pn\w*|stan|xs|s|m|l|xl|xxl|xxs|3xl|4xl|os|onesize|one\s*size|3[2-9]|4[0-9]|50|universalny)\b"
    exact_pattern = re.compile(pattern_str, re.IGNORECASE)

    kept_indices = set()
    CONTEXT_WINDOW = 3

    for i, line in enumerate(html_lines):
        if exact_pattern.search(line):
            for j in range(
                max(0, i - CONTEXT_WINDOW), min(len(html_lines), i + CONTEXT_WINDOW + 1)
            ):
                kept_indices.add(j)

    filtered_lines = []
    last_idx = -2
    for idx in sorted(kept_indices):
        if idx > last_idx + 1 and last_idx != -2:
            filtered_lines.append("[...]")
        clean_line = re.sub(r"[ \t]+", " ", html_lines[idx]).strip()
        if clean_line:
            filtered_lines.append(clean_line)
        last_idx = idx

    html_out = "\n".join(filtered_lines)

    final_parts = [html_out]
    if useful_scripts:
        final_parts.append(
            "\n\n--- HIDDEN SEO SCRIPTS (JSON-LD) ---\n\n" + "\n\n".join(useful_scripts)
        )
    if api_payloads:
        final_parts.append(
            "\n\n--- API PAYLOADS (XHR) ---\n\n" + "\n\n".join(api_payloads)
        )

    return "".join(final_parts)


def main():
    monitor_logger.info("Starting monitoring script with Playwright (Rendered HTML)...")
    if not settings.llm_api_key or settings.llm_api_key == "your_gemini_api_key_here":
        monitor_logger.error("LLM_API_KEY is missing. Script halted.")
        sys.exit(1)

    last_checked = {}
    last_error_email_time = {}

    while True:
        try:
            if os.path.exists(ITEMS_FILE):
                with open(ITEMS_FILE, "r", encoding="utf-8") as f:
                    items = json.load(f)
            else:
                items = {}

            items_to_check = []
            current_time = time.time()

            for item_id, item_data in items.items():
                url = item_data.get("url")
                sizes = item_data.get("sizes", [])
                interval = item_data.get("interval_seconds", 300)
                if not url or not sizes:
                    continue
                if (
                    item_id not in last_checked
                    or (current_time - last_checked[item_id]) >= interval
                ):
                    items_to_check.append((item_id, url, sizes))

            if items_to_check:
                for item_id, url, sizes in items_to_check:
                    monitor_logger.info(f"Checking: {url} for sizes: {sizes}")
                    try:
                        text_content = fetch_page_text(url)
                        monitor_logger.info(
                            f"Sending LLM query for {url} to check sizes {sizes}. Text length to analyze: {len(text_content)} chars."
                        )
                        available, product_name = check_availability(
                            text_content, sizes
                        )
                        if available:
                            monitor_logger.info(
                                f"Available sizes found: {available} for {product_name} ({url})"
                            )
                            subject = f"PRODUCT AVAILABLE! {product_name} - Sizes: {', '.join(available)}"
                            body = f"Great news!\n\nYour tracked product '{product_name}' is now available in sizes: {', '.join(available)}.\n\nLink to purchase: {url}\n\nHappy shopping!"
                            send_email(subject, body)
                            monitor_logger.info("Notification email sent.")
                        else:
                            monitor_logger.info(f"Unavailable: {product_name} ({url})")
                        last_checked[item_id] = time.time()
                    except Exception as e:
                        monitor_logger.error(f"Error while checking {url}: {e}")
                        if current_time - last_error_email_time.get(item_id, 0) > 3600:
                            send_email(
                                f"StockSniper Monitor Error",
                                f"An error occurred while checking {url}:\n\n{type(e).__name__}: {e}",
                            )
                            last_error_email_time[item_id] = current_time
        except Exception as e:
            monitor_logger.error(f"Main loop error: {e}")
            if time.time() - last_error_email_time.get("MAIN_LOOP", 0) > 3600:
                send_email(
                    "StockSniper Main Loop Error",
                    f"A critical error occurred in the main monitoring loop:\n\n{type(e).__name__}: {e}",
                )
                last_error_email_time["MAIN_LOOP"] = time.time()

        time.sleep(TICK_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        monitor_logger.info("Script stopped manually.")
        sys.exit(0)
