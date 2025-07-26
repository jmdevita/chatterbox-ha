"""Config flow for Chatterbox text-to-speech integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
import aiohttp

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    CONF_SERVER_URL,
    CONF_VOICE,
    CONF_SPEED,
    CONF_SEED,
    DEFAULT_VOICE,
    DEFAULT_SPEED,
    DEFAULT_SEED,
    SUPPORTED_VOICES,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SERVER_URL): str,
        vol.Optional(CONF_VOICE, default=DEFAULT_VOICE): vol.In(SUPPORTED_VOICES),
        vol.Optional(CONF_SPEED, default=DEFAULT_SPEED): vol.All(
            vol.Coerce(float), vol.Range(min=0.1, max=5.0)
        ),
        vol.Optional(CONF_SEED, default=DEFAULT_SEED): vol.Coerce(int),
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    try:
        async with aiohttp.ClientSession() as session:
            test_data = {
                "model": "chatterbox",
                "input": "Test connection",
                "voice": data[CONF_VOICE],
                "response_format": "mp3",
                "speed": data[CONF_SPEED],
                "seed": data[CONF_SEED],
            }
            
            async with session.post(data[CONF_SERVER_URL], json=test_data) as response:
                if response.status != 200:
                    raise CannotConnect(f"Error connecting to server: {response.status}")

    except aiohttp.ClientError as err:
        raise CannotConnect from err

    return {"title": f"Chatterbox TTS ({data[CONF_VOICE]})"}


class ChatterboxConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Chatterbox text-to-speech."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> ConfigFlowResult:
        """Handle reauthorization."""
        return await self.async_step_user()


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""