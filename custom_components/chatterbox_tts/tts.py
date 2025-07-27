"""Support for the Chatterbox TTS service."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from homeassistant.components.tts import TextToSpeechEntity, TtsAudioType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    CONF_SEED,
    CONF_SERVER_URL,
    CONF_SPEED,
    CONF_VOICE,
    DEFAULT_SEED,
    DEFAULT_SPEED,
    DEFAULT_VOICE,
)

_LOGGER = logging.getLogger(__name__)

# Options that can be overridden via the service call
SUPPORT_OPTIONS = ["voice", "speed", "seed"]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Chatterbox speech platform via config entry."""
    server_url = config_entry.data[CONF_SERVER_URL]
    voice = config_entry.data.get(CONF_VOICE, DEFAULT_VOICE)
    speed = config_entry.data.get(CONF_SPEED, DEFAULT_SPEED)
    seed = config_entry.data.get(CONF_SEED, DEFAULT_SEED)

    async_add_entities(
        [ChatterboxTTSEntity(config_entry, server_url, voice, speed, seed)]
    )


class ChatterboxTTSEntity(TextToSpeechEntity):
    """The Chatterbox speech API entity."""

    def __init__(
        self,
        config_entry: ConfigEntry,
        server_url: str,
        voice: str,
        speed: float,
        seed: int,
    ) -> None:
        """Init Chatterbox TTS service."""
        self._server_url = server_url
        self._voice = voice
        self._speed = speed
        self._seed = seed
        self._attr_name = (
            f"Chatterbox TTS ({config_entry.data.get(CONF_VOICE, DEFAULT_VOICE)})"
        )
        self._attr_unique_id = config_entry.entry_id

    @property
    def supported_options(self) -> list[str]:
        """Return a list of supported options."""
        return SUPPORT_OPTIONS

    @property
    def default_language(self) -> str:
        """Return the default language."""
        # This is required for the TTS manager, even if your service doesn't use it.
        # You can use a placeholder like "en"
        return "en"

    @property
    def supported_languages(self) -> list[str]:
        """Return a list of supported languages."""
        # This is required for the TTS manager.
        return [self.default_language]

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any] | None = None
    ) -> TtsAudioType:
        """Load TTS audio from the Chatterbox server."""
        opts = options or {}

        # Get voice, speed, and seed from options, falling back to configured defaults
        voice = opts.get("voice", self._voice)
        speed = opts.get("speed", self._speed)
        seed = opts.get("seed", self._seed)

        request_data = {
            "model": "chatterbox",
            "input": message,
            "voice": voice,
            "response_format": "mp3",
            "speed": speed,
            "seed": seed,
        }

        _LOGGER.debug(
            "Requesting TTS from Chatterbox server with data: %s", request_data
        )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self._server_url, json=request_data
                ) as response:
                    if response.status != 200:
                        # Log the detailed error from the server before raising
                        error_text = await response.text()
                        _LOGGER.error(
                            "Error from Chatterbox server: %s - %s",
                            response.status,
                            error_text,
                        )
                        raise HomeAssistantError(
                            f"Error from Chatterbox server: {response.status} - {error_text}"
                        )

                    audio_data = await response.read()

            # Return the audio format and the binary audio data
            return "mp3", audio_data

        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to Chatterbox server: %s", err)
            raise HomeAssistantError(
                f"Error connecting to Chatterbox server: {err}"
            ) from err
        except Exception as exc:
            _LOGGER.exception("Unexpected error during TTS request")
            raise HomeAssistantError(
                f"Unexpected error during TTS request: {exc}"
            ) from exc