# Testing Plan for Plugin-Only Refactor

## Quick Test Checklist

### 1. Service Start Test
```bash
ssh ledpi@ledpi.local
sudo systemctl restart ledmatrix
sudo systemctl status ledmatrix
```

**Expected:** Service starts without NameError or AttributeError

### 2. Check Logs for Errors
```bash
sudo journalctl -u ledmatrix -f
```

**Look for:**
- ✅ "Plugin system initialized"
- ✅ "Loaded plugin: <plugin_name>"
- ✅ Dynamic favorite teams logging (e.g., "Weather Favorite teams: []")
- ❌ No NameError about undefined variables
- ❌ No permission errors from pip

### 3. Plugin Loading Test
```bash
sudo journalctl -u ledmatrix | grep -i "plugin\|error\|favorite"
```

**Expected:**
- All enabled plugins load successfully
- Favorite teams logged for plugins that have them configured
- No "NameError: name 'nhl_enabled' is not defined"

### 4. Display Rotation Test
- Watch the display for 5 minutes
- Verify modes rotate properly
- Check that clock and plugin modes work

### 5. Dependency Installation Test
```bash
# Check if plugin dependencies installed correctly
pip3 list | grep -i requests  # or other plugin dependencies
```

**Expected:** 
- No permission errors during dependency installation
- System-wide installation when running as root (systemd service)
- User installation when running as non-root (development)

## What Was Fixed

1. **NameError** - Removed hard-coded sport variables that were causing crashes
2. **Permission Error** - Smart dependency installation (system-wide for root, user for development)
3. **Dynamic Structure** - System now works with any plugin configuration

## Troubleshooting

### If service won't start:
```bash
sudo journalctl -u ledmatrix -n 100 --no-pager
```
Look for the specific error and check PLUGIN_ONLY_REFACTOR.md for what changed

### If plugins don't load:
- Check plugin manifest.json files
- Verify plugin config in config.json
- Check plugin requirements.txt for dependency issues

### If display is blank:
- Verify at least one plugin or clock is enabled
- Check that display is within scheduled time
- Review display rotation logs

