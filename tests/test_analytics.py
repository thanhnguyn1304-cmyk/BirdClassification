"""Tests for the analytics endpoints."""
from datetime import datetime
from tests.conftest import seed_detections


class TestSummary:
    """Tests for GET /api/analytics/summary"""

    def test_summary_empty_db(self, client):
        """Empty database should return zero counts."""
        res = client.get("/api/analytics/summary")
        assert res.status_code == 200
        data = res.json()
        assert data["total_detections"] == 0
        assert data["unique_species"] == 0
        assert data["avg_confidence"] == 0

    def test_summary_with_data(self, client, db):
        """Should count detections and compute averages."""
        seed_detections(db, [
            {"species": "House Sparrow", "confidence": 0.90, "timestamp": "2026-01-15 06:00:00"},
            {"species": "House Sparrow", "confidence": 0.80, "timestamp": "2026-01-15 07:00:00"},
            {"species": "Barn Owl", "confidence": 0.95, "timestamp": "2026-01-15 08:00:00"},
        ])
        res = client.get("/api/analytics/summary")
        data = res.json()
        assert data["total_detections"] == 3
        assert data["unique_species"] == 2
        assert data["most_recent"]["species"] == "Barn Owl"


class TestSpeciesDistribution:
    """Tests for GET /api/analytics/species-distribution"""

    def test_distribution_counts(self, client, db):
        """Should group by species and count."""
        seed_detections(db, [
            {"species": "House Sparrow"},
            {"species": "House Sparrow"},
            {"species": "Barn Owl"},
        ])
        res = client.get("/api/analytics/species-distribution")
        data = res.json()
        assert len(data) == 2
        # Sparrow should be first (higher count)
        assert data[0]["name"] == "House Sparrow"
        assert data[0]["value"] == 2


class TestHourlyActivity:
    """Tests for GET /api/analytics/hourly-activity"""

    def test_returns_24_hours(self, client):
        """Should always return 24 hour buckets."""
        res = client.get("/api/analytics/hourly-activity")
        data = res.json()
        assert len(data) == 24
        assert data[0]["hour"] == "00:00"
        assert data[23]["hour"] == "23:00"

    def test_counts_by_hour(self, client, db):
        """Detections should be counted in the correct hour bucket."""
        seed_detections(db, [
            {"timestamp": "2026-01-15 06:30:00"},
            {"timestamp": "2026-01-15 06:45:00"},
            {"timestamp": "2026-01-15 14:00:00"},
        ])
        res = client.get("/api/analytics/hourly-activity")
        data = res.json()
        hour_06 = next(h for h in data if h["hour"] == "06:00")
        hour_14 = next(h for h in data if h["hour"] == "14:00")
        assert hour_06["count"] == 2
        assert hour_14["count"] == 1


class TestHealthEndpoint:
    """Tests for GET /api/analytics/health"""

    def test_health_no_data(self, client):
        """Empty DB should return concerning status."""
        res = client.get("/api/analytics/health")
        data = res.json()
        assert data["healthScore"] == 0
        assert data["status"] == "concerning"

    def test_health_with_activity(self, client, db):
        """Active detections should produce a positive health score."""
        today = datetime.now().strftime("%Y-%m-%d")
        seed_detections(db, [
            {"timestamp": f"{today} 06:00:00", "species": "Sparrow"},
            {"timestamp": f"{today} 07:00:00", "species": "Robin"},
            {"timestamp": f"{today} 08:00:00", "species": "Owl"},
            {"timestamp": f"{today} 14:00:00", "species": "Eagle"},
            {"timestamp": f"{today} 16:00:00", "species": "Finch"},
        ])
        res = client.get("/api/analytics/health")
        data = res.json()
        assert data["healthScore"] > 0
        assert data["totalActivity"] == 5


class TestConfidenceDistribution:
    """Tests for GET /api/analytics/confidence-distribution"""

    def test_buckets(self, client, db):
        """Confidences should land in the correct bucket."""
        seed_detections(db, [
            {"confidence": 0.72},
            {"confidence": 0.85},
            {"confidence": 0.97},
        ])
        res = client.get("/api/analytics/confidence-distribution")
        data = res.json()
        buckets = {d["range"]: d["count"] for d in data}
        assert buckets["70-75%"] == 1
        assert buckets["85-90%"] == 1
        assert buckets["95-100%"] == 1
