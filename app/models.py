import json
from pathlib import Path

DB_FILE = Path("products.json")

def load_from_db():
    if DB_FILE.exists():
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def save_to_db(product):
    products = load_from_db()
    products.append(product)
    with open(DB_FILE, "w") as f:
        json.dump(products, f, indent=4)
