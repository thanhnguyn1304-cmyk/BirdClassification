"""
Bird Image Service - Fetches bird photos from Wikipedia API with caching.
"""
import requests
import sqlite3
from typing import Optional
from ..config import DATABASE_PATH

# Wikipedia requires a proper User-Agent header
HEADERS = {
    "User-Agent": "AvianNet/1.0 (Bird Classification App; https://github.com/aviannet)"
}


def get_cached_bird_photo(species: str) -> Optional[str]:
    """
    Check if we already have a photo URL for this species in the database.
    Returns the URL if found, None otherwise.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT bird_photo_url FROM detections WHERE species = ? AND bird_photo_url IS NOT NULL LIMIT 1",
        (species,)
    )
    result = c.fetchone()
    conn.close()
    
    if result and result[0]:
        return result[0]
    return None


def fetch_bird_photo_from_wikipedia(species: str) -> Optional[str]:
    """
    Fetch a bird photo URL from Wikipedia API.
    Uses the Wikipedia REST API to get the main image for a species page.
    """
    try:
        # Clean up species name for Wikipedia search
        search_term = species.replace("'", "").strip()
        
        # Step 1: Search Wikipedia for the species
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "format": "json",
            "titles": search_term,
            "prop": "pageimages",
            "pithumbsize": 500,  # Get a 500px thumbnail
            "redirects": 1
        }
        
        response = requests.get(search_url, params=search_params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pages = data.get("query", {}).get("pages", {})
        
        for page_id, page_data in pages.items():
            if page_id != "-1":  # -1 means page not found
                thumbnail = page_data.get("thumbnail", {})
                image_url = thumbnail.get("source")
                if image_url:
                    print(f"🖼️ Found image for {species}: {image_url[:50]}...")
                    return image_url
        
        # If exact match failed, try with " (bird)" suffix
        search_params["titles"] = f"{search_term} (bird)"
        response = requests.get(search_url, params=search_params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if page_id != "-1":
                thumbnail = page_data.get("thumbnail", {})
                image_url = thumbnail.get("source")
                if image_url:
                    print(f"🖼️ Found image for {species} (bird): {image_url[:50]}...")
                    return image_url
        
        print(f"⚠️ No image found for {species}")
        return None
        
    except Exception as e:
        print(f"❌ Error fetching image for {species}: {e}")
        return None


def get_bird_photo(species: str) -> Optional[str]:
    """
    Main function to get a bird photo URL.
    First checks cache, then fetches from Wikipedia if not found.
    """
    # Check cache first
    cached_url = get_cached_bird_photo(species)
    if cached_url:
        print(f"📦 Using cached image for {species}")
        return cached_url
    
    # Fetch from Wikipedia
    print(f"🔍 Fetching image for {species} from Wikipedia...")
    return fetch_bird_photo_from_wikipedia(species)
