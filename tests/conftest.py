"""Fixtures for Chatterbox TTS integration tests."""
import pytest

from homeassistant.const import CONF_SERVER_URL
from custom_components.chatterbox.const import (
    DOMAIN,
    CONF_VOICE,
    CONF_SPEED,
    CONF_SEED,
    DEFAULT_VOICE,
    DEFAULT_SPEED,
    DEFAULT_SEED,
)

@pytest.fixture
def mock_setup_entry():
    """Mock setup entry."""
    return {
        CONF_SERVER_URL: "http://localhost:8004/v1/audio/speech",
        CONF_VOICE: DEFAULT_VOICE,
        CONF_SPEED: DEFAULT_SPEED,
        CONF_SEED: DEFAULT_SEED,
    }