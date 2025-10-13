from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
import json
import os
import subprocess
import time
from pathlib import Path
from src.config_manager import ConfigManager

# Create Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)
config_manager = ConfigManager()

# Register blueprints
from blueprints.pages_v3 import pages_v3
from blueprints.api_v3 import api_v3

# Initialize config_manager in blueprints
pages_v3.config_manager = config_manager
api_v3.config_manager = config_manager

app.register_blueprint(pages_v3, url_prefix='/v3')
app.register_blueprint(api_v3, url_prefix='/api/v3')

# SSE helper function
def sse_response(generator_func):
    """Helper to create SSE responses"""
    def generate():
        for data in generator_func():
            yield f"data: {json.dumps(data)}\n\n"
    return Response(generate(), mimetype='text/event-stream')

# System status generator for SSE
def system_status_generator():
    """Generate system status updates"""
    while True:
        try:
            # Get basic system info (could be expanded)
            status = {
                'timestamp': time.time(),
                'uptime': 'Running',
                'service_active': True,  # This would need to be checked from systemd
                'cpu_percent': 0,  # Would need psutil or similar
                'memory_used_percent': 0,
                'cpu_temp': 0,
                'disk_used_percent': 0
            }
            yield status
        except Exception as e:
            yield {'error': str(e)}
        time.sleep(5)  # Update every 5 seconds

# Display preview generator for SSE
def display_preview_generator():
    """Generate display preview updates"""
    while True:
        try:
            # This would integrate with the actual display controller
            # For now, return a placeholder
            preview_data = {
                'timestamp': time.time(),
                'width': 128,
                'height': 64,
                'image': None  # Base64 encoded image data
            }
            yield preview_data
        except Exception as e:
            yield {'error': str(e)}
        time.sleep(1)  # Update every second

# Logs generator for SSE
def logs_generator():
    """Generate log updates from journalctl"""
    last_position = None

    while True:
        try:
            # Get recent logs from journalctl (similar to original implementation)
            result = subprocess.run(
                ['sudo', 'journalctl', '-u', 'ledmatrix.service', '-n', '100', '--no-pager', '--since', '1 minute ago'],
                capture_output=True, text=True, check=True
            )

            logs_text = result.stdout.strip()

            # Check if logs have changed
            current_position = hash(logs_text)
            if last_position != current_position:
                last_position = current_position

                logs_data = {
                    'timestamp': time.time(),
                    'logs': logs_text if logs_text else 'No recent logs available'
                }
                yield logs_data

        except subprocess.CalledProcessError as e:
            # If journalctl fails, yield error message
            error_data = {
                'timestamp': time.time(),
                'logs': f'Error fetching logs: {e.stderr.strip()}'
            }
            yield error_data
        except Exception as e:
            error_data = {
                'timestamp': time.time(),
                'logs': f'Unexpected error: {str(e)}'
            }
            yield error_data

        time.sleep(3)  # Update every 3 seconds

# SSE endpoints
@app.route('/api/v3/stream/stats')
def stream_stats():
    return sse_response(system_status_generator)

@app.route('/api/v3/stream/display')
def stream_display():
    return sse_response(display_preview_generator)

@app.route('/api/v3/stream/logs')
def stream_logs():
    return sse_response(logs_generator)

# Main route - redirect to v3 interface as default
@app.route('/')
def index():
    """Redirect to v3 interface"""
    return redirect(url_for('pages_v3.index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
