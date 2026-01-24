"""
Bird Image Service - Fetches bird info from Wikipedia API with database caching.
Stores species data permanently so future lookups are instant.
"""
import requests
import sqlite3
import re
from typing import Optional, Dict, Any
from ..config import DATABASE_PATH

# Wikipedia requires a proper User-Agent header
HEADERS = {
    "User-Agent": "AvianNet/1.0 (Bird Classification App; https://github.com/aviannet)"
}


def get_cached_species_info(species: str) -> Optional[Dict[str, Any]]:
    """
    Check if we have cached info for this species in the database.
    Returns full species info dict if found, None otherwise.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(
        "SELECT * FROM species WHERE name = ?",
        (species,)
    )
    result = c.fetchone()
    conn.close()
    
    if result:
        return dict(result)
    return None


def save_species_info(species_info: Dict[str, Any]) -> None:
    """Save species info to the database cache."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    try:
        c.execute(
            """INSERT OR REPLACE INTO species 
               (name, scientific_name, image_url, description, region, habitat, conservation_status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                species_info.get("name"),
                species_info.get("scientific_name"),
                species_info.get("image_url"),
                species_info.get("description"),
                species_info.get("region"),
                species_info.get("habitat"),
                species_info.get("conservation_status"),
            )
        )
        conn.commit()
    except Exception as e:
        print(f"❌ Error saving species info: {e}")
    finally:
        conn.close()


def extract_region_from_text(text: str) -> str:
    """Extract region/distribution info from Wikipedia text."""
    # Look for common patterns
    region_patterns = [
        r"found in ([^.]+)",
        r"native to ([^.]+)",
        r"distributed (?:across|in|throughout) ([^.]+)",
        r"occurs (?:in|across|throughout) ([^.]+)",
        r"breeds (?:in|across) ([^.]+)",
    ]
    
    for pattern in region_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            region = match.group(1).strip()
            # Clean up and limit length
            if len(region) > 150:
                region = region[:147] + "..."
            return region
    
    return "Widespread"


def fetch_species_info_from_wikipedia(species: str) -> Optional[Dict[str, Any]]:
    """
    Fetch full species info from Wikipedia API.
    Returns dict with image_url, description, region, etc.
    """
    try:
        search_term = species.replace("'", "").strip()
        
        # Get both page image AND extract (summary text)
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "titles": search_term,
            "prop": "pageimages|extracts|info",
            "pithumbsize": 500,
            "exintro": True,  # Only get intro section
            "explaintext": True,  # Get plain text, not HTML
            "exsentences": 5,  # Limit to 5 sentences
            "redirects": 1
        }
        
        response = requests.get(search_url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pages = data.get("query", {}).get("pages", {})
        
        for page_id, page_data in pages.items():
            if page_id != "-1":
                thumbnail = page_data.get("thumbnail", {})
                image_url = thumbnail.get("source")
                extract = page_data.get("extract", "")
                
                # Clean up description
                description = extract.strip() if extract else ""
                if len(description) > 300:
                    description = description[:297] + "..."
                
                # Extract region from description
                region = extract_region_from_text(extract) if extract else "Unknown"
                
                if image_url or description:
                    return {
                        "name": species,
                        "scientific_name": None,  # Could be extracted with more parsing
                        "image_url": image_url,
                        "description": description,
                        "region": region,
                        "habitat": None,
                        "conservation_status": None
                    }
        
        # Try with " (bird)" suffix
        params["titles"] = f"{search_term} (bird)"
        response = requests.get(search_url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if page_id != "-1":
                thumbnail = page_data.get("thumbnail", {})
                image_url = thumbnail.get("source")
                extract = page_data.get("extract", "")
                
                description = extract.strip() if extract else ""
                if len(description) > 300:
                    description = description[:297] + "..."
                
                region = extract_region_from_text(extract) if extract else "Unknown"
                
                if image_url or description:
                    return {
                        "name": species,
                        "scientific_name": None,
                        "image_url": image_url,
                        "description": description,
                        "region": region,
                        "habitat": None,
                        "conservation_status": None
                    }
        
        print(f"⚠️ No info found for {species}")
        return None
        
    except Exception as e:
        print(f"❌ Error fetching info for {species}: {e}")
        return None


def get_species_info(species: str) -> Optional[Dict[str, Any]]:
    """
    Main function to get species info.
    First checks cache, then fetches from Wikipedia if not found.
    """
    # Check cache first
    cached_info = get_cached_species_info(species)
    if cached_info:
        print(f"📦 Using cached info for {species}")
        return cached_info
    
    # Fetch from Wikipedia
    print(f"🔍 Fetching info for {species} from Wikipedia...")
    species_info = fetch_species_info_from_wikipedia(species)
    
    if species_info:
        # Save to cache
        save_species_info(species_info)
        print(f"💾 Cached info for {species}")
    
    return species_info


def get_bird_photo(species: str) -> Optional[str]:
    """
    Legacy function - get just the bird photo URL.
    Uses the new species info system.
    """
    info = get_species_info(species)
    return info.get("image_url") if info else None
