"""
Re-analyze existing audio files with BirdNET to get correct detection timings,
then update the database and regenerate spectrograms with proper box positions.
"""
import sqlite3
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import STORAGE_DIR, DATABASE_PATH
from app.services.spectrogram import generate_session_spectrogram
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer

def reanalyze_and_fix():
    print("🦅 Loading BirdNET Model...")
    analyzer = Analyzer()
    print("✅ BirdNET Ready.")
    
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get unique audio files (sessions) - use image_url as the unique key
    c.execute("SELECT DISTINCT image_url, audio_url, timestamp, lat, lon FROM detections")
    sessions = c.fetchall()
    
    # Deduplicate by audio_url
    unique_sessions = {}
    for session in sessions:
        if session['audio_url'] not in unique_sessions:
            unique_sessions[session['audio_url']] = session
    
    print(f"\nFound {len(unique_sessions)} unique sessions to re-analyze...")
    
    for audio_url, session in unique_sessions.items():
        audio_filename = audio_url.replace('/storage/', '')
        audio_path = os.path.join(STORAGE_DIR, audio_filename)
        
        if not os.path.exists(audio_path):
            print(f"❌ Audio not found: {audio_path}")
            continue
        
        print(f"\n🔍 Re-analyzing: {audio_filename}")
        
        # Parse timestamp
        try:
            recorded_at = datetime.strptime(session['timestamp'], "%Y-%m-%d %H:%M:%S")
        except:
            recorded_at = datetime.now()
        
        # Run BirdNET analysis
        try:
            recording = Recording(
                analyzer, 
                audio_path, 
                lat=session['lat'], 
                lon=session['lon'], 
                date=recorded_at, 
                min_conf=0.5
            )
            recording.analyze()
            detections = recording.detections
            
            print(f"   Found {len(detections)} detections with timing:")
            
            # Get all detection IDs for this audio_url
            c.execute("""
                SELECT id FROM detections WHERE audio_url = ? ORDER BY id
            """, (audio_url,))
            db_ids = [row['id'] for row in c.fetchall()]
            
            # Update each detection in the database with timing
            for i, bird in enumerate(detections):
                if i >= len(db_ids):
                    break
                    
                species_name = bird.get('common_name', 'Unknown')
                start_time = bird.get('start_time', 0)
                end_time = bird.get('end_time', start_time + 3)
                confidence = bird.get('confidence', 0)
                
                print(f"   - {species_name}: {start_time}s - {end_time}s (ID: {db_ids[i]})")
                
                # Update the database record by ID
                c.execute("""
                    UPDATE detections 
                    SET start_time = ?, end_time = ?
                    WHERE id = ?
                """, (start_time, end_time, db_ids[i]))
            
            conn.commit()
            
            # Regenerate the session spectrogram with correct timings
            image_filename = audio_filename.replace('.wav', '.png')
            image_path = os.path.join(STORAGE_DIR, image_filename)
            
            print(f"   🎨 Regenerating spectrogram...")
            generate_session_spectrogram(
                audio_path,
                image_path,
                detections,
                session['timestamp'],
                session['lat'],
                session['lon']
            )
            print(f"   ✅ Done!")
            
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
    
    conn.close()
    print("\n✨ All sessions re-analyzed and spectrograms regenerated!")


if __name__ == "__main__":
    reanalyze_and_fix()
