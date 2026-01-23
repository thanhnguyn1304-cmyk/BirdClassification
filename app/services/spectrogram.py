import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import librosa
import librosa.display
import numpy as np

def generate_session_spectrogram(audio_path: str, image_path: str, detections: list, recorded_at: str, lat, lon):
    """Generate the main session spectrogram with all detection boxes."""
    try:
        y, sr = librosa.load(audio_path, sr=None)
        file_duration = len(y) / sr
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
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Draw boxes around birds
        for i, bird in enumerate(detections):
            t_start = bird['start_time']
            t_end = bird['end_time']
            duration = t_end - t_start

            rect = patches.Rectangle(
                (t_start, 0), duration, 8000, 
                linewidth=2, edgecolor='#FF0000', facecolor='#FF0000', alpha=0.15, zorder=10
            )
            center_x = t_start + (duration / 2)
            safe_text_x = max(center_x, 0.5)

            ax.add_patch(rect)
            lane = i % 4
            text_height = 7500 - (lane * 1500)
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
        plt.savefig(image_path, bbox_inches='tight', pad_inches=0.1, dpi=300)
        plt.close()
        print(f"🎨 Spectrogram with highlights saved.")

    except Exception as e:
        print(f"❌ Spectrogram Error: {e}")


def generate_single_spectrogram(audio_path: str, single_image_path: str, bird: dict, recorded_at: str, lat, lon):
    """Generate a spectrogram for a single bird detection."""
    try:
        y, sr = librosa.load(audio_path, sr=None)
        file_duration = len(y) / sr
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
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Get start and end time of the chirp
        t_start = bird["start_time"]
        t_end = bird["end_time"]
        duration = t_end - t_start

        rect = patches.Rectangle(
            (t_start, 0), duration, 8000, 
            linewidth=2, edgecolor='#FF0000', facecolor='#FF0000', alpha=0.15, zorder=10
        )
        ax.add_patch(rect)

        center_x = t_start + (duration / 2)
        safe_text_x = max(center_x, 2.0)
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

    except Exception as e:
        print(f"❌ Single Spectrogram Error: {e}")
