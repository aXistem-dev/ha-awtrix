"""Awtrix."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import homeassistant.helpers.config_validation as cv
from homeassistant.components import mqtt
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN, Platform
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity_registry import async_entries_for_device, async_get

from .const import DOMAIN, FLAVOR_NG, FLAVOR_V3
from .messages import HANDLERS, UnsupportedError, build

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant, ServiceCall

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR]

# Entity of the device whose state holds the MQTT topic prefix.
PREFIX_ENTITY_V3 = "Device topic"
PREFIX_ENTITY_NG = "MQTT prefix"

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, _: dict):
    """Awtrix integration setup."""

    def make_handler(action: str):
        async def handler(call: ServiceCall) -> None:
            flavor, prefix = _resolve_device(hass, call.data.get("device"))
            data = dict(call.data)
            try:
                messages = build(action, flavor, prefix, data)
            except UnsupportedError as err:
                raise ServiceValidationError(str(err)) from err
            except (KeyError, ValueError, TypeError) as err:
                raise ServiceValidationError(f"Invalid data for awtrix.{action}: {err}") from err

            for message in messages:
                await mqtt.async_publish(hass, message.topic, message.payload)

        return handler

    for action in HANDLERS:
        hass.services.async_register(DOMAIN, action, make_handler(action))

    return True


async def async_setup_entry(_: HomeAssistant, __: ConfigEntry) -> bool:
    """Initialise entry configuration."""
    return True


async def async_unload_entry(_: HomeAssistant, __: ConfigEntry) -> bool:
    """Remove entry after unload component."""
    return True


def _resolve_device(hass: HomeAssistant, device_id: str | None) -> tuple[str, str]:
    """Return ``(flavor, topic prefix)`` for a device, raising a user-facing error if it cannot be resolved."""
    if not device_id:
        raise ServiceValidationError("An Awtrix device is required")

    device = dr.async_get(hass).async_get(device_id)
    is_ng = device is not None and "ng" in (device.model or "").lower().split()

    for entity in async_entries_for_device(async_get(hass), device_id, True):
        if entity.original_name == PREFIX_ENTITY_NG:
            is_ng = True
        elif entity.original_name != PREFIX_ENTITY_V3:
            continue
        state = hass.states.get(entity.entity_id)
        if state is not None and state.state not in ("", STATE_UNKNOWN, STATE_UNAVAILABLE):
            return (FLAVOR_NG if is_ng else FLAVOR_V3), state.state

    raise ServiceValidationError("Could not find the MQTT topic of this Awtrix device; is the device connected to MQTT?")


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old config entries."""
    version = entry.version
    if version < 2:
        if entry.title == "Atriwx":
            hass.config_entries.async_update_entry(entry, title="Awtrix", version=2)

    return True
