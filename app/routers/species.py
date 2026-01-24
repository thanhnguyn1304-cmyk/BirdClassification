from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from ..database import get_db_connection
from ..services.bird_images import get_species_info

router = APIRouter()


@router.get("/api/species")
def get_all_species() -> List[Dict[str, Any]]:
    """Get all species from the cache with their info."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM species ORDER BY name")
    rows = c.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


@router.get("/api/species/{species_name}")
def get_species_by_name(species_name: str) -> Dict[str, Any]:
    """
    Get species info by name. 
    If not in cache, fetches from Wikipedia and caches it.
    """
    info = get_species_info(species_name)
    
    if not info:
        raise HTTPException(status_code=404, detail=f"Species '{species_name}' not found")
    
    return info


@router.get("/api/species-summary")
def get_species_summary() -> List[Dict[str, Any]]:
    """
    Get a summary of all detected species with their info.
    Combines detection stats with species info from cache.
    """
    conn = get_db_connection()
    c = conn.cursor()
    
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
    
    conn.close()
    
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
