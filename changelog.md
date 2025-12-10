# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2024-12-10

### Changed
- **Complete rewrite to support Arlec (Tuya-based) smart plugs** instead of TP-Link Tapo
- Replaced `tapo.py` module with new `arlec.py` module using the `tinytuya` library
- Updated settings to require Device ID and Local Key instead of username/password
- Added Protocol Version selector (supports 3.1, 3.2, 3.3, 3.4, 3.5)
- Updated settings template with helpful instructions for obtaining device credentials
- Changed dependency from `pycryptodome` to `tinytuya>=1.12.0`

### Added
- Support for Arlec PC191BKHA Series 2 smart plugs
- Support for other Tuya-based smart plugs
- Detailed README with setup instructions
- Troubleshooting guide

### Removed
- TP-Link Tapo protocol support (old protocol in `tapo.py`)
- `pycryptodome` dependency (no longer needed)

## Previous Versions

### [0.4.0] - Original Tapo Version
- Original TP-Link Tapo smart plug support by Dennis Schwerdel
- Supported P100, P110, and other Tapo devices

