from fastapi import APIRouter, Depends
from collections import Counter
from datetime import datetime, timedelta
import sqlite3

from ..database import get_db

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def _parse_timestamp(raw: str) -> datetime | None:
    """Try to parse a timestamp string into a datetime object."""
    for fmt in ("%Y-%m-%d %H:%M:%S",):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(raw)
    except (ValueError, TypeError):
        return None


@router.get("/summary")
def get_summary(db: sqlite3.Connection = Depends(get_db)):
    """Get overall summary statistics."""
    c = db.cursor()

    c.execute("SELECT COUNT(*) FROM detections")
    total_detections = c.fetchone()[0]

    c.execute("SELECT COUNT(DISTINCT species) FROM detections")
    unique_species = c.fetchone()[0]

    c.execute("SELECT AVG(confidence) FROM detections")
    avg_confidence = c.fetchone()[0] or 0

    c.execute("SELECT timestamp, species FROM detections ORDER BY timestamp DESC LIMIT 1")
    recent = c.fetchone()

    return {
        "total_detections": total_detections,
        "unique_species": unique_species,
        "avg_confidence": round(avg_confidence * 100, 1),
        "most_recent": {
            "timestamp": recent[0] if recent else None,
            "species": recent[1] if recent else None
        }
    }


@router.get("/species-distribution")
def get_species_distribution(db: sqlite3.Connection = Depends(get_db)):
    """Get detection counts by species for pie chart."""
    c = db.cursor()

    c.execute("SELECT species, COUNT(*) as count FROM detections GROUP BY species ORDER BY count DESC")
    rows = c.fetchall()

    return [{"name": row[0], "value": row[1]} for row in rows]


@router.get("/trends")
def get_trends(period: str = "day", db: sqlite3.Connection = Depends(get_db)):
    """Get detection trends over time for line/bar charts."""
    c = db.cursor()

    c.execute("SELECT timestamp, species FROM detections ORDER BY timestamp")
    rows = c.fetchall()

    trends = {}
    for row in rows:
        dt = _parse_timestamp(row[0])
        if dt is None:
            continue

        if period == "day":
            key = dt.strftime("%Y-%m-%d")
        elif period == "week":
            week_start = dt - timedelta(days=dt.weekday())
            key = week_start.strftime("%Y-%m-%d")
        elif period == "month":
            key = dt.strftime("%Y-%m")
        elif period == "hour":
            key = dt.strftime("%Y-%m-%d %H:00")
        else:
            key = dt.strftime("%Y-%m-%d")

        if key not in trends:
            trends[key] = {"date": key, "count": 0, "species": {}}
        trends[key]["count"] += 1

        species = row[1]
        if species not in trends[key]["species"]:
            trends[key]["species"][species] = 0
        trends[key]["species"][species] += 1

    result = sorted(trends.values(), key=lambda x: x["date"])
    return result


def _compute_hourly_activity(db: sqlite3.Connection) -> list[dict]:
    """Shared logic for hourly activity (used by endpoint and health calc)."""
    c = db.cursor()
    c.execute("SELECT timestamp FROM detections")
    rows = c.fetchall()

    hours = Counter()
    for row in rows:
        dt = _parse_timestamp(row[0])
        if dt is None:
            continue
        hours[dt.hour] += 1

    return [{"hour": f"{h:02d}:00", "count": hours.get(h, 0)} for h in range(24)]


@router.get("/hourly-activity")
def get_hourly_activity(db: sqlite3.Connection = Depends(get_db)):
    """Get detection activity by hour of day."""
    return _compute_hourly_activity(db)


@router.get("/confidence-distribution")
def get_confidence_distribution(db: sqlite3.Connection = Depends(get_db)):
    """Get distribution of confidence scores."""
    c = db.cursor()

    c.execute("SELECT confidence FROM detections")
    rows = c.fetchall()

    buckets = {
        "70-75%": 0,
        "75-80%": 0,
        "80-85%": 0,
        "85-90%": 0,
        "90-95%": 0,
        "95-100%": 0
    }

    for row in rows:
        conf = row[0] * 100
        if conf < 75:
            buckets["70-75%"] += 1
        elif conf < 80:
            buckets["75-80%"] += 1
        elif conf < 85:
            buckets["80-85%"] += 1
        elif conf < 90:
            buckets["85-90%"] += 1
        elif conf < 95:
            buckets["90-95%"] += 1
        else:
            buckets["95-100%"] += 1

    return [{"range": k, "count": v} for k, v in buckets.items()]


@router.get("/health")
def get_population_health(db: sqlite3.Connection = Depends(get_db)):
    """Analyze population health based on activity patterns."""
    # 1. Get Hourly Data (reuse shared logic with same DB connection)
    hourly_data = _compute_hourly_activity(db)

    if not hourly_data:
        return None

    # 2. Calculate Stats
    total_activity = sum(h["count"] for h in hourly_data)
    if total_activity == 0:
        return {
            "healthScore": 0,
            "status": "concerning",
            "message": "No activity detected.",
            "peakHours": [],
            "quietHours": [],
            "dawnActivity": 0,
            "totalActivity": 0
        }

    avg_activity = total_activity / len(hourly_data)

    peak_hours = [h["hour"] for h in hourly_data if h["count"] > avg_activity]
    quiet_hours = [h["hour"] for h in hourly_data if h["count"] < (avg_activity / 2)]

    # Dawn Chorus (5-8 AM)
    dawn_activity = 0
    for h in hourly_data:
        hour_int = int(h["hour"].split(":")[0])
        if 5 <= hour_int <= 8:
            dawn_activity += h["count"]

    # 3. Calculate Score
    dawn_ratio = dawn_activity / max(total_activity, 1)
    dawn_score = dawn_ratio * 100 * 0.3
    diversity_score = 30 if len(peak_hours) >= 4 else len(peak_hours) * 7
    activity_score = min(total_activity / 10, 40)

    # D. Recency Decay (Penalty) — uses the SAME db connection
    c = db.cursor()
    c.execute("SELECT timestamp FROM detections ORDER BY timestamp DESC LIMIT 1")
    last_detection = c.fetchone()

    decay_penalty = 0
    hours_since = 0

    if last_detection:
        last_dt = _parse_timestamp(last_detection[0])
        if last_dt is None:
            last_dt = datetime.now()

        time_diff = datetime.now() - last_dt
        hours_since = time_diff.total_seconds() / 3600

        if hours_since > 24:
            days_over = (hours_since - 24) / 24
            decay_penalty = days_over * 5

    raw_score = activity_score + diversity_score + dawn_score - decay_penalty
    health_score = max(0, round(raw_score))

    # 4. Determine Status
    if health_score >= 70:
        status = 'healthy'
        message = 'Strong bird activity indicates a healthy ecosystem with good biodiversity.'
    elif health_score >= 40:
        status = 'moderate'
        message = 'Moderate bird activity. Consider monitoring for changes in habitat conditions.'
    else:
        status = 'concerning'
        message = 'Low bird activity detected. This may indicate environmental stressors.'

    if decay_penalty > 5:
        message += f" Score reduced due to lack of recent activity ({int(hours_since // 24)} days)."

    return {
        "healthScore": health_score,
        "status": status,
        "message": message,
        "peakHours": peak_hours[:4],
        "quietHours": quiet_hours[:4],
        "dawnActivity": dawn_activity,
        "totalActivity": total_activity
    }
