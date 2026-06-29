"""Config flow for Better Thermostat."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
import yaml

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_AVAILABILITY_TEMPLATE,
    CONF_CURRENT_HUMIDITY_TEMPLATE,
    CONF_CURRENT_TEMP_TEMPLATE,
    CONF_FAN_MODE_TEMPLATE,
    CONF_FAN_MODES,
    CONF_HVAC_ACTION_TEMPLATE,
    CONF_HVAC_MODE_TEMPLATE,
    CONF_ICON_TEMPLATE,
    CONF_MAX_HUMIDITY_TEMPLATE,
    CONF_MAX_TEMP_TEMPLATE,
    CONF_MIN_HUMIDITY_TEMPLATE,
    CONF_MIN_TEMP_TEMPLATE,
    CONF_MODES,
    CONF_PRECISION,
    CONF_PRESET_MODE_TEMPLATE,
    CONF_PRESET_MODES,
    CONF_SET_FAN_MODE_ACTION,
    CONF_SET_HUMIDITY_ACTION,
    CONF_SET_HVAC_MODE_ACTION,
    CONF_SET_PRESET_MODE_ACTION,
    CONF_SET_SWING_MODE_ACTION,
    CONF_SET_TEMP_ACTION,
    CONF_SWING_MODE_TEMPLATE,
    CONF_SWING_MODES,
    CONF_TARGET_HUMIDITY_TEMPLATE,
    CONF_TARGET_TEMP_HIGH_TEMPLATE,
    CONF_TARGET_TEMP_LOW_TEMPLATE,
    CONF_TARGET_TEMP_TEMPLATE,
    CONF_TEMP_MAX,
    CONF_TEMP_MIN,
    CONF_TEMP_STEP,
    CONF_VARIABLES,
    DEFAULT_NAME,
    DEFAULT_TEMP_STEP,
    DOMAIN,
)

CONF_ENABLE_PRESET = "enable_preset"
CONF_ENABLE_FAN = "enable_fan"
CONF_ENABLE_SWING = "enable_swing"
CONF_ENABLE_HUMIDITY = "enable_humidity"
CONF_ENABLE_HEAT_COOL = "enable_heat_cool"
CONF_ENABLE_ADVANCED = "enable_advanced"

ALL_MODES = ["off", "heat", "cool", "heat_cool", "auto", "dry", "fan_only"]


def _stringify_yaml(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        return yaml.dump(value, default_flow_style=False).strip()
    except Exception:
        return str(value)


class BetterThermostatConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            unique_id = user_input.get("unique_id") or user_input["name"].lower().replace(" ", "_")
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
            self._config_data = user_input
            return await self.async_step_temperature()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("name"): str,
                    vol.Optional("unique_id"): str,
                    vol.Optional(CONF_MODES, default=["off", "heat"]): cv.multi_select(
                        {m: m for m in ALL_MODES}
                    ),
                    vol.Optional(CONF_TEMP_MIN, default=7): vol.Coerce(float),
                    vol.Optional(CONF_TEMP_MAX, default=35): vol.Coerce(float),
                    vol.Optional(CONF_TEMP_STEP, default=DEFAULT_TEMP_STEP): vol.Coerce(float),
                }
            ),
            errors=errors,
        )

    async def async_step_temperature(self, user_input=None):
        errors = {}
        if user_input is not None:
            self._config_data.update(user_input)
            return await self.async_step_features()

        return self.async_show_form(
            step_id="temperature",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_CURRENT_TEMP_TEMPLATE): str,
                    vol.Optional(CONF_TARGET_TEMP_TEMPLATE): str,
                    vol.Optional(CONF_TARGET_TEMP_HIGH_TEMPLATE): str,
                    vol.Optional(CONF_TARGET_TEMP_LOW_TEMPLATE): str,
                    vol.Optional(CONF_HVAC_MODE_TEMPLATE): str,
                    vol.Optional(CONF_HVAC_ACTION_TEMPLATE): str,
                    vol.Optional(CONF_SET_TEMP_ACTION): str,
                    vol.Optional(CONF_SET_HVAC_MODE_ACTION): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "template_hint": "Inserisci template Jinja2 (es. {{ states('sensor.temperatura') }})",
            },
        )

    async def async_step_features(self, user_input=None):
        errors = {}
        if user_input is not None:
            self._config_data.update(user_input)

            show_preset = user_input.get(CONF_ENABLE_PRESET, False)
            show_fan = user_input.get(CONF_ENABLE_FAN, False)
            show_swing = user_input.get(CONF_ENABLE_SWING, False)
            show_humidity = user_input.get(CONF_ENABLE_HUMIDITY, False)
            show_advanced = user_input.get(CONF_ENABLE_ADVANCED, False)

            self._show_preset = show_preset
            self._show_fan = show_fan
            self._show_swing = show_swing
            self._show_humidity = show_humidity
            self._show_advanced = show_advanced

            return await self.async_step_optional()

        return self.async_show_form(
            step_id="features",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_ENABLE_PRESET, default=False): bool,
                    vol.Optional(CONF_ENABLE_FAN, default=False): bool,
                    vol.Optional(CONF_ENABLE_SWING, default=False): bool,
                    vol.Optional(CONF_ENABLE_HUMIDITY, default=False): bool,
                    vol.Optional(CONF_ENABLE_ADVANCED, default=False): bool,
                }
            ),
            errors=errors,
        )

    async def async_step_optional(self, user_input=None):
        errors = {}
        if user_input is not None:
            self._config_data.update({k: v for k, v in user_input.items() if v})
            return await self.async_step_advanced()

        schema = {}
        if getattr(self, "_show_preset", False):
            schema.update(
                {
                    vol.Optional(CONF_PRESET_MODE_TEMPLATE): str,
                    vol.Optional(CONF_PRESET_MODES, default=[]): str,
                    vol.Optional(CONF_SET_PRESET_MODE_ACTION): str,
                }
            )
        if getattr(self, "_show_fan", False):
            schema.update(
                {
                    vol.Optional(CONF_FAN_MODE_TEMPLATE): str,
                    vol.Optional(CONF_FAN_MODES, default=[]): str,
                    vol.Optional(CONF_SET_FAN_MODE_ACTION): str,
                }
            )
        if getattr(self, "_show_swing", False):
            schema.update(
                {
                    vol.Optional(CONF_SWING_MODE_TEMPLATE): str,
                    vol.Optional(CONF_SWING_MODES, default=[]): str,
                    vol.Optional(CONF_SET_SWING_MODE_ACTION): str,
                }
            )
        if getattr(self, "_show_humidity", False):
            schema.update(
                {
                    vol.Optional(CONF_CURRENT_HUMIDITY_TEMPLATE): str,
                    vol.Optional(CONF_TARGET_HUMIDITY_TEMPLATE): str,
                    vol.Optional(CONF_MIN_HUMIDITY_TEMPLATE): str,
                    vol.Optional(CONF_MAX_HUMIDITY_TEMPLATE): str,
                    vol.Optional(CONF_SET_HUMIDITY_ACTION): str,
                }
            )

        if not schema:
            return await self.async_step_advanced()

        return self.async_show_form(
            step_id="optional",
            data_schema=vol.Schema(schema),
            errors=errors,
        )

    async def async_step_advanced(self, user_input=None):
        errors = {}
        if user_input is not None:
            self._config_data.update({k: v for k, v in user_input.items() if v})

            data = {}
            for k, v in self._config_data.items():
                if k in (CONF_ENABLE_PRESET, CONF_ENABLE_FAN, CONF_ENABLE_SWING,
                         CONF_ENABLE_HUMIDITY, CONF_ENABLE_ADVANCED):
                    continue
                if k in (CONF_PRESET_MODES, CONF_FAN_MODES, CONF_SWING_MODES):
                    if isinstance(v, str):
                        data[k] = [m.strip() for m in v.split(",") if m.strip()]
                    else:
                        data[k] = v
                elif k in (CONF_SET_TEMP_ACTION, CONF_SET_HVAC_MODE_ACTION,
                           CONF_SET_PRESET_MODE_ACTION, CONF_SET_FAN_MODE_ACTION,
                           CONF_SET_SWING_MODE_ACTION, CONF_SET_HUMIDITY_ACTION):
                    if v:
                        try:
                            data[k] = yaml.safe_load(v)
                        except yaml.YAMLError:
                            data[k] = v
                else:
                    data[k] = v

            unique_id = (
                self._config_data.get("unique_id")
                or self._config_data["name"].lower().replace(" ", "_")
            )
            return self.async_create_entry(
                title=self._config_data["name"],
                data=data,
            )

        schema = {}
        if getattr(self, "_show_advanced", False):
            schema.update(
                {
                    vol.Optional(CONF_MIN_TEMP_TEMPLATE): str,
                    vol.Optional(CONF_MAX_TEMP_TEMPLATE): str,
                    vol.Optional(CONF_AVAILABILITY_TEMPLATE): str,
                    vol.Optional(CONF_ICON_TEMPLATE): str,
                    vol.Optional(CONF_PRECISION): vol.In(
                        {0.1: "0.1", 0.5: "0.5", 1.0: "1.0"}
                    ),
                    vol.Optional(CONF_VARIABLES): str,
                }
            )

        if not schema:
            return await self._finish()

        return self.async_show_form(
            step_id="advanced",
            data_schema=vol.Schema(schema),
            errors=errors,
        )

    async def _finish(self):
        data = {}
        for k, v in self._config_data.items():
            if k in (CONF_ENABLE_PRESET, CONF_ENABLE_FAN, CONF_ENABLE_SWING,
                     CONF_ENABLE_HUMIDITY, CONF_ENABLE_ADVANCED):
                continue
            if k in (CONF_PRESET_MODES, CONF_FAN_MODES, CONF_SWING_MODES):
                if isinstance(v, str):
                    data[k] = [m.strip() for m in v.split(",") if m.strip()]
                else:
                    data[k] = v
            elif k in (CONF_SET_TEMP_ACTION, CONF_SET_HVAC_MODE_ACTION,
                       CONF_SET_PRESET_MODE_ACTION, CONF_SET_FAN_MODE_ACTION,
                       CONF_SET_SWING_MODE_ACTION, CONF_SET_HUMIDITY_ACTION):
                if v:
                    try:
                        data[k] = yaml.safe_load(v)
                    except yaml.YAMLError:
                        data[k] = v
            else:
                data[k] = v

        unique_id = (
            self._config_data.get("unique_id")
            or self._config_data["name"].lower().replace(" ", "_")
        )
        return self.async_create_entry(
            title=self._config_data["name"],
            data=data,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return BetterThermostatOptionsFlow(config_entry)


class BetterThermostatOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self._config_entry = config_entry
        self._config_data = dict(config_entry.data)

    async def async_step_init(self, user_input=None):
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            self._config_data.update(user_input)
            return await self.async_step_temperature()

        data = self._config_data
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("name", default=data.get("name", DEFAULT_NAME)): str,
                    vol.Optional(CONF_MODES, default=data.get(CONF_MODES, ["off", "heat"])): cv.multi_select(
                        {m: m for m in ALL_MODES}
                    ),
                    vol.Optional(CONF_TEMP_MIN, default=data.get(CONF_TEMP_MIN, 7)): vol.Coerce(float),
                    vol.Optional(CONF_TEMP_MAX, default=data.get(CONF_TEMP_MAX, 35)): vol.Coerce(float),
                    vol.Optional(CONF_TEMP_STEP, default=data.get(CONF_TEMP_STEP, DEFAULT_TEMP_STEP)): vol.Coerce(float),
                }
            ),
            errors=errors,
        )

    async def async_step_temperature(self, user_input=None):
        errors = {}
        if user_input is not None:
            self._config_data.update(user_input)
            return await self.async_step_features()

        data = self._config_data
        return self.async_show_form(
            step_id="temperature",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_CURRENT_TEMP_TEMPLATE,
                                 default=data.get(CONF_CURRENT_TEMP_TEMPLATE, "")): str,
                    vol.Optional(CONF_TARGET_TEMP_TEMPLATE,
                                 default=data.get(CONF_TARGET_TEMP_TEMPLATE, "")): str,
                    vol.Optional(CONF_TARGET_TEMP_HIGH_TEMPLATE,
                                 default=data.get(CONF_TARGET_TEMP_HIGH_TEMPLATE, "")): str,
                    vol.Optional(CONF_TARGET_TEMP_LOW_TEMPLATE,
                                 default=data.get(CONF_TARGET_TEMP_LOW_TEMPLATE, "")): str,
                    vol.Optional(CONF_HVAC_MODE_TEMPLATE,
                                 default=data.get(CONF_HVAC_MODE_TEMPLATE, "")): str,
                    vol.Optional(CONF_HVAC_ACTION_TEMPLATE,
                                 default=data.get(CONF_HVAC_ACTION_TEMPLATE, "")): str,
                    vol.Optional(CONF_SET_TEMP_ACTION,
                                 default=_stringify_yaml(data.get(CONF_SET_TEMP_ACTION))): str,
                    vol.Optional(CONF_SET_HVAC_MODE_ACTION,
                                 default=_stringify_yaml(data.get(CONF_SET_HVAC_MODE_ACTION))): str,
                }
            ),
            errors=errors,
        )

    async def async_step_features(self, user_input=None):
        errors = {}
        if user_input is not None:
            self._config_data.update(user_input)
            return await self._save()

        data = self._config_data
        return self.async_show_form(
            step_id="features",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_PRESET_MODE_TEMPLATE,
                                 default=data.get(CONF_PRESET_MODE_TEMPLATE, "")): str,
                    vol.Optional(CONF_PRESET_MODES,
                                 default=",".join(data.get(CONF_PRESET_MODES, []))): str,
                    vol.Optional(CONF_SET_PRESET_MODE_ACTION,
                                 default=_stringify_yaml(data.get(CONF_SET_PRESET_MODE_ACTION))): str,
                    vol.Optional(CONF_FAN_MODE_TEMPLATE,
                                 default=data.get(CONF_FAN_MODE_TEMPLATE, "")): str,
                    vol.Optional(CONF_FAN_MODES,
                                 default=",".join(data.get(CONF_FAN_MODES, []))): str,
                    vol.Optional(CONF_SET_FAN_MODE_ACTION,
                                 default=_stringify_yaml(data.get(CONF_SET_FAN_MODE_ACTION))): str,
                    vol.Optional(CONF_SWING_MODE_TEMPLATE,
                                 default=data.get(CONF_SWING_MODE_TEMPLATE, "")): str,
                    vol.Optional(CONF_SWING_MODES,
                                 default=",".join(data.get(CONF_SWING_MODES, []))): str,
                    vol.Optional(CONF_SET_SWING_MODE_ACTION,
                                 default=_stringify_yaml(data.get(CONF_SET_SWING_MODE_ACTION))): str,
                    vol.Optional(CONF_TARGET_HUMIDITY_TEMPLATE,
                                 default=data.get(CONF_TARGET_HUMIDITY_TEMPLATE, "")): str,
                    vol.Optional(CONF_CURRENT_HUMIDITY_TEMPLATE,
                                 default=data.get(CONF_CURRENT_HUMIDITY_TEMPLATE, "")): str,
                    vol.Optional(CONF_MIN_HUMIDITY_TEMPLATE,
                                 default=data.get(CONF_MIN_HUMIDITY_TEMPLATE, "")): str,
                    vol.Optional(CONF_MAX_HUMIDITY_TEMPLATE,
                                 default=data.get(CONF_MAX_HUMIDITY_TEMPLATE, "")): str,
                    vol.Optional(CONF_SET_HUMIDITY_ACTION,
                                 default=_stringify_yaml(data.get(CONF_SET_HUMIDITY_ACTION))): str,
                    vol.Optional(CONF_MIN_TEMP_TEMPLATE,
                                 default=data.get(CONF_MIN_TEMP_TEMPLATE, "")): str,
                    vol.Optional(CONF_MAX_TEMP_TEMPLATE,
                                 default=data.get(CONF_MAX_TEMP_TEMPLATE, "")): str,
                    vol.Optional(CONF_AVAILABILITY_TEMPLATE,
                                 default=data.get(CONF_AVAILABILITY_TEMPLATE, "")): str,
                    vol.Optional(CONF_ICON_TEMPLATE,
                                 default=data.get(CONF_ICON_TEMPLATE, "")): str,
                    vol.Optional(CONF_VARIABLES,
                                 default=_stringify_yaml(data.get(CONF_VARIABLES, {}))): str,
                }
            ),
            errors=errors,
        )

    async def _save(self):
        data = {}
        for k, v in self._config_data.items():
            if k in (CONF_PRESET_MODES, CONF_FAN_MODES, CONF_SWING_MODES):
                if isinstance(v, str):
                    data[k] = [m.strip() for m in v.split(",") if m.strip()]
                else:
                    data[k] = v
            elif k in (CONF_SET_TEMP_ACTION, CONF_SET_HVAC_MODE_ACTION,
                       CONF_SET_PRESET_MODE_ACTION, CONF_SET_FAN_MODE_ACTION,
                       CONF_SET_SWING_MODE_ACTION, CONF_SET_HUMIDITY_ACTION,
                       CONF_VARIABLES):
                if v:
                    try:
                        data[k] = yaml.safe_load(v)
                    except yaml.YAMLError:
                        data[k] = v
                else:
                    data[k] = v
            else:
                data[k] = v

        return self.async_create_entry(title="", data=data)
