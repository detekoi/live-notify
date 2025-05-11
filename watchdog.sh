#!/bin/bash

# Watchdog script for twitch_discord_notifier.py
# This script monitors the notifier process and restarts it if it dies

# Set SCRIPT_DIR to the directory of this script, or override with an environment variable
SCRIPT_DIR="${SCRIPT_DIR:-$(cd "$(dirname "$0")" && pwd)}"
SCRIPT_NAME="twitch_discord_notifier.py"
LOG_FILE="$SCRIPT_DIR/watchdog.log"

cd "$SCRIPT_DIR" || exit 1

log_message() {
    echo "$(date +"%Y-%m-%d %H:%M:%S") - $1" >> "$LOG_FILE"
    echo "$(date +"%Y-%m-%d %H:%M:%S") - $1"
}

log_message "Starting watchdog for $SCRIPT_NAME"

while true; do
    # Check if the script is running
    if ! pgrep -f "$SCRIPT_NAME" > /dev/null; then
        log_message "Process not found. Restarting $SCRIPT_NAME..."
        
        # Start the script
        cd "$SCRIPT_DIR" && python "$SCRIPT_NAME" >> "$SCRIPT_DIR/output.log" 2>> "$SCRIPT_DIR/error.log" &
        
        # Give it some time to start
        sleep 5
        
        # Verify it started
        if pgrep -f "$SCRIPT_NAME" > /dev/null; then
            log_message "$SCRIPT_NAME successfully restarted"
        else
            log_message "Failed to restart $SCRIPT_NAME"
        fi
    fi
    
    # Check every 60 seconds
    sleep 60
done
