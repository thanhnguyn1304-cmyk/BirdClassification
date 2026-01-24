from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil
import os
import uuid
import sqlite3
import time

from birdnetlib import Recording

from ..config import STORAGE_DIR, DATABASE_PATH
from ..services.analyzer import analyzer
from ..services.spectrogram import generate_session_spectrogram, generate_single_spectrogram
from ..services.audio import generate_single_audio
from ..services.bird_images import get_bird_photo

router = APIRouter()

# Thread pool for parallel processing (limit to avoid overloading CPU)
EXECUTOR = ThreadPoolExecutor(max_workers=4)


def process_single_detection(
    audio_path: str,
    unique_id: str,
    index: int,
    bird: Dict[str, Any],
    recorded_at: str,
    lat: Optional[float],
    lon: Optional[float]
) -> Dict[str, Any]:
    """Process a single detection: generate spectrogram and audio segment."""
    single_image_filename = f"{unique_id}{index}.png"
    single_audio_filename = f"{unique_id}{index}.wav"
    single_image_path = os.path.join(STORAGE_DIR, single_image_filename)
    single_audio_path = os.path.join(STORAGE_DIR, single_audio_filename)

    # Generate spectrogram and audio (these are the slow parts)
    generate_single_spectrogram(audio_path, single_image_path, bird, recorded_at, lat, lon)
    generate_single_audio(audio_path, single_audio_path, bird["start_time"], bird["end_time"])

    return {
        "index": index,
        "single_image_filename": single_image_filename,
        "single_audio_filename": single_audio_filename,
    }


def fetch_bird_photos_background(unique_species: List[str]):
    """Background task to fetch bird photos for unique species."""
    for species in unique_species:
        try:
            get_bird_photo(species)
            print(f"📸 Fetched photo for {species}")
        except Exception as e:
            print(f"❌ Failed to fetch photo for {species}: {e}")


@router.post("/upload")
async def receive_data(
    file: UploadFile = File(...), 
    lat: Optional[float] = Form(None),
    lon: Optional[float] = Form(None),
    recorded_at: str = Form(...),
    background_tasks: BackgroundTasks = None
):
    start_time = time.time()
    
    # --- A. PREPARATION ---
    unique_id = str(uuid.uuid4())
    audio_filename = f"{unique_id}.wav"
    image_filename = f"{unique_id}.png"

    audio_path = os.path.join(STORAGE_DIR, audio_filename)
    image_path = os.path.join(STORAGE_DIR, image_filename)

    # Save Audio
    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    prep_time = time.time()
    print(f"⏱️ Prep: {prep_time - start_time:.2f}s")

    # --- B. RUN AI (FIRST) ---
    print(f"🔍 Analyzing {unique_id}...")
    detections = []

    # Parse GPS Time
    try:
        start_time_obj = datetime.strptime(recorded_at, "%Y-%m-%d %H:%M:%S")
    except:
        start_time_obj = datetime.now()

    try:
        recording = Recording(
            analyzer, audio_path, lat=lat, lon=lon, date=start_time_obj, min_conf=0.7
        )

        recording.analyze()
        detections = recording.detections
    except Exception as e:
        print(f"❌ AI Error: {e}")

    ai_time = time.time()
    print(f"⏱️ AI Analysis: {ai_time - prep_time:.2f}s - Found {len(detections)} birds")

    # --- C. PARALLEL PROCESSING ---
    # Generate session spectrogram (runs in parallel with individual spectrograms)
    session_future = EXECUTOR.submit(
        generate_session_spectrogram, audio_path, image_path, detections, recorded_at, lat, lon
    )
    
    # Submit all individual spectrograms/audio in parallel
    futures = []
    for i, bird in enumerate(detections):
        future = EXECUTOR.submit(
            process_single_detection,
            audio_path, unique_id, i, bird, recorded_at, lat, lon
        )
        futures.append(future)

    # Collect results as they complete
    processed_detections = {}
    for future in as_completed(futures):
        try:
            result = future.result()
            processed_detections[result["index"]] = result
        except Exception as e:
            print(f"❌ Processing error: {e}")

    # Wait for session spectrogram to complete
    try:
        session_future.result()
    except Exception as e:
        print(f"❌ Session spectrogram error: {e}")

    process_time = time.time()
    print(f"⏱️ Parallel Processing: {process_time - ai_time:.2f}s")

    # --- D. GET BIRD PHOTOS (with deduplication) ---
    unique_species = list(set(bird.get('common_name', 'Unknown') for bird in detections))
    species_photos = {}
    
    for species in unique_species:
        try:
            photo_url = get_bird_photo(species)
            species_photos[species] = photo_url
        except Exception as e:
            print(f"❌ Photo error for {species}: {e}")
            species_photos[species] = None

    photo_time = time.time()
    print(f"⏱️ Photo Fetching ({len(unique_species)} species): {photo_time - process_time:.2f}s")

    # --- E. BATCH INSERT TO DB ---
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    batch_data = []
    for i, bird in enumerate(detections):
        species_name = bird.get('common_name') or bird.get('label', 'Unknown Bird')
        start_seconds = bird.get('start_time', 0.0)
        exact_time = start_time_obj + timedelta(seconds=start_seconds)
        
        # Get processed filenames
        processed = processed_detections.get(i, {})
        single_image_filename = processed.get("single_image_filename", f"{unique_id}{i}.png")
        single_audio_filename = processed.get("single_audio_filename", f"{unique_id}{i}.wav")
        
        # Get photo from deduplicated cache
        bird_photo_url = species_photos.get(species_name)
        
        batch_data.append((
            exact_time,
            lat,
            lon,
            species_name,
            bird["confidence"],
            f"/storage/{audio_filename}",
            f"/storage/{single_audio_filename}",
            f"/storage/{image_filename}",
            f"/storage/{single_image_filename}",
            bird_photo_url,
        ))
        print(f"✅ Found {species_name} at {exact_time}")

    # Batch insert all at once
    c.executemany(
        """
        INSERT INTO detections 
        (timestamp, lat, lon, species, confidence, audio_url, single_audio_url, image_url, single_image_url, bird_photo_url) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        batch_data
    )
    
    conn.commit()
    conn.close()

    db_time = time.time()
    print(f"⏱️ DB Insert: {db_time - photo_time:.2f}s")
    
    total_time = time.time() - start_time
    print(f"✨ TOTAL TIME: {total_time:.2f}s for {len(detections)} detections")

    return {
        "status": "success", 
        "birds_found": len(detections),
        "processing_time_seconds": round(total_time, 2)
    }
