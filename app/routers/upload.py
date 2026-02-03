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



from starlette.concurrency import run_in_threadpool

router = APIRouter()

# --- HELPER: BACKGROUND PROCESSING LOGIC ---
def process_upload_logic(audio_path, image_path, lat, lon, recorded_at, unique_id, audio_filename, image_filename):
    print(f"🧵 [Thread] Processing {unique_id}...")
    detections = []

    # Parse GPS Time
    try:
        start_time_obj = datetime.strptime(recorded_at, "%Y-%m-%d %H:%M:%S")
    except:
        start_time_obj = datetime.now()

    # 1. Run AI
    try:
        recording = Recording(
            analyzer, audio_path, lat=lat, lon=lon, date=start_time_obj, min_conf=0.7
        )
        recording.analyze()
        detections = recording.detections
    except Exception as e:
        print(f"❌ AI Error: {e}")

    # 2. Draw Spectrogram
    generate_session_spectrogram(audio_path, image_path, detections, recorded_at, lat, lon)

    # 3. Save to DB
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    k = 0
    for bird in detections:
        start_seconds = bird.get('start_time', 0.0)
        
        single_image_filename = f"{unique_id}{k}.png"
        single_audio_filename = f"{unique_id}{k}.wav"
        k += 1
        single_image_path = os.path.join(STORAGE_DIR, single_image_filename)
        single_audio_path = os.path.join(STORAGE_DIR, single_audio_filename)

        # Generate single assets
        generate_single_spectrogram(audio_path, single_image_path, bird, recorded_at, lat, lon)
        generate_single_audio(audio_path, single_audio_path, bird["start_time"], bird["end_time"])

        # Exact Time Calculation
        exact_time = start_time_obj + timedelta(seconds=start_seconds)

        c.execute(
            """
            INSERT INTO detections 
            (timestamp, lat, lon, species, confidence, audio_url, single_audio_url, image_url, single_image_url) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                exact_time, lat, lon, bird["common_name"], bird["confidence"],
                f"/storage/{audio_filename}", f"/storage/{single_audio_filename}",
                f"/storage/{image_filename}", f"/storage/{single_image_filename}",
            ),
        )
        print(f"✅ Found {bird['common_name']} at {exact_time}")

    conn.commit()
    conn.close()
    return len(detections)


from fastapi import Request, Query

@router.post("/upload")
async def receive_data(
    request: Request,
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    recorded_at: str = Query(...) 
):
    print(f"\n📨 RECEIVED UPLOAD REQUEST (Raw Stream)")
    
    # --- A. PREPARATION ---
    unique_id = str(uuid.uuid4())
    audio_filename = f"{unique_id}.wav"
    image_filename = f"{unique_id}.png"

    audio_path = os.path.join(STORAGE_DIR, audio_filename)
    image_path = os.path.join(STORAGE_DIR, image_filename)

    # Save Audio from Raw Stream (HTTPClient sends raw bytes)
    # We iterate over the stream to save RAM on server too
    with open(audio_path, "wb") as buffer:
        async for chunk in request.stream():
            buffer.write(chunk)

    print(f"   Saved {audio_filename}. Offloading analysis...")

    # --- B. OFFLOAD HEAVY LIFTING TO THREAD ---
    birds_found = await run_in_threadpool(
        process_upload_logic, 
        audio_path, image_path, lat, lon, recorded_at, unique_id, audio_filename, image_filename
    )

    return {"status": "success", "birds_found": birds_found}


@router.post("/upload/manual")
async def manual_upload(
    file: UploadFile = File(...),
    lat: Optional[float] = Form(None),
    lon: Optional[float] = Form(None),
    recorded_at: str = Form(...) 
):
    """
    Browser/Swagger friendly upload (Multipart Form).
    Does NOT affect ESP32 flow.
    """
    print(f"\\n📨 RECEIVED MANUAL UPLOAD REQUEST")
    
    unique_id = str(uuid.uuid4())
    audio_filename = f"{unique_id}.wav"
    image_filename = f"{unique_id}.png"

    audio_path = os.path.join(STORAGE_DIR, audio_filename)
    image_path = os.path.join(STORAGE_DIR, image_filename)

    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print(f"   Saved {audio_filename}. Offloading analysis...")

    birds_found = await run_in_threadpool(
        process_upload_logic, 
        audio_path, image_path, lat, lon, recorded_at, unique_id, audio_filename, image_filename
    )

    return {"status": "success", "birds_found": birds_found}

