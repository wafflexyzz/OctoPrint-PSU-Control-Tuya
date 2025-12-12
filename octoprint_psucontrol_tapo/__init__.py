# coding=utf-8
from __future__ import absolute_import
import threading
import logging

# Debug: Log when module is being imported
_startup_logger = logging.getLogger("octoprint.plugins.psucontrol_tapo.startup")
_startup_logger.info("=== PSU Control Shenzhen module is being imported ===")

__author__ = "Dennis Schwerdel <schwerdel@gmail.com>, Modified for Shenzhen SM-PW701A1"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"
__copyright__ = "Copyright (C) 2022 Dennis Schwerdel - Released under terms of the AGPLv3 License"

# Import modules for standalone usage
from .shenzhen import ShenzhenSmartPlug, TasmotaSmartPlug, RobustTuyaSmartPlug
from . import shenzhen

_startup_logger.info("=== Shenzhen module imports successful ===")

# Import octoprint
import octoprint.plugin

_startup_logger.info("=== OctoPrint plugin import successful ===")


class PSUControl_Shenzhen(octoprint.plugin.StartupPlugin,
                          octoprint.plugin.RestartNeedingPlugin,
                          octoprint.plugin.TemplatePlugin,
                          octoprint.plugin.SettingsPlugin):

    def __init__(self):
        self.config = dict()
        self.device = None
        self.last_status = None
        self._status_lock = threading.Lock()

    def get_settings_defaults(self):
        return dict(
            protocol='tasmota',  # 'tasmota' (recommended) or 'tuya'
            address='',
            # Tasmota settings
            tasmota_username='',
            tasmota_password='',
            # Tuya settings (for stock firmware)
            device_id='',
            local_key='',
            version='3.3'
        )

    def on_settings_initialized(self):
        self.reload_settings()

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.reload_settings()

    def get_settings_version(self):
        return 2

    def on_settings_migrate(self, target, current=None):
        if current is None or current < 2:
            # Migrate from old Tuya-only settings
            self._settings.set(["protocol"], "tuya")

    def _reconnect(self):
        protocol = self.config.get('protocol', 'tasmota')
        self._logger.info(f"Reconnecting to {protocol} device at {self.config['address']}")
        
        try:
            if protocol == 'tasmota':
                self.device = ShenzhenSmartPlug(
                    protocol="tasmota",
                    address=self.config["address"],
                    username=self.config.get("tasmota_username", ""),
                    password=self.config.get("tasmota_password", "")
                )
            else:  # tuya
                self.device = ShenzhenSmartPlug(
                    protocol="tuya",
                    address=self.config["address"],
                    device_id=self.config.get("device_id", ""),
                    local_key=self.config.get("local_key", ""),
                    version=self.config.get("version", "3.3")
                )
            self._logger.info(f"{protocol.title()} device reconnected successfully")
        except Exception as e:
            self._logger.error(f"Failed to reconnect to {protocol} device: {type(e).__name__}: {e}")
            self.device = None
            raise

    def reload_settings(self):
        for k, v in self.get_settings_defaults().items():
            if type(v) == str:
                v = self._settings.get([k])
            elif type(v) == int:
                v = self._settings.get_int([k])
            elif type(v) == float:
                v = self._settings.get_float([k])
            elif type(v) == bool:
                v = self._settings.get_boolean([k])

            self.config[k] = v
            self._logger.debug("{}: {}".format(k, v))
        
        try:
            protocol = self.config.get('protocol', 'tasmota')
            self._logger.info(f"Config loaded: protocol={protocol}, address={self.config.get('address')}")
            shenzhen.log = self._logger
            self._reconnect()
        except Exception as e:
            self._logger.error(f"Failed to connect to device: {type(e).__name__}: {e}", exc_info=True)
            self.device = None

    def on_startup(self, host, port):
        self._logger.info("=== PSU Control Shenzhen on_startup called ===")
        psucontrol_helpers = self._plugin_manager.get_helpers("psucontrol")
        if not psucontrol_helpers or 'register_plugin' not in psucontrol_helpers.keys():
            self._logger.warning("The version of PSUControl that is installed does not support plugin registration.")
            return

        self._logger.info("Registering plugin with PSUControl")
        psucontrol_helpers['register_plugin'](self)

    def turn_psu_on(self):
        self._logger.info("=== TURN PSU ON requested ===")
        if not self.device:
            self._logger.warning("Device not connected, reconnecting...")
            self._reconnect()
        self._logger.info("Switching PSU On")
        try:
            self.device.set_status(True)
            with self._status_lock:
                self.last_status = True
            self._logger.info("PSU turned ON successfully")
        except Exception as e:
            self._logger.error(f"Failed to switch PSU On: {type(e).__name__}: {e}", exc_info=True)
            self.device = None
            raise

    def turn_psu_off(self):
        self._logger.info("=== TURN PSU OFF requested ===")
        if not self.device:
            self._logger.warning("Device not connected, reconnecting...")
            self._reconnect()
        self._logger.info("Switching PSU Off")
        try:
            self.device.set_status(False)
            with self._status_lock:
                self.last_status = False
            self._logger.info("PSU turned OFF successfully")
        except Exception as e:
            self._logger.error(f"Failed to switch PSU Off: {type(e).__name__}: {e}", exc_info=True)
            self.device = None
            raise

    def _fetch_psu_state(self):
        if not self.device:
            self._logger.warning("Device not connected, reconnecting...")
            self._reconnect()
        self._logger.info("Fetching PSU state")
        try:
            status = self.device.get_status()
            with self._status_lock:
                self.last_status = status
            self._logger.info(f"PSU state fetched: {status}")
        except Exception as e:
            self._logger.error(f"Failed to get PSU state: {type(e).__name__}: {e}", exc_info=True)
            self.device = None
            raise

    def get_psu_state(self):
        with self._status_lock:
            cached_status = self.last_status
        
        if cached_status is None:
            self._fetch_psu_state()
            with self._status_lock:
                return self.last_status
        else:
            # Fetch in background to update cache
            threading.Thread(target=self._fetch_psu_state, daemon=True).start()
            return cached_status

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]

    def get_update_information(self):
        return dict(
            psucontrol_shenzhen=dict(
                displayName="PSU Control - Shenzhen",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="wafflexyzz",
                repo="OctoPrint-PSU-Control-Tuya",
                current=self._plugin_version,

                # update method: pip w/ dependency links
                pip="https://github.com/wafflexyzz/OctoPrint-PSU-Control-Tuya/archive/{target_version}.zip"
            )
        )


__plugin_name__ = "PSU Control - Shenzhen"
__plugin_pythoncompat__ = ">=3.7,<4"

_startup_logger.info("=== About to define __plugin_load__ ===")

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = PSUControl_Shenzhen()
    _startup_logger.info(f"=== Plugin implementation created: {__plugin_implementation__} ===")

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }

_startup_logger.info("=== PSU Control Shenzhen module fully loaded ===")
