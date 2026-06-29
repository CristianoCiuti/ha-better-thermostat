"""Constants for the Better Thermostat integration."""

from homeassistant.components.climate.const import DEFAULT_MAX_TEMP, DEFAULT_MIN_TEMP

DOMAIN = "better_thermostat"
PLATFORMS = ["climate"]

DEFAULT_NAME = "Better Thermostat"
DEFAULT_TEMP_STEP = 1.0

CONF_MODES = "modes"
CONF_FAN_MODES = "fan_modes"
CONF_PRESET_MODES = "preset_modes"
CONF_SWING_MODES = "swing_modes"
CONF_TEMP_MIN = "min_temp"
CONF_TEMP_MAX = "max_temp"
CONF_TEMP_STEP = "temp_step"
CONF_PRECISION = "precision"

CONF_CURRENT_TEMP_TEMPLATE = "current_temperature_template"
CONF_CURRENT_HUMIDITY_TEMPLATE = "current_humidity_template"
CONF_TARGET_TEMP_TEMPLATE = "target_temperature_template"
CONF_TARGET_TEMP_HIGH_TEMPLATE = "target_temperature_high_template"
CONF_TARGET_TEMP_LOW_TEMPLATE = "target_temperature_low_template"
CONF_HVAC_MODE_TEMPLATE = "hvac_mode_template"
CONF_HVAC_ACTION_TEMPLATE = "hvac_action_template"
CONF_PRESET_MODE_TEMPLATE = "preset_mode_template"
CONF_FAN_MODE_TEMPLATE = "fan_mode_template"
CONF_SWING_MODE_TEMPLATE = "swing_mode_template"
CONF_TARGET_HUMIDITY_TEMPLATE = "target_humidity_template"
CONF_MIN_HUMIDITY_TEMPLATE = "min_humidity_template"
CONF_MAX_HUMIDITY_TEMPLATE = "max_humidity_template"
CONF_MIN_TEMP_TEMPLATE = "min_temp_template"
CONF_MAX_TEMP_TEMPLATE = "max_temp_template"
CONF_AVAILABILITY_TEMPLATE = "availability_template"
CONF_ICON_TEMPLATE = "icon_template"

CONF_SET_TEMP_ACTION = "set_temperature"
CONF_SET_HVAC_MODE_ACTION = "set_hvac_mode"
CONF_SET_PRESET_MODE_ACTION = "set_preset_mode"
CONF_SET_FAN_MODE_ACTION = "set_fan_mode"
CONF_SET_SWING_MODE_ACTION = "set_swing_mode"
CONF_SET_HUMIDITY_ACTION = "set_humidity"
CONF_VARIABLES = "variables"

TEMPLATE_KEYS = [
    CONF_CURRENT_TEMP_TEMPLATE,
    CONF_CURRENT_HUMIDITY_TEMPLATE,
    CONF_TARGET_TEMP_TEMPLATE,
    CONF_TARGET_TEMP_HIGH_TEMPLATE,
    CONF_TARGET_TEMP_LOW_TEMPLATE,
    CONF_HVAC_MODE_TEMPLATE,
    CONF_HVAC_ACTION_TEMPLATE,
    CONF_PRESET_MODE_TEMPLATE,
    CONF_FAN_MODE_TEMPLATE,
    CONF_SWING_MODE_TEMPLATE,
    CONF_TARGET_HUMIDITY_TEMPLATE,
    CONF_MIN_HUMIDITY_TEMPLATE,
    CONF_MAX_HUMIDITY_TEMPLATE,
    CONF_MIN_TEMP_TEMPLATE,
    CONF_MAX_TEMP_TEMPLATE,
    CONF_AVAILABILITY_TEMPLATE,
    CONF_ICON_TEMPLATE,
]

ACTION_KEYS = [
    CONF_SET_TEMP_ACTION,
    CONF_SET_HVAC_MODE_ACTION,
    CONF_SET_PRESET_MODE_ACTION,
    CONF_SET_FAN_MODE_ACTION,
    CONF_SET_SWING_MODE_ACTION,
    CONF_SET_HUMIDITY_ACTION,
]
