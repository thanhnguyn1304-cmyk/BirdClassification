"""
Shared test fixtures for AvianNET tests.

Creates an in-memory SQLite database and a FastAPI test client
so tests run fast and don't touch the real database.

Key design: both `client` and `db` share the SAME in-memory connection
so data seeded via `db` is visible through API requests on `client`.
"""
import sqlite3
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db


@pytest.fixture()
def db():
    """In-memory SQLite database for testing."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row

    # Create tables (same schema as init_db)
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
          single_image_url TEXT,
          bird_photo_url TEXT)"""
    )
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

    yield conn
    conn.close()


@pytest.fixture()
def client(db):
    """
    FastAPI test client that shares the same in-memory DB.
    
    Uses dependency_overrides to inject the test DB connection
    into all endpoints that use Depends(get_db).
    """
    def _override_get_db():
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def seed_detections(conn: sqlite3.Connection, detections: list[dict]) -> None:
    """Helper to insert test detections into the database."""
    c = conn.cursor()
    for d in detections:
        c.execute(
            """INSERT INTO detections 
               (timestamp, lat, lon, species, confidence, audio_url, single_audio_url, image_url, single_image_url) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                d.get("timestamp", "2026-01-15 08:30:00"),
                d.get("lat", 21.0),
                d.get("lon", 105.0),
                d.get("species", "House Sparrow"),
                d.get("confidence", 0.92),
                d.get("audio_url", "/storage/test.wav"),
                d.get("single_audio_url", "/storage/test0.wav"),
                d.get("image_url", "/storage/test.png"),
                d.get("single_image_url", "/storage/test0.png"),
            ),
        )
    conn.commit()
