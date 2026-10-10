import sqlite3
import os
import datetime

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "usage.db")

def get_db_connection():
    """Establish a connection to the SQLite database."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS minute_usage (
            timestamp TEXT PRIMARY KEY, -- Formatted as 'YYYY-MM-DD HH:MM'
            download_bytes INTEGER DEFAULT 0,
            upload_bytes INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def log_usage(download_bytes, upload_bytes):
    """
    Log network usage for the current minute.
    Aggregates bytes for the same minute using UPSERT.
    """
    if download_bytes <= 0 and upload_bytes <= 0:
        return
        
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO minute_usage (timestamp, download_bytes, upload_bytes)
            VALUES (?, ?, ?)
            ON CONFLICT(timestamp) DO UPDATE SET
                download_bytes = download_bytes + excluded.download_bytes,
                upload_bytes = upload_bytes + excluded.upload_bytes
        """, (timestamp, download_bytes, upload_bytes))
        conn.commit()
    except Exception as e:
        print(f"Error logging usage: {e}")
    finally:
        conn.close()

def get_today_totals():
    """Calculate the total download and upload bytes for today."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(download_bytes) as total_down, SUM(upload_bytes) as total_up
        FROM minute_usage
        WHERE timestamp LIKE ?
    """, (f"{today}%",))
    row = cursor.fetchone()
    conn.close()
    
    down = row["total_down"] if row and row["total_down"] is not None else 0
    up = row["total_up"] if row and row["total_up"] is not None else 0
    return {"download_bytes": down, "upload_bytes": up}

def get_month_totals():
    """Calculate the total download and upload bytes for the current month."""
    this_month = datetime.datetime.now().strftime("%Y-%m")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(download_bytes) as total_down, SUM(upload_bytes) as total_up
        FROM minute_usage
        WHERE timestamp LIKE ?
    """, (f"{this_month}%",))
    row = cursor.fetchone()
    conn.close()
    
    down = row["total_down"] if row and row["total_down"] is not None else 0
    up = row["total_up"] if row and row["total_up"] is not None else 0
    return {"download_bytes": down, "upload_bytes": up}

def get_hourly_history():
    """
    Retrieve aggregated download/upload bytes grouped by hour for the current day.
    Returns a complete list of 24 hours (00:00 to 23:00) with data.
    """
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUBSTR(timestamp, 12, 2) || ':00' AS hr,
               SUM(download_bytes) AS down,
               SUM(upload_bytes) AS up
        FROM minute_usage
        WHERE timestamp LIKE ?
        GROUP BY hr
        ORDER BY hr ASC
    """, (f"{today}%",))
    rows = cursor.fetchall()
    conn.close()
    
    # Initialize dictionary for 24 hours
    hourly_data = {f"{str(h).zfill(2)}:00": {"download": 0, "upload": 0} for h in range(24)}
    
    for row in rows:
        hr = row["hr"]
        if hr in hourly_data:
            hourly_data[hr] = {
                "download": row["down"],
                "upload": row["up"]
            }
            
    # Convert to sorted list
    return [{"hour": hr, "download": data["download"], "upload": data["upload"]} 
            for hr, data in sorted(hourly_data.items())]

def get_daily_history(limit=7):
    """
    Retrieve aggregated daily usage for the last 'limit' days.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUBSTR(timestamp, 1, 10) AS dt,
               SUM(download_bytes) AS down,
               SUM(upload_bytes) AS up
        FROM minute_usage
        GROUP BY dt
        ORDER BY dt DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    daily_data = []
    for row in rows:
        daily_data.append({
            "date": row["dt"],
            "download": row["down"],
            "upload": row["up"]
        })
    
    # Return chronological order (oldest to newest)
    daily_data.reverse()
    
    # If empty, insert today with 0
    if not daily_data:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        daily_data.append({"date": today, "download": 0, "upload": 0})
        
    return daily_data

def get_last_hour_usage():
    """
    Calculate the total download and upload bytes in the last 60 minutes.
    Used for hourly notifications.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get minutes in the last 60 minutes
    now = datetime.datetime.now()
    timestamps = []
    for i in range(60):
        t = (now - datetime.timedelta(minutes=i)).strftime("%Y-%m-%d %H:%M")
        timestamps.append(t)
        
    placeholders = ",".join(["?"] * len(timestamps))
    cursor.execute(f"""
        SELECT SUM(download_bytes) as total_down, SUM(upload_bytes) as total_up
        FROM minute_usage
        WHERE timestamp IN ({placeholders})
    """, timestamps)
    row = cursor.fetchone()
    conn.close()
    
    down = row["total_down"] if row and row["total_down"] is not None else 0
    up = row["total_up"] if row and row["total_up"] is not None else 0
    return {"download_bytes": down, "upload_bytes": up}
