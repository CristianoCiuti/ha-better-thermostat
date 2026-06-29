"""Tests for the Better Thermostat climate entity."""

from homeassistant.components.climate import (
    HVACMode,
    ClimateEntityFeature,
)
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.better_thermostat.const import DOMAIN

from tests.common import MockConfigEntry


async def test_entity_creation(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "name": "Test Thermostat",
            "modes": ["off", "heat"],
            "min_temp": 7,
            "max_temp": 35,
            "temp_step": 1.0,
        },
        entry_id="test_1",
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("climate.test_thermostat")
    assert state is not None
    assert state.state == HVACMode.OFF
    assert state.attributes["hvac_modes"] == [HVACMode.OFF, HVACMode.HEAT]
    assert state.attributes["min_temp"] == 7
    assert state.attributes["max_temp"] == 35
    assert state.attributes["temperature"] == 21.0


async def test_entity_with_fan_mode(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "name": "Fan Thermostat",
            "modes": ["off", "cool", "fan_only"],
            "fan_modes": ["low", "medium", "high"],
        },
        entry_id="test_2",
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("climate.fan_thermostat")
    assert state is not None
    assert state.attributes["fan_modes"] == ["low", "medium", "high"]
    assert state.attributes["fan_mode"] == "low"


async def test_entity_with_preset_mode(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "name": "Preset Thermostat",
            "modes": ["off", "heat"],
            "preset_modes": ["none", "away", "eco"],
        },
        entry_id="test_3",
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("climate.preset_thermostat")
    assert state is not None
    assert state.attributes["preset_modes"] == ["none", "away", "eco"]
    assert state.attributes["preset_mode"] == "none"


async def test_entity_set_hvac_mode_optimistic(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "name": "Optimistic Thermostat",
            "modes": ["off", "heat", "cool"],
        },
        entry_id="test_4",
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("climate.optimistic_thermostat")
    assert state is not None
    assert state.state == HVACMode.OFF

    await hass.services.async_call(
        "climate",
        "set_hvac_mode",
        {"entity_id": "climate.optimistic_thermostat", "hvac_mode": "heat"},
        blocking=True,
    )
    await hass.async_block_till_done()

    state = hass.states.get("climate.optimistic_thermostat")
    assert state.state == HVACMode.HEAT


async def test_entity_set_temperature_optimistic(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "name": "Temp Thermostat",
            "modes": ["off", "heat"],
        },
        entry_id="test_5",
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    await hass.services.async_call(
        "climate",
        "set_temperature",
        {
            "entity_id": "climate.temp_thermostat",
            ATTR_TEMPERATURE: 22.5,
        },
        blocking=True,
    )
    await hass.async_block_till_done()

    state = hass.states.get("climate.temp_thermostat")
    assert state.attributes[ATTR_TEMPERATURE] == 22.5


async def test_entity_features(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "name": "Features Thermostat",
            "modes": ["off", "heat", "cool", "heat_cool"],
            "fan_modes": ["low", "high"],
            "preset_modes": ["none", "away"],
            "swing_modes": ["on", "off"],
        },
        entry_id="test_6",
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("climate.features_thermostat")
    assert state is not None

    entry_registry = er.async_get(hass)
    entry_er = entry_registry.async_get("climate.features_thermostat")
    assert entry_er is not None
    assert entry_er.unique_id == entry.entry_id


async def test_entity_registry(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "name": "Registry Thermostat",
            "modes": ["off", "heat"],
            "unique_id": "registry_test",
        },
        entry_id="test_7",
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    entry_registry = er.async_get(hass)
    entry_er = entry_registry.async_get("climate.registry_thermostat")
    assert entry_er is not None
    assert entry_er.unique_id == entry.entry_id
