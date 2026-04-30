#!/usr/bin/env bash


# Path
FILE="Screenshot-$(date).png"

# Screenshot to clippboard

grimblast save window "$FILE"
sleep 2
# Notification
notify-send -t 5000 -h string:x-canonical-private-synchronous:grimblast \
"Screenshot Saved clipboard" "File: $(basename "$FILE")"
