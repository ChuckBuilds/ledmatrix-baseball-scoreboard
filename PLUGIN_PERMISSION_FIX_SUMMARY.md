# Plugin Dependency Permission Fix Summary

**Date:** October 17, 2025  
**Issue:** Permission errors when installing plugin dependencies  
**Status:** ✅ Fixed

## Problem Description

When the LEDMatrix system tried to install plugin dependencies automatically, it encountered permission errors:

```
ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied: '/root/.local'
WARNING: The directory '/root/.cache/pip' or its parent directory is not owned or is not writable
```

## Root Cause

The pip package installer was trying to use the cache directory and install to locations with permission issues. This occurred when:
1. The systemd service (running as root) tried to install dependencies
2. Pip attempted to use `/root/.cache/pip` which had permission issues
3. Installation failed, preventing plugins from loading properly

## Solution Implemented

### 1. Updated Plugin Manager (Core Fix)

**File:** `src/plugin_system/plugin_manager.py`

**Changes:**
- Added `--no-cache-dir` flag to all pip install commands
- This bypasses the pip cache entirely, avoiding cache permission issues
- Updated error handling to provide more helpful messages
- Added environment variable handling for better subprocess execution

**Key code change:**
```python
# Before:
cmd = ['pip3', 'install', '--break-system-packages', '-r', str(requirements_file)]

# After:
cmd = ['pip3', 'install', '--break-system-packages', '--no-cache-dir', '-r', str(requirements_file)]
```

### 2. Created Helper Script

**File:** `scripts/install_plugin_dependencies.sh`

A new utility script that:
- Automatically finds all plugins with dependencies
- Installs them with correct permissions
- Uses `--no-cache-dir` to avoid permission issues
- Provides detailed logging and error messages
- Works for both root and non-root users

### 3. Added Comprehensive Documentation

**Files Created:**
- `PLUGIN_DEPENDENCY_TROUBLESHOOTING.md` - Detailed troubleshooting guide
- `PLUGIN_PERMISSION_FIX_SUMMARY.md` - This summary

**Files Updated:**
- `PLUGIN_DEPENDENCY_GUIDE.md` - Added troubleshooting section with helper script info

## How to Apply the Fix

### Option 1: Deploy Updated Code (Recommended)

1. **Push changes to your repository** (if working on the plugins branch):
   ```bash
   git add .
   git commit -m "Fix plugin dependency permission issues"
   git push origin plugins
   ```

2. **On your Raspberry Pi**, pull the updates:
   ```bash
   cd /home/ledpi/LEDMatrix
   git pull origin plugins
   ```

3. **Make the helper script executable:**
   ```bash
   chmod +x /home/ledpi/LEDMatrix/scripts/install_plugin_dependencies.sh
   ```

4. **Restart the service to use the updated code:**
   ```bash
   sudo systemctl restart ledmatrix
   ```

### Option 2: Manual Dependency Installation (Quick Fix)

If you need to install dependencies right now without deploying code:

1. **Use the new helper script** (after deploying the code):
   ```bash
   sudo /home/ledpi/LEDMatrix/scripts/install_plugin_dependencies.sh
   sudo systemctl restart ledmatrix
   ```

2. **Or manually install for a specific plugin:**
   ```bash
   cd /home/ledpi/LEDMatrix/plugins/PLUGIN-NAME
   sudo pip3 install --break-system-packages --no-cache-dir -r requirements.txt
   sudo systemctl restart ledmatrix
   ```

## Verification

After applying the fix, check that it's working:

```bash
# Check the service logs
sudo journalctl -u ledmatrix -n 50 --no-pager

# You should NOT see:
# - "Permission denied: '/root/.local'"
# - "not owned or is not writable"

# You SHOULD see:
# - "Successfully installed dependencies"
# - Plugins loading correctly
```

## Prevention

To avoid this issue in the future:

1. **Use the web interface** for plugin installation when possible
2. **Use the helper script** when installing manually:
   ```bash
   sudo /home/ledpi/LEDMatrix/scripts/install_plugin_dependencies.sh
   ```
3. **Always restart the service** after manual plugin changes:
   ```bash
   sudo systemctl restart ledmatrix
   ```

## Technical Details

### What Changed in the Code

The `_install_plugin_dependencies()` method in `plugin_manager.py` now:

1. **Avoids pip cache** with `--no-cache-dir` flag
   - Prevents permission errors on `/root/.cache/pip`
   - Slightly slower but much more reliable

2. **Better error handling**
   - More descriptive error messages
   - Logs helpful troubleshooting hints
   - Continues plugin loading even if deps fail (user can install manually)

3. **Environment setup**
   - Properly handles subprocess environment
   - Sets `PYTHONUNBUFFERED=1` for better logging

### Why This Works

The `--no-cache-dir` flag tells pip to:
- Skip reading from cache (no need for read permissions)
- Skip writing to cache (no need for write permissions)
- Install directly to the target location
- Trade-off: Slower installation but more reliable

## Testing Checklist

- [ ] Code deployed to Raspberry Pi
- [ ] Helper script is executable
- [ ] Service restarted successfully
- [ ] No permission errors in logs
- [ ] Plugins with dependencies load correctly
- [ ] Existing functionality still works

## Rollback Plan

If the fix causes issues:

```bash
# Revert to previous commit
cd /home/ledpi/LEDMatrix
git log --oneline  # Find the commit before the fix
git checkout <previous-commit-hash>
sudo systemctl restart ledmatrix
```

## Related Issues

This fix addresses:
- Permission denied errors when installing plugin dependencies
- Cache directory permission issues
- Plugin loading failures due to missing dependencies

## Next Steps

1. **Deploy the fix** to your Raspberry Pi
2. **Test with an existing plugin** that has dependencies
3. **Install a new plugin** to verify automatic dependency installation works
4. **Monitor logs** for any remaining issues

## Support Resources

- [Plugin Dependency Guide](PLUGIN_DEPENDENCY_GUIDE.md)
- [Plugin Dependency Troubleshooting](PLUGIN_DEPENDENCY_TROUBLESHOOTING.md)
- [Troubleshooting Quick Start](TROUBLESHOOTING_QUICK_START.md)

---

**Questions or Issues?**

If you continue to see permission errors after applying this fix:
1. Check the logs: `sudo journalctl -u ledmatrix -f`
2. Try the helper script: `sudo /home/ledpi/LEDMatrix/scripts/install_plugin_dependencies.sh`
3. Review the troubleshooting guide: `PLUGIN_DEPENDENCY_TROUBLESHOOTING.md`

