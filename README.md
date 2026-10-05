# HA Awtrix

This component uses the MQTT API of [Awtrix 3](https://blueforcer.github.io/awtrix3/#/) and of [AWTRIX NG](https://github.com/Blueforcer/awtrix-ng) in Home Assistant easily by adding several additional actions.

Both firmwares are supported by the same actions: the integration detects which one a device runs and publishes to the matching MQTT topics. Awtrix 3 field names keep working on AWTRIX NG (they are translated), and AWTRIX NG's own option names can be used directly.

## Installation

### HACS

You can add the component automatically using HACS by clicking the following link:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=miguelangellv&repository=ha-awtrix&category=integration)

### Manual

You can install the component manually by copying the contents of the `custom_components/ha_awtrix` folder into the `custom_components` folder of your configuration.

## Configuration

Once installed, go to _Devices and Services -> Add Integration_ and search for _Awtrix_. After adding it, you will have the new actions available.

You MUST have configured your device MQTT settings to connect correctly to your mqtt server before being able to see the device using the awtrix actions bellow. If you skip this step you'll have "no matching device" message in the dropdown menu of the actions.

Ex. 

<img width="461" height="286" alt="image" src="https://github.com/user-attachments/assets/9c20324f-13e6-48f4-9ff4-26df2b796613" />

Click, save configurations and then Restart ESP. You can use default mqtt user/pass but it's a good security practice to add one dedicated to this device in the addon configuration.

## Actions

### Awtrix Settings

The `awtrix.settings` action allows you to configure various parameters of the Awtrix display, such as brightness, clock settings, enabling and disabling applications, etc.

### Awtrix Notification

The `awtrix.notification` action allows you to send notifications to the Awtrix display. It has many options to customize the notification according to your needs.

### Awtrix Custom APP

The `awtrix.custom_app` action allows you to create and update custom Awtrix applications. You can create custom applications with various elements such as text, icons, etc.

### More actions

| Action | Awtrix 3 | AWTRIX NG | What it does |
|---|---|---|---|
| `awtrix.dismiss` | yes | yes | Dismiss the active notification (NG: or one sent with a `name`) |
| `awtrix.delete_custom_app` | yes | yes | Remove a custom app |
| `awtrix.switch_app` | yes | yes | Switch to an app (NG: optionally `fast`) |
| `awtrix.next_app` / `awtrix.previous_app` | yes | yes | Step through the rotation |
| `awtrix.power` | yes | yes | Matrix on/off |
| `awtrix.overlay` | yes | yes | Device-wide weather overlay: `rain`, `snow`, `drizzle`, `storm`, `thunder`, `frost` or `clear` |
| `awtrix.moodlight` | yes | yes | Moodlight colour/brightness (or off) |
| `awtrix.indicator` | yes | yes | The three indicator pixels: colour, blink, fade |
| `awtrix.play_sound` | `sound`, `rtttl` | `sound`, `rtttl`, `mp3`, `melody`, `track`, `station`, `index`, `url` | Play a sound or start the radio; give exactly one field |
| `awtrix.stop_sound` | - | yes | Stop sounds and/or the radio stream |
| `awtrix.app_order` | yes | yes | Order of the app rotation and which apps are switched off |
| `awtrix.deep_sleep` | yes | yes | Deep sleep, in seconds |
| `awtrix.reboot` | yes | yes | Reboot |
| `awtrix.update_firmware` | yes | - | Start the OTA update |
| `awtrix.reset_settings` | - | yes | Clear stored settings and reboot |
| `awtrix.get_screen` | - | yes | Publish the current screen to `<prefix>/state/screen` |

Calling an action on a firmware that does not have it fails with a clear error instead of publishing nothing.

## AWTRIX NG

AWTRIX NG devices show up through MQTT discovery (enable *HA discovery* on the device). The integration finds the topic prefix from the device's `MQTT prefix` entity, or from `Device topic` on Awtrix 3.

On an NG device the existing actions translate the Awtrix 3 vocabulary, for example:

- `color` -> `textColor`, `background` -> `backgroundColor`, `progressC`/`progressBC` -> `progressColor`/`progressTrackColor`
- `duration`/`lifetime` (seconds) -> `durationMs`/`lifetimeMs`
- `bar`/`line` -> `barChart`/`lineChart`, `pushIcon` -> `iconMode`, `rtttl` -> `soundRtttl`
- `draw` commands (`{"dp": [...]}`) -> NG draw arrays (`["pixel", ...]`)
- settings such as `BRI`, `ATIME`, `TEFF`, `TSPEED`, `CEL`, `WD`, `OVERLAY`, `MATP` -> `brightness`, `appDurationMs`, `transitionEffect`, ...

Anything that is not an Awtrix 3 key is passed through untouched, so NG-only options (`overlay`, `effect`, `effectSpeed`, `palette`, `paletteBlend`, `font`, `scroll`, `transitionEffect`, `timeMode`, ...) work directly in the same actions. Awtrix 3 options with no NG equivalent (for example `TMODE`, `topText`, the per-app toggles `TIM`/`DAT`/`HUM`/`TEMP`/`BAT`) are ignored on NG; use `awtrix.app_order` for the app toggles.

## Development

The topic and payload logic lives in `messages.py` and `translate.py` and has no Home Assistant dependency:

```
python -m unittest discover -s tests -t .
```
