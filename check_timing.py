"""Check BirdNET detection timings for the audio file."""
import os
from datetime import datetime
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

print("Loading BirdNET...")
analyzer = Analyzer()
print("Ready!")

audio_path = 'storage/ec480b34-5a4f-4b04-a51f-3be6afcab4bc.wav'

recording = Recording(analyzer, audio_path, lat=None, lon=None, date=datetime.now(), min_conf=0.5)
recording.analyze()

print(f"\nAll detections ({len(recording.detections)}):")
for i, d in enumerate(recording.detections):
    name = d.get("common_name", "Unknown")
    start = d.get("start_time", 0)
    end = d.get("end_time", 0)
    conf = d.get("confidence", 0)
    print(f"  {i}: {name} - {start}s to {end}s (conf: {conf:.2f})")
