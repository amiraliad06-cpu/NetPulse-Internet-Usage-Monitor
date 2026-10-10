import time
import threading
from plyer import notification
import database

def format_bytes(b):
    """Convert bytes into a human-readable string representation."""
    if b < 1024:
        return f"{b} B"
    elif b < 1024 * 1024:
        return f"{b / 1024:.2f} KB"
    elif b < 1024 * 1024 * 1024:
        return f"{b / (1024 * 1024):.2f} MB"
    else:
        return f"{b / (1024 * 1024 * 1024):.2f} GB"

def send_usage_notification(monitor=None):
    """
    Compile statistics and trigger a native system notification.
    Retrieves the actual traffic spent in the last 60 minutes and total today.
    """
    try:
        # Get last hour usage from SQLite logs
        last_hour = database.get_last_hour_usage()
        last_hour_down = last_hour["download_bytes"]
        last_hour_up = last_hour["upload_bytes"]
        
        # Get today's cumulative usage (including active live session bytes if monitor is provided)
        if monitor:
            live = monitor.get_live_data()
            today_down = live["today_download_bytes"]
            today_up = live["today_upload_bytes"]
        else:
            db_today = database.get_today_totals()
            today_down = db_today["download_bytes"]
            today_up = db_today["upload_bytes"]
            
        title = "Internet Usage Monitor"
        message = (
            f"Last Hour:\n"
            f"  ⬇️ Down: {format_bytes(last_hour_down)} | ⬆️ Up: {format_bytes(last_hour_up)}\n\n"
            f"Today's Totals:\n"
            f"  ⬇️ Down: {format_bytes(today_down)} | ⬆️ Up: {format_bytes(today_up)}"
        )
        
        # Trigger Plyer notification (works on Windows, macOS, and Linux)
        notification.notify(
            title=title,
            message=message,
            app_name="InternetUsageMonitor",
            timeout=8
        )
        print("Desktop Notification sent.")
        return True
    except Exception as e:
        print(f"Failed to trigger desktop notification: {e}")
        return False

def start_notification_scheduler(monitor, interval_seconds=3600):
    """
    Start a background thread that scheduled a notification every 'interval_seconds'.
    Default is 1 hour (3600 seconds). Sleeping in 10-second intervals so it stays light.
    """
    def scheduler_loop():
        print(f"Notification Scheduler running. Interval: {interval_seconds} seconds.")
        last_sent = time.time()
        
        while True:
            # Check every 10 seconds if the interval has elapsed
            time.sleep(10)
            now = time.time()
            if now - last_sent >= interval_seconds:
                send_usage_notification(monitor)
                last_sent = now
                
    thread = threading.Thread(target=scheduler_loop, daemon=True)
    thread.start()
    return thread
