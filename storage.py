import os
import sys
import json

DATA_FILE = "data.json"

def resource_path(*parts):
    """Use _MEIPASS when bundled, else the script/exe directory."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.argv[0])))
    return os.path.join(base, *parts)

def data_path(filename):
    """Keep data next to the .exe (or script), not inside _MEIPASS temp."""
    if getattr(sys, "_MEIPASS", None):
        return os.path.join(os.path.dirname(sys.executable), filename)
    return os.path.abspath(filename)

def load_data():
    """Load weight tracking data from JSON file."""
    path = data_path(DATA_FILE)
    if not os.path.exists(path):
        return {"start": 95, "goal": 83, "current": 95, "history": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    """Save weight tracking data to JSON file."""
    path = data_path(DATA_FILE)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

