from flask import Flask, jsonify
from flask_cors import CORS
import json
import os
import datetime
import random
import time
from datetime import datetime, timezone, timedelta
import tempfile
import shutil

app = Flask(__name__)
CORS(app)

# Path to waf_logs.json
LOG_FILE = 'waf_logs.json'

# Ensure waf_logs.json exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w') as f:
        json.dump([], f)

# Function to append a new log entry with a timestamp in a specified hour
def append_log_entry(hour_offset=0):
    try:
        # Load existing logs
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)

        # Base timestamp: current UTC time minus the hour offset
        base_time = datetime.now(timezone.utc) - timedelta(hours=hour_offset)
        timestamp = base_time.isoformat()

        # Simulate a new log entry with varied HTTP status and attack class
        http_status = random.choice([200, 403])  # Randomly choose ALLOWED or BLOCKED
        attack_class = random.choice(["None", "SQLi", "DDoS", "XSS", "DirectoryTraversal", "CommandInjection"])
        confidence_score = random.uniform(0.1, 1.0)  # Random confidence score between 0.1 and 1.0

        new_entry = {
            "general_request_data": {
                "timestamp": timestamp,
                "source_ip": str(random.randint(1, 255)),  # Random source IP as string
                "dest_ip": 7,
                "source_port": random.randint(10000, 60000),
                "dest_port": 80,
                "request_method": random.choice(["GET", "POST"]),
                "requested_path": "/login",
                "query_params": {},
                "user_agent": "curl/8.10.1",
                "referrer": "Unknown",
                "http_status": http_status
            },
            "traffic_ddos_monitoring": {
                "total_requests_per_second": 1.0,
                "packets_per_second": 150.0,
                "packet_length": 40,
                "traffic_volume_bytes_per_second": 6000.0,
                "unique_ips": [8],
                "flagged_ddos_attacks": 0
            },
            "anomaly_detection_metrics": {
                "path_entropy": 0,
                "body_entropy": 0,
                "url_length": 27,
                "body_length": 25,
                "single_quotes_count": 0,
                "double_quotes_count": 0,
                "dashes_count": 0,
                "braces_count": 0,
                "spaces_count": 4,
                "sql_injection_patterns": 2,
                "xss_patterns": 0,
                "directory_traversal_attempts": 0,
                "command_injection_count": 0,
                "csrf_count": 0
            },
            "ml_attack_detection": {
                "attack_class": attack_class,
                "ml_confidence_score": confidence_score,
                "anomaly_score": 1.508619785308838,
                "feature_contributions": {
                    "feature_0": 27.0,
                    "feature_1": 25.0,
                    "feature_2": 0.0,
                    "feature_3": 0.0,
                    "feature_4": 0.0,
                    "feature_5": 0.0,
                    "feature_6": 4.0,
                    "feature_7": 2.0,
                    "feature_8": 0.0,
                    "feature_9": 0.0,
                    "feature_10": 0.0,
                    "feature_11": 0.0
                }
            },
            "log_performance_insights": {
                "total_requests_handled": 1,
                "normal_requests": 1 if http_status == 200 else 0,  # Correctly set based on http_status
                "malicious_requests": 0 if http_status == 200 else 1,  # Correctly set based on http_status
                "attack_detection_accuracy": None,
                "average_processing_time": 1.3449146747589111,
                "most_frequent_attack_patterns": []
            }
        }

        logs.append(new_entry)

        # Write to a temporary file first, then move to avoid partial reads
        temp_fd, temp_path = tempfile.mkstemp()
        try:
            with os.fdopen(temp_fd, 'w') as temp_file:
                json.dump(logs, temp_file, indent=2)
            shutil.move(temp_path, LOG_FILE)  # Atomic move to replace the original file
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)  # Clean up temp file if move fails

        print(f"Added new log entry at {new_entry['general_request_data']['timestamp']}: HTTP {http_status}, Attack: {attack_class}")
    except Exception as e:
        print(f"Error appending log entry: {str(e)}")

@app.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
        return jsonify(logs)
    except FileNotFoundError as e:
        print(f"Error: Log file '{LOG_FILE}' not found: {str(e)}")
        return jsonify({"error": "Log file not found"}), 500
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON in '{LOG_FILE}': {str(e)}")
        return jsonify({"error": "Failed to parse log file"}), 500
    except Exception as e:
        print(f"Error reading logs: {str(e)}")
        return jsonify({"error": "Failed to read logs"}), 500

# Endpoint to simulate adding a new log entry
@app.route('/api/simulate-log', methods=['POST'])
def simulate_log():
    append_log_entry()
    return jsonify({"message": "Log entry added"}), 200

# Simulate adding a new log entry every 5 seconds with varied timestamps
def simulate_logs():
    hour_offset = 0
    while True:
        # Start from 23 hours ago up to the current time
        hour_offset = (hour_offset + 1) % 24  # Cycle through 0 to 23 hours
        append_log_entry(hour_offset=hour_offset)
        time.sleep(5)  # Add a new log every 5 seconds

if __name__ == '__main__':
    # Start the simulation in a separate thread to avoid blocking the Flask server
    import threading
    thread = threading.Thread(target=simulate_logs, daemon=True)
    thread.start()
    app.run(debug=True, host='0.0.0.0', port=5000)