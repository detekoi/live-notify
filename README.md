# Live Notify for Twitch and Discord

A Python script that polls the Twitch API to detect when a channel goes live and sends customized notifications to a Discord webhook.

## Features

- Automatic notifications when a stream goes live
- Customizable Discord embed notifications
- Game change notifications
- Viewer milestone notifications (e.g., when reaching 50, 100, 500 viewers)
- Configurable polling intervals
- Test notification mode
- State persistence between runs
- Robust error handling with retry logic
- Network connectivity checking
- Watchdog service to auto-restart on failures

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure your settings using either environment variables or a config file:

   **Option 1 (Recommended for Security): Using Environment Variables**
   
   You can set the essential environment variables directly in your terminal or create a `.env` file in the project directory:
   
   ```
   TWITCH_CLIENT_ID=your_client_id
   TWITCH_CLIENT_SECRET=your_client_secret
   TWITCH_CHANNEL_NAME=channel_to_monitor
   DISCORD_WEBHOOK_URL=your_webhook_url
   ```
   
   **Option 2: Using Config File**
   
   If you prefer using a config file:
   ```
   cp config.template.json config.json
   ```
   
   Then edit `config.json` with your favorite text editor and add your credentials.
   
   **IMPORTANT**: Never commit files with real credentials to public repositories

3. Run the script:
   ```
   python twitch_discord_notifier.py
   ```

## Configuration

You can customize the notifier using environment variables (recommended) or a config file. Environment variables take precedence over the config file if both are present.

### Environment Variables

The following environment variables are essential for using the application:

**Required Settings:**
```
TWITCH_CLIENT_ID=your_client_id
TWITCH_CLIENT_SECRET=your_client_secret
TWITCH_CHANNEL_NAME=channel_to_monitor
DISCORD_WEBHOOK_URL=your_webhook_url
```

**Optional Settings:**
```
NOTIFICATION_MESSAGE_TEMPLATE=🔴 **LIVE NOW!** {streamer} is streaming {game}
NOTIFICATION_INCLUDE_TITLE=true
NOTIFICATION_INCLUDE_GAME=true
NOTIFICATION_INCLUDE_VIEWER_COUNT=true
NOTIFICATION_INCLUDE_THUMBNAIL=true
NOTIFICATION_EMBED_COLOR=FF0000
POLLING_INTERVAL_SECONDS=60
POLLING_OFFLINE_CHECK_MULTIPLIER=3
POLLING_NOTIFICATION_COOLDOWN_MINUTES=15
ADVANCED_VIEWER_MILESTONE_NOTIFICATIONS=50,100,500,1000
ADVANCED_SILENT_MODE=false
```

#### Making Environment Variables Permanent

To avoid setting environment variables each time you open a new terminal:

* **Using .env file (Recommended)**:
  Create a `.env` file in the project directory with your variables.

* **macOS/Linux**:
  Add to your `~/.zshrc` or `~/.bash_profile`:
  ```
  export TWITCH_CLIENT_ID=your_client_id
  export TWITCH_CLIENT_SECRET=your_client_secret
  export TWITCH_CHANNEL_NAME=channel_to_monitor
  export DISCORD_WEBHOOK_URL=your_webhook_url
  ```

### Config File

Alternatively, you can use a `config.json` file with this structure:

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
    "notify_on_game_change": false,
    "embed_color": "FF0000"
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
- `--debug-api`: Print API request details for debugging

## Using the Watchdog Service

To ensure the script keeps running even if it encounters errors, you can use the included watchdog service:

1. Make the watchdog script executable:
   ```
   chmod +x watchdog.sh
   ```

2. Start the watchdog:
   ```
   ./watchdog.sh
   ```

The watchdog will monitor the main script and restart it automatically if it crashes.

## Setting Up as a System Service (macOS)

For a more permanent solution on macOS, you can set up the script as a LaunchAgent:

1. Copy the provided plist file to your LaunchAgents directory:
   ```
   cp com.user.twitch-discord-notifier.plist ~/Library/LaunchAgents/
   ```

2. Load the LaunchAgent:
   ```
   launchctl load ~/Library/LaunchAgents/com.user.twitch-discord-notifier.plist
   ```

The service will now start automatically when you log in and will be restarted if it crashes.

## Getting Twitch API Credentials

1. Create a Twitch Developer account at [dev.twitch.tv](https://dev.twitch.tv/)
2. Register a new application to obtain a client ID and client secret
3. Make sure to use valid credentials - invalid credentials will result in authentication errors like:
   ```
   Failed to authenticate with Twitch: 400 Client Error: Bad Request
   ```

## Troubleshooting

### Common Issues

#### Network Connectivity Problems
If you see errors like:
```
Error fetching stream info: HTTPSConnectionPool(host='api.twitch.tv', port=443): Max retries exceeded with url: /helix/streams?user_login=channelname (Caused by NameResolutionError("<urllib3.connection.HTTPSConnection object at 0x...>: Failed to resolve 'api.twitch.tv' ([Errno 8] nodename nor servname provided, or not known)"))
```

This indicates DNS resolution or network connectivity issues. The script now includes:
- Network connectivity checks before making API calls
- Automatic retry logic with exponential backoff
- A watchdog service that restarts the script if it crashes

#### Authentication Issues
If you encounter errors with Twitch authentication:
- Verify your client ID and client secret are correct
- Ensure your Twitch Developer application has the correct scopes
- Check that your application is approved by Twitch

### Log Files
The script generates log files that can help with troubleshooting:
- `output.log`: Contains standard output messages
- `error.log`: Contains error messages
- `watchdog.log`: Contains watchdog service logs

## License

This project is licensed under the BSD 2-Clause License - see the [LICENSE](LICENSE) file for details.