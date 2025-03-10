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

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure your settings using either environment variables or a config file:

   **Option 1 (Recommended for Security): Using Environment Variables**
   
   You can set the essential environment variables directly in your terminal:
   
   * **Windows Command Prompt**:
     ```
     set TWITCH_CLIENT_ID=your_client_id
     set TWITCH_CLIENT_SECRET=your_client_secret
     set TWITCH_CHANNEL_NAME=channel_to_monitor
     set DISCORD_WEBHOOK_URL=your_webhook_url
     ```
   
   * **Windows PowerShell**:
     ```
     $env:TWITCH_CLIENT_ID="your_client_id"
     $env:TWITCH_CLIENT_SECRET="your_client_secret"
     $env:TWITCH_CHANNEL_NAME="channel_to_monitor"
     $env:DISCORD_WEBHOOK_URL="your_webhook_url"
     ```
   
   * **macOS/Linux**:
     ```
     export TWITCH_CLIENT_ID=your_client_id
     export TWITCH_CLIENT_SECRET=your_client_secret
     export TWITCH_CHANNEL_NAME=channel_to_monitor
     export DISCORD_WEBHOOK_URL=your_webhook_url
     ```
   
   After setting these variables, run the script in the same terminal session.
   
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

All other settings can be customized through the config file. For advanced users who prefer to set everything through environment variables, see the `.env.template` file for all available options.

#### Making Environment Variables Permanent

To avoid setting environment variables each time you open a new terminal:

* **Windows**:
  1. Search for "Environment Variables" in the Start menu
  2. Click "Edit the system environment variables"
  3. Click "Environment Variables" button
  4. Under "User variables", click "New" to add each variable

* **macOS**:
  Add to your `~/.zshrc` or `~/.bash_profile`:
  ```
  export TWITCH_CLIENT_ID=your_client_id
  export TWITCH_CLIENT_SECRET=your_client_secret
  export TWITCH_CHANNEL_NAME=channel_to_monitor
  export DISCORD_WEBHOOK_URL=your_webhook_url
  ```

* **Linux**:
  Add to your `~/.bashrc` or equivalent shell config file:
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

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.