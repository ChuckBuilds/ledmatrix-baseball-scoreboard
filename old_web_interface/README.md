# Old Web Interface (V1 & V2)

⚠️ **LEGACY CODE - FOR REFERENCE ONLY**

This directory contains the old V1 and V2 web interface implementations. These are kept for reference purposes and may be removed in a future cleanup.

## Contents

- `web_interface.py` - Original V1 web interface
- `web_interface_v2.py` - V2 web interface implementation
- `start_web_v2.py` - V2 startup script
- `start_web_conditionally.py` - Old conditional starter (superseded by root version)
- `run_web_v2.sh` - V2 shell runner
- `requirements_web_v2.txt` - V2 dependencies
- `templates/` - Old HTML templates
  - `index.html` - V1 template
  - `index_v2.html` - V2 template

## Why Keep This?

These files are retained temporarily to:
1. Reference old functionality while developing V3
2. Compare implementation approaches
3. Ensure no features were lost during migration
4. Help with troubleshooting if issues arise

## Current Status

**DO NOT USE THESE FILES FOR PRODUCTION**

The active web interface is now in `web_interface/` directory.

## Migration Notes

The V3 interface includes all features from V1 and V2, plus:
- Modern UI with better UX
- Plugin system support
- Real-time SSE streams
- Better organization and maintainability
- RESTful API design

## Removal Plan

This directory will be removed once:
1. V3 interface is fully tested and stable
2. All V1/V2 features are confirmed working in V3
3. No references remain in active code
4. Team confirms no need for legacy code

**Target for removal: TBD**

## If You Need to Reference This Code

When looking at these files, remember:
- They may have outdated dependencies
- Security issues may exist
- Better patterns exist in V3
- Don't copy-paste without reviewing for improvements

