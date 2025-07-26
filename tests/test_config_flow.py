"""Test the Chatterbox TTS config flow."""
from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_SERVER_URL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.chatterbox.const import (
    DOMAIN,
    CONF_VOICE,
    CONF_SPEED,
    CONF_SEED,
    DEFAULT_VOICE,
    DEFAULT_SPEED,
    DEFAULT_SEED,
)

async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    with patch(
        "custom_components.chatterbox.config_flow.validate_input",
        return_value={"title": "Chatterbox TTS (jarvis_voice.wav)"},
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_SERVER_URL: "http://localhost:8004/v1/audio/speech",
                CONF_VOICE: DEFAULT_VOICE,
                CONF_SPEED: DEFAULT_SPEED,
                CONF_SEED: DEFAULT_SEED,
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Chatterbox TTS (jarvis_voice.wav)"
    assert result2["data"] == {
        CONF_SERVER_URL: "http://localhost:8004/v1/audio/speech",
        CONF_VOICE: DEFAULT_VOICE,
        CONF_SPEED: DEFAULT_SPEED,
        CONF_SEED: DEFAULT_SEED,
    }