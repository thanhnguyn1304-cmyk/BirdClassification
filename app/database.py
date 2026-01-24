import sqlite3
from .config import DATABASE_PATH

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Detections table
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
                  single_image_url TEXT,
                  bird_photo_url TEXT)"""
    )
    
    # Add column if it doesn't exist (for existing databases)
    try:
        c.execute("ALTER TABLE detections ADD COLUMN bird_photo_url TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Species cache table - stores bird info fetched from Wikipedia
    c.execute(
        """CREATE TABLE IF NOT EXISTS species
                 (id INTEGER PRIMARY KEY,
                  name TEXT UNIQUE,
                  scientific_name TEXT,
                  image_url TEXT,
                  description TEXT,
                  region TEXT,
                  habitat TEXT,
                  conservation_status TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)"""
    )
        
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn
