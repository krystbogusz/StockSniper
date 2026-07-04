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

    def add_item(self, url: str, size: str, interval_seconds: int) -> tuple[bool, str]:
        with self.lock:
            data = self._read_data()

            existing_id = None
            for k, v in data.items():
                if v.get("url") == url:
                    existing_id = k
                    break

            if existing_id:
                if size in data[existing_id].get("sizes", []):
                    return False, "This size is already tracked for this product."
                else:
                    data[existing_id]["sizes"].append(size)
                    data[existing_id]["interval_seconds"] = interval_seconds
                    self._write_data(data)
                    return (
                        True,
                        f"Size {size} added to existing product (ID {existing_id}). Interval updated.",
                    )

            existing_ids = set(int(k) for k in data.keys() if k.isdigit())
            new_id_int = 1
            while new_id_int in existing_ids:
                new_id_int += 1
            new_id = str(new_id_int)

            data[new_id] = {
                "url": url,
                "sizes": [size],
                "interval_seconds": interval_seconds,
            }
            self._write_data(data)
            return (
                True,
                f"New product added with ID {new_id}, size {size} and interval {interval_seconds}s.",
            )

    def update_item(
        self, item_id: str, new_url: str, new_interval_seconds: int
    ) -> tuple[bool, str]:
        with self.lock:
            data = self._read_data()

            if item_id not in data:
                return False, "Item ID not found."

            for k, v in data.items():
                if k != item_id and v.get("url") == new_url:
                    return (
                        False,
                        "Another item with this URL already exists in the watchlist.",
                    )

            data[item_id]["url"] = new_url
            data[item_id]["interval_seconds"] = new_interval_seconds
            self._write_data(data)
            return True, f"Item {item_id} updated successfully."

    def delete_item(self, item_id: str, size: str) -> tuple[bool, str]:
        with self.lock:
            data = self._read_data()

            if item_id not in data:
                return False, "Product not found in the watchlist."

            sizes = data[item_id].get("sizes", [])
            if size not in sizes:
                return False, "Size not found for this product."

            sizes.remove(size)

            if not sizes:
                del data[item_id]
                self._write_data(data)
                return (
                    True,
                    f"Last size removed. Product with ID {item_id} has been completely deleted.",
                )
            else:
                data[item_id]["sizes"] = sizes
                self._write_data(data)
                return True, f"Size {size} removed from product (ID {item_id})."


item_manager = ItemManager()
