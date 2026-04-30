#!/usr/bin/env python3
##=========================================================##
 # SPDX-License-Identifier: GPL-3.0-or-later               #
 # Copyright (c) 2025 Jimmy Källhagen                      #
 # Part of Yggdrasil - Nordix desktop environment          #
##=========================================================##

"""Yggdrasil Hyprland Decorations GUI
A graphical settings panel for Hyprland window decorations"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib
import subprocess
import re
import shutil
from pathlib import Path

# Config path
CONFIG_PATH = Path.home() / ".config/nordix/yggdrasil/settings/Yggdrasil-decorations.conf"

# Nordix color palette from colors.conf
NORDIX_COLORS = {
    '$nordix-pblack': {'name': 'Pure Black', 'rgba': 'rgba(000000ff)'},
    '$nordix-pred': {'name': 'Pure Red', 'rgba': 'rgba(ff0000ff)'},
    '$nordix-ppink': {'name': 'Pure Pink', 'rgba': 'rgba(eb4899ff)'},
    '$nordix-pwhite': {'name': 'Pure White', 'rgba': 'rgba(ffffffff)'},
    '$nordix-pblue': {'name': 'Pure Blue', 'rgba': 'rgba(01ccffff)'},
    '$nordix-blue': {'name': 'Blue', 'rgba': 'rgba(13abc6ff)'},
    '$nordix-ice': {'name': 'Ice', 'rgba': 'rgba(0084afff)'},
    '$nordix-artic': {'name': 'Artic', 'rgba': 'rgba(9ce6ffff)'},
    '$nordix-glacier': {'name': 'Glacier', 'rgba': 'rgba(50c8ffff)'},
    '$nordix-frost': {'name': 'Frost', 'rgba': 'rgba(d2ffffff)'},
    '$nordix-hyprblue': {'name': 'Hyprblue', 'rgba': 'rgba(00d2ffff)'},
    '$nordix-green': {'name': 'Green', 'rgba': 'rgba(00ff00ff)'},
    '$nordix-mint': {'name': 'Mint', 'rgba': 'rgba(00aa86ff)'},
    '$nordix-violet': {'name': 'Violet', 'rgba': 'rgba(998cc9ff)'},
    '$nordix-ghost': {'name': 'Ghost', 'rgba': 'rgba(aabaaeff)'},
    '$nordix-mustard': {'name': 'Mustard', 'rgba': 'rgba(a1b116ff)'},
    '$nordix-iblue': {'name': 'Ice Blue', 'rgba': 'rgba(affbfdff)'},
    '$nordix-forest': {'name': 'Forest', 'rgba': 'rgba(4AC283ff)'},
    '$nordix-fish': {'name': 'Fish', 'rgba': 'rgba(8a9685ff)'},
    '$nordix-arora': {'name': 'Arora', 'rgba': 'rgba(6c63ffff)'},
    '$nordix-retro': {'name': 'Retro Green', 'rgba': 'rgba(17d67bff)'},
    '$nordix-studio': {'name': 'Studio', 'rgba': 'rgba(9856C4ff)'},
    '$nordix-babyblue': {'name': 'Baby Blue', 'rgba': 'rgba(73CFFFff)'},
    '$nordix-tpblack': {'name': 'Transparent Pure Black', 'rgba': 'rgba(000000aa)'},
    '$nordix-tpred': {'name': 'Transparent Pure Red', 'rgba': 'rgba(ff0000aa)'},
    '$nordix-tpink': {'name': 'Transparent Pure Pink', 'rgba': 'rgba(eb4899aa)'},
    '$nordix-tpwhite': {'name': 'Transparent Pure White', 'rgba': 'rgba(ffffffaa)'},
    '$nordix-tpblue': {'name': 'Transparent Pure Blue', 'rgba': 'rgba(01ccffaa)'},
    '$nordix-tblue': {'name': 'Transparent Blue', 'rgba': 'rgba(13abc6aa)'},
    '$nordix-tice': {'name': 'Transparent Ice', 'rgba': 'rgba(0084afaa)'},
    '$nordix-tartic': {'name': 'Transparent Artic', 'rgba': 'rgba(9ce6ffaa)'},
    '$nordix-tglacier': {'name': 'Transparent Glacier', 'rgba': 'rgba(50c8ffaa)'},
    '$nordix-tfrost': {'name': 'Transparent Frost', 'rgba': 'rgba(d2ffffaa)'},
    '$nordix-thyprblue': {'name': 'Transparent Hyprblue', 'rgba': 'rgba(00d2ffaa)'},
    '$nordix-tgreen': {'name': 'Transparent Green', 'rgba': 'rgba(00ff00aa)'},
    '$nordix-tmint': {'name': 'Transparent Mint', 'rgba': 'rgba(00aa86aa)'},
    '$nordix-tviolet': {'name': 'Transparent Violet', 'rgba': 'rgba(998cc9aa)'},
    '$nordix-tghost': {'name': 'Transparent Ghost', 'rgba': 'rgba(aabaaeaa)'},
    '$nordix-tmustard': {'name': 'Transparent Mustard', 'rgba': 'rgba(a1b116ba)'},
    '$nordix-tvblue': {'name': 'Transparent Ice Blue', 'rgba': 'rgba(affbfdaa)'},
    '$nordix-tforest': {'name': 'Transparent Forest', 'rgba': 'rgba(4AC283aa)'},
    '$nordix-tfish': {'name': 'Transparent Fish', 'rgba': 'rgba(8a9685aa)'},
    '$nordix-tarora': {'name': 'Transparent Arora', 'rgba': 'rgba(6c63ffaa)'},
    '$nordix-tretro': {'name': 'Transparent Retro Green', 'rgba': 'rgba(17d67baa)'},
    '$nordix-tstudio': {'name': 'Transparent Studio', 'rgba': 'rgba(9856C4aa)'},
    '$nordix-tbabyblue': {'name': 'Transparent Baby Blue', 'rgba': 'rgba(73CFFFaa)'},
    '$nordix-glacier-blue': {'name': 'Glacier Blue', 'rgba': 'rgba(4aa3ffee)'},
    '$frost-crystal': {'name': 'Frost Crystal', 'rgba': 'rgba(8fcbffff)'},
    '$winter-aurora': {'name': 'Winter Aurora', 'rgba': 'rgba(6ad4b2ee)'},
    '$nordic-mist': {'name': 'Nordic Mist', 'rgba': 'rgba(2b7af0ee)'},
    '$crystal-ice': {'name': 'Crystal Ice', 'rgba': 'rgba(b3f0ffee)'},
    '$gwenview-pink': {'name': 'Gwenview Pink', 'rgba': 'rgba(cc3884ee)'},
    '$ghost-ice': {'name': 'Ghost Ice', 'rgba': 'rgba(4abecfff)'},
    '$ghost-frost': {'name': 'Ghost Frost', 'rgba': 'rgba(59d8e5ee)'},
    '$nordix-nice-green': {'name': 'Nice Green', 'rgba': 'rgba(2b7a10ee)'},
    '$frozen-text1': {'name': 'Frozen', 'rgba': 'rgba(81d1f1aa)'},
    '$frozen-text2': {'name': 'Frozen 2', 'rgba': 'rgba(11d1f5ff)'},
    '$nordix-gray': {'name': 'Nordix Gray', 'rgba': 'rgba(1c2328ee)'},
    '$nordix-grey2': {'name': 'Nordix Grey 2', 'rgba': 'rgba(3d444dee)'},
    '$subl-gray': {'name': 'Sublime Gray', 'rgba': 'rgba(4f565eee)'},
    '$subl-light-gray': {'name': 'Sublime Light Gray', 'rgba': 'rgba(4f565eee)'},
    '$subl-white-gray': {'name': 'Sublime White Gray', 'rgba': 'rgba(696f75ee)'},
    '$cosmic-gray': {'name': 'Cosmic Gray', 'rgba': 'rgba(8d9199ee)'},
}

# Default configuration values - these match nordix-decorations.conf
DEFAULT_SETTINGS = {
    # Window Opacity
    'active_opacity': 1.0,
    'inactive_opacity': 0.9,
    'fullscreen_opacity': 1.0,
    # Rounded Corners
    'rounding': 10,
    'rounding_power': 2.0,
    # Dim
    'dim_modal': True,
    'dim_inactive': True,
    'dim_strength': 0.5,
    'dim_special': 0.4,
    'dim_around': 0.6,
    # Window Border
    'border_part_of_window': True,
    # Blur
    'blur_enabled': True,
    'blur_size': 10,
    'blur_passes': 2,
    'blur_ignore_opacity': True,
    'blur_new_optimizations': True,
    'blur_xray': False,
    'blur_noise': 0.0117,
    'blur_contrast': 0.8916,
    'blur_brightness': 0.8172,
    'blur_vibrancy': 0.2696,
    'blur_vibrancy_darkness': 0.1421,
    'blur_special': False,
    'blur_popups': False,
    'blur_popups_ignorealpha': 0.2,
    'blur_input_methods': False,
    'blur_input_methods_ignorealpha': 0.2,
    # Shadow
    'shadow_enabled': True,
    'shadow_range': 355,
    'shadow_render_power': 4,
    'shadow_sharp': False,
    'shadow_color': '$nordix-tartic',
    'shadow_color_inactive': '$nordix-tpblack',
    'shadow_offset_x': 5,
    'shadow_offset_y': 10,
    'shadow_scale': 0.9,
}

# Shadow presets from the presets file
SHADOW_PRESETS = {
    'Default Nordix': {
        'shadow_range': 355,
        'shadow_render_power': 4,
        'shadow_scale': 0.9,
        'shadow_offset_x': 5,
        'shadow_offset_y': 10,
    },
    'Alternative': {
        'shadow_range': 30,
        'shadow_render_power': 2,
        'shadow_scale': 1.0,
        'shadow_offset_x': 6,
        'shadow_offset_y': 8,
    },
    'Big Shadows': {
        'shadow_range': 65,
        'shadow_render_power': 4,
        'shadow_scale': 2.0,
        'shadow_offset_x': 1,
        'shadow_offset_y': 5,
    },
    'Medium Shadows': {
        'shadow_range': 35,
        'shadow_render_power': 4,
        'shadow_scale': 2.0,
        'shadow_offset_x': 1,
        'shadow_offset_y': 5,
    },
    'Small Shadows': {
        'shadow_range': 15,
        'shadow_render_power': 4,
        'shadow_scale': 2.0,
        'shadow_offset_x': 1,
        'shadow_offset_y': 5,
    },
    'Neon Glow': {
        'shadow_range': 55,
        'shadow_render_power': 4,
        'shadow_scale': 2.0,
        'shadow_offset_x': 5,
        'shadow_offset_y': 10,
    },
    'Big Fuzz': {
        'shadow_range': 55,
        'shadow_render_power': 1,
        'shadow_scale': 2.0,
        'shadow_offset_x': 0,
        'shadow_offset_y': 0,
    },
    'Medium Fuzz': {
        'shadow_range': 30,
        'shadow_render_power': 1,
        'shadow_scale': 2.0,
        'shadow_offset_x': 0,
        'shadow_offset_y': 0,
    },
    'Small Fuzz': {
        'shadow_range': 15,
        'shadow_render_power': 1,
        'shadow_scale': 2.0,
        'shadow_offset_x': 0,
        'shadow_offset_y': 0,
    },
    'Mighty Glower': {
        'shadow_range': 550,
        'shadow_render_power': 7,
        'shadow_scale': 1.0,
        'shadow_offset_x': 1,
        'shadow_offset_y': 5,
    },
}


class DecorationSettings:
    """Handles reading and writing of decorations.conf"""
    
    def __init__(self, config_path=None):
        if config_path is None:
            self.config_path = CONFIG_PATH
        else:
            self.config_path = Path(config_path)
        
        # Initialize with default settings
        self.settings = DEFAULT_SETTINGS.copy()
        
        # Ensure config exists before loading
        self._ensure_config_exists()
        self.load_config()
    
    def _ensure_config_exists(self):
        """Ensure config directory and file exist - fail-safe initialization"""
        try:
            # Create parent directories if they don't exist
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # If config file doesn't exist, create it with defaults
            if not self.config_path.exists():
                print(f"Config not found: {self.config_path}")
                print("Creating config directory and file with default settings...")
                self._write_default_config()
                print(f"Created: {self.config_path}")
        except PermissionError as e:
            print(f"Permission denied creating config: {e}")
            print("Will use default settings in memory.")
        except Exception as e:
            print(f"Error ensuring config exists: {e}")
            print("Will use default settings in memory.")
    
    def _write_default_config(self):
        """Write default configuration to file"""
        try:
            config_content = self.generate_config()
            self.config_path.write_text(config_content)
            return True
        except Exception as e:
            print(f"Error writing default config: {e}")
            return False
    
    def load_config(self):
        """Reads current settings from config file with fail-safe handling"""
        if not self.config_path.exists():
            print(f"Config file not found, using defaults: {self.config_path}")
            return
        
        try:
            content = self.config_path.read_text()
            
            # Track which section we're in
            in_blur_section = False
            in_shadow_section = False
            brace_depth = 0
            
            for line in content.split('\n'):
                stripped = line.strip()
                
                # Skip comments
                if stripped.startswith('# '):
                    continue
                
                # Track sections by brace depth
                if 'blur {' in stripped or 'blur{' in stripped:
                    in_blur_section = True
                    brace_depth = 1
                    continue
                elif 'shadow {' in stripped or 'shadow{' in stripped:
                    in_shadow_section = True
                    brace_depth = 1
                    continue
                elif 'decoration {' in stripped or 'decoration{' in stripped:
                    continue
                
                if '{' in stripped:
                    brace_depth += stripped.count('{')
                if '}' in stripped:
                    brace_depth -= stripped.count('}')
                    if brace_depth <= 0:
                        in_blur_section = False
                        in_shadow_section = False
                        brace_depth = 0
                    continue
                
                # Parse key = value pairs
                if '=' in stripped:
                    parts = stripped.split('=', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        
                        # Remove inline comments
                        if '# ' in value:
                            value = value.split('# ')[0].strip()
                        
                        self._set_value(key, value, in_blur_section, in_shadow_section)
            
            print(f"Config loaded successfully: {self.config_path}")
                        
        except PermissionError as e:
            print(f"Permission denied reading config: {e}")
            print("Using default settings.")
        except Exception as e:
            print(f"Error loading config: {e}")
            print("Using default settings.")
    
    def _set_value(self, key, value, in_blur, in_shadow):
        """Sets a setting value based on key and current section"""
        
        # Map config keys to our settings keys
        if in_blur:
            key_map = {
                'enabled': 'blur_enabled',
                'size': 'blur_size',
                'passes': 'blur_passes',
                'ignore_opacity': 'blur_ignore_opacity',
                'new_optimizations': 'blur_new_optimizations',
                'xray': 'blur_xray',
                'noise': 'blur_noise',
                'contrast': 'blur_contrast',
                'brightness': 'blur_brightness',
                'vibrancy': 'blur_vibrancy',
                'vibrancy_darkness': 'blur_vibrancy_darkness',
                'special': 'blur_special',
                'popups': 'blur_popups',
                'popups_ignorealpha': 'blur_popups_ignorealpha',
                'input_methods': 'blur_input_methods',
                'input_methods_ignorealpha': 'blur_input_methods_ignorealpha',
            }
            settings_key = key_map.get(key)
        elif in_shadow:
            if key == 'offset':
                # Parse offset as "x y"
                parts = value.split()
                if len(parts) >= 2:
                    try:
                        self.settings['shadow_offset_x'] = int(parts[0])
                        self.settings['shadow_offset_y'] = int(parts[1])
                    except ValueError:
                        pass
                return
            key_map = {
                'enabled': 'shadow_enabled',
                'range': 'shadow_range',
                'render_power': 'shadow_render_power',
                'sharp': 'shadow_sharp',
                'color': 'shadow_color',
                'color_inactive': 'shadow_color_inactive',
                'scale': 'shadow_scale',
            }
            settings_key = key_map.get(key)
        else:
            # Main decoration section
            settings_key = key
        
        if settings_key and settings_key in self.settings:
            current_type = type(self.settings[settings_key])
            try:
                if current_type == bool:
                    self.settings[settings_key] = value.lower() == 'true'
                elif current_type == int:
                    self.settings[settings_key] = int(value)
                elif current_type == float:
                    self.settings[settings_key] = float(value)
                else:
                    self.settings[settings_key] = value
            except ValueError:
                pass
    
    def generate_config(self):
        """Generates new config file based on settings"""
        s = self.settings
        config = f'''
##==========================================##
 #         Yggdrasil's - Decoration         #
 #         Hyprland - Configuration         #
##==========================================##
 # * Generated by Nordix Decorations GUI    #
##==========================================##
source = ~/.config/nordix/yggdrasil/color/colors.conf


decoration {{

##================##
 # WINDOW OPACITY #
##================##

# opacity of active windows. [0.0 - 1.0] (float)
active_opacity = {s['active_opacity']:.2f}

# opacity of inactive windows. [0.0 - 1.0] (float)
inactive_opacity = {s['inactive_opacity']:.2f}

# opacity of fullscreen windows. [0.0 - 1.0] (float)
fullscreen_opacity = {s['fullscreen_opacity']:.2f}




##=================##
 # ROUNDED CORNERS #
##=================##

# rounded corners radius (in layout px) (int)
rounding = {s['rounding']}

# adjusts the curve used for rounding corners [1.0 - 10.0] (float)
rounding_power = {s['rounding_power']:.1f}




##=====##
 # DIM #
##=====##

# enables dimming of parents of modal windows (bool)
dim_modal = {'true' if s['dim_modal'] else 'false'}

# enables dimming of inactive windows (bool)
dim_inactive = {'true' if s['dim_inactive'] else 'false'}

# how much inactive windows should be dimmed [0.0 - 1.0] (float)
dim_strength = {s['dim_strength']:.2f}

# how much to dim the rest of the screen by when a special workspace is open [0.0 - 1.0] (float)
dim_special = {s['dim_special']:.2f}

# how much the dim_around window rule should dim by [0.0 - 1.0] (float)
dim_around = {s['dim_around']:.2f}


##===============##
 # WINDOW BORDER #
##===============##

# whether the window border should be a part of the window (bool)
border_part_of_window = {'true' if s['border_part_of_window'] else 'false'}


##==============##
 # BLUR EFFECTS #
##==============##

blur {{
# enable kawase window background blur (bool)
enabled = {'true' if s['blur_enabled'] else 'false'}

# blur size (distance) (int)
size = {s['blur_size']}

# the amount of passes to perform (int)
passes = {s['blur_passes']}

# make the blur layer ignore the opacity of the window (bool)
ignore_opacity = {'true' if s['blur_ignore_opacity'] else 'false'}

# whether to enable further optimizations to the blur (bool)
new_optimizations = {'true' if s['blur_new_optimizations'] else 'false'}

# if enabled, floating windows will ignore tiled windows in their blur (bool)
xray = {'true' if s['blur_xray'] else 'false'}

# how much noise to apply [0.0 - 1.0] (float)
noise = {s['blur_noise']:.4f}

# contrast modulation for blur [0.0 - 2.0] (float)
contrast = {s['blur_contrast']:.4f}

# brightness modulation for blur [0.0 - 2.0] (float)
brightness = {s['blur_brightness']:.4f}

# increase saturation of blurred colors [0.0 - 1.0] (float)
vibrancy = {s['blur_vibrancy']:.4f}

# how strong the effect of vibrancy is on dark areas [0.0 - 1.0] (float)
vibrancy_darkness = {s['blur_vibrancy_darkness']:.4f}

# whether to blur behind the special workspace (note: expensive) (bool)
special = {'true' if s['blur_special'] else 'false'}

# whether to blur popups (e.g. right-click menus) (bool)
popups = {'true' if s['blur_popups'] else 'false'}

# works like ignore_alpha in layer rules [0.0 - 1.0] (float)
popups_ignorealpha = {s['blur_popups_ignorealpha']:.2f}

# whether to blur input methods (e.g. fcitx5) (bool)
input_methods = {'true' if s['blur_input_methods'] else 'false'}

# works like ignore_alpha in layer rules [0.0 - 1.0] (float)
input_methods_ignorealpha = {s['blur_input_methods_ignorealpha']:.2f}


}}

##=================##
 # WINDOWS SHADOWS #
##=================##

shadow {{

# enable drop shadows on windows (bool)
enabled = {'true' if s['shadow_enabled'] else 'false'}

# Shadow range (size) in layout px (int)
range = {s['shadow_range']}

# in what power to render the falloff (more power, the faster the falloff) [1 - 4] (int)
render_power = {s['shadow_render_power']}

# if enabled, will make the shadows sharp, akin to an infinite render power (bool)
sharp = {'true' if s['shadow_sharp'] else 'false'}

# shadow color. Alpha dictates shadow opacity (color)
color = {s['shadow_color']}

# inactive shadow color (color)
color_inactive = {s['shadow_color_inactive']}

# shadow rendering offset (vec2)
offset = {s['shadow_offset_x']} {s['shadow_offset_y']}

# shadow scale [0.0 - 1.0] (float)
scale = {s['shadow_scale']:.1f}

}}

}}
'''
        return config
    
    def save_config(self):
        """Saves the configuration to file with fail-safe handling"""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup
            if self.config_path.exists():
                backup_path = self.config_path.with_suffix('.conf.backup')
                try:
                    shutil.copy2(self.config_path, backup_path)
                except Exception as e:
                    print(f"Warning: Could not create backup: {e}")
            
            # Write new config
            self.config_path.write_text(self.generate_config())
            return True
        except PermissionError as e:
            print(f"Permission denied saving config: {e}")
            return False
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def reload_hyprland(self):
        """Reloads the Hyprland configuration"""
        try:
            subprocess.run(['hyprctl', 'reload'], check=True)
            return True
        except Exception as e:
            print(f"Error reloading Hyprland: {e}")
            return False
    
    def reset_to_defaults(self):
        """Resets all settings to default values"""
        self.settings = DEFAULT_SETTINGS.copy()


class SliderRow(Adw.ActionRow):
    """A row with slider for numeric values"""
    
    def __init__(self, title, subtitle, min_val, max_val, step, value, callback, digits=2):
        super().__init__()
        self.set_title(title)
        self.set_subtitle(subtitle)
        
        self.callback = callback
        
        self.adjustment = Gtk.Adjustment(
            value=value,
            lower=min_val,
            upper=max_val,
            step_increment=step,
            page_increment=step * 10
        )
        
        self.scale = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL,
            adjustment=self.adjustment,
            draw_value=True,
            digits=digits,
            hexpand=True
        )
        self.scale.set_size_request(200, -1)
        self.scale.connect('value-changed', self._on_value_changed)
        
        self.add_suffix(self.scale)
    
    def _on_value_changed(self, scale):
        self.callback(scale.get_value())
    
    def set_value(self, value):
        self.adjustment.set_value(value)


class SwitchRow(Adw.ActionRow):
    """A row with switch for boolean values"""
    
    def __init__(self, title, subtitle, active, callback):
        super().__init__()
        self.set_title(title)
        self.set_subtitle(subtitle)
        self.set_activatable(True)
        
        self.callback = callback
        
        self.switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        self.switch.set_active(active)
        self.switch.connect('notify::active', self._on_toggled)
        
        self.add_suffix(self.switch)
        self.set_activatable_widget(self.switch)
    
    def _on_toggled(self, switch, _):
        self.callback(switch.get_active())
    
    def set_active(self, active):
        self.switch.set_active(active)


from gi.repository import Gtk, Adw, Gio, GLib, Gdk, GdkPixbuf

class ColorRow(Adw.ActionRow):
    """A row with dropdown for color selection - theme immune color preview"""
    
    def __init__(self, title, subtitle, current_value, callback, show_transparent=True):
        super().__init__()
        self.set_title(title)
        self.set_subtitle(subtitle)
        self.callback = callback
        self.color_keys = []
        
        # Build color list
        string_list = Gtk.StringList()
        current_index = 0
        
        for i, (color_var, color_info) in enumerate(NORDIX_COLORS.items()):
            # Filter transparent or solid based on preference
            is_transparent = color_var.startswith('$nordix-t')
            if show_transparent or not is_transparent:
                self.color_keys.append(color_var)
                string_list.append(color_info['name'])
                if color_var == current_value:
                    current_index = len(self.color_keys) - 1
        
        self.dropdown = Gtk.DropDown(model=string_list)
        self.dropdown.set_selected(current_index)
        self.dropdown.connect('notify::selected', self._on_selected)
        
        # Color preview using Picture + Pixbuf (immune to themes)
        self.color_preview = Gtk.Picture()
        self.color_preview.set_size_request(24, 24)
        self.current_color = self._get_hex_color(current_value)
        self._update_preview()
        
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        box.append(self.color_preview)
        box.append(self.dropdown)
        
        self.add_suffix(box)
    
    def _get_hex_color(self, color_var):
        """Convert Nordix color variable to hex for preview"""
        if color_var in NORDIX_COLORS:
            rgba = NORDIX_COLORS[color_var]['rgba']
            # Extract hex from rgba(RRGGBBAA)
            match = re.search(r'rgba\(([0-9a-fA-F]{6})', rgba)
            if match:
                return f"#{match.group(1)}"
        return "#000000"
    
    def _create_color_pixbuf(self, hex_color, width=24, height=24):
        """Create a pixbuf with exact color - completely immune to themes"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Create raw pixel data (RGB)
        pixels = bytes([r, g, b] * (width * height))
        
        return GdkPixbuf.Pixbuf.new_from_data(
            pixels,
            GdkPixbuf.Colorspace.RGB,
            False,  # no alpha
            8,      # bits per sample
            width,
            height,
            width * 3  # rowstride
        )
    
    def _update_preview(self):
        """Update the color preview with current color"""
        pixbuf = self._create_color_pixbuf(self.current_color)
        texture = Gdk.Texture.new_for_pixbuf(pixbuf)
        self.color_preview.set_paintable(texture)
    
    def _on_selected(self, dropdown, _):
        selected = dropdown.get_selected()
        if selected < len(self.color_keys):
            color_var = self.color_keys[selected]
            self.current_color = self._get_hex_color(color_var)
            self._update_preview()
            self.callback(color_var)
    
    def set_color(self, color_var):
        """Set the selected color"""
        if color_var in self.color_keys:
            index = self.color_keys.index(color_var)
            self.dropdown.set_selected(index)
            self.current_color = self._get_hex_color(color_var)
            self._update_preview()

class NordixDecorationsWindow(Adw.ApplicationWindow):
    """Main window for decoration settings"""
    
    def __init__(self, app):
        super().__init__(application=app, title="Yggdrasil Decorations")
        self.set_default_size(550, 800)
        
        # Initialize settings with fail-safe handling
        try:
            self.settings = DecorationSettings()
        except Exception as e:
            print(f"Critical error initializing settings: {e}")
            print("Starting with default settings...")
            self.settings = DecorationSettings.__new__(DecorationSettings)
            self.settings.config_path = CONFIG_PATH
            self.settings.settings = DEFAULT_SETTINGS.copy()
        
        self.widgets = {}  # Store references to widgets for refreshing
        self.setup_ui()
    
    def setup_ui(self):
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Header bar
        header = Adw.HeaderBar()
        
        # Apply button
        apply_btn = Gtk.Button(label="Apply")
        apply_btn.add_css_class("suggested-action")
        apply_btn.connect("clicked", self.on_apply)
        header.pack_end(apply_btn)
        
        # Reset button
        reset_btn = Gtk.Button(label="Reset to Default")
        reset_btn.connect("clicked", self.on_reset)
        header.pack_start(reset_btn)
        
        main_box.append(header)
        
        # Scrollable content
        scrolled = Gtk.ScrolledWindow(vexpand=True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        content.set_margin_start(12)
        content.set_margin_end(12)
        
        # =========================================
        # OPACITY SECTION
        # =========================================
        opacity_group = Adw.PreferencesGroup(
            title="Window Opacity",
            description="Control transparency for windows"
        )
        
        self.widgets['active_opacity'] = SliderRow(
            "Active Windows", "Opacity for focused window [0.0 - 1.0]",
            0.0, 1.0, 0.05, self.settings.settings['active_opacity'],
            lambda v: self.on_value_changed('active_opacity', v)
        )
        opacity_group.add(self.widgets['active_opacity'])
        
        self.widgets['inactive_opacity'] = SliderRow(
            "Inactive Windows", "Opacity for unfocused windows [0.0 - 1.0]",
            0.0, 1.0, 0.05, self.settings.settings['inactive_opacity'],
            lambda v: self.on_value_changed('inactive_opacity', v)
        )
        opacity_group.add(self.widgets['inactive_opacity'])
        
        self.widgets['fullscreen_opacity'] = SliderRow(
            "Fullscreen Windows", "Opacity for fullscreen windows [0.0 - 1.0]",
            0.0, 1.0, 0.05, self.settings.settings['fullscreen_opacity'],
            lambda v: self.on_value_changed('fullscreen_opacity', v)
        )
        opacity_group.add(self.widgets['fullscreen_opacity'])
        
        content.append(opacity_group)
        
        # =========================================
        # ROUNDING SECTION
        # =========================================
        rounding_group = Adw.PreferencesGroup(
            title="Rounded Corners",
            description="Corner rounding for windows"
        )
        
        self.widgets['rounding'] = SliderRow(
            "Rounding Radius", "Corner radius in pixels [0 - 50]",
            0, 50, 1, self.settings.settings['rounding'],
            lambda v: self.on_value_changed('rounding', int(v)),
            digits=0
        )
        rounding_group.add(self.widgets['rounding'])
        
        self.widgets['rounding_power'] = SliderRow(
            "Rounding Power", "Curve shape: 2.0=circle, 4.0=squircle [1.0 - 10.0]",
            1.0, 10.0, 0.5, self.settings.settings['rounding_power'],
            lambda v: self.on_value_changed('rounding_power', v),
            digits=1
        )
        rounding_group.add(self.widgets['rounding_power'])
        
        content.append(rounding_group)
        
        # =========================================
        # DIM SECTION
        # =========================================
        dim_group = Adw.PreferencesGroup(
            title="Window Dimming",
            description="Dimming effects for inactive windows"
        )
        
        self.widgets['dim_modal'] = SwitchRow(
            "Dim Modal Parents", "Dim parents of modal windows",
            self.settings.settings['dim_modal'],
            lambda v: self.on_value_changed('dim_modal', v)
        )
        dim_group.add(self.widgets['dim_modal'])
        
        self.widgets['dim_inactive'] = SwitchRow(
            "Dim Inactive", "Dim inactive windows",
            self.settings.settings['dim_inactive'],
            lambda v: self.on_value_changed('dim_inactive', v)
        )
        dim_group.add(self.widgets['dim_inactive'])
        
        self.widgets['dim_strength'] = SliderRow(
            "Dim Strength", "How much to dim inactive windows [0.0 - 1.0]",
            0.0, 1.0, 0.05, self.settings.settings['dim_strength'],
            lambda v: self.on_value_changed('dim_strength', v)
        )
        dim_group.add(self.widgets['dim_strength'])
        
        self.widgets['dim_special'] = SliderRow(
            "Dim Special", "Dim amount for special workspace [0.0 - 1.0]",
            0.0, 1.0, 0.05, self.settings.settings['dim_special'],
            lambda v: self.on_value_changed('dim_special', v)
        )
        dim_group.add(self.widgets['dim_special'])
        
        self.widgets['dim_around'] = SliderRow(
            "Dim Around", "Dim amount for dim_around rule [0.0 - 1.0]",
            0.0, 1.0, 0.05, self.settings.settings['dim_around'],
            lambda v: self.on_value_changed('dim_around', v)
        )
        dim_group.add(self.widgets['dim_around'])
        
        content.append(dim_group)
        
        # =========================================
        # BORDER SECTION
        # =========================================
        border_group = Adw.PreferencesGroup(
            title="Window Border",
            description="Border rendering options"
        )
        
        self.widgets['border_part_of_window'] = SwitchRow(
            "Border Part of Window", "Include border as part of window",
            self.settings.settings['border_part_of_window'],
            lambda v: self.on_value_changed('border_part_of_window', v)
        )
        border_group.add(self.widgets['border_part_of_window'])
        
        content.append(border_group)
        
        # =========================================
        # BLUR SECTION
        # =========================================
        blur_group = Adw.PreferencesGroup(
            title="Blur Effects",
            description="Background blur for windows"
        )
        
        self.widgets['blur_enabled'] = SwitchRow(
            "Enable Blur", "Enable kawase window background blur",
            self.settings.settings['blur_enabled'],
            lambda v: self.on_value_changed('blur_enabled', v)
        )
        blur_group.add(self.widgets['blur_enabled'])
        
        self.widgets['blur_size'] = SliderRow(
            "Blur Size", "Blur distance [1 - 30]",
            1, 30, 1, self.settings.settings['blur_size'],
            lambda v: self.on_value_changed('blur_size', int(v)),
            digits=0
        )
        blur_group.add(self.widgets['blur_size'])
        
        self.widgets['blur_passes'] = SliderRow(
            "Blur Passes", "Number of blur passes [1 - 6]",
            1, 6, 1, self.settings.settings['blur_passes'],
            lambda v: self.on_value_changed('blur_passes', int(v)),
            digits=0
        )
        blur_group.add(self.widgets['blur_passes'])
        
        self.widgets['blur_ignore_opacity'] = SwitchRow(
            "Ignore Opacity", "Blur layer ignores window opacity",
            self.settings.settings['blur_ignore_opacity'],
            lambda v: self.on_value_changed('blur_ignore_opacity', v)
        )
        blur_group.add(self.widgets['blur_ignore_opacity'])
        
        self.widgets['blur_new_optimizations'] = SwitchRow(
            "New Optimizations", "Enable blur optimizations (recommended)",
            self.settings.settings['blur_new_optimizations'],
            lambda v: self.on_value_changed('blur_new_optimizations', v)
        )
        blur_group.add(self.widgets['blur_new_optimizations'])
        
        self.widgets['blur_xray'] = SwitchRow(
            "X-ray Mode", "Floating windows ignore tiled windows in blur",
            self.settings.settings['blur_xray'],
            lambda v: self.on_value_changed('blur_xray', v)
        )
        blur_group.add(self.widgets['blur_xray'])
        
        self.widgets['blur_noise'] = SliderRow(
            "Noise", "How much noise to apply [0.0 - 1.0]",
            0.0, 1.0, 0.01, self.settings.settings['blur_noise'],
            lambda v: self.on_value_changed('blur_noise', v),
            digits=4
        )
        blur_group.add(self.widgets['blur_noise'])
        
        self.widgets['blur_contrast'] = SliderRow(
            "Contrast", "Contrast modulation [0.0 - 2.0]",
            0.0, 2.0, 0.05, self.settings.settings['blur_contrast'],
            lambda v: self.on_value_changed('blur_contrast', v),
            digits=4
        )
        blur_group.add(self.widgets['blur_contrast'])
        
        self.widgets['blur_brightness'] = SliderRow(
            "Brightness", "Brightness modulation [0.0 - 2.0]",
            0.0, 2.0, 0.05, self.settings.settings['blur_brightness'],
            lambda v: self.on_value_changed('blur_brightness', v),
            digits=4
        )
        blur_group.add(self.widgets['blur_brightness'])
        
        self.widgets['blur_vibrancy'] = SliderRow(
            "Vibrancy", "Saturation of blurred colors [0.0 - 1.0]",
            0.0, 1.0, 0.05, self.settings.settings['blur_vibrancy'],
            lambda v: self.on_value_changed('blur_vibrancy', v),
            digits=4
        )
        blur_group.add(self.widgets['blur_vibrancy'])
        
        self.widgets['blur_vibrancy_darkness'] = SliderRow(
            "Vibrancy Darkness", "Vibrancy effect on dark areas [0.0 - 1.0]",
            0.0, 1.0, 0.05, self.settings.settings['blur_vibrancy_darkness'],
            lambda v: self.on_value_changed('blur_vibrancy_darkness', v),
            digits=4
        )
        blur_group.add(self.widgets['blur_vibrancy_darkness'])
        
        self.widgets['blur_special'] = SwitchRow(
            "Blur Special", "Blur behind special workspace (expensive)",
            self.settings.settings['blur_special'],
            lambda v: self.on_value_changed('blur_special', v)
        )
        blur_group.add(self.widgets['blur_special'])
        
        self.widgets['blur_popups'] = SwitchRow(
            "Blur Popups", "Blur behind popups (e.g. right-click menus)",
            self.settings.settings['blur_popups'],
            lambda v: self.on_value_changed('blur_popups', v)
        )
        blur_group.add(self.widgets['blur_popups'])
        
        self.widgets['blur_popups_ignorealpha'] = SliderRow(
            "Popups Ignore Alpha", "Ignore alpha threshold for popups [0.0 - 1.0]",
            0.0, 1.0, 0.05, self.settings.settings['blur_popups_ignorealpha'],
            lambda v: self.on_value_changed('blur_popups_ignorealpha', v)
        )
        blur_group.add(self.widgets['blur_popups_ignorealpha'])
        
        self.widgets['blur_input_methods'] = SwitchRow(
            "Blur Input Methods", "Blur behind input methods (e.g. fcitx5)",
            self.settings.settings['blur_input_methods'],
            lambda v: self.on_value_changed('blur_input_methods', v)
        )
        blur_group.add(self.widgets['blur_input_methods'])
        
        self.widgets['blur_input_methods_ignorealpha'] = SliderRow(
            "Input Methods Ignore Alpha", "Ignore alpha threshold for input methods [0.0 - 1.0]",
            0.0, 1.0, 0.05, self.settings.settings['blur_input_methods_ignorealpha'],
            lambda v: self.on_value_changed('blur_input_methods_ignorealpha', v)
        )
        blur_group.add(self.widgets['blur_input_methods_ignorealpha'])
        
        content.append(blur_group)
        
        # =========================================
        # SHADOW SECTION
        # =========================================
        shadow_group = Adw.PreferencesGroup(
            title="Window Shadows",
            description="Drop shadows for depth effect"
        )
        
        self.widgets['shadow_enabled'] = SwitchRow(
            "Enable Shadows", "Enable drop shadows on windows",
            self.settings.settings['shadow_enabled'],
            lambda v: self.on_value_changed('shadow_enabled', v)
        )
        shadow_group.add(self.widgets['shadow_enabled'])
        
        self.widgets['shadow_range'] = SliderRow(
            "Shadow Range", "Shadow size in pixels [0 - 600]",
            0, 600, 5, self.settings.settings['shadow_range'],
            lambda v: self.on_value_changed('shadow_range', int(v)),
            digits=0
        )
        shadow_group.add(self.widgets['shadow_range'])
        
        self.widgets['shadow_render_power'] = SliderRow(
            "Render Power", "Falloff power (higher = faster falloff) [1 - 7]",
            1, 7, 1, self.settings.settings['shadow_render_power'],
            lambda v: self.on_value_changed('shadow_render_power', int(v)),
            digits=0
        )
        shadow_group.add(self.widgets['shadow_render_power'])
        
        self.widgets['shadow_sharp'] = SwitchRow(
            "Sharp Shadows", "Make shadows sharp (infinite render power)",
            self.settings.settings['shadow_sharp'],
            lambda v: self.on_value_changed('shadow_sharp', v)
        )
        shadow_group.add(self.widgets['shadow_sharp'])
                
        self.widgets['shadow_offset_x'] = SliderRow(
            "Offset X", "Horizontal shadow offset [-50 - 50]",
            -50, 50, 1, self.settings.settings['shadow_offset_x'],
            lambda v: self.on_value_changed('shadow_offset_x', int(v)),
            digits=0
        )
        shadow_group.add(self.widgets['shadow_offset_x'])
        
        self.widgets['shadow_offset_y'] = SliderRow(
            "Offset Y", "Vertical shadow offset [-50 - 50]",
            -50, 50, 1, self.settings.settings['shadow_offset_y'],
            lambda v: self.on_value_changed('shadow_offset_y', int(v)),
            digits=0
        )
        shadow_group.add(self.widgets['shadow_offset_y'])
        
        self.widgets['shadow_scale'] = SliderRow(
            "Shadow Scale", "Shadow scale factor [0.0 - 3.0]",
            0.0, 3.0, 0.1, self.settings.settings['shadow_scale'],
            lambda v: self.on_value_changed('shadow_scale', v),
            digits=1
        )
        shadow_group.add(self.widgets['shadow_scale'])
        
        self.widgets['shadow_color'] = ColorRow(
            "Shadow Color", "Color for active window shadows",
            self.settings.settings['shadow_color'],
            lambda v: self.on_value_changed('shadow_color', v),
            show_transparent=True
        )
        shadow_group.add(self.widgets['shadow_color'])
        
        self.widgets['shadow_color_inactive'] = ColorRow(
            "Inactive Shadow Color", "Color for inactive window shadows",
            self.settings.settings['shadow_color_inactive'],
            lambda v: self.on_value_changed('shadow_color_inactive', v),
            show_transparent=True
        )
        shadow_group.add(self.widgets['shadow_color_inactive'])
        
        content.append(shadow_group)
        
        # =========================================
        # SHADOW PRESETS SECTION
        # =========================================
        presets_group = Adw.PreferencesGroup(
            title="Shadow Presets",
            description="Quick shadow configurations"
        )
        
        for preset_name, preset_values in SHADOW_PRESETS.items():
            row = Adw.ActionRow(title=preset_name)
            btn = Gtk.Button(label="Apply", valign=Gtk.Align.CENTER)
            btn.connect("clicked", lambda _, name=preset_name: self.apply_shadow_preset(name))
            row.add_suffix(btn)
            presets_group.add(row)
        
        content.append(presets_group)
        
        # =========================================
        # QUICK PROFILES SECTION
        # =========================================
        profiles_group = Adw.PreferencesGroup(
            title="Quick Profiles",
            description="Complete decoration styles"
        )
        
        perf_row = Adw.ActionRow(
            title="Performance",
            subtitle="Minimal effects for best performance"
        )
        perf_btn = Gtk.Button(label="Apply", valign=Gtk.Align.CENTER)
        perf_btn.connect("clicked", lambda _: self.apply_profile('performance'))
        perf_row.add_suffix(perf_btn)
        profiles_group.add(perf_row)
        
        bal_row = Adw.ActionRow(
            title="Balanced",
            subtitle="Good mix of appearance and performance"
        )
        bal_btn = Gtk.Button(label="Apply", valign=Gtk.Align.CENTER)
        bal_btn.connect("clicked", lambda _: self.apply_profile('balanced'))
        bal_row.add_suffix(bal_btn)
        profiles_group.add(bal_row)
        
        candy_row = Adw.ActionRow(
            title="Eye Candy",
            subtitle="Maximum beauty, more resource intensive"
        )
        candy_btn = Gtk.Button(label="Apply", valign=Gtk.Align.CENTER)
        candy_btn.connect("clicked", lambda _: self.apply_profile('eyecandy'))
        candy_row.add_suffix(candy_btn)
        profiles_group.add(candy_row)
        
        content.append(profiles_group)
        
        scrolled.set_child(content)
        main_box.append(scrolled)
        
        # Status bar
        self.status_bar = Gtk.Label(label="Ready")
        self.status_bar.add_css_class("dim-label")
        self.status_bar.set_margin_top(6)
        self.status_bar.set_margin_bottom(6)
        main_box.append(self.status_bar)
        
        self.set_content(main_box)
    
    def on_value_changed(self, key, value):
        """Updates a setting"""
        self.settings.settings[key] = value
        self.status_bar.set_text(f"Changed: {key} = {value}")
    
    def apply_shadow_preset(self, preset_name):
        """Applies a shadow preset"""
        if preset_name in SHADOW_PRESETS:
            for key, value in SHADOW_PRESETS[preset_name].items():
                self.settings.settings[key] = value
            self.refresh_ui()
            self.status_bar.set_text(f"Shadow preset '{preset_name}' applied - click Apply to save")
    
    def apply_profile(self, profile_name):
        """Applies a quick profile"""
        profiles = {
            'performance': {
                'active_opacity': 1.0,
                'inactive_opacity': 1.0,
                'rounding': 0,
                'dim_inactive': False,
                'blur_enabled': False,
                'shadow_enabled': False,
            },
            'balanced': {
                'active_opacity': 1.0,
                'inactive_opacity': 0.95,
                'rounding': 10,
                'dim_inactive': True,
                'dim_strength': 0.3,
                'blur_enabled': True,
                'blur_size': 8,
                'blur_passes': 2,
                'shadow_enabled': True,
                'shadow_range': 30,
                'shadow_render_power': 2,
            },
            'eyecandy': {
                'active_opacity': 1.0,
                'inactive_opacity': 0.85,
                'rounding': 15,
                'dim_inactive': True,
                'dim_strength': 0.5,
                'blur_enabled': True,
                'blur_size': 12,
                'blur_passes': 3,
                'blur_vibrancy': 0.4,
                'shadow_enabled': True,
                'shadow_range': 55,
                'shadow_render_power': 4,
            }
        }
        
        if profile_name in profiles:
            for key, value in profiles[profile_name].items():
                self.settings.settings[key] = value
            self.refresh_ui()
            self.status_bar.set_text(f"Profile '{profile_name}' applied - click Apply to save")
    
    def refresh_ui(self):
        """Updates all UI components with current values"""
        s = self.settings.settings
        
        for key, widget in self.widgets.items():
            if key in s:
                if isinstance(widget, SliderRow):
                    widget.set_value(s[key])
                elif isinstance(widget, SwitchRow):
                    widget.set_active(s[key])
                elif isinstance(widget, ColorRow):
                    widget.set_color(s[key])
    
    def on_apply(self, button):
        """Saves and applies changes"""
        if self.settings.save_config():
            if self.settings.reload_hyprland():
                self.status_bar.set_text("✓ Saved and applied successfully!")
            else:
                self.status_bar.set_text("✓ Saved (could not reload Hyprland)")
        else:
            self.status_bar.set_text("✗ Error saving configuration!")
    
    def on_reset(self, button):
        """Resets to default values"""
        self.settings.reset_to_defaults()
        self.refresh_ui()
        self.status_bar.set_text("Reset to default values - click Apply to save")


class NordixDecorationsApp(Adw.Application):
    """Main application"""
    
    def __init__(self):
        super().__init__(
            application_id='com.Nordix.Settings.Decoration',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
    
    def do_activate(self):
        win = NordixDecorationsWindow(self)
        win.present()


def main():
    app = NordixDecorationsApp()
    return app.run(None)


if __name__ == "__main__":
    main()
