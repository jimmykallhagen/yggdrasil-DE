#!/bin/bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2025 Nordix
#
# This configuration is part of Nordix Linux

# Shader Off Script for Nordix Desktop envirorment/Hyprland
# Turns off active shader and resets toggle index

STATE_FILE="/tmp/hypr_shader_index"

# Reset index so next toggle starts from first shaderecho "-1" > "$STATE_FILE"

# Turn off shaders
hyprctl keyword decoration:screen_shader ""

# Show notification (optional)
if command -v notify-send &> /dev/null; then
    notify-send -t 5000 -h string:x-canonical-private-synchronous:shader "Nordix shader's" "OFF"
fi
