# OctoPrint PSU Control - Tuya

Adds Tuya-based Smart Plug support to OctoPrint-PSUControl as a sub-plugin.

## Supported Devices

This plugin works with Tuya-based smart plugs, including:
- **Arlec PC191BKHA Series 2** (230-240V, 50Hz, Max 10A 2400W)
- Other Tuya-based smart plugs with similar functionality

## Requirements

- OctoPrint
- [PSU Control plugin](https://github.com/kantlivelong/OctoPrint-PSUControl)
- A Tuya-based smart plug (like the Arlec PC191BKHA)
- Device credentials (Device ID and Local Key)

## Installation

### From OctoPrint Plugin Manager
1. Open OctoPrint Settings
2. Go to Plugin Manager
3. Click "Get More"
4. Search for "PSU Control - Tuya" or install from URL:
   ```
[   https://github.com/wafflexyzz/OctoPrint-PSU-Control-Tuya/archive/main.zip
](https://github.com/wafflexyzz/OctoPrint-PSU-Control-Tuya/archive/refs/heads/main.zip)   ```

### Manual Installation
```bash
pip install [https://github.com/wafflexyzz/OctoPrint-PSU-Control-Tuya/archive/main.zip](https://github.com/wafflexyzz/OctoPrint-PSU-Control-Tuya/archive/refs/heads/main.zip)
```

## Configuration

### Step 1: Get Your Device Credentials

To control your Tuya smart plug locally, you need the **Device ID** and **Local Key**. There are two methods:

#### Method 1: Using tinytuya Wizard (Recommended)

1. Install tinytuya on a computer with Python:
   ```bash
   pip install tinytuya
   ```

2. Run the setup wizard:
   ```bash
   python -m tinytuya wizard
   ```

3. Follow the prompts:
   - Create a Tuya Developer account at https://developer.tuya.com/
   - Create a Cloud Project
   - Link your Smart Life / Tuya Smart app account
   - The wizard will retrieve all your device credentials

4. Look for your Tuya plug in the output and note the:
   - **Device ID** (e.g., `bf123456789abcdef`)
   - **Local Key** (16-character string)
   - **IP Address**

#### Method 2: Tuya Developer Portal (Manual)

1. Go to https://developer.tuya.com/ and create an account
2. Create a Cloud Project
3. Subscribe to the "Smart Home" API
4. Link your Smart Life / Tuya Smart app account to the project
5. Add your device to the project
6. Find the Device ID and Local Key in the device details

### Step 2: Set Static IP Address

It's recommended to assign a static IP to your smart plug:
1. Log into your router's admin panel
2. Find DHCP settings or address reservation
3. Reserve an IP for your smart plug's MAC address

### Step 3: Configure the Plugin

1. Open OctoPrint Settings
2. Go to "PSU Control - Tuya"
3. Enter:
   - **IP Address**: Your smart plug's IP (e.g., `192.168.1.100`)
   - **Device ID**: From Step 1
   - **Local Key**: From Step 1
   - **Protocol Version**: Start with `3.3`, try `3.4` or `3.5` if it doesn't work

### Step 4: Configure PSU Control

1. Go to OctoPrint Settings → PSU Control
2. Set **Switching Method** to "Plugin: PSU Control - Tuya"
3. Set **Sensing Method** to "Plugin: PSU Control - Tuya"
4. Save settings

## Troubleshooting

### "Error connecting to device"
- Verify the IP address is correct
- Check if the device is online (should be controllable via Smart Life app)
- Ensure OctoPrint and the plug are on the same network

### "Device error: -1"
- Try a different protocol version (3.3, 3.4, or 3.5)
- Some newer devices use version 3.4 or 3.5

### "Failed to authenticate"
- Double-check the Local Key is correct
- The Local Key may change if you re-pair the device with the app

### Device not responding
- Check if your firewall allows UDP port 6668 and TCP port 6668
- Try rebooting the smart plug by unplugging it for 10 seconds

### Finding your device IP
You can use tinytuya to scan your network:
```bash
python -m tinytuya scan
```

## Device Specifications (Arlec PC191BKHA Series 2)

- **Input**: 230-240V AC, 50Hz
- **Max Load**: 10A, 2400W
- **Wireless**: 2.4GHz Wi-Fi, BLE
- **Protocol**: Tuya-based

## How It Works

This plugin uses the [tinytuya](https://github.com/jasonacox/tinytuya) library to communicate with your smart plug locally over your network. No cloud connection is required once you have the device credentials.

## Credits

- Original Tapo plugin by Dennis Schwerdel
- Modified for Tuya support
- Uses [tinytuya](https://github.com/jasonacox/tinytuya) by Jason Cox

## License

GNU Affero General Public License v3.0 (AGPLv3)

## Support

For help, visit the [OctoPrint Community Forums](https://community.octoprint.org)
