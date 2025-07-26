"""Test the Chatterbox TTS component."""
from unittest.mock import patch
import pytest

from homeassistant.components.tts import DOMAIN as TTS_DOMAIN
from homeassistant.const import CONF_SERVER_URL
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

from custom_components.chatterbox.const import (
    DOMAIN,
    CONF_VOICE,
    CONF_SPEED,
    CONF_SEED,
    DEFAULT_VOICE,
    DEFAULT_SPEED,
    DEFAULT_SEED,
)

async def test_tts_service(hass: HomeAssistant) -> None:
    """Test the TTS service."""
    config = {
        TTS_DOMAIN: {
            "platform": DOMAIN,
            CONF_SERVER_URL: "http://localhost:8004/v1/audio/speech",
            CONF_VOICE: DEFAULT_VOICE,
            CONF_SPEED: DEFAULT_SPEED,
            CONF_SEED: DEFAULT_SEED,
        }
    }

    with patch("custom_components.chatterbox.tts.ChatterboxProvider.async_get_tts_audio") as mock_get_tts:
        mock_get_tts.return_value = ("mp3", b"audio data")
        assert await async_setup_component(hass, TTS_DOMAIN, config)
        await hass.async_block_till_done()

        await hass.services.async_call(
            TTS_DOMAIN,
            "speak",
            {
                "entity_id": "tts.chatterbox",
                "message": "Hello world",
            },
            blocking=True,
        )
        assert mock_get_tts.called
        assert mock_get_tts.call_args[0][0] == "Hello world"