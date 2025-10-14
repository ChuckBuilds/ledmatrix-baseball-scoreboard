#!/usr/bin/env python3
"""
Test script to replicate start.py's environment setup
"""

import os
import sys
from pathlib import Path

# Replicate exactly what start.py does
def main():
    print("🔧 Setting up environment like start.py...")

    # Change to project root directory (same as start.py)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    print(f"📁 Changing to: {project_root}")
    os.chdir(project_root)

    # Add to Python path (same as start.py)
    sys.path.insert(0, str(project_root))
    print(f"🔗 Added to Python path: {project_root}")
    print(f"🔍 Current working directory: {os.getcwd()}")
    print(f"🔍 Python path: {sys.path[:3]}...")  # Show first 3 paths

    print("\n🚀 Now testing imports...")

    # Test the import that was failing
    try:
        from web_interface.app import app
        print("✅ SUCCESS: web_interface.app imported!")
        print(f"📋 App object: {app}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Import test passed!")
    else:
        print("\n💥 Import test failed!")
