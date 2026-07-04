import json
import os
from threading import Lock

class ItemManager:
    def __init__(self, file_path: str = "data/items.json"):
        self.file_path = file_path
        self.lock = Lock()
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _read_data(self) -> dict:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _write_data(self, data: dict):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def list_items(self) -> dict:
        with self.lock:
            return self._read_data()

    def add_item(self, url: str) -> tuple[bool, str]:
        with self.lock:
            data = self._read_data()

            if url in data.values():
                return False, "Item already exists in the watchlist."

            existing_ids = set(int(k) for k in data.keys() if k.isdigit())
            new_id_int = 1
            while new_id_int in existing_ids:
                new_id_int += 1
            new_id = str(new_id_int)
                
            data[new_id] = url
            self._write_data(data)
            return True, f"Item added with ID {new_id}."

    def delete_item(self, url: str) -> tuple[bool, str]:
        with self.lock:
            data = self._read_data()

            item_id = None
            for k, v in data.items():
                if v == url:
                    item_id = k
                    break
                    
            if not item_id:
                return False, "Item not found in the watchlist."
                
            del data[item_id]
            self._write_data(data)
            return True, f"Item with ID {item_id} deleted."

item_manager = ItemManager()
