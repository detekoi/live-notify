#!/usr/bin/env python3
"""
Live Notify for Twitch and Discord

A script that polls Twitch API to detect when a channel goes live
and sends customized notifications to a Discord webhook.
"""

import os
import json
import time
import logging
import argparse
import datetime
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('LiveNotify')

class TwitchAPI:
    """Handle authentication and API calls to Twitch"""
    
    BASE_URL = "https://api.twitch.tv/helix"
    AUTH_URL = "https://id.twitch.tv/oauth2/token"
    
    def __init__(self, client_id: str, client_secret: str, debug_api: bool = False):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expiry = 0
        self.debug_api = debug_api
    
    def authenticate(self) -> None:
        """Get OAuth access token from Twitch"""
        if self.access_token and time.time() < self.token_expiry:
            return  # Token still valid
        
        try:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials'
            }
            
            if self.debug_api:
                logger.info(f"Auth request to: {self.AUTH_URL}")
                logger.info(f"Auth headers: {headers}")
                # Don't log full client secret, just the first and last few chars
                safe_data = data.copy()
                if 'client_secret' in safe_data:
                    secret = safe_data['client_secret']
                    if len(secret) > 8:
                        safe_data['client_secret'] = f"{secret[:4]}...{secret[-4:]}"
                    else:
                        safe_data['client_secret'] = "****"
                logger.info(f"Auth data (redacted): {safe_data}")
            
            response = requests.post(self.AUTH_URL, headers=headers, data=data)
            response.raise_for_status()
            data = response.json()
            
            self.access_token = data['access_token']
            # Set expiry time with a 10-minute buffer
            self.token_expiry = time.time() + data['expires_in'] - 600
            logger.info("Successfully authenticated with Twitch API")
        except requests.RequestException as e:
            error_msg = f"Failed to authenticate with Twitch: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    error_msg += f" - Details: {error_details}"
                except:
                    if e.response.text:
                        error_msg += f" - Response: {e.response.text[:200]}"
            logger.error(error_msg)
            raise
    
    def get_stream_info(self, channel_name: str) -> Optional[Dict[str, Any]]:
        """Get stream information for a channel"""
        self.authenticate()  # Ensure we have a valid token
        
        headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}'
        }
        
        try:
            request_url = f"{self.BASE_URL}/streams"
            request_params = {'user_login': channel_name}
            
            if self.debug_api:
                logger.info(f"Stream info request to: {request_url}")
                logger.info(f"Stream info headers: {headers}")
                logger.info(f"Stream info params: {request_params}")
            
            response = requests.get(
                request_url,
                headers=headers,
                params=request_params
            )
            response.raise_for_status()
            data = response.json()
            
            # If data is empty, stream is offline
            if not data['data']:
                return None
            
            # Return the stream info
            return data['data'][0]
        except requests.RequestException as e:
            error_msg = f"Error fetching stream info: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    error_msg += f" - Details: {error_details}"
                except:
                    if e.response.text:
                        error_msg += f" - Response: {e.response.text[:200]}"
            logger.error(error_msg)
            return None


class TwitchStreamInfo:
    """Store and format stream information"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data['id']
        self.user_id = data['user_id']
        self.user_name = data['user_name']
        self.game_name = data['game_name']
        self.title = data['title']
        self.viewer_count = data['viewer_count']
        self.started_at = data['started_at']
        # Add timestamp to thumbnail URL for cache busting
        self.thumbnail_url = data['thumbnail_url'].replace('{width}', '1280').replace('{height}', '720') + f"?t={int(time.time())}"
        self.language = data['language']
        self.url = f"https://twitch.tv/{data['user_login']}"
    
    def format_message(self, template: str) -> str:
        """Replace placeholders in template with actual stream data"""
        return template.format(
            streamer=self.user_name,
            title=self.title,
            game=self.game_name,
            viewers=self.viewer_count,
            url=self.url
        )
    
    def uptime(self) -> str:
        """Calculate stream uptime"""
        start_time = datetime.datetime.fromisoformat(self.started_at.replace('Z', '+00:00'))
        now = datetime.datetime.now(datetime.timezone.utc)
        delta = now - start_time
        
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        return f"{hours}h {minutes}m"
        
    def format_discord_embed(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a rich Discord embed with stream information"""
        embed = {
            "title": self.title if config['notification']['include_title'] else f"{self.user_name} is live on Twitch!",
            "type": "rich",
            "description": self.format_message(config['notification']['message_template']),
            "url": self.url,
            "color": int(config['notification']['embed_color'], 16) if 'embed_color' in config['notification'] else 0xFF0000,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "footer": {
                "text": "Twitch Stream Notification"
            },
            "fields": []
        }
        
        # Add fields based on configuration
        if config['notification']['include_game'] and self.game_name:
            embed["fields"].append({
                "name": "Game",
                "value": self.game_name,
                "inline": True
            })
        
        if config['notification']['include_viewer_count']:
            embed["fields"].append({
                "name": "Viewers",
                "value": str(self.viewer_count),
                "inline": True
            })
            
        embed["fields"].append({
            "name": "Uptime",
            "value": self.uptime(),
            "inline": True
        })
            
        # Add thumbnail if configured
        if config['notification']['include_thumbnail']:
            embed["image"] = {"url": self.thumbnail_url}
            
        return embed


class DiscordNotifier:
    """Handle sending messages to Discord webhook"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_notification(self, stream_info: TwitchStreamInfo, config: Dict[str, Any]) -> bool:
        """Send a notification to Discord about the stream"""
        if not self.webhook_url:
            logger.error("Discord webhook URL is not configured")
            return False
            
        embed = stream_info.format_discord_embed(config)
        
        payload = {
            "embeds": [embed]
        }
        
        # Add content message if specified (appears above embed)
        if 'content_text' in config['notification'] and config['notification']['content_text']:
            payload["content"] = stream_info.format_message(config['notification']['content_text'])
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload
            )
            response.raise_for_status()
            logger.info(f"Successfully sent Discord notification for {stream_info.user_name}")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to send Discord notification: {e}")
            return False


class StreamState:
    """Track the state of a stream and determine when to notify"""
    
    def __init__(self, config: Dict[str, Any]):
        self.last_online = False
        self.last_game = None
        self.last_title = None
        self.last_notification_time = 0
        self.triggered_milestones = set()
        self.config = config
        self.state_file = "stream_state.json"
        self.load_state()
    
    def load_state(self) -> None:
        """Load previous state from file if it exists"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.last_online = data.get('last_online', False)
                    self.last_game = data.get('last_game')
                    self.last_title = data.get('last_title')
                    self.last_notification_time = data.get('last_notification_time', 0)
                    self.triggered_milestones = set(data.get('triggered_milestones', []))
                    logger.info("Loaded previous stream state")
            except Exception as e:
                logger.warning(f"Failed to load state file: {e}")
    
    def save_state(self) -> None:
        """Save current state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({
                    'last_online': self.last_online,
                    'last_game': self.last_game,
                    'last_title': self.last_title,
                    'last_notification_time': self.last_notification_time,
                    'triggered_milestones': list(self.triggered_milestones)
                }, f)
        except Exception as e:
            logger.warning(f"Failed to save state file: {e}")
    
    def should_send_notification(self, stream_info: Optional[TwitchStreamInfo]) -> bool:
        """Determine if a notification should be sent based on current state"""
        current_time = time.time()
        cooldown = self.config['polling'].get('notification_cooldown_minutes', 15) * 60
        
        # Check if stream went from offline to online
        if stream_info and not self.last_online:
            if current_time - self.last_notification_time > cooldown:
                self.last_notification_time = current_time
                return True
            else:
                logger.info("Stream is online but notification is on cooldown")
                return False
        
        # Check for game change notification if enabled
        if (stream_info and self.last_online and 
            self.config['notification'].get('notify_on_game_change', False) and
            stream_info.game_name != self.last_game and
            current_time - self.last_notification_time > cooldown):
            self.last_notification_time = current_time
            return True
            
        return False
    
    def should_send_milestone_notification(self, stream_info: TwitchStreamInfo) -> bool:
        """Check if a viewer milestone has been reached"""
        if not stream_info:
            return False
            
        milestones = self.config['advanced'].get('viewer_milestone_notifications', [])
        
        for milestone in sorted(milestones):
            if (stream_info.viewer_count >= milestone and 
                milestone not in self.triggered_milestones):
                self.triggered_milestones.add(milestone)
                return True
                
        return False
        
    def update_state(self, stream_info: Optional[TwitchStreamInfo]) -> None:
        """Update state based on current stream info"""
        self.last_online = bool(stream_info)
        
        if stream_info:
            self.last_game = stream_info.game_name
            self.last_title = stream_info.title
        else:
            # Reset milestones when stream goes offline
            self.triggered_milestones = set()
            
        self.save_state()


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load configuration from JSON file and environment variables"""
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    config = {
        "twitch": {
            "client_id": os.environ.get("TWITCH_CLIENT_ID", ""),
            "client_secret": os.environ.get("TWITCH_CLIENT_SECRET", ""),
            "channel_name": os.environ.get("TWITCH_CHANNEL_NAME", "")
        },
        "discord": {
            "webhook_url": os.environ.get("DISCORD_WEBHOOK_URL", "")
        },
        "notification": {
            "message_template": os.environ.get(
                "NOTIFICATION_MESSAGE_TEMPLATE", 
                "🔴 **LIVE NOW!** {streamer} is streaming {game}"
            ),
            "content_text": os.environ.get("NOTIFICATION_CONTENT_TEXT", ""),
            "include_title": os.environ.get("NOTIFICATION_INCLUDE_TITLE", "true").lower() == "true",
            "include_game": os.environ.get("NOTIFICATION_INCLUDE_GAME", "true").lower() == "true",
            "include_viewer_count": os.environ.get("NOTIFICATION_INCLUDE_VIEWER_COUNT", "true").lower() == "true",
            "include_thumbnail": os.environ.get("NOTIFICATION_INCLUDE_THUMBNAIL", "true").lower() == "true",
            "include_channel_link": os.environ.get("NOTIFICATION_INCLUDE_CHANNEL_LINK", "true").lower() == "true",
            "embed_color": os.environ.get("NOTIFICATION_EMBED_COLOR", "FF0000"),
            "notify_on_game_change": os.environ.get("NOTIFICATION_NOTIFY_ON_GAME_CHANGE", "false").lower() == "true"
        },
        "polling": {
            "interval_seconds": int(os.environ.get("POLLING_INTERVAL_SECONDS", "60")),
            "offline_check_multiplier": int(os.environ.get("POLLING_OFFLINE_CHECK_MULTIPLIER", "3")),
            "notification_cooldown_minutes": int(os.environ.get("POLLING_NOTIFICATION_COOLDOWN_MINUTES", "15"))
        },
        "advanced": {
            "viewer_milestone_notifications": [int(x) for x in os.environ.get("ADVANCED_VIEWER_MILESTONE_NOTIFICATIONS", "50,100,500,1000").split(",") if x.strip()],
            "silent_mode": os.environ.get("ADVANCED_SILENT_MODE", "false").lower() == "true"
        }
    }
    
    # Try to load config from file and merge with environment variables
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                
            # Merge file config with env vars (env vars take precedence)
            def merge_configs(target, source, prefix=""):
                for key, value in source.items():
                    env_key = f"{prefix}_{key}".upper() if prefix else key.upper()
                    if isinstance(value, dict):
                        if key not in target:
                            target[key] = {}
                        merge_configs(target[key], value, env_key)
                    else:
                        # Only use file value if env var wasn't set
                        if key not in target or (isinstance(target[key], str) and target[key] == ""):
                            target[key] = value
            
            # Deep merge configs
            for section in file_config:
                if section not in config:
                    config[section] = {}
                if isinstance(file_config[section], dict):
                    merge_configs(config[section], file_config[section], section)
                else:
                    if section not in os.environ:  # Only use if not in env
                        config[section] = file_config[section]
            
            logger.info(f"Configuration loaded from {config_path} and environment variables")
        else:
            logger.info("Configuration loaded from environment variables only")
    except Exception as e:
        logger.error(f"Failed to load config file: {e}")
        logger.info("Using configuration from environment variables only")
    
    return config


def main():
    """Main function to run the notifier"""
    parser = argparse.ArgumentParser(description="Live Notify for Twitch and Discord")
    parser.add_argument("--config", default="config.json", help="Path to config file")
    parser.add_argument("--test", action="store_true", help="Send a test notification")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--debug-api", action="store_true", help="Print API request details for debugging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        
    # Set up API debugging if requested
    debug_api = args.debug_api
    
    config = load_config(args.config)
    
    # Check required configuration
    if not config['twitch']['client_id'] or not config['twitch']['client_secret']:
        logger.error("Twitch client ID and secret are required")
        return 1
    
    if not config['twitch']['channel_name']:
        logger.error("Twitch channel name is required")
        return 1
        
    if not config['discord']['webhook_url']:
        logger.error("Discord webhook URL is required")
        return 1
    
    # Initialize components
    twitch_api = TwitchAPI(
        config['twitch']['client_id'],
        config['twitch']['client_secret'],
        debug_api
    )
    
    discord_notifier = DiscordNotifier(config['discord']['webhook_url'])
    stream_state = StreamState(config)
    
    # Test notification if requested
    if args.test:
        logger.info("Sending test notification")
        test_data = {
            "id": "12345",
            "user_id": "67890",
            "user_name": config['twitch']['channel_name'],
            "user_login": config['twitch']['channel_name'].lower(),
            "game_name": "Test Game",
            "title": "Test Stream Title",
            "viewer_count": 42,
            "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "thumbnail_url": f"https://static-cdn.jtvnw.net/previews-ttv/live_user_{config['twitch']['channel_name'].lower()}-{{width}}x{{height}}.jpg",
            "language": "en"
        }
        test_stream = TwitchStreamInfo(test_data)
        discord_notifier.send_notification(test_stream, config)
        return 0
    
    logger.info(f"Starting monitor for channel: {config['twitch']['channel_name']}")
    
    try:
        while True:
            try:
                # Check if stream is online
                stream_data = twitch_api.get_stream_info(config['twitch']['channel_name'])
                
                if stream_data:
                    stream_info = TwitchStreamInfo(stream_data)
                    logger.debug(f"Stream online: {stream_info.title} playing {stream_info.game_name} with {stream_info.viewer_count} viewers")
                    
                    # Check if we should send a notification
                    if stream_state.should_send_notification(stream_info):
                        silent_mode = config['advanced'].get('silent_mode', False)
                        
                        if not silent_mode:
                            discord_notifier.send_notification(stream_info, config)
                        else:
                            logger.info("Silent mode enabled, not sending notification")
                    
                    # Check for viewer milestones
                    if stream_state.should_send_milestone_notification(stream_info):
                        if not config['advanced'].get('silent_mode', False):
                            milestone_config = config.copy()
                            milestone_config['notification']['message_template'] = f"🎉 **Milestone reached!** {stream_info.viewer_count} viewers watching {stream_info.user_name}"
                            discord_notifier.send_notification(stream_info, milestone_config)
                else:
                    logger.debug(f"Stream offline: {config['twitch']['channel_name']}")
                
                # Update state
                stream_state.update_state(stream_info if stream_data else None)
                
                # Sleep for the configured interval
                interval = config['polling']['interval_seconds']
                
                # If stream is offline and multiplier is set, poll less frequently
                if not stream_data and 'offline_check_multiplier' in config['polling']:
                    interval *= config['polling']['offline_check_multiplier']
                    
                logger.debug(f"Sleeping for {interval} seconds")
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                # Sleep for a short time to avoid rapid failure loops
                time.sleep(10)
                
    except KeyboardInterrupt:
        logger.info("Notifier stopped by user")
        return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)