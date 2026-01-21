import sqlite3
import pandas as pd

conn = sqlite3.connect("birds.db")
print(pd.read_sql_query("SELECT * FROM detections", conn))
conn.close()