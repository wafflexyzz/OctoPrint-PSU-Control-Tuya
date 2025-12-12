# coding=utf-8
"""
Shenzhen SM-PW701A1 Smart Outlet Control Module

This module provides control for the Shenzhen SM-PW701A1 WiFi smart outlet.
It supports two control methods:
1. Tuya protocol (stock firmware) - using tinytuya library
2. Tasmota protocol (custom firmware) - using HTTP API for more reliable control

The Tasmota method is recommended for reliability as it doesn't have the 
connection dropping issues common with Tuya cloud-dependent firmware.
"""

import logging
import time
import socket

log = logging.getLogger(__name__)


class TasmotaSmartPlug:
    """
    Control class for Tasmota/OpenBeken-flashed smart plugs via HTTP API.
    
    Works with:
    - Tasmota firmware (ESP8266/ESP32 devices)
    - OpenBeken firmware (BK7231N/BK7231T devices like Arlec PC191HA Series 2)
    
    Both firmwares use the same HTTP command API, providing reliable 
    local-only control with no cloud dependency.
    
    Attributes:
        address (str): IP address of the smart plug
        username (str): HTTP username (if configured)
        password (str): HTTP password (if configured)
    """
    
    def __init__(self, address: str, username: str = "", password: str = "", timeout: int = 10):
        """
        Initialize the Tasmota smart plug controller.
        
        Args:
            address: IP address of the smart plug
            username: HTTP Basic Auth username (optional)
            password: HTTP Basic Auth password (optional)
            timeout: Request timeout in seconds
        """
        self.address = address
        self.username = username
        self.password = password
        self.timeout = timeout
        self._verify_connection()
    
    def _make_request(self, command: str) -> dict:
        """Make HTTP request to Tasmota device."""
        import urllib.request
        import urllib.error
        import json
        
        url = f"http://{self.address}/cm?cmnd={command}"
        log.debug(f"Tasmota request: {url}")
        
        try:
            # Create request with optional auth
            request = urllib.request.Request(url)
            
            if self.username and self.password:
                import base64
                credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
                request.add_header("Authorization", f"Basic {credentials}")
            
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = response.read().decode('utf-8')
                log.debug(f"Tasmota response: {data}")
                return json.loads(data)
                
        except urllib.error.URLError as e:
            log.error(f"Tasmota connection error: {e}")
            raise Exception(f"Cannot connect to Tasmota device at {self.address}: {e}")
        except json.JSONDecodeError as e:
            log.error(f"Invalid Tasmota response: {e}")
            raise Exception(f"Invalid response from Tasmota device: {e}")
    
    def _verify_connection(self):
        """Verify connection to the Tasmota device."""
        log.info(f"Connecting to Tasmota device at {self.address}")
        try:
            status = self._make_request("Status%200")
            device_name = status.get("Status", {}).get("DeviceName", "Unknown")
            log.info(f"Connected to Tasmota device: {device_name}")
        except Exception as e:
            log.error(f"Failed to connect to Tasmota device: {e}")
            raise
    
    def get_status(self) -> bool:
        """
        Get the current on/off status of the plug.
        
        Returns:
            bool: True if the plug is on, False if off
        """
        log.info(f"Getting status from Tasmota device at {self.address}")
        try:
            result = self._make_request("Power")
            power_state = result.get("POWER", result.get("POWER1", "OFF"))
            is_on = power_state.upper() == "ON"
            log.info(f"Tasmota device is {'ON' if is_on else 'OFF'}")
            return is_on
        except Exception as e:
            log.error(f"Failed to get Tasmota status: {e}")
            raise
    
    def set_status(self, status: bool):
        """
        Set the on/off status of the plug.
        
        Args:
            status: True to turn on, False to turn off
        """
        action = "ON" if status else "OFF"
        log.info(f"Setting Tasmota device at {self.address} to {action}")
        try:
            result = self._make_request(f"Power%20{action}")
            power_state = result.get("POWER", result.get("POWER1", ""))
            if power_state.upper() != action:
                log.warning(f"Power state mismatch: expected {action}, got {power_state}")
            log.info(f"Successfully set Tasmota device to {action}")
        except Exception as e:
            log.error(f"Failed to set Tasmota status: {e}")
            raise
    
    def turn_on(self):
        """Turn the plug on."""
        self.set_status(True)
    
    def turn_off(self):
        """Turn the plug off."""
        self.set_status(False)
    
    def toggle(self):
        """Toggle the plug state."""
        log.info("Toggling Tasmota device")
        self._make_request("Power%20TOGGLE")


class RobustTuyaSmartPlug:
    """
    Enhanced Tuya smart plug controller with better connection handling.
    
    This class provides methods to turn the plug on/off and get its current status.
    It includes retry logic and connection recovery for better reliability.
    
    Attributes:
        address (str): IP address of the smart plug
        device_id (str): Tuya device ID
        local_key (str): Tuya local key for encryption
    """
    
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    def __init__(self, address: str, device_id: str, local_key: str, version: str = "3.3"):
        """
        Initialize the Tuya smart plug controller with retry logic.
        
        Args:
            address: IP address of the smart plug
            device_id: Tuya device ID
            local_key: Tuya local key for encryption
            version: Tuya protocol version (default "3.3")
        """
        self.address = address
        self.device_id = device_id
        self.local_key = local_key
        self.version = version
        self.device = None
        self._connect_with_retry()
    
    def _connect_with_retry(self):
        """Create a connection to the smart plug with retry logic."""
        import tinytuya
        
        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                log.info(f"Connecting to Tuya device at {self.address} (attempt {attempt + 1}/{self.MAX_RETRIES})")
                
                self.device = tinytuya.OutletDevice(
                    dev_id=self.device_id,
                    address=self.address,
                    local_key=self.local_key,
                    version=float(self.version) if self.version else 3.3
                )
                
                # Increase timeout for more reliability
                self.device.set_socketTimeout(10)
                self.device.set_socketRetryLimit(3)
                
                # Test the connection
                test_status = self.device.status()
                log.info(f"Connection test response: {test_status}")
                
                if "Error" in test_status:
                    error_msg = test_status.get("Error", "Unknown error")
                    raise Exception(f"Device error: {error_msg}")
                
                log.info(f"Successfully connected to Tuya device at {self.address}")
                return
                
            except Exception as e:
                last_error = e
                log.warning(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    log.info(f"Retrying in {self.RETRY_DELAY} seconds...")
                    time.sleep(self.RETRY_DELAY)
        
        raise Exception(f"Failed to connect after {self.MAX_RETRIES} attempts: {last_error}")
    
    def _ensure_connected(self):
        """Ensure the device is connected, reconnect if necessary."""
        if self.device is None:
            self._connect_with_retry()
    
    def _execute_with_retry(self, operation, operation_name: str):
        """Execute an operation with retry logic."""
        last_error = None
        for attempt in range(self.MAX_RETRIES):
            try:
                self._ensure_connected()
                return operation()
            except Exception as e:
                last_error = e
                log.warning(f"{operation_name} attempt {attempt + 1} failed: {e}")
                self.device = None  # Force reconnection
                if attempt < self.MAX_RETRIES - 1:
                    log.info(f"Retrying {operation_name} in {self.RETRY_DELAY} seconds...")
                    time.sleep(self.RETRY_DELAY)
        
        raise Exception(f"{operation_name} failed after {self.MAX_RETRIES} attempts: {last_error}")
    
    def get_status(self) -> bool:
        """
        Get the current on/off status of the plug.
        
        Returns:
            bool: True if the plug is on, False if off
        """
        def _get_status():
            log.info(f"Getting status from Tuya device at {self.address}")
            status = self.device.status()
            
            if "Error" in status:
                raise Exception(f"Device error: {status.get('Error', 'Unknown')}")
            
            dps = status.get("dps", {})
            is_on = dps.get("1", False)
            log.info(f"Tuya device is {'ON' if is_on else 'OFF'} (DPS: {dps})")
            return is_on
        
        return self._execute_with_retry(_get_status, "get_status")
    
    def set_status(self, status: bool):
        """
        Set the on/off status of the plug.
        
        Args:
            status: True to turn on, False to turn off
        """
        action = "ON" if status else "OFF"
        
        def _set_status():
            log.info(f"Setting Tuya device at {self.address} to {action}")
            if status:
                result = self.device.turn_on()
            else:
                result = self.device.turn_off()
            
            if result and "Error" in result:
                raise Exception(f"Device error: {result.get('Error', 'Unknown')}")
            
            log.info(f"Successfully set Tuya device to {action}")
            return result
        
        self._execute_with_retry(_set_status, f"set_status({action})")
    
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


class ShenzhenSmartPlug:
    """
    Factory class that creates the appropriate smart plug controller
    based on the selected protocol.
    
    Supports:
    - Tasmota (recommended for reliability)
    - Tuya (stock firmware with enhanced retry logic)
    """
    
    PROTOCOL_TASMOTA = "tasmota"
    PROTOCOL_TUYA = "tuya"
    
    def __init__(self, protocol: str, address: str, **kwargs):
        """
        Initialize the appropriate smart plug controller.
        
        Args:
            protocol: "tasmota" or "tuya"
            address: IP address of the smart plug
            **kwargs: Protocol-specific parameters
                For Tasmota: username, password, timeout
                For Tuya: device_id, local_key, version
        """
        self.protocol = protocol.lower()
        self.address = address
        self._device = None
        
        log.info(f"Creating {self.protocol} smart plug controller for {address}")
        
        if self.protocol == self.PROTOCOL_TASMOTA:
            self._device = TasmotaSmartPlug(
                address=address,
                username=kwargs.get("username", ""),
                password=kwargs.get("password", ""),
                timeout=kwargs.get("timeout", 10)
            )
        elif self.protocol == self.PROTOCOL_TUYA:
            self._device = RobustTuyaSmartPlug(
                address=address,
                device_id=kwargs.get("device_id", ""),
                local_key=kwargs.get("local_key", ""),
                version=kwargs.get("version", "3.3")
            )
        else:
            raise ValueError(f"Unknown protocol: {protocol}. Use 'tasmota' or 'tuya'")
    
    def get_status(self) -> bool:
        """Get the current on/off status of the plug."""
        return self._device.get_status()
    
    def set_status(self, status: bool):
        """Set the on/off status of the plug."""
        self._device.set_status(status)
    
    def turn_on(self):
        """Turn the plug on."""
        self._device.turn_on()
    
    def turn_off(self):
        """Turn the plug off."""
        self._device.turn_off()
    
    def toggle(self):
        """Toggle the plug state."""
        self._device.toggle()

