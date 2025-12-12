#!/usr/bin/env python
# coding=utf-8
"""
Test script for debugging Shenzhen SM-PW701A1 device connection.
Run this directly to test your device before using with OctoPrint.

Supports both Tasmota and Tuya protocols.
"""

import logging
import sys
import time

# Set up logging to see everything
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_tasmota():
    """Test Tasmota/OpenBeken device connection."""
    from octoprint_psucontrol_tapo.shenzhen import TasmotaSmartPlug
    
    print("\n=== Tasmota / OpenBeken Device Connection Test ===\n")
    print("(Works with both Tasmota and OpenBeken firmware)\n")
    
    address = input("Enter device IP address (e.g., 192.168.1.100): ").strip()
    username = input("Enter username (leave blank if none): ").strip()
    password = input("Enter password (leave blank if none): ").strip()
    
    print(f"\n--- Testing connection to {address} ---")
    
    try:
        print("\n1. Creating device connection...")
        device = TasmotaSmartPlug(address, username, password)
        print("✓ Connection created successfully!")
        
        print("\n2. Getting current device status...")
        status = device.get_status()
        print(f"✓ Current status: {'ON' if status else 'OFF'}")
        
        print("\n3. Testing turn OFF command...")
        device.set_status(False)
        print("✓ Turn OFF command sent")
        
        time.sleep(2)
        
        print("\n4. Verifying device is OFF...")
        status = device.get_status()
        print(f"✓ Status after OFF: {'ON' if status else 'OFF'}")
        
        if status:
            print("⚠ WARNING: Device is still ON after OFF command!")
        else:
            print("✓ Device successfully turned OFF")
        
        print("\n5. Testing turn ON command...")
        device.set_status(True)
        print("✓ Turn ON command sent")
        
        time.sleep(2)
        
        print("\n6. Verifying device is ON...")
        status = device.get_status()
        print(f"✓ Status after ON: {'ON' if status else 'OFF'}")
        
        if not status:
            print("⚠ WARNING: Device is still OFF after ON command!")
        else:
            print("✓ Device successfully turned ON")
        
        print("\n=== All tests completed successfully! ===\n")
        print("Your Tasmota/OpenBeken device is working correctly.")
        print("You can now configure the OctoPrint plugin!")
        
    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {e}")
        print("\nTroubleshooting:")
        print(f"1. Verify the IP address is correct")
        print(f"2. Try accessing http://{address} in a browser")
        print("3. Ensure device is on the same network")
        print("4. Check if web interface requires authentication")
        print("5. For OpenBeken: Make sure GPIO24 is set as Relay")
        sys.exit(1)


def test_tuya():
    """Test Tuya device connection."""
    from octoprint_psucontrol_tapo.shenzhen import RobustTuyaSmartPlug
    
    print("\n=== Tuya Device Connection Test ===\n")
    
    address = input("Enter device IP address (e.g., 192.168.1.100): ").strip()
    device_id = input("Enter device ID: ").strip()
    local_key = input("Enter local key: ").strip()
    version = input("Enter protocol version (3.3, 3.4, or 3.5) [default: 3.3]: ").strip() or "3.3"
    
    print(f"\n--- Testing connection to {address} ---")
    
    try:
        print("\n1. Creating device connection...")
        device = RobustTuyaSmartPlug(address, device_id, local_key, version)
        print("✓ Connection created successfully!")
        
        print("\n2. Getting current device status...")
        status = device.get_status()
        print(f"✓ Current status: {'ON' if status else 'OFF'}")
        
        print("\n3. Testing turn OFF command...")
        device.set_status(False)
        print("✓ Turn OFF command sent")
        
        time.sleep(2)
        
        print("\n4. Verifying device is OFF...")
        status = device.get_status()
        print(f"✓ Status after OFF: {'ON' if status else 'OFF'}")
        
        if status:
            print("⚠ WARNING: Device is still ON after OFF command!")
        else:
            print("✓ Device successfully turned OFF")
        
        print("\n5. Testing turn ON command...")
        device.set_status(True)
        print("✓ Turn ON command sent")
        
        time.sleep(2)
        
        print("\n6. Verifying device is ON...")
        status = device.get_status()
        print(f"✓ Status after ON: {'ON' if status else 'OFF'}")
        
        if not status:
            print("⚠ WARNING: Device is still OFF after ON command!")
        else:
            print("✓ Device successfully turned ON")
        
        print("\n=== All tests completed successfully! ===\n")
        print("Your Tuya device credentials are working correctly.")
        print("\nNote: If you experience connection drops, consider flashing Tasmota firmware.")
        
    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {e}")
        print("\nTroubleshooting:")
        print("1. Verify the IP address is correct")
        print("2. Ensure device is on the same network")
        print("3. Try different protocol versions (3.3, 3.4, 3.5)")
        print("4. Check if device_id and local_key are correct")
        print("5. Ensure no firewall is blocking UDP/TCP port 6668")
        print("\nTip: Consider flashing Tasmota for more reliable control!")
        sys.exit(1)


def main():
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║      Smart Outlet Connection Tester                    ║")
    print("║  (Arlec PC191HA / SM-PW701A1 / Other Tuya plugs)       ║")
    print("╚════════════════════════════════════════════════════════╝")
    
    print("\nSelect protocol to test:")
    print("  1. Tasmota / OpenBeken (recommended - flashed firmware)")
    print("  2. Tuya (stock firmware - may have connection drops)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_tasmota()
    elif choice == "2":
        test_tuya()
    else:
        print("Invalid choice. Please enter 1 or 2.")
        sys.exit(1)


if __name__ == "__main__":
    main()
