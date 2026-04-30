#!/usr/bin/env bash

FILE="~/Pictures/Screenshots/Screenshot-$(date).png"


mkdir -p ~/Pictures/Screenshots
# Screenshot


grimblast save area  ~/Pictures/Screenshots/"Screenshot-$(date)".png
sleep 2
# Notification
notify-send -t 5000 -h string:x-canonical-private-synchronous:grimblast \
"Screenshot Saved in ~/Pictures/screenshots" "File: $(basename "$FILE")"


