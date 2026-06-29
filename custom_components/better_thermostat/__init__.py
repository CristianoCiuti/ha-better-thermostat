"""The Better Thermostat integration."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import SERVICE_RELOAD
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.reload import (
    async_reload_integration_platforms,
    async_setup_reload_service,
)
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    PLATFORMS,
    TEMPLATE_KEYS,
    ACTION_KEYS,
    DEFAULT_MIN_TEMP,
    DEFAULT_MAX_TEMP,
    DEFAULT_TEMP_STEP,
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            cv.ensure_list,
            [
                vol.Schema(
                    {
                        vol.Required("name"): cv.string,
                        vol.Optional("unique_id"): cv.string,
                        vol.Optional("modes", default=["off", "heat"]): cv.ensure_list,
                        vol.Optional("fan_modes"): cv.ensure_list,
                        vol.Optional("preset_modes"): cv.ensure_list,
                        vol.Optional("swing_modes"): cv.ensure_list,
                        vol.Optional("min_temp", default=DEFAULT_MIN_TEMP): vol.Coerce(float),
                        vol.Optional("max_temp", default=DEFAULT_MAX_TEMP): vol.Coerce(float),
                        vol.Optional("temp_step", default=DEFAULT_TEMP_STEP): vol.Coerce(float),
                        vol.Optional("precision"): vol.In([0.1, 0.5, 1.0]),
                        vol.Optional("variables"): dict,
                    }
                ).extend(
                    {vol.Optional(k): cv.template for k in TEMPLATE_KEYS}
                ).extend(
                    {vol.Optional(k): cv.SCRIPT_SCHEMA for k in ACTION_KEYS}
                ),
            ],
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    if DOMAIN not in config:
        return True

    await async_setup_reload_service(hass, DOMAIN, PLATFORMS)

    for conf in config[DOMAIN]:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": "import"},
                data=conf,
            )
        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await async_reload_integration_platforms(hass, DOMAIN, PLATFORMS)
