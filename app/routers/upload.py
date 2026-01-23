from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from datetime import datetime, timedelta
import shutil
import os
import uuid
import sqlite3

from birdnetlib import Recording

from ..config import STORAGE_DIR, DATABASE_PATH
from ..services.analyzer import analyzer
from ..services.spectrogram import generate_session_spectrogram, generate_single_spectrogram
from ..services.audio import generate_single_audio
from ..services.bird_images import get_bird_photo


router = APIRouter()

@router.post("/upload")
async def receive_data(
    file: UploadFile = File(...), 
    lat: Optional[float] = Form(None),
    lon: Optional[float] = Form(None),
    recorded_at: str = Form(...) 
):
    # --- A. PREPARATION ---
    unique_id = str(uuid.uuid4())
    audio_filename = f"{unique_id}.wav"
    image_filename = f"{unique_id}.png"

    audio_path = os.path.join(STORAGE_DIR, audio_filename)
    image_path = os.path.join(STORAGE_DIR, image_filename)

    # Save Audio
    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

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

    # --- C. DRAW SPECTROGRAM (SECOND - WITH BOXES) ---
    generate_session_spectrogram(audio_path, image_path, detections, recorded_at, lat, lon)

    # --- D. SAVE TO DB ---
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    k = 0
    for bird in detections:
        start_seconds = bird.get('start_time', 0.0)
        species_name = bird.get('common_name') or bird.get('label', 'Unknown Bird')
        confidence_score = bird.get('confidence', 0.0)

        single_image_filename = f"{unique_id}{k}.png"
        single_audio_filename = f"{unique_id}{k}.wav"
        k += 1
        single_image_path = os.path.join(STORAGE_DIR, single_image_filename)
        single_audio_path = os.path.join(STORAGE_DIR, single_audio_filename)


        # Generate single spectrogram
        generate_single_spectrogram(audio_path, single_image_path, bird, recorded_at, lat, lon)

        generate_single_audio(audio_path, single_audio_path, bird["start_time"], bird["end_time"])

        # Fetch bird photo (with caching - only calls API if not already stored)
        bird_photo_url = get_bird_photo(species_name)

        # Exact Time Calculation Logic
        exact_time = start_time_obj + timedelta(seconds=start_seconds)

        c.execute(
            """
            INSERT INTO detections 
            (timestamp, lat, lon, species, confidence, audio_url, single_audio_url, image_url, single_image_url, bird_photo_url) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                exact_time,
                lat,
                lon,
                bird["common_name"],
                bird["confidence"],
                f"/storage/{audio_filename}",
                f"/storage/{single_audio_filename}",
                f"/storage/{image_filename}",
                f"/storage/{single_image_filename}",
                bird_photo_url,
            ),
        )
        print(f"✅ Found {bird['common_name']} at {exact_time}")
        

    conn.commit()
    conn.close()

    return {"status": "success", "birds_found": len(detections)}

