#!/usr/bin/env python3
"""
LED Matrix Web Interface V3 Startup Script
Modern web interface with real-time display preview and plugin management.
"""

import os
import sys
from pathlib import Path

def main():
    """Main startup function."""
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Add to Python path
    sys.path.insert(0, str(project_root))
    
    # Import and run the Flask app
    from web_interface.app import app
    
    print("Starting LED Matrix Web Interface V3...")
    print("Access the interface at: http://0.0.0.0:5000")
    
    # Run the web server
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()

