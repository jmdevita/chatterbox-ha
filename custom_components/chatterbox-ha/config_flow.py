"""Config flow for Chatterbox text-to-speech integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_SEED,
    CONF_SERVER_URL,
    CONF_SPEED,
    CONF_VOICE,
    DEFAULT_SEED,
    DEFAULT_SPEED,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


def _format_speech_url(base_url: str) -> str:
    """Formats the user-provided URL into the full speech API endpoint."""

    url = base_url
    if not url.startswith(("http://", "https://")):
        url = f"http://{url}"
    return f"{url.rstrip('/')}/v1/audio/speech"


def _format_voices_url(base_url: str) -> str:
    """Formats the user-provided URL into the full voices API endpoint."""

    url = base_url
    if not url.startswith(("http://", "https://")):
        url = f"http://{url}"
    return f"{url.rstrip('/')}/get_predefined_voices"


class ChatterboxConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Chatterbox text-to-speech."""

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.config_data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step where the user provides the server URL."""

        errors: dict[str, str] = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            base_url = user_input[CONF_SERVER_URL]
            voices_url = _format_voices_url(base_url)

            try:
                _LOGGER.debug("Fetching voices from %s", voices_url)
                async with session.get(voices_url) as response:
                    response.raise_for_status()
                    voices_json = await response.json()

                    self.config_data[CONF_SERVER_URL] = _format_speech_url(base_url)
                    self.config_data["voices"] = [
                        SelectOptionDict(
                            value=voice["filename"], label=voice["display_name"]
                        )
                        for voice in voices_json
                    ]

                    return await self.async_step_settings()

            except aiohttp.ClientError:
                _LOGGER.error("Error connecting to Chatterbox server at %s", base_url)
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error fetching voices")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_SERVER_URL): str}),
            errors=errors,
        )

    async def async_step_settings(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the step where the user selects the voice and other settings."""
        errors: dict[str, str] = {}
        if user_input is not None:
            # Combine data from this step with the stored server URL
            data_to_save = {
                CONF_SERVER_URL: self.config_data[CONF_SERVER_URL],
                CONF_VOICE: user_input[CONF_VOICE],
                CONF_SPEED: user_input[CONF_SPEED],
                CONF_SEED: user_input[CONF_SEED],
            }

            # Use the selected voice's filename for the title
            selected_voice_label = next(
                (
                    v["label"]
                    for v in self.config_data["voices"]
                    if v["value"] == user_input[CONF_VOICE]
                ),
                user_input[CONF_VOICE],
            )

            return self.async_create_entry(
                title=f"Chatterbox TTS ({selected_voice_label})", data=data_to_save
            )

        # Dynamically build the schema for this step using the fetched voices
        settings_schema = vol.Schema(
            {
                vol.Required(CONF_VOICE): SelectSelector(
                    SelectSelectorConfig(
                        options=self.config_data["voices"],
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_SPEED, default=DEFAULT_SPEED): vol.All(
                    vol.Coerce(float), vol.Range(min=0.1, max=5.0)
                ),
                vol.Optional(CONF_SEED, default=DEFAULT_SEED): vol.Coerce(int),
            }
        )

        return self.async_show_form(
            step_id="settings",
            data_schema=settings_schema,
            errors=errors,
        )