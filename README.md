# Chatterbox TTS Integration for Home Assistant

This is an unofficial Home Assistant integration for the Chatterbox-TTS-Server, a powerful, self-hosted text-to-speech engine created by devnen.

This integration allows you to use your self-hosted Chatterbox server as a Text-to-Speech (TTS) provider within Home Assistant, enabling you to generate dynamic voice notifications for your automations.

-----

## Prerequisites

Before installing this integration, you must have a running instance of the [Chatterbox-TTS-Server](https://github.com/devnen/Chatterbox-TTS-Server). Please follow the setup instructions in that repository to get your server up and running.

## Installation

The recommended way to install this integration is through the Home Assistant Community Store (HACS).

1.  **Add Custom Repository:**

      * Go to HACS in your Home Assistant.
      * Click on "Integrations", then click the three dots in the top right corner and select "Custom repositories".
      * Add the URL to this repository in the "Repository" field.
      * Select "Integration" as the category.
      * Click "Add".

2.  **Install the Integration:**

      * Search for "Chatterbox TTS" and install it.

3.  **Restart Home Assistant:**

      * Restart your Home Assistant instance to complete the installation.

## Configuration

Configuration is done entirely through the Home Assistant user interface.

1.  **Navigate to Devices & Services:**

      * Go to **Settings** \> **Devices & Services**.
      * Click the **+ Add Integration** button in the bottom right corner.

2.  **Search for Chatterbox TTS:**

      * Search for "Chatterbox TTS" and select it.

3.  **Enter Server URL:**

      * You will be prompted to enter the address of your Chatterbox TTS Server. Provide the base address and port (e.g., `192.168.1.100:8004`).
      * The integration will automatically connect to your server to fetch the list of available voices.

4.  **Configure Voice and Settings:**

      * On the next screen, select your desired default voice from the dropdown menu. This list is dynamically populated from your server.
      * You can also set the default speech speed and a random seed value if desired.
      * Click "Submit".

The integration is now configured and ready to use\!

## Usage

You can use the Chatterbox TTS service in your automations and scripts. The entity will be named based on the voice you selected during setup (e.g., `tts.chatterbox_tts_abigail`).

### Basic Example

Here is a basic example of how to use the service in a script to broadcast a message to a media player.

```yaml
- alias: "Announce Visitor"
  sequence:
    - service: tts.speak
      target:
        entity_id: tts.chatterbox_tts_abigail # Use the entity name from your setup
      data:
        media_player_entity_id: media_player.living_room_speaker
        message: "Hello, someone is at the front door."
```

### Overriding Default Options

You can override the default `voice`, `speed`, and `seed` directly in your service call. This is useful for creating dynamic announcements with different voice characteristics.

```yaml
- alias: "Critical Alert"
  sequence:
    - service: tts.speak
      target:
        entity_id: tts.chatterbox_tts_abigail
      data:
        media_player_entity_id: media_player.living_room_speaker
        message: "Warning: Water leak detected in the basement."
        options:
          voice: "Adrian.wav"  # Override the default voice
          speed: 1.2           # Speak slightly faster, but may cause echoing
          seed: 12345          # Use a specific seed for consistency
```

## Credits

  * This integration was created to work with the excellent **Chatterbox-TTS-Server** by **devnen** and the [Chatterbox-TTS](https://github.com/resemble-ai/chatterbox) work by the Resemble.AI team. Thank you!