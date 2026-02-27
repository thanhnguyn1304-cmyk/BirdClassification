"""Tests for the detections endpoints."""
from tests.conftest import seed_detections


class TestGetDetections:
    """Tests for GET /api/detections"""

    def test_empty_detections(self, client):
        """Empty DB should return empty list."""
        res = client.get("/api/detections")
        assert res.status_code == 200
        assert res.json() == []

    def test_returns_detections(self, client, db):
        """Should return all detections in newest-first order."""
        seed_detections(db, [
            {"species": "Sparrow", "timestamp": "2026-01-15 06:00:00"},
            {"species": "Owl", "timestamp": "2026-01-15 18:00:00"},
        ])
        res = client.get("/api/detections")
        data = res.json()
        assert len(data) == 2
        # Newest first
        assert data[0]["species"] == "Owl"
        assert data[1]["species"] == "Sparrow"

    def test_detection_fields(self, client, db):
        """Each detection should have the expected fields."""
        seed_detections(db, [{"species": "Robin", "confidence": 0.88}])
        res = client.get("/api/detections")
        detection = res.json()[0]
        assert "id" in detection
        assert "timestamp" in detection
        assert "species" in detection
        assert "confidence" in detection
        assert detection["species"] == "Robin"
