from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
import pandas as pd
import sqlite3

from ..database import get_db

router = APIRouter()


@router.get("/api/detections")
def get_detections(db: sqlite3.Connection = Depends(get_db)):
    """Get all detections, newest first."""
    c = db.cursor()
    c.execute("SELECT * FROM detections ORDER BY timestamp DESC")
    rows = c.fetchall()

    return [dict(row) for row in rows]


@router.get("/download-excel")
def download_excel(db: sqlite3.Connection = Depends(get_db)):
    """Export all detections as an Excel file."""
    df = pd.read_sql_query("SELECT * FROM detections", db)

    excel_file = "bird_data.xlsx"
    df.to_excel(excel_file, index=False)

    return FileResponse(excel_file, filename="bird_report.xlsx")
