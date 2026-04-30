#!/usr/bin/env bash
#!/usr/bin/env bash
# Nordix - screenshoot 
# Version: 1.0
#
#
#

FILE="~/Pictures/Screenshots/Screenshot-$(date).png"


mkdir -p ~/Pictures/Screenshots



# Screenshot
#grimblast save active "$FILE"

grimblast save active ~/Pictures/Screenshots/"Screenshot-$(date)".png 
sleep 2
# Notification

notify-send -t 5000 -h string:x-canonical-private-synchronous:grimblast \
"Screenshot Saved in $HOME/Pictures/Screenshots" "File: $(basename "$FILE")"
