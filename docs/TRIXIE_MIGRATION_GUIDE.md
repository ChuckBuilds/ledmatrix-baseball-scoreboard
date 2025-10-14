# Raspbian OS 13 Trixie Migration Guide

## Overview

This guide provides step-by-step instructions for migrating your existing LEDMatrix installation to Raspbian OS 13 "Trixie" or setting up a fresh installation on Trixie.

## Table of Contents

1. [Pre-Migration Checklist](#pre-migration-checklist)
2. [Fresh Installation on Trixie](#fresh-installation-on-trixie)
3. [Upgrading from Bookworm to Trixie](#upgrading-from-bookworm-to-trixie)
4. [Post-Migration Verification](#post-migration-verification)
5. [Troubleshooting](#troubleshooting)
6. [Rollback Procedure](#rollback-procedure)

## Pre-Migration Checklist

Before starting the migration, ensure you have:

- [ ] **Backup of configuration files**
- [ ] **Backup of custom scripts or modifications**
- [ ] **List of enabled managers and settings**
- [ ] **Access to physical Raspberry Pi** (in case of issues)
- [ ] **Stable internet connection**
- [ ] **At least 2GB free disk space**
- [ ] **Tested backup restoration procedure**

### Creating a Backup

```bash
# Stop services
sudo systemctl stop ledmatrix.service
sudo systemctl stop ledmatrix-web.service

# Create backup directory
BACKUP_DIR=~/ledmatrix-backup-$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

# Backup configuration files
cd ~/Github/LEDMatrix
cp -r config/ "$BACKUP_DIR/"
cp -r cache/ "$BACKUP_DIR/" 2>/dev/null || true

# Backup custom modifications (if any)
# Add any custom files or directories you've modified

# Create tarball
cd ~
tar -czf ledmatrix-backup-$(date +%Y%m%d_%H%M%S).tar.gz ledmatrix-backup-*

echo "Backup created: $(ls -1t ~/ledmatrix-backup-*.tar.gz | head -1)"
```

## Fresh Installation on Trixie

### Prerequisites

1. **Download Raspberry Pi OS 13 (Trixie)**
   - Visit [raspberrypi.com/software](https://www.raspberrypi.com/software/)
   - Download Raspberry Pi OS (64-bit) based on Debian 13
   - Flash to SD card using Raspberry Pi Imager

2. **Initial Pi Setup**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Enable SSH if not already enabled
   sudo systemctl enable ssh
   sudo systemctl start ssh
   
   # Set timezone
   sudo timedatectl set-timezone America/Chicago  # Adjust to your timezone
   ```

### Compatibility Check

Before installation, run the compatibility checker:

```bash
cd ~/Github/LEDMatrix
./scripts/check_system_compatibility.sh
```

Review the output and address any critical issues before proceeding.

### Installation Steps

1. **Clone the repository**
   ```bash
   cd ~/Github
   git clone https://github.com/yourusername/LEDMatrix.git
   cd LEDMatrix
   ```

2. **Checkout the latest branch** (if needed)
   ```bash
   git checkout plugins  # Or your desired branch
   ```

3. **Run the installation script**
   ```bash
   sudo ./first_time_install.sh
   ```

4. **Configure your settings**
   ```bash
   # Edit main configuration
   nano config/config.json
   
   # Edit secrets (API keys, etc.)
   nano config/config_secrets.json
   ```

5. **Start services**
   ```bash
   sudo systemctl start ledmatrix.service
   sudo systemctl start ledmatrix-web.service
   ```

6. **Enable services for auto-start**
   ```bash
   sudo systemctl enable ledmatrix.service
   sudo systemctl enable ledmatrix-web.service
   ```

## Upgrading from Bookworm to Trixie

### Important Notes

- **In-place upgrade is supported** but fresh installation is recommended for critical systems
- **Backup before proceeding** - this is crucial
- **Expect 30-60 minutes** for the upgrade process
- **Physical access recommended** in case of issues

### Step 1: Prepare System

```bash
# Update package lists
sudo apt update

# Upgrade current packages
sudo apt upgrade -y
sudo apt full-upgrade -y

# Clean up old packages
sudo apt autoremove -y
sudo apt autoclean

# Ensure enough free space
df -h /

# Reboot to ensure running latest Bookworm kernel
sudo reboot
```

### Step 2: Stop LEDMatrix Services

```bash
# Stop services to prevent conflicts during upgrade
sudo systemctl stop ledmatrix.service
sudo systemctl stop ledmatrix-web.service

# Verify services stopped
sudo systemctl status ledmatrix.service
sudo systemctl status ledmatrix-web.service
```

### Step 3: Update APT Sources

```bash
# Backup current sources
sudo cp /etc/apt/sources.list /etc/apt/sources.list.bookworm.backup

# Update to Trixie repositories
sudo sed -i 's/bookworm/trixie/g' /etc/apt/sources.list

# Also update sources.list.d if present
if [ -d /etc/apt/sources.list.d ]; then
    sudo sed -i 's/bookworm/trixie/g' /etc/apt/sources.list.d/*.list
fi

# Verify changes
cat /etc/apt/sources.list | grep trixie
```

### Step 4: Perform Distribution Upgrade

```bash
# Update package lists with new sources
sudo apt update

# Perform the distribution upgrade
# This may take 30-60 minutes depending on your system
sudo apt dist-upgrade -y

# Answer any prompts:
# - Keep existing configuration files when asked
# - Note any services that need restart
```

### Step 5: Update LEDMatrix Dependencies

```bash
cd ~/Github/LEDMatrix

# Pull latest updates (contains Trixie-compatible requirements)
git fetch origin
git pull origin plugins  # Or your branch

# Reinstall Python packages with updated versions
python3 -m pip install --break-system-packages --upgrade -r requirements.txt
python3 -m pip install --break-system-packages --upgrade -r requirements_web_v2.txt

# Rebuild rpi-rgb-led-matrix for new kernel
cd rpi-rgb-led-matrix-master
make clean
make build-python PYTHON=$(which python3)
cd bindings/python
python3 -m pip install --break-system-packages --force-reinstall .
cd ~/Github/LEDMatrix
```

### Step 6: Update System Configuration

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Ensure boot configuration is correct
# Check if isolcpus is still set
if [ -f /boot/firmware/cmdline.txt ]; then
    grep isolcpus /boot/firmware/cmdline.txt
elif [ -f /boot/cmdline.txt ]; then
    grep isolcpus /boot/cmdline.txt
fi

# Verify audio is disabled
if [ -f /boot/firmware/config.txt ]; then
    grep "dtparam=audio=off" /boot/firmware/config.txt
elif [ -f /boot/config.txt ]; then
    grep "dtparam=audio=off" /boot/config.txt
fi
```

### Step 7: Reboot and Verify

```bash
# Reboot to complete upgrade
sudo reboot
```

After reboot:

```bash
# Verify OS version
cat /etc/os-release | grep VERSION_ID

# Should show: VERSION_ID="13"

# Verify kernel version
uname -r

# Should show 6.12.x or higher

# Verify Python version
python3 --version

# Should show Python 3.11.x or 3.12.x

# Start services
sudo systemctl start ledmatrix.service
sudo systemctl start ledmatrix-web.service

# Check service status
sudo systemctl status ledmatrix.service
sudo systemctl status ledmatrix-web.service
```

## Post-Migration Verification

### System Health Check

Run the comprehensive compatibility checker:

```bash
cd ~/Github/LEDMatrix
./scripts/check_system_compatibility.sh
```

### Service Status Verification

```bash
# Check if services are running
systemctl is-active ledmatrix.service
systemctl is-active ledmatrix-web.service

# View recent logs
journalctl -u ledmatrix.service -n 50 --no-pager
journalctl -u ledmatrix-web.service -n 50 --no-pager

# Look for any error messages or warnings
```

### Functionality Tests

1. **Web Interface Test**
   ```bash
   # Access web interface
   # Open browser to: http://your-pi-ip:5001
   
   # Verify you can:
   # - View dashboard
   # - See logs
   # - Enable/disable managers
   # - Save configuration
   ```

2. **Display Test**
   ```bash
   # Check if LED matrix is displaying correctly
   # Verify:
   # - No flickering
   # - Correct colors
   # - Smooth animations
   # - Text rendering quality
   ```

3. **Manager Tests**
   ```bash
   # Test a few managers to ensure data fetching works
   # Check logs for successful API calls:
   journalctl -u ledmatrix.service -n 100 --no-pager | grep -i "nhl\|nba\|weather"
   ```

### Performance Verification

```bash
# Check CPU usage
top -bn1 | grep python3

# Check memory usage
free -h

# Check temperature
vcgencmd measure_temp

# Check for CPU throttling
vcgencmd get_throttled
# Should return: throttled=0x0 (no throttling)
```

## Troubleshooting

### Services Won't Start

**Symptom**: Services fail to start after upgrade

**Solution**:
```bash
# Check service status for errors
sudo systemctl status ledmatrix.service -l

# Check for Python import errors
python3 -c "from rgbmatrix import RGBMatrix, RGBMatrixOptions"

# If rgbmatrix import fails, rebuild:
cd ~/Github/LEDMatrix/rpi-rgb-led-matrix-master
make clean
make build-python PYTHON=$(which python3)
cd bindings/python
sudo python3 -m pip install --break-system-packages --force-reinstall .
```

### Missing Python Packages

**Symptom**: ImportError or ModuleNotFoundError

**Solution**:
```bash
# Reinstall all requirements
cd ~/Github/LEDMatrix
python3 -m pip install --break-system-packages --upgrade --force-reinstall -r requirements.txt
python3 -m pip install --break-system-packages --upgrade --force-reinstall -r requirements_web_v2.txt
```

### Display Flickering or Timing Issues

**Symptom**: LED matrix has flickering or poor image quality

**Solution**:
```bash
# Verify isolcpus is set
cat /boot/firmware/cmdline.txt | grep isolcpus

# Verify audio is disabled
cat /boot/firmware/config.txt | grep audio

# If not set, run first_time_install.sh again:
cd ~/Github/LEDMatrix
sudo ./first_time_install.sh

# Then reboot
sudo reboot
```

### Permission Errors

**Symptom**: Permission denied errors in logs

**Solution**:
```bash
cd ~/Github/LEDMatrix

# Fix cache permissions
sudo bash scripts/fix_perms/fix_cache_permissions.sh

# Fix assets permissions
sudo bash scripts/fix_perms/fix_assets_permissions.sh

# Fix web permissions
sudo bash scripts/fix_perms/fix_web_permissions.sh

# Restart services
sudo systemctl restart ledmatrix.service
sudo systemctl restart ledmatrix-web.service
```

### Web Interface Not Accessible

**Symptom**: Cannot access web interface at port 5001

**Solution**:
```bash
# Check if web service is running
sudo systemctl status ledmatrix-web.service

# Check if port 5001 is listening
sudo netstat -tuln | grep 5001

# Check firewall (if enabled)
sudo ufw status

# Restart web service
sudo systemctl restart ledmatrix-web.service

# View web service logs
journalctl -u ledmatrix-web.service -n 50 --no-pager
```

### Eventlet Compatibility Issues

**Symptom**: Eventlet errors in web service logs

**Solution**:
```bash
# Upgrade eventlet to latest version
python3 -m pip install --break-system-packages --upgrade 'eventlet>=0.35.0'

# If issues persist, consider switching to gevent:
# Edit requirements_web_v2.txt and replace eventlet with:
# gevent>=23.9.0,<24.0.0
# gevent-websocket>=0.10.1,<1.0.0

# Then reinstall:
python3 -m pip install --break-system-packages -r requirements_web_v2.txt
```

## Rollback Procedure

If the upgrade causes critical issues, you can rollback to Bookworm:

### Option 1: Restore from Backup (Recommended)

1. **Reflash SD card** with Raspberry Pi OS 12 (Bookworm)
2. **Restore backup**:
   ```bash
   cd ~
   tar -xzf ledmatrix-backup-YYYYMMDD_HHMMSS.tar.gz
   cd ~/Github/LEDMatrix
   cp -r ~/ledmatrix-backup-*/config/ .
   cp -r ~/ledmatrix-backup-*/cache/ . 2>/dev/null || true
   ```
3. **Run installation**:
   ```bash
   sudo ./first_time_install.sh
   ```

### Option 2: Downgrade APT Sources (Not Recommended)

```bash
# Stop services
sudo systemctl stop ledmatrix.service
sudo systemctl stop ledmatrix-web.service

# Restore old sources
sudo cp /etc/apt/sources.list.bookworm.backup /etc/apt/sources.list

# Downgrade packages (risky)
sudo apt update
sudo apt dist-upgrade -y --allow-downgrades

# Reboot
sudo reboot
```

**Note**: Option 2 is not recommended and may cause system instability. Fresh installation is preferred.

## Additional Resources

- [Raspbian Trixie Compatibility Analysis](RASPBIAN_TRIXIE_COMPATIBILITY_ANALYSIS.md)
- [LEDMatrix Documentation](https://github.com/yourusername/LEDMatrix/wiki)
- [Raspberry Pi OS Documentation](https://www.raspberrypi.com/documentation/computers/os.html)
- [Debian 13 Release Notes](https://www.debian.org/releases/trixie/)

## Getting Help

If you encounter issues not covered in this guide:

1. **Check logs**: `journalctl -u ledmatrix.service -n 100`
2. **Run compatibility checker**: `./scripts/check_system_compatibility.sh`
3. **Search existing issues**: [GitHub Issues](https://github.com/yourusername/LEDMatrix/issues)
4. **Create new issue**: Include:
   - Output of compatibility checker
   - Service logs
   - Steps to reproduce
   - System information (OS version, Python version, Pi model)

## Changelog

- **2025-10-14**: Initial migration guide created for Trixie release
- Added compatibility checker script
- Updated requirements files with Trixie-compatible versions

---

**Document Version**: 1.0  
**Last Updated**: October 14, 2025  
**Compatible with**: Raspbian OS 12 (Bookworm) → Raspbian OS 13 (Trixie)

