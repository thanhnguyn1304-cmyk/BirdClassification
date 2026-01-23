import sqlite3
from .config import DATABASE_PATH

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS detections 
                 (id INTEGER PRIMARY KEY, 
                  timestamp TEXT, 
                  lat REAL, 
                  lon REAL, 
                  species TEXT, 
                  confidence REAL,
                  audio_url TEXT,  
                  single_audio_url TEXT,
                  image_url TEXT,
                  single_image_url TEXT)"""
    )
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn
