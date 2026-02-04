from fastapi import APIRouter
from collections import Counter
from datetime import datetime, timedelta

from ..database import get_db_connection

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
def get_summary():
    """Get overall summary statistics."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Total detections
    c.execute("SELECT COUNT(*) FROM detections")
    total_detections = c.fetchone()[0]
    
    # Unique species
    c.execute("SELECT COUNT(DISTINCT species) FROM detections")
    unique_species = c.fetchone()[0]
    
    # Average confidence
    c.execute("SELECT AVG(confidence) FROM detections")
    avg_confidence = c.fetchone()[0] or 0
    
    # Most recent detection
    c.execute("SELECT timestamp, species FROM detections ORDER BY timestamp DESC LIMIT 1")
    recent = c.fetchone()
    
    conn.close()
    
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
def get_species_distribution():
    """Get detection counts by species for pie chart."""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT species, COUNT(*) as count FROM detections GROUP BY species ORDER BY count DESC")
    rows = c.fetchall()
    conn.close()
    
    return [{"name": row[0], "value": row[1]} for row in rows]


@router.get("/trends")
def get_trends(period: str = "day"):
    """Get detection trends over time for line/bar charts."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get all detections with timestamps
    c.execute("SELECT timestamp, species FROM detections ORDER BY timestamp")
    rows = c.fetchall()
    conn.close()
    
    # Group by period
    trends = {}
    for row in rows:
        try:
            dt = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        except:
            try:
                dt = datetime.fromisoformat(row[0])
            except:
                continue
        
        if period == "day":
            key = dt.strftime("%Y-%m-%d")
        elif period == "week":
            # Get the Monday of the week
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
    
    # Convert to list and sort
    result = sorted(trends.values(), key=lambda x: x["date"])
    return result


@router.get("/hourly-activity")
def get_hourly_activity():
    """Get detection activity by hour of day."""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT timestamp FROM detections")
    rows = c.fetchall()
    conn.close()
    
    hours = Counter()
    for row in rows:
        try:
            dt = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        except:
            try:
                dt = datetime.fromisoformat(row[0])
            except:
                continue
        hours[dt.hour] += 1
    
    # Fill in missing hours with 0
    result = []
    for h in range(24):
        result.append({
            "hour": f"{h:02d}:00",
            "count": hours.get(h, 0)
        })
    
    return result


@router.get("/confidence-distribution")
def get_confidence_distribution():
    """Get distribution of confidence scores."""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT confidence FROM detections")
    rows = c.fetchall()
    conn.close()
    
    # Create buckets: 70-75, 75-80, 80-85, 85-90, 90-95, 95-100
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
def get_population_health():
    """
    Analyze population health based on activity patterns.
    (Ported from Frontend)
    """
    # 1. Get Hourly Data (Internal Call)
    hourly_data = get_hourly_activity()
    
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

    # Peak Hours (> avg)
    peak_hours = [h["hour"] for h in hourly_data if h["count"] > avg_activity]
    
    # Quiet Hours (< avg / 2)
    quiet_hours = [h["hour"] for h in hourly_data if h["count"] < (avg_activity / 2)]

    # Dawn Chorus (5-8 AM)
    dawn_activity = 0
    for h in hourly_data:
        hour_int = int(h["hour"].split(":")[0])
        if 5 <= hour_int <= 8:
            dawn_activity += h["count"]

    # 3. Calculate Score
    # A. Dawn Ratio (30% weight) -> More dawn chorus is good
    dawn_ratio = dawn_activity / max(total_activity, 1)
    dawn_score = dawn_ratio * 100 * 0.3

    # B. Diversity Score (Max 30) -> More peak hours means spread out activity
    diversity_score = 30 if len(peak_hours) >= 4 else len(peak_hours) * 7

    # C. Activity Score (Max 40) -> Raw volume of birds
    activity_score = min(total_activity / 10, 40)

    health_score = round(activity_score + diversity_score + dawn_score)

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

    return {
        "healthScore": health_score,
        "status": status,
        "message": message,
        # Take just the simple hour string for frontend display
        "peakHours": peak_hours[:4], 
        "quietHours": quiet_hours[:4],
        "dawnActivity": dawn_activity,
        "totalActivity": total_activity
    }
