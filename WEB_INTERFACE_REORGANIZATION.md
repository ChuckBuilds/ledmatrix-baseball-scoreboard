# Web Interface Reorganization Summary

## Overview

The web interface files have been reorganized for better maintainability and clarity. All active V3 web interface files are now consolidated in the `web_interface/` directory, while legacy V1/V2 files have been moved to `old_web_interface/` for reference.

## New Directory Structure

### Active Web Interface (V3)
```
web_interface/
├── __init__.py
├── app.py                    # Main Flask application (was: web_interface_v3.py)
├── start.py                  # Startup script
├── run.sh                    # Shell runner script  
├── requirements.txt          # Web dependencies (was: requirements_web_v2.txt)
├── README.md                 # Web interface documentation
├── blueprints/               # Flask blueprints (was: /blueprints)
│   ├── __init__.py
│   ├── api_v3.py            # API endpoints
│   └── pages_v3.py          # Page routes
├── templates/                # HTML templates (was: /templates)
│   └── v3/
│       ├── base.html
│       ├── index.html
│       └── partials/
│           ├── display.html
│           ├── durations.html
│           ├── fonts.html
│           ├── general.html
│           ├── logs.html
│           ├── overview.html
│           ├── plugins.html
│           ├── raw_json.html
│           └── sports.html
└── static/                   # CSS/JS assets (was: /static)
    └── v3/
        ├── app.css
        └── app.js
```

### Legacy Web Interface (V1/V2 - For Reference)
```
old_web_interface/
├── README.md                 # Explains this is legacy code
├── web_interface.py          # V1 implementation
├── web_interface_v2.py       # V2 implementation
├── start_web_v2.py          # V2 startup script
├── start_web_conditionally.py  # Old conditional starter
├── run_web_v2.sh            # V2 shell runner
├── requirements_web_v2.txt  # V2 dependencies
└── templates/
    ├── index.html           # V1 template
    └── index_v2.html        # V2 template
```

### Root Level Files (Updated)
- `start_web_conditionally.py` - Updated to launch new web_interface/start.py
- `ledmatrix-web.service` - Systemd service (already points to start_web_conditionally.py)
- `install_web_service.sh` - Service installer (no changes needed)

## What Changed

### File Movements
1. **Blueprints**: `/blueprints/` → `/web_interface/blueprints/`
2. **Templates**: `/templates/v3/` → `/web_interface/templates/v3/`
3. **Static files**: `/static/v3/` → `/web_interface/static/v3/`
4. **Main app**: `/web_interface_v3.py` → `/web_interface/app.py`
5. **Legacy files**: Various → `/old_web_interface/`

### Code Updates
1. **web_interface/app.py**:
   - Added parent directory to Python path for imports
   - Updated plugins_dir to be relative to project root
   - Updated blueprint imports to use `web_interface.blueprints.*`

2. **start_web_conditionally.py**:
   - Updated to point to `web_interface/start.py`
   - Updated requirements path to `web_interface/requirements.txt`

3. **New files created**:
   - `web_interface/__init__.py` - Package initialization
   - `web_interface/start.py` - Clean startup script
   - `web_interface/run.sh` - Shell runner
   - `web_interface/README.md` - Documentation
   - `old_web_interface/README.md` - Legacy code explanation

## Running the Web Interface

### Development
```bash
# From project root:
python3 web_interface/start.py

# Or using the shell script:
./web_interface/run.sh
```

### Production (Systemd Service)
The existing systemd service will work without changes:
```bash
sudo systemctl start ledmatrix-web
sudo systemctl enable ledmatrix-web
```

The service uses `start_web_conditionally.py` which has been updated to launch the new V3 interface.

## Benefits

1. ✅ **Better Organization**: All web-related code in one directory
2. ✅ **Cleaner Project Root**: Removed scattered web files from root
3. ✅ **Clear Separation**: Active code vs legacy code
4. ✅ **Easier Maintenance**: Related files grouped together
5. ✅ **Future-Ready**: Easy to remove legacy code when no longer needed
6. ✅ **Better Documentation**: README files explain structure and usage

## Migration Path for Development

If you have any local scripts or shortcuts that reference the old paths:

### Old paths → New paths
- `web_interface_v3.py` → `web_interface/app.py`
- `requirements_web_v2.txt` → `web_interface/requirements.txt`
- `templates/v3/` → `web_interface/templates/v3/`
- `static/v3/` → `web_interface/static/v3/`
- `blueprints/` → `web_interface/blueprints/`

## Next Steps

1. ✅ Test the web interface to ensure it works correctly
2. ✅ Update any documentation that references old file paths
3. ⏳ Eventually remove `old_web_interface/` when no longer needed for reference

## Rollback Plan

If you need to rollback:
1. All files are tracked in git
2. Use `git status` to see changes
3. Run `git checkout .` to restore original structure (will lose new organization)
4. Or cherry-pick files from `old_web_interface/` back to root

## Testing Checklist

- [ ] Web interface starts successfully
- [ ] All pages load correctly
- [ ] API endpoints work
- [ ] Static files (CSS/JS) load
- [ ] Templates render properly
- [ ] Systemd service starts correctly
- [ ] Plugin management works
- [ ] Configuration saves properly

## Troubleshooting

If you encounter issues after reorganization:

### No Logging / Service Not Starting

**Important:** The service logs to **syslog**, not stdout. View logs with:
```bash
sudo journalctl -u ledmatrix-web -n 50 --no-pager
```

### Quick Diagnostic

Run the diagnostic script on your Raspberry Pi:
```bash
cd ~/LEDMatrix
bash scripts/diagnose_web_interface.sh
```

This will check:
- Service status
- Configuration settings
- File structure
- Python imports
- Network ports
- Recent logs

### Full Troubleshooting Guide

See `docs/WEB_INTERFACE_TROUBLESHOOTING.md` for comprehensive troubleshooting steps including:
- Common issues and solutions
- Manual testing procedures
- Import error diagnosis
- Service configuration verification
- Recovery procedures

### Common Quick Fixes

1. **Service not running:** `sudo systemctl start ledmatrix-web`
2. **Check logs:** `sudo journalctl -u ledmatrix-web -f`
3. **Test manual start:** `python3 web_interface/start.py`
4. **Enable autostart:** Set `"web_display_autostart": true` in `config/config.json`

---

*Date: October 14, 2025*
*Branch: plugins*

