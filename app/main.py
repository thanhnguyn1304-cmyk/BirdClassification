from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings, STORAGE_DIR
from .database import init_db
from .logging_config import setup_logging, get_logger
from .routers import upload, detections, analytics, species

# Initialize logging first
setup_logging()
logger = get_logger("main")

app = FastAPI(title="AvianNET API", version="2.0.0")

# CORS Middleware — origins controlled via .env
origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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


# Global exception handler — catches any unhandled errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled error on %s %s: %s",
        request.method,
        request.url.path,
        exc,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    logger.info("Database initialized")
    logger.info("Storage directory: %s", STORAGE_DIR)
    logger.info("CORS origins: %s", origins)
