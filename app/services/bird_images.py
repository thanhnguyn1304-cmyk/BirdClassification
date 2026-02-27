"""
Bird Image Service - Fetches bird info from Wikipedia API with database caching.
Stores species data permanently so future lookups are instant.
"""
import requests
import sqlite3
import re
from typing import Optional, Dict, Any

from ..config import DATABASE_PATH
from ..logging_config import get_logger

logger = get_logger("bird_images")

# Wikipedia requires a proper User-Agent header
HEADERS = {
    "User-Agent": "AvianNet/1.0 (Bird Classification App; https://github.com/aviannet)"
}


def get_cached_species_info(species: str) -> Optional[Dict[str, Any]]:
    """Check if we have cached info for this species in the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM species WHERE name = ?", (species,))
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
        logger.error("Failed to save species info for '%s': %s", species_info.get("name"), e)
    finally:
        conn.close()


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


def fetch_species_info_from_wikipedia(species: str) -> Optional[Dict[str, Any]]:
    """Fetch full species info from Wikipedia API."""
    try:
        search_term = species.replace("'", "").strip()

        search_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "titles": search_term,
            "prop": "pageimages|extracts|info",
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

        logger.warning("No Wikipedia info found for '%s'", species)
        return None

    except Exception as e:
        logger.error("Failed to fetch Wikipedia info for '%s': %s", species, e)
        return None


def get_species_info(species: str) -> Optional[Dict[str, Any]]:
    """Main function: check cache first, then fetch from Wikipedia."""
    cached_info = get_cached_species_info(species)
    if cached_info:
        logger.debug("Cache hit for '%s'", species)
        return cached_info

    logger.info("Fetching info for '%s' from Wikipedia", species)
    species_info = fetch_species_info_from_wikipedia(species)

    if species_info:
        save_species_info(species_info)
        logger.info("Cached info for '%s'", species)

    return species_info


def get_bird_photo(species: str) -> Optional[str]:
    """Legacy function - get just the bird photo URL."""
    info = get_species_info(species)
    return info.get("image_url") if info else None
