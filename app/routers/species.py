from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import sqlite3

from ..database import get_db


router = APIRouter()


@router.get("/api/species")
def get_all_species(db: sqlite3.Connection = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get all species from the cache with their info."""
    c = db.cursor()
    c.execute("SELECT * FROM species ORDER BY name")
    rows = c.fetchall()

    return [dict(row) for row in rows]


@router.get("/api/species/{species_name}")
def get_species_by_name(species_name: str, db: sqlite3.Connection = Depends(get_db)) -> Dict[str, Any]:
    """Get species info by name from the database cache."""
    c = db.cursor()
    c.execute("SELECT * FROM species WHERE name = ?", (species_name,))
    row = c.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail=f"Species '{species_name}' not found")

    return dict(row)


@router.get("/api/species-summary")
def get_species_summary(db: sqlite3.Connection = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Get a summary of all detected species with their info.
    Combines detection stats with species info from cache.
    """
    c = db.cursor()

    # Get detection stats per species
    c.execute("""
        SELECT 
            species,
            COUNT(*) as detection_count,
            AVG(confidence) as avg_confidence,
            MAX(timestamp) as last_seen,
            MIN(timestamp) as first_seen
        FROM detections 
        GROUP BY species 
        ORDER BY detection_count DESC
    """)
    detection_stats = {row['species']: dict(row) for row in c.fetchall()}

    # Get species info from cache
    c.execute("SELECT * FROM species")
    species_info = {row['name']: dict(row) for row in c.fetchall()}

    # Combine stats with species info
    result = []
    for species_name, stats in detection_stats.items():
        info = species_info.get(species_name, {})
        result.append({
            "name": species_name,
            "detection_count": stats['detection_count'],
            "avg_confidence": round(stats['avg_confidence'] * 100, 1),
            "last_seen": stats['last_seen'],
            "first_seen": stats['first_seen'],
            "image_url": info.get('image_url'),
            "description": info.get('description'),
            "region": info.get('region'),
            "scientific_name": info.get('scientific_name'),
            "habitat": info.get('habitat'),
            "conservation_status": info.get('conservation_status'),
        })

    return result
