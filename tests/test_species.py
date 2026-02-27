"""Tests for the species endpoints."""
from tests.conftest import seed_detections
import sqlite3


def _seed_species(db: sqlite3.Connection, species_list: list[dict]):
    """Insert species info for testing."""
    c = db.cursor()
    for s in species_list:
        c.execute(
            """INSERT INTO species (name, scientific_name, description, region, habitat, conservation_status)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                s.get("name", "Test Bird"),
                s.get("scientific_name", "Testus birdus"),
                s.get("description", "A test bird."),
                s.get("region", "Global"),
                s.get("habitat", "Urban"),
                s.get("conservation_status", "Least Concern"),
            ),
        )
    db.commit()


class TestGetAllSpecies:
    """Tests for GET /api/species"""

    def test_empty(self, client):
        res = client.get("/api/species")
        assert res.status_code == 200
        assert res.json() == []

    def test_returns_species(self, client, db):
        _seed_species(db, [{"name": "House Sparrow"}, {"name": "Barn Owl"}])
        res = client.get("/api/species")
        data = res.json()
        assert len(data) == 2


class TestGetSpeciesByName:
    """Tests for GET /api/species/{species_name}"""

    def test_not_found(self, client):
        res = client.get("/api/species/Nonexistent Bird")
        assert res.status_code == 404

    def test_found(self, client, db):
        _seed_species(db, [{"name": "House Sparrow", "scientific_name": "Passer domesticus"}])
        res = client.get("/api/species/House Sparrow")
        data = res.json()
        assert data["name"] == "House Sparrow"
        assert data["scientific_name"] == "Passer domesticus"


class TestSpeciesSummary:
    """Tests for GET /api/species-summary"""

    def test_combines_detection_stats(self, client, db):
        _seed_species(db, [{"name": "House Sparrow"}])
        seed_detections(db, [
            {"species": "House Sparrow", "confidence": 0.90},
            {"species": "House Sparrow", "confidence": 0.80},
        ])
        res = client.get("/api/species-summary")
        data = res.json()
        assert len(data) == 1
        assert data[0]["detection_count"] == 2
        assert data[0]["scientific_name"] is not None
