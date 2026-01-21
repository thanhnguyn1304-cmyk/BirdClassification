import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from datetime import datetime

# 1. SETUP BIRDNET
print("Loading Model...")
analyzer = Analyzer()

filename = "my_forest_audio/test.wav" # Replace with your actual file name!

# 2. RUN DETECTION
print("Analyzing...")
recording = Recording(
    analyzer,
    filename,
    lat=None, lon=None,
    date=datetime(2024, 7, 12),
    min_conf=0.75
)
recording.analyze()

# 3. VISUALIZE
# Load the audio for drawing
y, sr = librosa.load(filename)
S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
S_dB = librosa.power_to_db(S, ref=np.max)

# Create the plot
plt.figure(figsize=(12, 6))
librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel')
plt.colorbar(format='%+2.0f dB')

# 4. DRAW BOXES AROUND BIRDS
# We loop through what BirdNET found and draw a rectangle for each one
for detection in recording.detections:
    start = detection['start_time']
    end = detection['end_time']
    label = detection['common_name']
    conf = detection['confidence']
    
    # Draw a shaded red box over the time period
    plt.axvspan(start, end, color='red', alpha=0.3)
    
    # Put the text label above the box
    plt.text(start, 8000, f"{label}\n({conf:.2f})", color='white', fontweight='bold')

plt.title(f"BirdNET Detections in {filename}")

plt.show()


