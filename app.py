import sys
import os
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

import database
from monitor import NetworkMonitor
from notification import start_notification_scheduler, send_usage_notification

# Initialize database
database.init_db()

# Create and start Network Monitor
monitor = NetworkMonitor()
monitor.start()

# Start background notification scheduler (runs every 1 hour / 3600 seconds)
# For demonstration and monitoring, we keep the default at 3600 seconds.
start_notification_scheduler(monitor, interval_seconds=3600)

# Create Flask application
app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)
CORS(app)  # Enable Cross-Origin Resource Sharing for API accessibility

@app.route("/")
def index():
    """Serve the main HTML dashboard."""
    return render_template("index.html")

@app.route("/api/status", methods=["GET"])
def get_status():
    """Retrieve real-time network speeds, cumulative totals, uptime, and IP address."""
    try:
        data = monitor.get_live_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/charts", methods=["GET"])
def get_charts():
    """Retrieve hourly history for today and daily history for the last 7 days."""
    try:
        hourly = database.get_hourly_history()
        daily = database.get_daily_history(limit=7)
        return jsonify({
            "hourly": hourly,
            "daily": daily
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/interfaces", methods=["GET"])
def get_interfaces():
    """Retrieve the list of available network interfaces and the currently monitored one."""
    try:
        return jsonify({
            "interfaces": monitor.get_interfaces(),
            "selected": monitor.selected_interface
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/settings", methods=["POST"])
def update_settings():
    """Update the monitored network interface."""
    try:
        req_data = request.get_json() or {}
        interface_name = req_data.get("interface")
        if not interface_name:
            return jsonify({"error": "Interface name is required"}), 400
            
        success = monitor.set_interface(interface_name)
        if success:
            return jsonify({
                "message": f"Successfully switched to monitoring {interface_name}",
                "selected": interface_name
            })
        else:
            return jsonify({"error": "Interface not found or invalid"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/test-notification", methods=["POST"])
def trigger_test_notification():
    """Trigger a manual desktop notification immediately for testing."""
    try:
        success = send_usage_notification(monitor)
        if success:
            return jsonify({"message": "Test notification triggered successfully!"})
        else:
            return jsonify({"error": "Failed to send notification. Verify system notifications are enabled."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Start the Flask development server on port 5000
    print("*" * 50)
    print("  INTERNET USAGE MONITOR SERVER STARTED")
    print("  Access dashboard at: http://127.0.0.1:5000")
    print("*" * 50)
    app.run(host="127.0.0.1", port=5000, debug=False)
