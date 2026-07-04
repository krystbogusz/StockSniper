import os
import json
import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app.core.config import settings
from app.core.email_client import send_email
from app.core.llm_client import check_availability

ITEMS_FILE = "data/items.json"
TICK_SECONDS = 5

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.managed_default_content_settings.plugins": 2,
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.media_stream": 2,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--log-level=3")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver

def main():
    print("Starting monitoring script with individual intervals (Selenium Headless)...", flush=True)
    if not settings.llm_api_key or settings.llm_api_key == "your_gemini_api_key_here":
        print("ERROR: LLM_API_KEY is missing. Script halted.", flush=True)
        sys.exit(1)
    
    last_checked = {}
    
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
                if item_id not in last_checked or (current_time - last_checked[item_id]) >= interval:
                    items_to_check.append((item_id, url, sizes))
                    
            if items_to_check:
                driver = None
                try:
                    driver = setup_driver()
                    for item_id, url, sizes in items_to_check:
                        print(f"Checking: {url} for sizes: {sizes}", flush=True)
                        try:
                            driver.get(url)
                            time.sleep(3)
                            body_element = driver.find_element(By.TAG_NAME, "body")
                            text_content = body_element.text
                            available = check_availability(text_content, sizes)
                            if available:
                                print(f"Available sizes: {available}", flush=True)
                                subject = f"PRODUCT AVAILABLE! Sizes: {', '.join(available)}"
                                body = f"Your observed product is available in sizes: {', '.join(available)}\n\nLink: {url}"
                                send_email(subject, body)
                            else:
                                print(f"Unavailable: {url}", flush=True)
                            last_checked[item_id] = time.time()
                        except Exception as e:
                            print(f"Error while checking {url}: {e}", flush=True)
                except Exception as driver_err:
                    print(f"Error initializing Selenium driver: {driver_err}", flush=True)
                finally:
                    if driver:
                        driver.quit()
        except Exception as e:
            print(f"Main loop error: {e}", flush=True)
        time.sleep(TICK_SECONDS)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Script stopped manually.", flush=True)
        sys.exit(0)
