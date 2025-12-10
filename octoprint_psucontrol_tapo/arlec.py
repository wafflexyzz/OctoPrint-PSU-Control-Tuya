# coding=utf-8
"""
Arlec/Tuya Smart Plug Control Module

This module provides control for Arlec (and other Tuya-based) smart plugs.
The Arlec PC191BKHA Series 2 is a Tuya-based device that can be controlled
locally using the tinytuya library.

To use this module, you need:
- Device IP address (static IP recommended)
- Device ID (from Tuya Developer account or tinytuya wizard)
- Local Key (from Tuya Developer account or tinytuya wizard)
"""

import logging
import tinytuya

log = logging.getLogger(__name__)


class ArlecSmartPlug:
    """
    Control class for Arlec/Tuya smart plugs.
    
    This class provides methods to turn the plug on/off and get its current status.
    It uses the tinytuya library for local control (no cloud dependency).
    
    Attributes:
        address (str): IP address of the smart plug
        device_id (str): Tuya device ID
        local_key (str): Tuya local key for encryption
        device (tinytuya.OutletDevice): The tinytuya device instance
    """
    
    def __init__(self, address: str, device_id: str, local_key: str, version: str = "3.3"):
        """
        Initialize the Arlec smart plug controller.
        
        Args:
            address: IP address of the smart plug
            device_id: Tuya device ID
            local_key: Tuya local key for encryption
            version: Tuya protocol version (default "3.3", can be "3.1", "3.2", "3.3", "3.4", "3.5")
        """
        self.address = address
        self.device_id = device_id
        self.local_key = local_key
        self.version = version
        self.device = None
        self._connect()
    
    def _connect(self):
        """Create a connection to the smart plug."""
        log.debug(f"Connecting to Arlec device at {self.address}")
        self.device = tinytuya.OutletDevice(
            dev_id=self.device_id,
            address=self.address,
            local_key=self.local_key,
            version=float(self.version) if self.version else 3.3
        )
        # Set socket timeout for faster responses
        self.device.set_socketTimeout(5)
        log.debug(f"Connected to Arlec device at {self.address}")
    
    def get_status(self) -> bool:
        """
        Get the current on/off status of the plug.
        
        Returns:
            bool: True if the plug is on, False if off
            
        Raises:
            Exception: If unable to communicate with the device
        """
        try:
            status = self.device.status()
            log.debug(f"Device status response: {status}")
            
            if "Error" in status:
                error_msg = status.get("Error", "Unknown error")
                log.error(f"Error getting device status: {error_msg}")
                raise Exception(f"Device error: {error_msg}")
            
            # The switch state is typically in dps key "1" for most Tuya plugs
            dps = status.get("dps", {})
            is_on = dps.get("1", False)
            log.debug(f"Device is {'ON' if is_on else 'OFF'}")
            return is_on
            
        except Exception as e:
            log.error(f"Failed to get device status: {e}")
            raise
    
    def set_status(self, status: bool):
        """
        Set the on/off status of the plug.
        
        Args:
            status: True to turn on, False to turn off
            
        Raises:
            Exception: If unable to communicate with the device
        """
        try:
            if status:
                log.debug(f"Turning device ON")
                result = self.device.turn_on()
            else:
                log.debug(f"Turning device OFF")
                result = self.device.turn_off()
            
            log.debug(f"Set status result: {result}")
            
            if result and "Error" in result:
                error_msg = result.get("Error", "Unknown error")
                log.error(f"Error setting device status: {error_msg}")
                raise Exception(f"Device error: {error_msg}")
                
        except Exception as e:
            log.error(f"Failed to set device status: {e}")
            raise
    
    def turn_on(self):
        """Turn the plug on."""
        self.set_status(True)
    
    def turn_off(self):
        """Turn the plug off."""
        self.set_status(False)
    
    def toggle(self):
        """Toggle the plug state."""
        current_status = self.get_status()
        self.set_status(not current_status)
    
    def get_energy_info(self) -> dict:
        """
        Get energy monitoring information if supported by the device.
        
        The Arlec PC191BKHA has an energy meter, so this may return:
        - Current (mA)
        - Power (W)
        - Voltage (V)
        
        Returns:
            dict: Energy information from device DPS values
        """
        try:
            status = self.device.status()
            log.debug(f"Energy info response: {status}")
            
            if "Error" in status:
                error_msg = status.get("Error", "Unknown error")
                log.error(f"Error getting energy info: {error_msg}")
                return {}
            
            dps = status.get("dps", {})
            
            # Common DPS mappings for Tuya energy monitoring plugs:
            # DPS 1: Switch state (bool)
            # DPS 17: Current in mA (int)
            # DPS 18: Power in W*10 or W (int)
            # DPS 19: Voltage in V*10 (int)
            # Note: Actual DPS numbers may vary by device
            
            energy_info = {
                "switch": dps.get("1", False),
                "current_ma": dps.get("18", 0),  # May need adjustment
                "power_w": dps.get("19", 0),     # May need adjustment
                "voltage_v": dps.get("20", 0),   # May need adjustment
            }
            
            return energy_info
            
        except Exception as e:
            log.error(f"Failed to get energy info: {e}")
            return {}

