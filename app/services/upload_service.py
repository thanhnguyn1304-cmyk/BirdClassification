"""
Upload processing service.

Contains the heavy business logic for processing audio uploads:
AI analysis, spectrogram generation, and database insertion.
Separated from the router to keep endpoints thin.
"""
import os
import sqlite3
from datetime import datetime, timedelta

from birdnetlib import Recording

from ..config import STORAGE_DIR, DATABASE_PATH
from ..services.analyzer import analyzer
from ..services.spectrogram import generate_session_spectrogram, generate_single_spectrogram
from ..services.audio import generate_single_audio
from ..logging_config import get_logger

logger = get_logger("upload_service")


def process_upload(
    audio_path: str,
    image_path: str,
    lat: float | None,
    lon: float | None,
    recorded_at: str,
    unique_id: str,
    audio_filename: str,
    image_filename: str,
) -> int:
    """
    Process an uploaded audio file: run AI, generate spectrograms, save to DB.
    
    Returns the number of bird species detected.
    Raises exceptions on failure (handled by the router).
    """
    logger.info("Processing upload %s", unique_id)
    detections = []

    # Parse GPS Time
    try:
        start_time_obj = datetime.strptime(recorded_at, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        logger.warning("Could not parse timestamp '%s', using current time", recorded_at)
        start_time_obj = datetime.now()

    # 1. Run AI Analysis
    try:
        recording = Recording(
            analyzer, audio_path, lat=lat, lon=lon, date=start_time_obj, min_conf=0.7
        )
        recording.analyze()
        detections = recording.detections
        logger.info("AI detected %d birds in %s", len(detections), unique_id)
    except Exception as e:
        logger.error("AI analysis failed for %s: %s", unique_id, e)
        raise

    # 2. Generate Session Spectrogram
    generate_session_spectrogram(audio_path, image_path, detections, recorded_at, lat, lon)

    # 3. Save Each Detection to DB
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    try:
        for k, bird in enumerate(detections):
            start_seconds = bird.get('start_time', 0.0)

            single_image_filename = f"{unique_id}{k}.png"
            single_audio_filename = f"{unique_id}{k}.wav"
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
            logger.info("Saved detection: %s at %s", bird['common_name'], exact_time)

        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error("Database save failed for %s: %s", unique_id, e)
        raise
    finally:
        conn.close()

    return len(detections)
