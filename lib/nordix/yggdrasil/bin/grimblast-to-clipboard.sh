#!/usr/bin/env bash
#!/usr/bin/env bash
# Nordix - screenshoot
# Version: 1.0

# Path
FILE="Screenshot-$(date '+%m-%d %H:%M:%S').png"

# Screenshot to clippboard
grimblast save window "$FILE"
sleep 1

# Notification
notify-send -t 5000 -h string:x-canonical-private-synchronous:grimblast \
"Screenshot Saved clipboard" "File: $(basename "$FILE")"

