"""Upload router — accepts audio from ESP32 and manual browser uploads."""
from fastapi import APIRouter, UploadFile, File, Form, Request, Query, HTTPException
from typing import Optional
import shutil
import os
import uuid

from starlette.concurrency import run_in_threadpool

from ..config import STORAGE_DIR
from ..services.upload_service import process_upload
from ..logging_config import get_logger

logger = get_logger("upload")
router = APIRouter()


@router.post("/upload")
async def receive_data(
    request: Request,
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    recorded_at: str = Query(...),
):
    """Accept raw audio stream from ESP32 devices."""
    logger.info("Received upload request (raw stream)")

    unique_id = str(uuid.uuid4())
    audio_filename = f"{unique_id}.wav"
    image_filename = f"{unique_id}.png"
    audio_path = os.path.join(STORAGE_DIR, audio_filename)
    image_path = os.path.join(STORAGE_DIR, image_filename)

    # Save Audio from Raw Stream
    with open(audio_path, "wb") as buffer:
        async for chunk in request.stream():
            buffer.write(chunk)

    logger.info("Saved %s, offloading analysis", audio_filename)

    try:
        birds_found = await run_in_threadpool(
            process_upload,
            audio_path, image_path, lat, lon, recorded_at,
            unique_id, audio_filename, image_filename,
        )
    except Exception as e:
        logger.error("Upload processing failed: %s", e)
        raise HTTPException(status_code=500, detail="Audio processing failed")

    return {"status": "success", "birds_found": birds_found}


@router.post("/upload/manual")
async def manual_upload(
    file: UploadFile = File(...),
    lat: Optional[float] = Form(None),
    lon: Optional[float] = Form(None),
    recorded_at: str = Form(...),
):
    """Browser/Swagger friendly upload (Multipart Form)."""
    logger.info("Received manual upload: %s", file.filename)

    unique_id = str(uuid.uuid4())
    audio_filename = f"{unique_id}.wav"
    image_filename = f"{unique_id}.png"
    audio_path = os.path.join(STORAGE_DIR, audio_filename)
    image_path = os.path.join(STORAGE_DIR, image_filename)

    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    logger.info("Saved %s, offloading analysis", audio_filename)

    try:
        birds_found = await run_in_threadpool(
            process_upload,
            audio_path, image_path, lat, lon, recorded_at,
            unique_id, audio_filename, image_filename,
        )
    except Exception as e:
        logger.error("Manual upload processing failed: %s", e)
        raise HTTPException(status_code=500, detail="Audio processing failed")

    return {"status": "success", "birds_found": birds_found}
