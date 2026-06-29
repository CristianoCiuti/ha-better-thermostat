# Better Thermostat

[![GitHub Release](https://img.shields.io/github/v/release/CristianoCiuti/ha-better-thermostat)](https://github.com/CristianoCiuti/ha-better-thermostat/releases)
[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/CristianoCiuti/ha-better-thermostat)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2026.6-%23049BD9)](https://www.home-assistant.io/)

A custom Home Assistant integration for creating **template-driven climate entities** with full **UI-based configuration**. Create virtual thermostats whose state is computed from templates and whose commands trigger arbitrary scripts or services.

Inspired by [jcwillox/hass-template-climate](https://github.com/jcwillox/hass-template-climate), rewritten from scratch for modern Home Assistant (2026.6+) — no dependency on deprecated internal template APIs.

---

## Features

- **Template-driven reads** — every climate attribute (current temperature, target, HVAC mode, action, preset, fan, swing, humidity, min/max temp, availability, icon) can be computed from a Jinja2 template referencing any entity in your system.
- **Script-driven writes** — `set_temperature`, `set_hvac_mode`, `set_preset_mode`, `set_fan_mode`, `set_swing_mode`, and `set_humidity` each support a full Home Assistant action sequence (service calls, conditions, choices, delays, etc.).
- **Optimistic mode** — when no read template is configured for an attribute, the entity assumes the command succeeded and updates state immediately.
- **State restoration** — the entity restores its last known state (target temperature, HVAC mode, etc.) across restarts.
- **UI configuration** — create and modify entities entirely from the Home Assistant UI (no YAML editing required once installed).
- **YAML import** — for power users, you can also define entities via `configuration.yaml` and they will be imported as config entries on first load.
- **Supports all HVAC features** — heat, cool, heat_cool, auto, dry, fan_only; preset, fan, swing, humidity modes.
- **Trigger-based templates supported** — the entity uses `async_track_template_result` internally, so templates react instantly when referenced entities change state.

---

## Installation

### Via HACS (recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed in your Home Assistant.
2. Add this repository as a custom HACS repository:
   - Go to **HACS → Integrations → Three-dot menu → Custom repositories**
   - URL: `https://github.com/CristianoCiuti/ha-better-thermostat`
   - Category: **Integration**
3. Click **Install**.
4. Restart Home Assistant.

### Manual installation

1. Download the latest release from [GitHub releases](https://github.com/CristianoCiuti/ha-better-thermostat/releases).
2. Extract the `custom_components/better_thermostat/` folder into your Home Assistant `custom_components/` directory.
3. Restart Home Assistant.

---

## Configuration

### UI Configuration (recommended)

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Better Thermostat** and select it.
3. Follow the multi-step wizard:

| Step | Fields | Description |
|------|--------|-------------|
| **1. Basic** | Name, Modes, Min/Max Temp, Temp Step | Core identity and HVAC capabilities. Modes: `off`, `heat`, `cool`, `heat_cool`, `auto`, `dry`, `fan_only`. |
| **2. Temperature & HVAC** | Templates & Actions for temperature and HVAC mode | Input Jinja2 templates for reading state, YAML action sequences for writing. |
| **3. Optional Features** | Enable/disable preset, fan, swing, humidity, advanced settings | Toggle which extra features you want to configure. |
| **4. Feature Config** | Templates, mode lists, and actions for each enabled feature | Comma-separated mode lists (e.g. `none,away,eco,comfort`), YAML actions. |
| **5. Advanced** | Min/max temp templates, availability template, icon template, precision, variables | Override static temp bounds dynamically, set availability, extra template variables. |

### YAML Configuration

You can also define entities in `configuration.yaml` and they will be auto-imported as UI-managed config entries on first startup:

```yaml
# configuration.yaml
better_thermostat:
  - name: "Living Room Thermostat"
    unique_id: living_room_thermo
    modes:
      - "off"
      - "heat"
      - "cool"
      - "auto"
    min_temp: 10
    max_temp: 30
    temp_step: 0.5
    precision: 0.5

    # Templates (reading)
    current_temperature_template: "{{ state_attr('climate.living_room', 'current_temperature') | float }}"
    target_temperature_template: "{{ state_attr('climate.living_room', 'temperature') | float }}"
    hvac_mode_template: "{{ states('climate.living_room') }}"
    hvac_action_template: "{{ state_attr('climate.living_room', 'hvac_action') }}"
    preset_mode_template: "{{ state_attr('climate.living_room', 'preset_mode') }}"
    preset_modes:
      - none
      - away
      - comfort
      - eco
      - home
      - sleep

    # Actions (writing)
    set_temperature:
      - service: climate.set_temperature
        target:
          entity_id: climate.living_room
        data:
          temperature: "{{ temperature }}"
    set_hvac_mode:
      - service: climate.set_hvac_mode
        target:
          entity_id: climate.living_room
        data:
          hvac_mode: "{{ hvac_mode }}"
    set_preset_mode:
      - service: climate.set_preset_mode
        target:
          entity_id: climate.living_room
        data:
          preset_mode: "{{ preset_mode }}"
```

After restart, the entity appears in **Settings → Devices & Services → Better Thermostat** where you can edit it from the UI. Remove the YAML block once imported if you prefer full UI management.

---

## Template & Action Reference

All template fields accept [Home Assistant Jinja2 templates](https://www.home-assistant.io/docs/configuration/templating/). All action fields accept [Home Assistant action sequences](https://www.home-assistant.io/docs/scripts/) (YAML lists of service calls, conditions, etc.).

### Read Templates

| Config Key | Attribute | Type | Description |
|------------|-----------|------|-------------|
| `current_temperature_template` | Current temperature | float | Raw sensor value or derived from other entities |
| `current_humidity_template` | Current humidity | float | |
| `target_temperature_template` | Target temperature | float | |
| `target_temperature_high_template` | Target high (heat_cool) | float | |
| `target_temperature_low_template` | Target low (heat_cool) | float | |
| `hvac_mode_template` | HVAC mode | string | Must be one of: `off`, `heat`, `cool`, `heat_cool`, `auto`, `dry`, `fan_only` |
| `hvac_action_template` | HVAC action | string | Must be one of: `off`, `heating`, `cooling`, `drying`, `idle`, `fan`, `preheating`, `defrosting` |
| `preset_mode_template` | Preset mode | string | Must be in your `preset_modes` list |
| `fan_mode_template` | Fan mode | string | Must be in your `fan_modes` list |
| `swing_mode_template` | Swing mode | string | Must be in your `swing_modes` list |
| `target_humidity_template` | Target humidity | float | |
| `min_humidity_template` | Min humidity | float | |
| `max_humidity_template` | Max humidity | float | |
| `min_temp_template` | Min temperature | float | Overrides the static `min_temp` setting |
| `max_temp_template` | Max temperature | float | Overrides the static `max_temp` setting |
| `availability_template` | Available | boolean | If the template returns `true`, the entity is available. If any other value, unavailable. If not configured, always available. |
| `icon_template` | Icon | string | Must be a valid [Material Design Icon](https://pictogrammers.com/library/mdi/) (e.g. `mdi:home-thermometer`) |

### Write Actions

Each action receives template variables from the user's interaction:

| Config Key | Available Variables | Description |
|------------|-------------------|-------------|
| `set_temperature` | `temperature`, `target_temp_high`, `target_temp_low`, `hvac_mode` | Called when user changes temperature in the UI |
| `set_hvac_mode` | `hvac_mode` | Called when user changes HVAC mode |
| `set_preset_mode` | `preset_mode` | Called when user changes preset |
| `set_fan_mode` | `fan_mode` | Called when user changes fan mode |
| `set_swing_mode` | `swing_mode` | Called when user changes swing mode |
| `set_humidity` | `humidity` | Called when user changes target humidity |

### Template Variables

If you configure `variables` (as a YAML dictionary), they are passed to every action script. The `this` variable is automatically available and points to the entity itself.

### Optimistic Behavior

- If a **read template** is configured, the attribute's value comes from the template (external system).
- If a **read template** is NOT configured but a **write action** is, the entity updates **optimistically** — it immediately reflects the user's command as the new state.
- If neither is configured, the corresponding feature is not advertised (no UI controls for it).

---

## Example: Thermostat Proxy with Scheduling

Recreate the setup from the original `climate.yaml` — a thermostat that proxies another climate entity with a virtual `auto` mode for scheduling:

```yaml
better_thermostat:
  - name: "Bathroom Scheduled"
    unique_id: bathroom_scheduled
    modes:
      - "off"
      - "heat"
      - "auto"
    temp_step: 0.1
    current_temperature_template: "{{ state_attr('climate.bathroom', 'current_temperature') | float }}"
    target_temperature_template: "{{ state_attr('climate.bathroom', 'temperature') | float }}"
    min_temp_template: "{{ state_attr('climate.bathroom', 'min_temp') | float }}"
    max_temp_template: "{{ state_attr('climate.bathroom', 'max_temp') | float }}"
    hvac_action_template: "{{ state_attr('climate.bathroom', 'hvac_action') }}"
    preset_mode_template: "{{ state_attr('climate.bathroom', 'preset_mode') }}"
    preset_modes:
      - none
      - away
      - comfort
      - eco
      - home
      - sleep
    set_preset_mode:
      choose:
        - conditions: "{{ states('climate.bathroom_scheduled') == 'auto' }}"
          sequence:
            - service: climate.set_temperature
              target:
                entity_id: climate.bathroom_scheduled
              data:
                temperature: "{{ state_attr('climate.climate_scheduler_bathroom','temperature') | float }}"
        - conditions: "{{ states('climate.bathroom_scheduled') != 'auto' }}"
          sequence:
            - service: climate.set_preset_mode
              target:
                entity_id: climate.bathroom
              data:
                preset_mode: "{{ preset_mode }}"
    set_temperature:
      choose:
        - conditions: "{{ states('climate.bathroom_scheduled') == 'auto' }}"
          sequence:
            - service: climate.set_temperature
              target:
                entity_id: climate.bathroom_scheduled
              data:
                temperature: "{{ state_attr('climate.climate_scheduler_bathroom','temperature') | float }}"
        - conditions: "{{ states('climate.bathroom_scheduled') != 'auto' }}"
          sequence:
            - service: climate.set_temperature
              target:
                entity_id: climate.bathroom
              data:
                temperature: "{{ temperature }}"
    set_hvac_mode:
      choose:
        - conditions: "{{ hvac_mode == 'auto' }}"
          sequence:
            - service: climate.set_hvac_mode
              target:
                entity_id: climate.bathroom
              data:
                hvac_mode: "heat"
        - conditions: "{{ hvac_mode in ['heat','off'] }}"
          sequence:
            - service: climate.set_hvac_mode
              target:
                entity_id: climate.bathroom
              data:
                hvac_mode: "{{ hvac_mode }}"
```

When the proxy is in `auto` mode, temperature changes are forwarded to a `climate_scheduler` entity. When not in `auto`, changes pass through to the real thermostat. Switching to `auto` forces the real thermostat to `heat` mode.

---

## Services

### `better_thermostat.reload`

Reload all entities defined via YAML under `better_thermostat:` in `configuration.yaml`. This is useful when you edit the YAML config and don't want to restart HA.

```yaml
service: better_thermostat.reload
```

---

## Development

### Requirements

- Python 3.13+
- Home Assistant 2026.6+

### Running Tests

```bash
pip install -r requirements-test.txt
pip install pytest-homeassistant-custom-component
pytest tests/
```

### Project Structure

```
custom_components/better_thermostat/
├── __init__.py          # Integration setup, YAML config import
├── climate.py           # BetterThermostatEntity (ClimateEntity + RestoreEntity)
├── config_flow.py       # ConfigFlow + OptionsFlow (5-step wizard)
├── const.py             # Constants and configuration keys
├── manifest.json        # Component manifest
├── services.yaml        # Service definitions
└── strings.json         # UI translations (Italian)
```

---

## Migration from hass-template-climate

If you were using `jcwillox/hass-template-climate` (the `climate_template` platform), here is what changed:

1. **Install** Better Thermostat via HACS or manually.
2. **Create entities** via UI or paste your YAML config under `better_thermostat:`.
3. **Remove** the old `climate: - platform: climate_template` block from your `configuration.yaml`.
4. **Restart** Home Assistant.

Your existing template strings and action sequences are compatible — the configuration keys are identical.

---

## License

MIT
