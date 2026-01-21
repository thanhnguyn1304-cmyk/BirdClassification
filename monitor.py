from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
import shutil
import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import uuid
import matplotlib.pyplot as plt
import matplotlib.patches as patches # <--- NEW: For drawing the red boxes
import librosa
import librosa.display
import numpy as np
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from typing import Optional

app = FastAPI()

# 1. Setup Storage
os.makedirs("storage", exist_ok=True)
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# 2. Load AI Model
print("🦅 Loading BirdNET Model...")
analyzer = Analyzer()
print("✅ BirdNET Ready.")  

def init_db():
    conn = sqlite3.connect("birds.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS detections 
                 (id INTEGER PRIMARY KEY, 
                  timestamp TEXT, 
                  lat REAL, 
                  lon REAL, 
                  species TEXT, 
                  confidence REAL,
                  audio_url TEXT,  
                  image_url TEXT,
                  single_image_url TEXT)"""
    )
    conn.commit()
    conn.close()

init_db()

@app.post("/upload")
async def receive_data(
    file: UploadFile = File(...), 
    lat: Optional[float] = Form(None), # If ESP32 doesn't send it, it becomes None
    lon: Optional[float] = Form(None),
    recorded_at: str = Form(...) 
):
    # --- A. PREPARATION ---
    unique_id = str(uuid.uuid4())
    audio_filename = f"{unique_id}.wav"
    image_filename = f"{unique_id}.png"

    audio_path = os.path.join("storage", audio_filename)
    image_path = os.path.join("storage", image_filename)

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

    try:
        y, sr = librosa.load(audio_path, sr=None)
        # Calculate duration of the whole file
        file_duration = len(y) / sr

        # Formula: 10 inches base width + 1 inch for every 10 seconds of audio
        # We assume a max width of 50 to prevent crashing on huge files
        dynamic_width = min(50, 10 + (file_duration / 10))

        fig, ax = plt.subplots(figsize=(dynamic_width, 6))

        # Draw the Heatmap
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
        S_dB = librosa.power_to_db(S, ref=np.max)
        img = librosa.display.specshow(S_dB, x_axis='time', y_axis='mel', sr=sr, fmax=8000, ax=ax)

        # Add Colorbar
        fig.colorbar(img, ax=ax, format="%+2.0f dB", shrink=0.7, pad=0.03)

        ax.spines['left'].set_position(('outward', 10))
        ax.spines['bottom'].set_position(('outward', 10))
        
        # Clean up the other borders
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # 🆕 DRAW BOXES AROUND BIRDS
        for i, bird in enumerate(detections):
            # Get start and end time of the chirp
            t_start = bird['start_time']
            t_end = bird['end_time']
            duration = t_end - t_start

            # Create a Red Rectangle (overlay)
            # (x, y, width, height) -> x=time, y=0 (bottom), h=8000 (top)
            rect = patches.Rectangle(
                (t_start, 0), duration, 8000, 
                linewidth=2, edgecolor='#FF0000', facecolor='#FF0000', alpha=0.15, zorder = 10
            )
            center_x = t_start + (duration / 2)
            # 2. Clamp it so it never goes below 2.0 seconds (keeps text on screen)
            safe_text_x = max(center_x, 0.5)

            ax.add_patch(rect)
            lane = i % 4
            text_height = 7500 - (lane * 1500)
            # Add Label Text above the box (e.g., "Sparrow")
            ax.text(
                safe_text_x,
                text_height,
                bird["common_name"],
                color="white",
                fontweight="bold",
                fontsize=8,
                backgroundcolor="red",
                zorder=11,
                ha="center",
            )

        # Add Titles
        ax.set_title(f"Recorded: {recorded_at} | Lat: {lat}, Lon: {lon}")
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Frequency (Hz)")

        # Save
        plt.tight_layout()
        plt.savefig(image_path, bbox_inches='tight', pad_inches=0.1, dpi = 300)
        plt.close()
        print(f"🎨 Spectrogram with highlights saved.")

    except Exception as e:
        print(f"❌ Spectrogram Error: {e}")

    # --- D. SAVE TO DB ---
    conn = sqlite3.connect("birds.db")
    c = conn.cursor()
    k = 0
    for bird in detections:
        start_seconds = bird.get('start_time', 0.0)
        species_name = bird.get('common_name') or bird.get('label', 'Unknown Bird')
        confidence_score = bird.get('confidence', 0.0)

        single_image_filename = f"{unique_id}{k}.png"
        k += 1
        single_image_path = os.path.join("storage", single_image_filename)

        y, sr = librosa.load(audio_path, sr=None)
        # Calculate duration of the whole file
        file_duration = len(y) / sr

        # Formula: 10 inches base width + 1 inch for every 10 seconds of audio
        # We assume a max width of 50 to prevent crashing on huge files
        dynamic_width = min(50, 10 + (file_duration / 10))

        fig, ax = plt.subplots(figsize=(10, 6))

        # Draw the Heatmap
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
        S_dB = librosa.power_to_db(S, ref=np.max)
        img = librosa.display.specshow(
            S_dB, x_axis="time", y_axis="mel", sr=sr, fmax=8000, ax=ax
        )

        # Add Colorbar
        fig.colorbar(img, ax=ax, format='%+2.0f dB', shrink=0.6, pad=0.03, anchor=(0.0, 0.2))

        ax.spines['left'].set_position(('outward', 10))
        ax.spines['bottom'].set_position(('outward', 10))
        
        # Clean up the other borders
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Get start and end time of the chirp
        t_start = bird["start_time"]
        t_end = bird["end_time"]
        duration = t_end - t_start

        # Create a Red Rectangle (overlay)
        # (x, y, width, height) -> x=time, y=0 (bottom), h=8000 (top)
        rect = patches.Rectangle(
                (t_start, 0), duration, 8000, 
                linewidth=2, edgecolor='#FF0000', facecolor='#FF0000', alpha=0.15, zorder = 10
            )
        ax.add_patch(rect)

        center_x = t_start + (duration / 2)
        safe_text_x = max(center_x, 2.0)
        # Add Label Text above the box (e.g., "Sparrow")
        ax.text(
            safe_text_x,
            7500,
            bird["common_name"],
            color="white",
            fontweight="bold",
            fontsize=8,
            backgroundcolor="red",
            zorder=11,
            ha="center",
        )

        # Add Titles
        ax.set_title(f"Recorded: {recorded_at} | Lat: {lat}, Lon: {lon}")
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Frequency (Hz)")

        # Save
        plt.tight_layout()
        plt.savefig(single_image_path, bbox_inches="tight", pad_inches=0.1, dpi=300)
        plt.close()
        print(f"🎨 Single spectrogram with highlights saved.")

        # 2. Exact Time Calculation Logic
        # Start Time (14:00:00) + Offset (2.5s) = 14:00:02.5
        exact_time = start_time_obj + timedelta(seconds=start_seconds)

        c.execute(
            """
            INSERT INTO detections 
            (timestamp, lat, lon, species, confidence, audio_url, image_url, single_image_url) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                exact_time,
                lat,
                lon,
                bird["common_name"],
                bird["confidence"],
                f"/storage/{audio_filename}",
                f"/storage/{image_filename}",
                f"/storage/{single_image_filename}",
            ),
        )
        print(f"✅ Found {bird['common_name']} at {exact_time}")

    conn.commit()
    conn.close()

    return {"status": "success", "birds_found": len(detections)}


@app.get("/download-excel")
def download_excel():
    conn = sqlite3.connect("birds.db")
    df = pd.read_sql_query("SELECT * FROM detections", conn)
    conn.close()
    
    excel_file = "bird_data.xlsx"
    df.to_excel(excel_file, index=False)
    
    from fastapi.responses import FileResponse
    return FileResponse(excel_file, filename="bird_report.xlsx")

# uvicorn monitor:app --host 0.0.0.0 --port 8000
