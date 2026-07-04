import os
import json
import logging
from logging.handlers import RotatingFileHandler

SETTINGS_FILE = "data/settings.json"

class SettingsToggleFilter(logging.Filter):
    """
    Filtr, który odczytuje plik settings.json przy każdym logu 
    i decyduje czy przepuścić log. Dzięki temu ustawienie działa natychmiast
    w obu procesach bez restartu aplikacji.
    """
    def filter(self, record):
        if not os.path.exists(SETTINGS_FILE):
            return False
        
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings_data = json.load(f)
                return settings_data.get("logging_enabled", False)
        except Exception:
            return False

def _setup_logger(name: str, log_file: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Zapobiega duplikowaniu logów jeśli logger już ma handlery
    if not logger.handlers:
        os.makedirs("logs", exist_ok=True)
        
        handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2, encoding="utf-8")
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        handler.addFilter(SettingsToggleFilter())
        
        logger.addHandler(handler)
        
    return logger

api_logger = _setup_logger("api", "logs/api.log")
monitor_logger = _setup_logger("monitor", "logs/monitor.log")
