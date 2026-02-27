"""
Regenerate missing spectrograms for existing detections.
Now uses full session audio for single spectrograms to show where the bird was detected.
"""
import sqlite3
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import STORAGE_DIR, DATABASE_PATH
from app.services.spectrogram import generate_session_spectrogram, generate_single_spectrogram

def regenerate_spectrograms():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get all detections with timing info
    c.execute("""
        SELECT id, audio_url, single_image_url, species, start_time, end_time, timestamp, lat, lon 
        FROM detections
    """)
    detections = c.fetchall()
    
    print(f"Found {len(detections)} detections to regenerate single spectrograms...")
    
    for detection in detections:
        audio_url = detection['audio_url']
        single_image_url = detection['single_image_url']
        
        # Get paths
        audio_filename = audio_url.replace('/storage/', '')
        single_image_filename = single_image_url.replace('/storage/', '')
        
        session_audio_path = os.path.join(STORAGE_DIR, audio_filename)
        single_image_path = os.path.join(STORAGE_DIR, single_image_filename)
        
        if not os.path.exists(session_audio_path):
            print(f"❌ Session audio not found: {session_audio_path}")
            continue
        
        # Build bird detection info
        bird = {
            'common_name': detection['species'],
            'start_time': detection['start_time'] or 0,
            'end_time': detection['end_time'] or 3,
        }
        
        print(f"🎨 Regenerating: {single_image_filename} ({bird['common_name']} at {bird['start_time']}s-{bird['end_time']}s)")
        
        try:
            # Use SESSION audio for single spectrogram (not trimmed audio)
            generate_single_spectrogram(
                session_audio_path,
                single_image_path,
                bird,
                detection['timestamp'],
                detection['lat'],
                detection['lon']
            )
            print(f"   ✅ Done!")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    conn.close()
    print("\n✨ All single spectrograms regenerated!")


if __name__ == "__main__":
    regenerate_spectrograms()
