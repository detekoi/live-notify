# Twitch Stream Discord Notifier

A Python script that polls the Twitch API to detect when a channel goes live and sends customized notifications to a Discord webhook.

## Features

- Automatic notifications when a stream goes live
- Customizable Discord embed notifications
- Game change notifications
- Viewer milestone notifications (e.g., when reaching 50, 100, 500 viewers)
- Configurable polling intervals
- Test notification mode
- State persistence between runs

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure the `config.json` file with your:
   - Twitch API credentials (client ID and secret)
   - Discord webhook URL
   - Channel name to monitor
   - Notification preferences

3. Run the script:
   ```
   python twitch_discord_notifier.py
   ```

## Configuration

Edit the `config.json` file to customize your notification settings.

**Important**: The example credentials in the repository are not valid. You must replace them with your own:

```json
{
  "twitch": {
    "client_id": "YOUR_TWITCH_CLIENT_ID",
    "client_secret": "YOUR_TWITCH_CLIENT_SECRET",
    "channel_name": "CHANNEL_TO_MONITOR"
  },
  "discord": {
    "webhook_url": "YOUR_DISCORD_WEBHOOK_URL"
  },
  "notification": {
    "message_template": "🔴 **LIVE NOW!** {streamer} is streaming {game}",
    "include_title": true,
    "include_game": true,
    "include_viewer_count": true,
    "include_thumbnail": true,
    "notify_on_game_change": false
  },
  "polling": {
    "interval_seconds": 60,
    "offline_check_multiplier": 3,
    "notification_cooldown_minutes": 15
  },
  "advanced": {
    "viewer_milestone_notifications": [50, 100, 500, 1000],
    "silent_mode": false
  }
}
```

## Command Line Options

- `--config PATH`: Specify an alternative config file path
- `--test`: Send a test notification
- `--verbose`: Enable verbose logging

## Getting Twitch API Credentials

1. Create a Twitch Developer account at [dev.twitch.tv](https://dev.twitch.tv/)
2. Register a new application to obtain a client ID and client secret
3. Make sure to use valid credentials - invalid credentials will result in authentication errors like:
   ```
   Failed to authenticate with Twitch: 400 Client Error: Bad Request
   ```

## Troubleshooting

If you encounter errors with Twitch authentication:
- Verify your client ID and client secret are correct
- Ensure your Twitch Developer application has the correct scopes
- Check that your application is approved by Twitch

## License

This project is open-source. Feel free to modify and use it as needed.