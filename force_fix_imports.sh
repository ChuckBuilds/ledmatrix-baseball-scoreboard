#!/bin/bash
# Force fix the import issues in app.py

echo "🔧 Forcing correct imports in app.py..."

# Backup the current file
cp ~/LEDMatrix/web_interface/app.py ~/LEDMatrix/web_interface/app.py.backup

# Get the correct version from git
cd ~/LEDMatrix
git checkout HEAD -- web_interface/app.py

echo "✅ Restored correct app.py from git"

# Verify the imports are now correct
echo ""
echo "🔍 Checking imports after fix:"
python3 check_imports.py

echo ""
echo "🧹 Clearing Python cache..."
find ~/LEDMatrix -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find ~/LEDMatrix -name "*.pyc" -delete 2>/dev/null || true

echo ""
echo "🚀 Now try running the web interface:"
echo "cd ~/LEDMatrix"
echo "python3 web_interface/start.py"
