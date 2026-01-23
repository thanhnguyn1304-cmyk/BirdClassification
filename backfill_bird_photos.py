"""
Backfill script to add Wikipedia bird photos to existing detections.
Run this once to update all existing records.
"""
import sqlite3
import requests
from typing import Optional

DATABASE_PATH = "birds.db"

# Wikipedia requires a proper User-Agent
HEADERS = {
    "User-Agent": "AvianNet/1.0 (Bird Classification App; contact@example.com)"
}


def fetch_bird_photo_from_wikipedia(species: str) -> Optional[str]:
    """Fetch a bird photo URL from Wikipedia API."""
    try:
        search_term = species.replace("'", "").strip()
        
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "format": "json",
            "titles": search_term,
            "prop": "pageimages",
            "pithumbsize": 500,
            "redirects": 1
        }
        
        response = requests.get(search_url, params=search_params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pages = data.get("query", {}).get("pages", {})
        
        for page_id, page_data in pages.items():
            if page_id != "-1":
                thumbnail = page_data.get("thumbnail", {})
                image_url = thumbnail.get("source")
                if image_url:
                    return image_url
        
        # Try with " (bird)" suffix
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
                    return image_url
        
        return None
        
    except Exception as e:
        print(f"❌ Error fetching image for {species}: {e}")
        return None


def backfill_bird_photos():
    """Update all existing detections with Wikipedia bird photos."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Get all unique species
    c.execute("SELECT DISTINCT species FROM detections")
    species_list = [row[0] for row in c.fetchall()]
    
    print(f"🐦 Found {len(species_list)} unique species to process...")
    
    for species in species_list:
        print(f"\n🔍 Processing: {species}")
        
        # Check if any detection for this species already has a photo
        c.execute(
            "SELECT bird_photo_url FROM detections WHERE species = ? AND bird_photo_url IS NOT NULL LIMIT 1",
            (species,)
        )
        existing = c.fetchone()
        
        if existing and existing[0]:
            print(f"   ✅ Already has photo, skipping...")
            continue
        
        # Fetch from Wikipedia
        photo_url = fetch_bird_photo_from_wikipedia(species)
        
        if photo_url:
            # Update all detections for this species
            c.execute(
                "UPDATE detections SET bird_photo_url = ? WHERE species = ?",
                (photo_url, species)
            )
            conn.commit()
            print(f"   🖼️ Updated with: {photo_url[:60]}...")
        else:
            print(f"   ⚠️ No photo found on Wikipedia")
    
    conn.close()
    print("\n✅ Backfill complete!")


if __name__ == "__main__":
    backfill_bird_photos()
