"""Climate entity for Better Thermostat."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.components.climate.const import (
    ATTR_HVAC_MODE,
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
    ATTR_TEMPERATURE,
)
from homeassistant.const import (
    ATTR_FAN_MODE,
    ATTR_HUMIDITY,
    ATTR_PRESET_MODE,
    ATTR_SWING_MODE,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import template as template_m
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import TrackTemplate, async_track_template_result
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.script import Script
from homeassistant.helpers.template import result_as_boolean
from homeassistant.config_entries import ConfigEntry

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

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    config = dict(config_entry.data)
    config.update(dict(config_entry.options))
    unique_id = config_entry.entry_id
    async_add_entities([BetterThermostatEntity(hass, config, unique_id)])


class BetterThermostatEntity(ClimateEntity, RestoreEntity):
    _attr_should_poll = False

    def __init__(
        self, hass: HomeAssistant, config: dict[str, Any], unique_id: str
    ) -> None:
        super().__init__()
        self.hass = hass
        self._attr_unique_id = unique_id
        self._config = config
        self._attr_name = config.get("name", DEFAULT_NAME)

        self._template_cache: dict[str, template_m.Template] = {}
        self._template_callbacks: dict[int, tuple[str, Any]] = {}
        self._track_templates: list[TrackTemplate] = []

        modes = config.get(CONF_MODES, ["off", "heat"])
        self._attr_hvac_modes = [HVACMode(m) if isinstance(m, str) else m for m in modes]

        self._attr_min_temp = config.get(CONF_TEMP_MIN, 7)
        self._attr_max_temp = config.get(CONF_TEMP_MAX, 35)
        self._attr_target_temperature_step = config.get(
            CONF_TEMP_STEP, DEFAULT_TEMP_STEP
        )
        self._attr_temperature_unit = hass.config.units.temperature_unit

        precision = config.get(CONF_PRECISION)
        if precision is not None:
            self._attr_precision = precision

        self._attr_hvac_mode = HVACMode.OFF
        self._attr_target_temperature = 21.0
        self._attr_target_temperature_high = None
        self._attr_target_temperature_low = None
        self._attr_current_temperature = None
        self._attr_current_humidity = None
        self._attr_target_humidity = None
        self._attr_min_humidity = None
        self._attr_max_humidity = None
        self._attr_hvac_action = None

        fan_modes = config.get(CONF_FAN_MODES, [])
        self._attr_fan_modes = list(fan_modes) if fan_modes else None
        self._attr_fan_mode = fan_modes[0] if fan_modes else None

        preset_modes = config.get(CONF_PRESET_MODES, [])
        self._attr_preset_modes = list(preset_modes) if preset_modes else None
        self._attr_preset_mode = preset_modes[0] if preset_modes else None

        swing_modes = config.get(CONF_SWING_MODES, [])
        self._attr_swing_modes = list(swing_modes) if swing_modes else None
        self._attr_swing_mode = swing_modes[0] if swing_modes else None

        self._variables = config.get(CONF_VARIABLES, {})

        self._setup_templates()
        self._setup_actions()
        self._setup_features()

    def _setup_templates(self) -> None:
        template_mapping = [
            (CONF_CURRENT_TEMP_TEMPLATE, "current_temperature", self._make_float_updater("_attr_current_temperature")),
            (CONF_CURRENT_HUMIDITY_TEMPLATE, "current_humidity", self._make_float_updater("_attr_current_humidity")),
            (CONF_TARGET_TEMP_TEMPLATE, "target_temperature", self._make_float_updater("_attr_target_temperature")),
            (CONF_TARGET_TEMP_HIGH_TEMPLATE, "target_temperature_high", self._make_float_updater("_attr_target_temperature_high")),
            (CONF_TARGET_TEMP_LOW_TEMPLATE, "target_temperature_low", self._make_float_updater("_attr_target_temperature_low")),
            (CONF_TARGET_HUMIDITY_TEMPLATE, "target_humidity", self._make_float_updater("_attr_target_humidity")),
            (CONF_MIN_HUMIDITY_TEMPLATE, "min_humidity", self._make_float_updater("_attr_min_humidity")),
            (CONF_MAX_HUMIDITY_TEMPLATE, "max_humidity", self._make_float_updater("_attr_max_humidity")),
            (CONF_HVAC_MODE_TEMPLATE, "hvac_mode", self._make_hvac_mode_updater()),
            (CONF_HVAC_ACTION_TEMPLATE, "hvac_action", self._make_action_updater()),
            (CONF_PRESET_MODE_TEMPLATE, "preset_mode", self._make_str_updater("_attr_preset_mode")),
            (CONF_FAN_MODE_TEMPLATE, "fan_mode", self._make_str_updater("_attr_fan_mode")),
            (CONF_SWING_MODE_TEMPLATE, "swing_mode", self._make_str_updater("_attr_swing_mode")),
            (CONF_MIN_TEMP_TEMPLATE, "min_temp", self._make_float_updater("_attr_min_temp")),
            (CONF_MAX_TEMP_TEMPLATE, "max_temp", self._make_float_updater("_attr_max_temp")),
            (CONF_AVAILABILITY_TEMPLATE, "available", self._make_availability_updater()),
            (CONF_ICON_TEMPLATE, "icon", self._make_str_updater("_attr_icon")),
        ]

        for config_key, attr_name, callback_fn in template_mapping:
            template_str = self._config.get(config_key)
            if template_str is None:
                continue
            template_obj = template_m.Template(template_str, self.hass)
            self._template_cache[config_key] = template_obj
            self._template_callbacks[id(template_obj)] = (attr_name, callback_fn)
            self._track_templates.append(TrackTemplate(template_obj, None))

    def _setup_actions(self) -> None:
        action_configs = [
            (CONF_SET_TEMP_ACTION, "_set_temp_script"),
            (CONF_SET_HVAC_MODE_ACTION, "_set_hvac_script"),
            (CONF_SET_PRESET_MODE_ACTION, "_set_preset_script"),
            (CONF_SET_FAN_MODE_ACTION, "_set_fan_script"),
            (CONF_SET_SWING_MODE_ACTION, "_set_swing_script"),
            (CONF_SET_HUMIDITY_ACTION, "_set_humidity_script"),
        ]

        for config_key, attr_name in action_configs:
            action = self._config.get(config_key)
            if action:
                setattr(
                    self,
                    attr_name,
                    Script(self.hass, action, self._attr_name, DOMAIN),
                )
            else:
                setattr(self, attr_name, None)

    def _setup_features(self) -> None:
        features = ClimateEntityFeature(0)

        if self._config.get(CONF_TARGET_TEMP_TEMPLATE) or self._set_temp_script:
            features |= ClimateEntityFeature.TARGET_TEMPERATURE

        if HVACMode.HEAT_COOL in self._attr_hvac_modes:
            features |= ClimateEntityFeature.TARGET_TEMPERATURE_RANGE

        if self._config.get(CONF_PRESET_MODE_TEMPLATE) or self._set_preset_script:
            features |= ClimateEntityFeature.PRESET_MODE

        if self._config.get(CONF_FAN_MODE_TEMPLATE) or self._set_fan_script:
            features |= ClimateEntityFeature.FAN_MODE

        if self._config.get(CONF_SWING_MODE_TEMPLATE) or self._set_swing_script:
            features |= ClimateEntityFeature.SWING_MODE

        if self._config.get(CONF_TARGET_HUMIDITY_TEMPLATE) or self._set_humidity_script:
            features |= ClimateEntityFeature.TARGET_HUMIDITY

        self._attr_supported_features = features

    def _make_float_updater(self, attr: str):
        @callback
        def _update(value: Any) -> None:
            if value in (STATE_UNKNOWN, STATE_UNAVAILABLE, None):
                return
            try:
                new_val = float(value)
                if getattr(self, attr) != new_val:
                    setattr(self, attr, new_val)
                    self.async_write_ha_state()
            except (ValueError, TypeError):
                pass

        return _update

    def _make_str_updater(self, attr: str):
        @callback
        def _update(value: Any) -> None:
            if value in (STATE_UNKNOWN, STATE_UNAVAILABLE, None):
                return
            new_val = str(value)
            if getattr(self, attr) != new_val:
                setattr(self, attr, new_val)
                self.async_write_ha_state()

        return _update

    def _make_hvac_mode_updater(self):
        @callback
        def _update(value: Any) -> None:
            if value in (STATE_UNKNOWN, STATE_UNAVAILABLE, None):
                return
            try:
                hvac_mode = HVACMode(str(value))
                if hvac_mode in self._attr_hvac_modes and self._attr_hvac_mode != hvac_mode:
                    self._attr_hvac_mode = hvac_mode
                    self.async_write_ha_state()
            except (ValueError, TypeError):
                pass

        return _update

    def _make_action_updater(self):
        @callback
        def _update(value: Any) -> None:
            if value in (STATE_UNKNOWN, STATE_UNAVAILABLE, None):
                if self._attr_hvac_action is not None:
                    self._attr_hvac_action = None
                    self.async_write_ha_state()
                return
            try:
                hvac_action = HVACAction(str(value))
                if self._attr_hvac_action != hvac_action:
                    self._attr_hvac_action = hvac_action
                    self.async_write_ha_state()
            except (ValueError, TypeError):
                pass

        return _update

    def _make_availability_updater(self):
        @callback
        def _update(value: Any) -> None:
            if value in (STATE_UNKNOWN, STATE_UNAVAILABLE, None):
                self._attr_available = True
                self.async_write_ha_state()
                return
            self._attr_available = result_as_boolean(value)
            self.async_write_ha_state()

        return _update

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is not None:
            if last_state.state in self._attr_hvac_modes:
                self._attr_hvac_mode = HVACMode(last_state.state)

            for attr, key in [
                ("_attr_target_temperature", ATTR_TEMPERATURE),
                ("_attr_target_temperature_high", ATTR_TARGET_TEMP_HIGH),
                ("_attr_target_temperature_low", ATTR_TARGET_TEMP_LOW),
                ("_attr_current_temperature", "current_temperature"),
                ("_attr_current_humidity", "current_humidity"),
                ("_attr_target_humidity", ATTR_HUMIDITY),
                ("_attr_fan_mode", ATTR_FAN_MODE),
                ("_attr_preset_mode", ATTR_PRESET_MODE),
                ("_attr_swing_mode", ATTR_SWING_MODE),
            ]:
                if (val := last_state.attributes.get(key)) is not None:
                    try:
                        if attr in ("_attr_fan_mode", "_attr_preset_mode", "_attr_swing_mode"):
                            setattr(self, attr, str(val))
                        else:
                            setattr(self, attr, float(val))
                    except (ValueError, TypeError):
                        pass

            if (hvac_action := last_state.attributes.get("hvac_action")) is not None:
                try:
                    self._attr_hvac_action = HVACAction(hvac_action)
                except (ValueError, TypeError):
                    pass

        if self._track_templates:
            result_info = async_track_template_result(
                self.hass,
                self._track_templates,
                self._handle_template_results,
            )
            self.async_on_remove(result_info.async_remove)
            result_info.async_refresh()

    @callback
    def _handle_template_results(
        self, event, updates: list
    ) -> None:
        for update in updates:
            entry = self._template_callbacks.get(id(update.template))
            if entry is None:
                continue
            _, callback_fn = entry
            callback_fn(update.result)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if self._set_hvac_script is None:
            self._attr_hvac_mode = hvac_mode
            self.async_write_ha_state()
            return
        await self._run_script(
            self._set_hvac_script,
            {ATTR_HVAC_MODE: hvac_mode},
        )

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        if self._set_preset_script is None:
            self._attr_preset_mode = preset_mode
            self.async_write_ha_state()
            return
        await self._run_script(
            self._set_preset_script,
            {ATTR_PRESET_MODE: preset_mode},
        )

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        if self._set_fan_script is None:
            self._attr_fan_mode = fan_mode
            self.async_write_ha_state()
            return
        await self._run_script(
            self._set_fan_script,
            {ATTR_FAN_MODE: fan_mode},
        )

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        if self._set_swing_script is None:
            self._attr_swing_mode = swing_mode
            self.async_write_ha_state()
            return
        await self._run_script(
            self._set_swing_script,
            {ATTR_SWING_MODE: swing_mode},
        )

    async def async_set_temperature(self, **kwargs) -> None:
        updated = False
        if kwargs.get(ATTR_HVAC_MODE, self._attr_hvac_mode) == HVACMode.HEAT_COOL:
            high = kwargs.get(ATTR_TARGET_TEMP_HIGH)
            low = kwargs.get(ATTR_TARGET_TEMP_LOW)
            if high is not None and high != self._attr_target_temperature_high:
                self._attr_target_temperature_high = float(high)
                updated = True
            if low is not None and low != self._attr_target_temperature_low:
                self._attr_target_temperature_low = float(low)
                updated = True
        else:
            temp = kwargs.get(ATTR_TEMPERATURE)
            if temp is not None and temp != self._attr_target_temperature:
                self._attr_target_temperature = float(temp)
                updated = True

        if updated:
            self.async_write_ha_state()

        if operation_mode := kwargs.get(ATTR_HVAC_MODE):
            hvac_mode = HVACMode(operation_mode) if operation_mode else None
            if hvac_mode != self._attr_hvac_mode:
                await self.async_set_hvac_mode(hvac_mode)

        if self._set_temp_script:
            await self._run_script(
                self._set_temp_script,
                {
                    ATTR_TEMPERATURE: kwargs.get(ATTR_TEMPERATURE),
                    ATTR_TARGET_TEMP_HIGH: kwargs.get(ATTR_TARGET_TEMP_HIGH),
                    ATTR_TARGET_TEMP_LOW: kwargs.get(ATTR_TARGET_TEMP_LOW),
                    ATTR_HVAC_MODE: kwargs.get(ATTR_HVAC_MODE),
                },
            )

    async def async_set_humidity(self, humidity: int) -> None:
        if self._set_humidity_script is None:
            self._attr_target_humidity = humidity
            self.async_write_ha_state()
            return
        await self._run_script(
            self._set_humidity_script,
            {ATTR_HUMIDITY: humidity},
        )

    async def _run_script(
        self, script: Script, extra_vars: dict[str, Any]
    ) -> None:
        await script.async_run(
            run_variables={
                **self._variables,
                **extra_vars,
            },
            context=self._context,
        )
