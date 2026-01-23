from fastapi import APIRouter
from fastapi.responses import FileResponse
import pandas as pd

from ..database import get_db_connection, DATABASE_PATH

router = APIRouter()

@router.get("/api/detections")
def get_detections():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM detections ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    
    # Convert to list of dicts
    detections = [dict(row) for row in rows]
    return detections


@router.get("/download-excel")
def download_excel():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM detections", conn)
    conn.close()
    
    excel_file = "bird_data.xlsx"
    df.to_excel(excel_file, index=False)
    
    return FileResponse(excel_file, filename="bird_report.xlsx")
