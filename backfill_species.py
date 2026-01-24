"""
Backfill script to populate species table with Wikipedia info.
Run this once to update all existing species.
"""
import sqlite3
import requests
import re
from typing import Optional, Dict, Any

DATABASE_PATH = "birds.db"

HEADERS = {
    "User-Agent": "AvianNet/1.0 (Bird Classification App; https://github.com/aviannet)"
}


def extract_region_from_text(text: str) -> str:
    """Extract region/distribution info from Wikipedia text."""
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
            if len(region) > 150:
                region = region[:147] + "..."
            return region
    
    return "Widespread"


def fetch_species_info(species: str) -> Optional[Dict[str, Any]]:
    """Fetch species info from Wikipedia."""
    try:
        search_term = species.replace("'", "").strip()
        
        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "titles": search_term,
            "prop": "pageimages|extracts",
            "pithumbsize": 500,
            "exintro": True,
            "explaintext": True,
            "exsentences": 5,
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
        
        return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def backfill_species():
    """Populate species table with Wikipedia info."""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Create species table if not exists
    c.execute(
        """CREATE TABLE IF NOT EXISTS species
                 (id INTEGER PRIMARY KEY,
                  name TEXT UNIQUE,
                  scientific_name TEXT,
                  image_url TEXT,
                  description TEXT,
                  region TEXT,
                  habitat TEXT,
                  conservation_status TEXT,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP)"""
    )
    conn.commit()
    
    # Get unique species from detections
    c.execute("SELECT DISTINCT species FROM detections")
    species_list = [row[0] for row in c.fetchall()]
    
    print(f"🐦 Found {len(species_list)} unique species to process...")
    
    for species in species_list:
        # Check if already in species table
        c.execute("SELECT id FROM species WHERE name = ?", (species,))
        if c.fetchone():
            print(f"   ✅ {species} already in database, skipping...")
            continue
        
        print(f"\n🔍 Fetching info for: {species}")
        info = fetch_species_info(species)
        
        if info:
            c.execute(
                """INSERT OR REPLACE INTO species 
                   (name, scientific_name, image_url, description, region, habitat, conservation_status)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    info["name"],
                    info["scientific_name"],
                    info["image_url"],
                    info["description"],
                    info["region"],
                    info["habitat"],
                    info["conservation_status"],
                )
            )
            conn.commit()
            print(f"   💾 Saved: {info['description'][:60]}..." if info['description'] else "   💾 Saved (no description)")
        else:
            print(f"   ⚠️ No info found")
    
    conn.close()
    print("\n✅ Species backfill complete!")


if __name__ == "__main__":
    backfill_species()
