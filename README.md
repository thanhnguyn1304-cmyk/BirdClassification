# 🦅 AvianNET — IoT Bioacoustic Monitoring Platform

A full-stack environmental monitoring system that processes real-time audio from ESP32 IoT sensors, classifies bird species using the **BirdNET AI model**, and provides analytics for ecological health assessment.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128-green)
![React](https://img.shields.io/badge/React-Vite+TS-purple)
![AI](https://img.shields.io/badge/AI-BirdNET-orange)
![CI](https://img.shields.io/badge/CI-GitHub_Actions-black)

---

## Architecture

```
ESP32 Sensor                  AvianNET Server                  Frontend
┌──────────┐    WAV Audio    ┌──────────────────┐             ┌──────────────┐
│ Mic +    │ ──────────────> │  FastAPI          │             │  React +     │
│ GPS      │   POST /upload  │  ├── Upload Router│ <────────> │  Recharts    │
└──────────┘                 │  ├── BirdNET AI   │  REST API  │  Analytics   │
                             │  ├── Spectrogram  │             │  Dashboard   │
                             │  ├── Analytics    │             └──────────────┘
                             │  └── SQLite DB    │
                             └──────────────────┘
```

## Features

- **🎙️ IoT Audio Ingestion** — Accepts raw audio streams from ESP32 and manual browser uploads
- **🧠 AI Classification** — BirdNET model identifies 400+ species with confidence scoring
- **📊 Analytics Dashboard** — Species distribution, hourly activity, detection trends, confidence distribution
- **🏥 Population Health** — Composite health score with dawn chorus analysis and recency decay
- **🖼️ Spectrograms** — High-res (300 DPI) visualizations with labeled detection bounding boxes
- **📑 Data Export** — One-click Excel export of all detection data
- **🔍 Species Encyclopedia** — Wikipedia-sourced species info with caching

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, FastAPI, SQLite, Pydantic |
| **AI** | BirdNET-Analyzer (birdnetlib) |
| **Audio** | Librosa, PyDub, Matplotlib |
| **Frontend** | React, TypeScript, Vite, Recharts, Tailwind CSS |
| **Hardware** | ESP32 (I2S Microphone + GPS) |
| **DevOps** | Docker, GitHub Actions CI |

---

## Quick Start

### With Docker (Recommended)
```bash
git clone https://github.com/your-username/AvianNET.git
cd AvianNET
cp .env.example .env
docker compose up --build
```
App available at `http://localhost:8000`

### Manual Setup
```bash
# Backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
python run.py

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Accept raw audio from ESP32 |
| `POST` | `/upload/manual` | Browser/Swagger file upload |
| `GET` | `/api/detections` | List all detections |
| `GET` | `/api/analytics/summary` | Summary statistics |
| `GET` | `/api/analytics/health` | Population health score |
| `GET` | `/api/analytics/trends?period=day` | Detection trends |
| `GET` | `/api/analytics/hourly-activity` | Activity by hour |
| `GET` | `/api/analytics/species-distribution` | Species pie chart data |
| `GET` | `/api/analytics/confidence-distribution` | Confidence score buckets |
| `GET` | `/api/species` | All cached species info |
| `GET` | `/api/species/{name}` | Species detail |
| `GET` | `/api/species-summary` | Species with detection stats |
| `GET` | `/download-excel` | Export detections as Excel |

Interactive API docs: `http://localhost:8000/docs`

---

## Testing

```bash
python -m pytest tests/ -v
```

---

## Project Structure

```
AvianNET/
├── app/
│   ├── main.py              # FastAPI app, middleware, error handler
│   ├── config.py             # Pydantic settings (.env support)
│   ├── database.py           # SQLite with dependency injection
│   ├── logging_config.py     # Structured logging
│   ├── routers/
│   │   ├── upload.py         # Upload endpoints (thin)
│   │   ├── detections.py     # Detection CRUD + Excel export
│   │   ├── analytics.py      # Analytics & health score
│   │   └── species.py        # Species info endpoints
│   └── services/
│       ├── upload_service.py  # Upload processing logic
│       ├── analyzer.py        # BirdNET model loader
│       ├── spectrogram.py     # Matplotlib visualizations
│       ├── audio.py           # Audio slicing
│       └── bird_images.py     # Wikipedia species info
├── tests/
│   ├── conftest.py           # Shared fixtures (in-memory DB)
│   ├── test_analytics.py
│   ├── test_detections.py
│   └── test_species.py
├── frontend/                 # React + Vite + TypeScript
├── esp32/                    # ESP32 firmware
├── Dockerfile                # Multi-stage build
├── docker-compose.yml
├── requirements.txt
└── .github/workflows/ci.yml  # CI pipeline
```

---

## Credits

- **BirdNET-Analyzer** by the K. Lisa Yang Center for Conservation Bioacoustics
- Built for the **VinUni Computer Science** program