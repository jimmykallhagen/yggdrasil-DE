#!/bin/bash
##=========================================================##
 # SPDX-License-Identifier: GPL-3.0-or-later               #
 # Copyright (c) 2025 Jimmy Källhagen                      #
 # Part of Yggdrasil - Nordix desktop environment          #
##=========================================================##
# Fil: /usr/libexec/myde-autostart.sh
# Autostarts all desktop entries in~/.config/autostart

AUTOSTART_DIR="$HOME/.config/autostart"
DESKTOP="Hyprland"

[ -d "$AUTOSTART_DIR" ] || exit 0

for file in "$AUTOSTART_DIR"/*.desktop; do
    [ -f "$file" ] || continue

    # Variabler
    in_entry=false
    exec_cmd=""
    hidden=false
    enabled=true
    only_show_in=""
    not_show_in=""
    try_exec=""

# Read the file line by line
    while IFS= read -r line || [ -n "$line" ]; do
        line="${line%%#*}"         # ta bort kommentarer
        line="${line%%$'\r'}"      # ta bort CR om Windows-fil
        line="${line%"${line##*[![:space:]]}"}"  # trim trailing spaces

        [[ "$line" =~ ^\[Desktop\ Entry\]$ ]] && in_entry=true && continue
        [[ "$line" =~ ^\[.*\]$ ]] && in_entry=false

        if $in_entry; then
            case "$line" in
                Exec=*) exec_cmd="${line#Exec=}" ;;
                Hidden=*) [[ "${line#Hidden=}" == "true" ]] && hidden=true ;;
                X-GNOME-Autostart-enabled=*) [[ "${line#X-GNOME-Autostart-enabled=}" == "false" ]] && enabled=false ;;
                OnlyShowIn=*) only_show_in="${line#OnlyShowIn=}" ;;
                NotShowIn=*) not_show_in="${line#NotShowIn=}" ;;
                TryExec=*) try_exec="${line#TryExec=}" ;;
            esac
        fi
    done < "$file"

    # Check conditions
    $hidden && continue
    ! $enabled && continue
    [[ -n "$only_show_in" ]] && [[ ! "$only_show_in" =~ "$DESKTOP" ]] && continue
    [[ -n "$not_show_in" ]] && [[ "$not_show_in" =~ "$DESKTOP" ]] && continue
    [[ -n "$try_exec" ]] && ! command -v "$try_exec" >/dev/null 2>&1 && continue

# Clear placeholders (%U, %F, %u, %f)
    exec_cmd="${exec_cmd//%U/}"
    exec_cmd="${exec_cmd//%F/}"
    exec_cmd="${exec_cmd//%u/}"
    exec_cmd="${exec_cmd//%f/}"

    # Run the program
    [[ -n "$exec_cmd" ]] && sh -c "$exec_cmd" &
done
