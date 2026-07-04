import os
import pytest
from fastapi.testclient import TestClient

os.environ["API_BEARER_TOKEN"] = "test_token"
os.environ["API_USERNAME"] = "admin"
os.environ["API_PASSWORD"] = "testpass"
os.environ["LLM_API_KEY"] = "fake_test_key"
os.environ["ITEMS_FILE_PATH"] = "data/test_items.json"

from app.main import app
from app.core.item_manager import item_manager
from app.core.config import settings

@pytest.fixture(scope="module")
def client():
    item_manager.file_path = "data/test_items.json"
    item_manager._ensure_file_exists()
    
    with TestClient(app) as c:
        yield c
        
    if os.path.exists("data/test_items.json"):
        os.remove("data/test_items.json")

@pytest.fixture
def auth_headers():
    return {"Authorization": f"Bearer {settings.api_token}"}
