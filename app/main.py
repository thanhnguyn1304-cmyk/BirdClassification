from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .config import STORAGE_DIR
from .database import init_db
from .routers import upload, detections, analytics, species

app = FastAPI(title="Bird Classification API", version="1.0.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/storage", StaticFiles(directory=STORAGE_DIR), name="storage")

# Include routers
app.include_router(upload.router)
app.include_router(detections.router)
app.include_router(analytics.router)
app.include_router(species.router)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    print("🗄️ Database initialized.")


