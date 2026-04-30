#!/bin/bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2025 Nordix

# term-run - Auto-detects and runs terminal commands

TERM_CMD="$1"

if [ -z "$TERM_CMD" ]; then
    echo "Usage: term-run <command>"
    echo "Example: term-run 'htop'"
    exit 1
fi

# Detect default terminal from mimeapps
MAIN_TERM="$(grep 'x-terminal-emulator' ~/.config/mimeapps.list | cut -d'=' -f2 | awk -F'.' '{print $(NF-1)}')"

# Fallback list
TERMINALS=("wezterm" "ghostty" "cosmic-term" "alacritty" "kitty" "foot" "gnome-terminal" "konsole" "xterm" "urxvt")

# Put default terminal first if found
if [ -n "$MAIN_TERM" ]; then
    TERMINALS=("$MAIN_TERM" "${TERMINALS[@]}")
fi

run_in_terminal() {
    local term="$1"
    local cmd="$2"
    case "$term" in
        "wezterm")
            exec wezterm start -- sh -c "$cmd"
            ;;
        "ghostty")
            exec ghostty -e sh -c "$cmd"
            ;;
        "cosmic-term")
            exec cosmic-term -e sh -c "$cmd"
            ;;
        "alacritty")
            exec alacritty -e sh -c "$cmd"
            ;;
        "kitty")
            exec kitty --hold sh -c "$cmd"
            ;;
        "foot")
            exec foot sh -c "$cmd"
            ;;
        "gnome-terminal")
            exec gnome-terminal -- sh -c "$cmd"
            ;;
        "konsole")
            exec konsole -e sh -c "$cmd"
            ;;
        "xterm")
            exec xterm -e sh -c "$cmd"
            ;;
        "urxvt")
            exec urxvt -e sh -c "$cmd"
            ;;
        *)
            exec "$term" -e sh -c "$cmd"
            ;;
    esac
}

for term in "${TERMINALS[@]}"; do
    if command -v "$term" >/dev/null 2>&1; then
        run_in_terminal "$term" "$TERM_CMD"
    fi
done

echo "Error: No terminal found!"
exit 1
