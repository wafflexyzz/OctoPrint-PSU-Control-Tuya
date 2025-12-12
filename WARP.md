# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview
This is an **OctoPrint sub-plugin** that adds Tuya-based smart plug support to the [OctoPrint-PSUControl plugin](https://github.com/kantlivelong/OctoPrint-PSUControl). It enables OctoPrint to control 3D printer power supplies via Arlec PC191BKHA and other Tuya-compatible smart plugs using local network control (no cloud dependency).

**Key Point**: Despite being rewritten for Tuya devices, the plugin identifier remains `psucontrol_tapo` for backwards compatibility with existing user settings. The package name is `octoprint_psucontrol_tapo`.

## Architecture

### Plugin Registration Flow
1. OctoPrint loads the plugin via entry point `psucontrol_tapo` → `octoprint_psucontrol_tapo`
2. `__init__.py::on_startup()` registers with PSUControl using the helper interface
3. PSUControl calls `turn_psu_on()`, `turn_psu_off()`, and `get_psu_state()` methods
4. These methods delegate to the `ArlecSmartPlug` class which wraps tinytuya

### Module Structure
```
octoprint_psucontrol_tapo/
  __init__.py         - PSUControl_Arlec plugin class implementing OctoPrint plugin mixins
                        (StartupPlugin, RestartNeedingPlugin, TemplatePlugin, SettingsPlugin)
  arlec.py            - ArlecSmartPlug device control class using tinytuya library
  templates/
    psucontrol_tapo_settings.jinja2  - Settings UI template
```

### Device Communication
- Uses **tinytuya** library for local Tuya protocol communication (UDP/TCP port 6668)
- Protocol versions: 3.1, 3.2, 3.3, 3.4, 3.5 (default 3.3)
- DPS (Data Point) mapping: DPS "1" = switch on/off state
- Connection is lazy-initialized and reconnected on errors
- Socket timeout: 5 seconds
- State caching: `last_status` is cached and refreshed asynchronously to avoid blocking

## Development Commands

### Installation (Development)
```bash
# Install in development mode
pip install -e .

# Or install from repository
pip install https://github.com/wafflexyzz/OctoPrint-PSU-Control-Tuya/archive/refs/heads/main.zip
```

### Testing Device Communication
```bash
# Scan network for Tuya devices
python -m tinytuya scan

# Run tinytuya wizard to get device credentials
python -m tinytuya wizard
```

### Python Environment
- Requires Python 3.7+
- Dependencies: `OctoPrint`, `tinytuya>=1.12.0`

## Security Considerations
**Never commit Tuya credentials**. The following files are git-ignored:
- `devices.json`, `snapshot.json`, `tinytuya.json`, `tuya-raw.json`, `*.keys`

Device credentials (Device ID, Local Key) are stored in OctoPrint's config.yaml and should be obtained via:
1. `python -m tinytuya wizard` (recommended)
2. Tuya Developer Portal (manual)

## Settings Migration Note
Settings version is currently 1. The `on_settings_migrate()` method is a no-op placeholder for future schema changes.

## Common Issues During Development

### Plugin Not Appearing in PSUControl
- Verify PSU Control plugin supports `register_plugin` helper (check OctoPrint logs)
- Check that `on_startup()` is called and registration succeeds

### Device Connection Failures
- Device must be on same network as OctoPrint
- Verify Device ID, Local Key, and IP address are correct
- Try different protocol versions (3.3, 3.4, 3.5) - newer devices often use 3.4/3.5
- Check firewall allows UDP/TCP port 6668

### State Synchronization
- `get_psu_state()` uses cached `last_status` and refreshes asynchronously
- If state appears stale, the device connection may have failed (check logs)
- Device reconnection is automatic on errors but logs exceptions

## Code Patterns

### Reconnection Pattern
Device connections are lazy and auto-reconnect on failures:
```python
if not self.device:
    self._reconnect()
```

### Error Handling
All device operations catch exceptions, log them, clear `self.device`, and re-raise to notify PSUControl of failures.

### Logging
Use `self._logger` in plugin code and module-level `log` in `arlec.py`. The plugin sets `arlec.log = self._logger` during initialization.
