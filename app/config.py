import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
DATABASE_PATH = os.path.join(BASE_DIR, "birds.db")

# Ensure storage directory exists
os.makedirs(STORAGE_DIR, exist_ok=True)
