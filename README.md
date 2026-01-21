# 🦅 BioAcoustic IoT Server

A centralized backend system that processes environmental audio from IoT devices (ESP32), detects bird species using the **BirdNET AI**, and visualizes the data with high-resolution spectrograms.

![Project Status](https://img.shields.io/badge/Status-Active-green)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![AI](https://img.shields.io/badge/AI-BirdNET-orange)

## 🌟 Features

* **🎙️ Automated Ingestion:** Accepts raw audio uploads (Multipart/Form-Data) from ESP32 or other edge devices.
* **🧠 AI Analysis:** Integrated **BirdNET Analyzer** to detect and classify bird species with confidence scores.
* **📊 Dynamic Visualization:**
    * Generates **High-Res Spectrograms** (300 DPI) using `librosa` and `matplotlib`.
    * Draws **Visual Bounding Boxes** around specific bird calls.
    * Smart label placement ("Staggered Lanes") to prevent overlapping text on crowded recordings.
* **💾 Database & Reporting:**
    * Stores all detections (Time, GPS, Species, Confidence) in **SQLite**.
    * **Excel Export:** One-click download of all data via `/download-excel`.

## 🛠️ Tech Stack

* **Framework:** FastAPI (Python)
* **AI Model:** BirdNET-Analyzer (`birdnetlib`)
* **Audio Processing:** Librosa, NumPy, Wave
* **Visualization:** Matplotlib
* **Database:** SQLite3

---

## 🚀 Installation

### 1. Prerequisites
You need **Python 3.9+** and **FFmpeg** installed on your system.

### 2. Install Dependencies
Create a `requirements.txt` file (or run manually):
```bash
pip install fastapi uvicorn python-multipart birdnetlib librosa matplotlib numpy pandas openpyxl wave
Here is the `README.md` content in a single code block for easy copying.

```markdown
# 🦅 BioAcoustic IoT Server

A centralized backend system that processes environmental audio from IoT devices (ESP32), detects bird species using the **BirdNET AI**, and visualizes the data with high-resolution spectrograms.

![Project Status](https://img.shields.io/badge/Status-Active-green)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![AI](https://img.shields.io/badge/AI-BirdNET-orange)

## 🌟 Features

* **🎙️ Automated Ingestion:** Accepts raw audio uploads (Multipart/Form-Data) from ESP32 or other edge devices.
* **🧠 AI Analysis:** Integrated **BirdNET Analyzer** to detect and classify bird species with confidence scores.
* **📊 Dynamic Visualization:**
    * Generates **High-Res Spectrograms** (300 DPI) using `librosa` and `matplotlib`.
    * Draws **Visual Bounding Boxes** around specific bird calls.
    * Smart label placement ("Staggered Lanes") to prevent overlapping text on crowded recordings.
* **💾 Database & Reporting:**
    * Stores all detections (Time, GPS, Species, Confidence) in **SQLite**.
    * **Excel Export:** One-click download of all data via `/download-excel`.

## 🛠️ Tech Stack

* **Framework:** FastAPI (Python)
* **AI Model:** BirdNET-Analyzer (`birdnetlib`)
* **Audio Processing:** Librosa, NumPy, Wave
* **Visualization:** Matplotlib
* **Database:** SQLite3

---

## 🚀 Installation

### 1. Prerequisites
You need **Python 3.9+** and **FFmpeg** installed on your system.

### 2. Install Dependencies
Create a `requirements.txt` file (or run manually):
```bash
pip install fastapi uvicorn python-multipart birdnetlib librosa matplotlib numpy pandas openpyxl

```

### 3. Setup Folders

The server automatically creates the necessary database (`birds.db`) and storage folder (`/storage`) on the first run.

---

## 🏃‍♂️ Usage

### Start the Server

Run the following command in your terminal:

```powershell
uvicorn monitor:app --host 0.0.0.0 --port 8000

```

* **Host:** `0.0.0.0` allows devices on the same Wi-Fi network (like your ESP32) to connect.
* **Port:** `8000` is the default port.

### Access the API

Once running, open your browser:

* **Docs:** `http://localhost:8000/docs` (Interactive API tester)
* **Report:** `http://localhost:8000/download-excel` (Downloads the .xlsx report)

---

## 🔌 API Endpoints

### 1. Upload Audio (`POST /upload`)

The endpoint expected by the ESP32 hardware.

**Form Data Parameters:**
| Key | Type | Description |
| :--- | :--- | :--- |
| `file` | File | The raw audio file (PCM/WAV). |
| `recorded_at` | String | Timestamp: `YYYY-MM-DD HH:MM:SS` |
| `lat` | Float | (Optional) GPS Latitude. |
| `lon` | Float | (Optional) GPS Longitude. |

**Hardware Note:**
The server is configured to accept **Raw PCM** (16-bit, Mono) and automatically converts it to a valid WAV file with a header. Ensure your microphone sample rate matches the `SAMPLE_RATE` variable in `monitor.py` (Default: **44100 Hz**).

### 2. Download Report (`GET /download-excel`)

Triggers a download of `bird_report.xlsx` containing the full history of detections.

---

## 🖼️ Spectrogram Features

The visualization engine includes several logic fixes for readability:

* **Linear Frequency Scale:** Displays scientifically accurate Hz (0-8000Hz).
* **Smart Layout:**
* **Dynamic Width:** Graph gets wider for longer recordings to prevent squishing.
* **Staggered Labels:** Text labels drop down in steps to avoid overlapping when birds chirp simultaneously.
* **Safe Margins:** Start/End detections are clamped to keep text inside the image.



---

## 🤝 Credits

* **BirdNET-Analyzer** by the K. Lisa Yang Center for Conservation Bioacoustics.
* Built for the **VinUni Computer Science** freshman project.

```

```