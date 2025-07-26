"""Support for the Chatterbox TTS service."""

from __future__ import annotations

from io import BytesIO
import logging
from typing import Any
import aiohttp
import voluptuous as vol

from homeassistant.components.tts import (
    CONF_LANG,
    PLATFORM_SCHEMA as TTS_PLATFORM_SCHEMA,
    Provider,
    TextToSpeechEntity,
    TtsAudioType,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
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

SUPPORT_OPTIONS = ["voice", "speed", "seed"]

PLATFORM_SCHEMA = TTS_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SERVER_URL): str,
        vol.Optional(CONF_VOICE, default=DEFAULT_VOICE): vol.In(SUPPORTED_VOICES),
        vol.Optional(CONF_SPEED, default=DEFAULT_SPEED): vol.All(
            vol.Coerce(float), vol.Range(min=0.25, max=4.0)
        ),
        vol.Optional(CONF_SEED, default=DEFAULT_SEED): vol.Coerce(int),
    }
)


async def async_get_engine(
    hass: HomeAssistant,
    config: ConfigType,
    discovery_info: DiscoveryInfoType | None = None,
) -> ChatterboxProvider:
    """Set up Chatterbox speech component."""
    return ChatterboxProvider(
        hass,
        config[CONF_SERVER_URL],
        config[CONF_VOICE],
        config[CONF_SPEED],
        config[CONF_SEED],
    )


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

    async_add_entities([ChatterboxTTSEntity(config_entry, server_url, voice, speed, seed)])


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
        self._attr_name = f"Chatterbox TTS {voice}"
        self._attr_unique_id = config_entry.entry_id

    @property
    def supported_options(self) -> list[str]:
        """Return a list of supported options."""
        return SUPPORT_OPTIONS

    async def async_get_tts_audio(
        self, message: str, options: dict[str, Any] | None = None
    ) -> TtsAudioType:
        """Load TTS from Chatterbox."""
        opts = options or {}

        request_data = {
            "model": "chatterbox",
            "input": message,
            "voice": opts.get("voice", self._voice),
            "response_format": "mp3",
            "speed": opts.get("speed", self._speed),
            "seed": opts.get("seed", self._seed),
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self._server_url, json=request_data) as response:
                    if response.status != 200:
                        raise HomeAssistantError(
                            f"Error requesting Chatterbox TTS: {response.status}"
                        )
                    audio_data = await response.read()

            return "mp3", audio_data

        except Exception as exc:
            _LOGGER.exception("Error during processing of TTS request: %s", exc)
            raise HomeAssistantError(str(exc)) from exc


class ChatterboxProvider(Provider):
    """The Chatterbox speech API provider."""

    def __init__(
        self,
        hass: HomeAssistant,
        server_url: str,
        voice: str,
        speed: float,
        seed: int,
    ) -> None:
        """Init Chatterbox TTS service."""
        self.hass = hass
        self._server_url = server_url
        self._voice = voice
        self._speed = speed
        self._seed = seed
        self.name = "Chatterbox"

    @property
    def supported_options(self) -> list[str]:
        """Return a list of supported options."""
        return SUPPORT_OPTIONS

    async def async_get_tts_audio(
        self, message: str, language: str, options: dict[str, Any]
    ) -> TtsAudioType:
        """Load TTS from Chatterbox."""
        request_data = {
            "model": "chatterbox",
            "input": message,
            "voice": options.get("voice", self._voice),
            "response_format": "mp3",
            "speed": options.get("speed", self._speed),
            "seed": options.get("seed", self._seed),
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self._server_url, json=request_data) as response:
                    if response.status != 200:
                        _LOGGER.error(
                            "Error requesting Chatterbox TTS: %s", response.status
                        )
                        return None, None
                    audio_data = await response.read()

            return "mp3", audio_data

        except Exception as exc:
            _LOGGER.exception("Error during processing of TTS request: %s", exc)
            return None, None