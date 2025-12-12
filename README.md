# OctoPrint PSU Control - Smart Outlet

Adds WiFi Smart Outlet support to OctoPrint-PSUControl as a sub-plugin.

## Supported Devices

This plugin works with various Tuya-based smart outlets including:
- **Arlec PC191HA Series 2** (Australian, BK7231N/BK7231T chip)
- **Shenzhen SM-PW701A1**
- Other Tuya-based smart plugs

It supports two control methods:

| Protocol | Firmware | Reliability | Cloud Dependency | Setup Difficulty |
|----------|----------|-------------|------------------|------------------|
| **Tasmota** (Recommended) | Custom | ⭐⭐⭐⭐⭐ Excellent | None - 100% local | Medium (requires flashing) |
| **Tuya** | Stock | ⭐⭐⭐ Fair | Partial - may drop connection | Easy |

## Why Tasmota?

If you've experienced connection drops with Tuya-based smart plugs, **flashing Tasmota firmware is the solution**. Tasmota provides:

- ✅ **100% local control** - no cloud dependency
- ✅ **Rock-solid reliability** - no random disconnections
- ✅ **Fast response** - direct HTTP API
- ✅ **No account required** - no Tuya developer account needed
- ✅ **Privacy** - no data sent to the cloud

## Requirements

- OctoPrint
- [PSU Control plugin](https://github.com/kantlivelong/OctoPrint-PSUControl)
- A Shenzhen SM-PW701A1 smart outlet (or compatible device)

## Installation

### From OctoPrint Plugin Manager
1. Open OctoPrint Settings
2. Go to Plugin Manager
3. Click "Get More"
4. Install from URL:
```
https://github.com/your-github-username/OctoPrint-PSU-Control-Shenzhen/archive/refs/heads/main.zip
```

### Manual Installation
```bash
pip install https://github.com/your-github-username/OctoPrint-PSU-Control-Shenzhen/archive/refs/heads/main.zip
```

---

## Option 1: Custom Firmware Setup (Recommended)

### Arlec PC191HA Series 2 - OpenBeken Flash Guide

The PC191HA Series 2 uses a **BK7231N** or **BK7231T** chip, so it needs **OpenBeken** (not Tasmota). Don't worry - OpenBeken uses the same HTTP API, so this plugin works perfectly with it!

#### Step 1: Flash OpenBeken using Cloudcutter (No Soldering!)

1. **Requirements:**
   - A Raspberry Pi (any model with WiFi) or Linux laptop
   - Your PC191HA in pairing mode (hold button until it blinks fast)

2. **On your Raspberry Pi/Linux machine:**
   ```bash
   # Clone Cloudcutter
   git clone https://github.com/tuya-cloudcutter/tuya-cloudcutter
   cd tuya-cloudcutter
   
   # Run the exploit (requires sudo for WiFi control)
   sudo ./tuya-cloudcutter.sh
   ```

3. **Follow the prompts:**
   - Select **"Flash 3rd party firmware"**
   - For firmware version, try **"1.1.8 – BK7231N / oem_bk7231n_plug"**
   - For device, select **"Tuya Generic → LSPA9 Plug v1.1.8"** or similar
   - Choose **OpenBeken** as the firmware to flash

4. **During the process:**
   - Cloudcutter will show the chip family (BK7231N or BK7231T)
   - If it doesn't match, cancel and try a different profile
   - The plug will reboot with OpenBeken installed!

> **Note:** Firmware versions up to v1.3.5 work with Cloudcutter. If yours is newer, you may need serial flashing.

#### Step 2: Configure OpenBeken

1. **Connect to OpenBeken WiFi:**
   - After flashing, the plug creates a WiFi hotspot called `OpenBK7231N_XXXX`
   - Connect to it and go to `http://192.168.4.1`
   - Configure your home WiFi credentials

2. **Configure GPIOs for PC191HA Series 2:**
   - Go to `http://YOUR_PLUG_IP` in a browser
   - Navigate to **Config → Configure Module**
   - Set the following GPIO configuration:
   
   | GPIO | Function |
   |------|----------|
   | GPIO6 | BL0937SEL |
   | GPIO7 | BL0937CF1 |
   | GPIO8 | BL0937CF |
   | GPIO10 | Button |
   | GPIO24 | Relay |
   | GPIO26 | WiFi LED |

3. **Enable Power Saving (recommended):**
   - Go to **Config → Console**
   - Enter: `PowerSave 1`

4. **Set Static IP:**
   - In your router, assign a static IP to the plug
   - This prevents connection issues if the IP changes

5. **Test it:**
   - Visit `http://YOUR_PLUG_IP` - you should see the OpenBeken web interface
   - Click the toggle to turn the relay on/off

---

### Other Devices (ESP8266-based) - Tasmota Flash Guide

For ESP8266-based plugs (like SM-PW701A1), you can flash Tasmota:

#### Method A: Tuya Cloudcutter (No Hardware Required)

1. **Requirements:**
   - A Raspberry Pi or Linux computer with WiFi
   - Your smart plug in pairing mode

2. **Instructions:**
   - Visit [Tuya Cloudcutter](https://github.com/tuya-cloudcutter/tuya-cloudcutter)
   - Follow the step-by-step guide
   - Select your device profile (or generic profile)
   - Flash Tasmota-lite or full Tasmota

#### Method B: Serial Flashing (Hardware Required)

If Cloudcutter doesn't work:
1. Open the smart plug (be careful - mains voltage!)
2. Connect a USB-to-Serial adapter to the chip
3. Flash using appropriate tool for your chip

### Step 3: Configure the Plugin

1. Open OctoPrint Settings
2. Go to "PSU Control - Shenzhen"
3. Select **Protocol: Tasmota**
4. Enter the **IP Address** of your plug
5. Leave username/password blank unless you've set up Tasmota authentication

### Step 4: Configure PSU Control

1. Go to OctoPrint Settings → PSU Control
2. Set **Switching Method** to "Plugin: PSU Control - Shenzhen"
3. Set **Sensing Method** to "Plugin: PSU Control - Shenzhen"
4. Save settings

---

## Option 2: Tuya Setup (Stock Firmware)

If you prefer to use the stock firmware (not recommended due to reliability issues):

### Step 1: Get Your Device Credentials

To control your Tuya smart plug locally, you need the **Device ID** and **Local Key**.

#### Using tinytuya Wizard (Recommended)

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

4. Look for your plug in the output and note the:
   - **Device ID** (e.g., `bf123456789abcdef`)
   - **Local Key** (16-character string)
   - **IP Address**

### Step 2: Set Static IP Address

1. Log into your router's admin panel
2. Find DHCP settings or address reservation
3. Reserve an IP for your smart plug's MAC address

### Step 3: Configure the Plugin

1. Open OctoPrint Settings
2. Go to "PSU Control - Shenzhen"
3. Select **Protocol: Tuya**
4. Enter:
   - **IP Address**: Your smart plug's IP
   - **Device ID**: From Step 1
   - **Local Key**: From Step 1
   - **Protocol Version**: Start with `3.3`, try `3.4` or `3.5` if it doesn't work

### Step 4: Configure PSU Control

1. Go to OctoPrint Settings → PSU Control
2. Set **Switching Method** to "Plugin: PSU Control - Shenzhen"
3. Set **Sensing Method** to "Plugin: PSU Control - Shenzhen"
4. Save settings

---

## Troubleshooting

### Tasmota Issues

#### "Cannot connect to Tasmota device"
- Verify the IP address is correct
- Check if you can access `http://YOUR_IP` in a browser
- Ensure OctoPrint and the plug are on the same network/VLAN

#### Plug not responding to commands
- Check if the correct template is applied in Tasmota
- Verify GPIO configuration matches your device

### Tuya Issues

#### "Device error: -1" or connection drops
- **This is why we recommend Tasmota!**
- Try a different protocol version (3.3, 3.4, or 3.5)
- The device may be trying to connect to Tuya cloud

#### "Failed to authenticate"
- Double-check the Local Key is correct
- The Local Key changes if you re-pair the device with the app
- Re-run the tinytuya wizard to get the new key

#### Finding your device IP
```bash
python -m tinytuya scan
```

---

## Device Specifications

**Shenzhen SM-PW701A1:**
- Input: 100-240V AC, 50/60Hz
- Max Load: 10A
- Wireless: 2.4GHz WiFi
- Chip: Usually ESP8266-based (Tuya module)

---

## How It Works

### Tasmota Mode
The plugin sends HTTP commands directly to the Tasmota web API:
- `http://IP/cm?cmnd=Power%20ON` - Turn on
- `http://IP/cm?cmnd=Power%20OFF` - Turn off
- `http://IP/cm?cmnd=Power` - Get status

### Tuya Mode
The plugin uses the [tinytuya](https://github.com/jasonacox/tinytuya) library to communicate locally over your network using the Tuya protocol. This mode includes enhanced retry logic to handle connection drops.

---

## Credits

- Original Tapo plugin by Dennis Schwerdel
- Modified for Shenzhen SM-PW701A1 support
- Uses [tinytuya](https://github.com/jasonacox/tinytuya) by Jason Cox

## License

GNU Affero General Public License v3.0 (AGPLv3)

## Support

For help, visit the [OctoPrint Community Forums](https://community.octoprint.org)
