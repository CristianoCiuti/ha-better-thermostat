"""Tests for the Better Thermostat config flow."""

from unittest.mock import patch

from homeassistant import config_entries, data_entry_flow
from homeassistant.core import HomeAssistant

from custom_components.better_thermostat.const import DOMAIN


async def test_config_flow_user(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            "name": "Test Thermostat",
            "mode": ["off", "heat"],
            "min_temp": 7,
            "max_temp": 35,
            "temp_step": 1.0,
        },
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "temperature"


async def test_config_flow_complete(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            "name": "Living Room",
            "modes": ["off", "heat", "cool"],
            "min_temp": 5,
            "max_temp": 40,
            "temp_step": 0.5,
        },
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "temperature"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            "current_temperature_template": "{{ states('sensor.temp') }}",
            "target_temperature_template": "{{ state_attr('climate.thermo', 'temperature') }}",
            "hvac_mode_template": "{{ states('climate.thermo') }}",
        },
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "features"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            "enable_preset": True,
            "enable_fan": False,
            "enable_swing": False,
            "enable_humidity": False,
            "enable_advanced": False,
        },
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "optional"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            "preset_mode_template": "{{ state_attr('climate.thermo', 'preset_mode') }}",
            "preset_modes": "none,away,eco,comfort",
        },
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "advanced"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={},
    )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "Living Room"
    assert result["data"]["name"] == "Living Room"
    assert result["data"]["modes"] == ["off", "heat", "cool"]


async def test_config_flow_minimal(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            "name": "Min Thermostat",
            "modes": ["off", "heat"],
            "min_temp": 7,
            "max_temp": 35,
            "temp_step": 1.0,
        },
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={},
    )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == "Min Thermostat"


async def test_config_flow_duplicate(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            "name": "Unique Thermostat",
            "unique_id": "test_unique",
        },
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={}
    )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            "name": "Duplicate Thermostat",
            "unique_id": "test_unique",
        },
    )
    assert result["type"] == data_entry_flow.FlowResultType.ABORT
    assert result["reason"] == "already_configured"
