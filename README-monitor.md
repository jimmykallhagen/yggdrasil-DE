# Nordix Monitor Settings

A graphical settings panel for Hyprland monitor configuration in the Yggdrasil desktop environment.

## Overview

Nordix Monitor Settings provides an intuitive GTK4/libadwaita interface for configuring monitors in Hyprland. It supports single and dual monitor setups with full HDR, 10-bit color, and VRR (Variable Refresh Rate) configuration.

## Features

- **Single and Dual Monitor Support** - Easy setup mode selection with recommended workspace assignments
- **HDR Configuration** - Full HDR support including luminance settings, wide color gamut, and SDR brightness mapping
- **10-bit Color** - Enable 10-bit color depth for supported monitors
- **VRR / Adaptive Sync** - Configure variable refresh rate per monitor
- **Color Management** - Multiple color space presets (sRGB, BT2020, HDR, DCI-P3, Adobe RGB, etc.)
- **Scrolling Layout** - Optional scrolling layout for secondary monitor workspace
- **Resolution and Refresh Rate** - Automatic detection of available modes per monitor
- **Scaling and Rotation** - Display scaling from 100% to 200% and rotation/transform options
- **Live Preview** - Apply changes and reload Hyprland configuration instantly

## Dual Monitor Workspace Layout

When using dual monitor mode, the GUI configures workspaces as follows:

- **Secondary Monitor (Left)** - Locked to Workspace 1 with optional scrolling layout
- **Primary Monitor (Right)** - Workspaces 2-10 with workspace 2 as default

This prevents unwanted workspace jumping between monitors and provides a predictable multi-monitor experience.

## HDR Support

### Per-Monitor HDR Settings

- Wide Color Gamut (auto/force on/force off)
- HDR Support (auto/force on/force off)
- SDR Min/Max Luminance for HDR tone mapping
- Monitor luminance values (min, average, max)
- SDR Brightness and Saturation when HDR is active

### Global HDR Settings

- WINE_HDR_ENABLE - HDR support for Wine/Proton games
- ENABLE_HDR_WSI - Wayland HDR WSI support
- DXVK_HDR - DXVK HDR support
- Color Management v4 Protocol
- Prefer HDR Mode (off/always/gamescope only)
- Fullscreen Color Passthrough

## HDR Gaming Quick Reference

### Steam with Gamescope

```
DXVK_HDR=1 gamescope -f --hdr-enabled -- %command%
```

### Steam with Wayland Proton

```
ENABLE_HDR_WSI=1 DXVK_HDR=1 %command%
```

### Non-Steam Wine Games

```
ENABLE_HDR_WSI=1 DXVK_HDR=1 WINE_HDR_ENABLE=1 wine game.exe
```

### MPV Video Player

```
mpv --vo=gpu-next --target-colorspace-hint --gpu-api=vulkan --gpu-context=waylandvk "filename"
```

## Configuration File

Settings are saved to:

```
~/.config/nordix/yggdrasil/settings/nordix-monitors.conf
```

The configuration uses Hyprland's monitorv2 syntax and is automatically reloaded when applying changes.

## Dependencies

- Python 3
- GTK 4
- libadwaita
- Hyprland
- hyprctl (for monitor detection and config reload)

## Installation

The GUI is part of the Yggdrasil desktop environment and is installed automatically with Nordix. It can also be run standalone:

```bash
python3 nordix-monitors-gui.py
```

## Usage

1. Launch from Yggdrasil settings or run directly
2. Select setup mode (Single or Dual Monitor)
3. Configure each monitor's resolution, scale, and features
4. Adjust HDR settings if your monitor supports it
5. Click "Apply" to save and reload Hyprland

## Tips

- Run `wlr-randr` in terminal to see detailed monitor specifications
- For 10-bit color, set Color Management to "wide" or "hdr"
- HDR requires 10-bit color depth to be enabled
- Use "Detect Monitors" button if monitors are not showing correctly

## License

---

**Author:** Jimmy Källhagen  
**Project:** [Nordix](https://github.com/jimmykallhagen/Nordix)  
**License:** SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0  
**Copyright (c) 2025 Jimmy Källhagen**

---
