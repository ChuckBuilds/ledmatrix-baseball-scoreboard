#!/bin/bash
# Fix permissions for the plugins directory
# This script sets up proper permissions for both root service and web service access

echo "Fixing permissions for plugins directory..."

# Get the actual user who invoked sudo
if [ -n "$SUDO_USER" ]; then
    ACTUAL_USER="$SUDO_USER"
else
    ACTUAL_USER=$(whoami)
fi

# Get the project root directory (parent of scripts directory)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT_DIR="$( cd "$SCRIPT_DIR/../.." && pwd )"
PLUGINS_DIR="$PROJECT_ROOT_DIR/plugins"

echo "Project root directory: $PROJECT_ROOT_DIR"
echo "Plugins directory: $PLUGINS_DIR"
echo "Actual user: $ACTUAL_USER"

# Ensure plugins directory exists
if [ ! -d "$PLUGINS_DIR" ]; then
    echo "Creating plugins directory..."
    mkdir -p "$PLUGINS_DIR"
fi

# Set ownership to root:ACTUAL_USER for mixed access
# Root service can read/write, web service (ACTUAL_USER) can read/write
echo "Setting ownership to root:$ACTUAL_USER..."
sudo chown -R root:"$ACTUAL_USER" "$PLUGINS_DIR"

# Set directory permissions (775: rwxrwxr-x)
# Root: read/write/execute, Group (ACTUAL_USER): read/write/execute, Others: read/execute
echo "Setting directory permissions to 775..."
find "$PLUGINS_DIR" -type d -exec sudo chmod 775 {} \;

# Set file permissions (664: rw-rw-r--)
# Root: read/write, Group (ACTUAL_USER): read/write, Others: read
echo "Setting file permissions to 664..."
find "$PLUGINS_DIR" -type f -exec sudo chmod 664 {} \;

echo "Plugin permissions fixed successfully!"
echo ""
echo "Directory structure:"
ls -la "$PLUGINS_DIR"
echo ""
echo "Permissions summary:"
echo "- Root service: Can read/write plugins (for PWM hardware access)"
echo "- Web service ($ACTUAL_USER): Can read/write plugins (for installation)"
echo "- Others: Can read plugins"

