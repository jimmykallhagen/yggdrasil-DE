#!/usr/bin/env python3
##=========================================================##
 # SPDX-License-Identifier: GPL-3.0-or-later               #
 # Copyright (c) 2025 Jimmy Källhagen                      #
 # Part of Yggdrasil - Nordix desktop environment          #
##=========================================================##

"""Yggdrasil Groups Settings GUI
A graphical settings panel for Hyprland window group configuration
Handles: group behavior, merging, groupbar appearance, colors"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib
import subprocess
import os
import re
import shutil
from pathlib import Path


# =============================================
# NORDIX COLOR PALETTE
# =============================================
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
    '$subl-white-gray': {'name': 'Sublime White Gray', 'rgba': 'rgba(696f75ee)'},
    '$cosmic-gray': {'name': 'Cosmic Gray', 'rgba': 'rgba(8d9199ee)'},
}


# =============================================
# FONT WEIGHT OPTIONS
# =============================================
FONT_WEIGHT_OPTIONS = [
    {'value': 'thin', 'name': 'Thin'},
    {'value': 'extralight', 'name': 'Extra Light'},
    {'value': 'light', 'name': 'Light'},
    {'value': 'normal', 'name': 'Normal'},
    {'value': 'medium', 'name': 'Medium'},
    {'value': 'semibold', 'name': 'Semi Bold'},
    {'value': 'bold', 'name': 'Bold'},
    {'value': 'extrabold', 'name': 'Extra Bold'},
    {'value': 'black', 'name': 'Black'},
]


# =============================================
# DEFAULT SETTINGS
# =============================================
DEFAULT_SETTINGS = {
    # Group behavior
    'auto_group': True,
    'insert_after_current': True,
    'focus_removed_window': True,
    'drag_into_group': 1,
    'merge_groups_on_drag': True,
    'merge_groups_on_groupbar': True,
    'merge_floated_into_tiled_on_groupbar': True,
    'group_on_movetoworkspace': False,
    # Group border colors
    'col.border_active': '$nordix-hyprblue',
    'col.border_inactive': '$nordix-artic',
    'col.border_locked_active': '$nordix-artic',
    'col.border_locked_inactive': '$nordix-hyprblue',
    # Groupbar general
    'gb_enabled': True,
    'gb_font_family': 'Comfortaa',
    'gb_font_size': 12,
    'gb_font_weight_active': 'bold',
    'gb_font_weight_inactive': 'normal',
    'gb_gradients': True,
    'gb_height': 20,
    'gb_indicator_gap': 3,
    'gb_indicator_height': 0,
    'gb_stacked': false,
    'gb_priority': 5,
    'gb_render_titles': True,
    'gb_text_offset': 0,
    'gb_text_padding': 0,
    'gb_scrolling': True,
    # Groupbar rounding
    'gb_rounding': 15,
    'gb_rounding_power': 4.0,
    'gb_gradient_rounding': 45,
    'gb_gradient_rounding_power': 8.5,
    'gb_round_only_edges': false,
    'gb_gradient_round_only_edges': false,
    # Groupbar gaps
    'gb_gaps_in': 0,
    'gb_gaps_out': 1,
    'gb_keep_upper_gap': True,
    # Groupbar effects
    'gb_blur': False,
    # Groupbar colors
    'gb_text_color': '$nordix-tice',
    'gb_col_active': '$nordix-grey2',
    'gb_col_inactive': '$nordix-gray',
    'gb_col_locked_active': '$nordix-artic',
    'gb_col_locked_inactive': '$nordix-ghost',
}


# =============================================
# FILE PATH
# =============================================
CONFIG_PATH = Path.home() / ".config" / "nordix" / "yggdrasil" / "settings" / "Yggdrasil-groups.conf"

# =============================================
# SETTINGS HANDLER
# =============================================
class GroupSettings:
    """Handles reading and writing of nordix-groups.conf"""

    def __init__(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.load_config()

    def load_config(self):
        """Read current settings from config file"""
        if not CONFIG_PATH.exists():
            print(f"Config not found: {CONFIG_PATH}, using defaults")
            return

        try:
            content = CONFIG_PATH.read_text()

            in_group = False
            in_groupbar = False
            brace_depth = 0

            for line in content.split('\n'):
                stripped = line.strip()

                if stripped.startswith('# ') or not stripped:
                    continue

                # Track sections
                if re.match(r'^group\s*\{', stripped):
                    in_group = True
                    brace_depth = 1
                    continue
                elif re.match(r'^groupbar\s*\{', stripped) or ('groupbar' in stripped and '{' in stripped):
                    in_groupbar = True
                    brace_depth += 1
                    continue

                if '{' in stripped:
                    brace_depth += stripped.count('{')
                if '}' in stripped:
                    brace_depth -= stripped.count('}')
                    if brace_depth <= 1 and in_groupbar:
                        in_groupbar = False
                    if brace_depth <= 0:
                        in_group = False
                        in_groupbar = False
                        brace_depth = 0
                    continue

                if not in_group:
                    continue

                # Parse key = value
                if '=' in stripped:
                    parts = stripped.split('=', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()

                        # Remove inline comments
                        if '# ' in value:
                            value = value.split('# ')[0].strip()

                        # Remove quotes from strings
                        value = value.strip('"').strip("'")

                        self._set_value(key, value, in_groupbar)

        except Exception as e:
            print(f"Error loading config: {e}")

    def _set_value(self, key, value, in_groupbar):
        """Set a setting value based on key and section"""
        if in_groupbar:
            key_map = {
                'enabled': 'gb_enabled',
                'font_family': 'gb_font_family',
                'font_size': 'gb_font_size',
                'font_weight_active': 'gb_font_weight_active',
                'font_weight_inactive': 'gb_font_weight_inactive',
                'gradients': 'gb_gradients',
                'height': 'gb_height',
                'indicator_gap': 'gb_indicator_gap',
                'indicator_height': 'gb_indicator_height',
                'stacked': 'gb_stacked',
                'priority': 'gb_priority',
                'render_titles': 'gb_render_titles',
                'text_offset': 'gb_text_offset',
                'text_padding': 'gb_text_padding',
                'scrolling': 'gb_scrolling',
                'rounding': 'gb_rounding',
                'rounding_power': 'gb_rounding_power',
                'gradient_rounding': 'gb_gradient_rounding',
                'gradient_rounding_power': 'gb_gradient_rounding_power',
                'round_only_edges': 'gb_round_only_edges',
                'gradient_round_only_edges': 'gb_gradient_round_only_edges',
                'gaps_in': 'gb_gaps_in',
                'gaps_out': 'gb_gaps_out',
                'keep_upper_gap': 'gb_keep_upper_gap',
                'blur': 'gb_blur',
                'text_color': 'gb_text_color',
                'col.active': 'gb_col_active',
                'col.inactive': 'gb_col_inactive',
                'col.locked_active': 'gb_col_locked_active',
                'col.locked_inactive': 'gb_col_locked_inactive',
            }
            settings_key = key_map.get(key)
        else:
            # Group section - direct mapping for most, color keys as-is
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
        """Generate config file content"""
        s = self.settings

        def b(val):
            return 'true' if val else 'false'

        config = f'''
##=============================================##
 #        Yggdrasil's -  Group Settings        #
 #          Hyprland - Configuration           #
##=============================================##
 # Generated by Yggdrasil Groups Settings GUI  #
##=============================================##
source = ~/.config/nordix/yggdrasil/color/colors.conf

group {{


##==================##
 # GROUP BEHAVIOR   #
##==================##

# Automatically group new windows into focused unlocked group (bool)
auto_group = {b(s['auto_group'])}

# New windows in a group spawn after current or at group tail (bool)
insert_after_current = {b(s['insert_after_current'])}

# Focus window that was moved out of group (bool)
focus_removed_window = {b(s['focus_removed_window'])}

# Drag into group: 0 = disabled, 1 = enabled, 2 = only via groupbar (int)
drag_into_group = {s['drag_into_group']}

# Window groups can be dragged into other groups (bool)
merge_groups_on_drag = {b(s['merge_groups_on_drag'])}

# Merge groups when dragged into groupbar (bool)
merge_groups_on_groupbar = {b(s['merge_groups_on_groupbar'])}

# Merge floating window into tiled window groupbar (bool)
merge_floated_into_tiled_on_groupbar = {b(s['merge_floated_into_tiled_on_groupbar'])}

# Merge window into workspace solitary unlocked group on movetoworkspace (bool)
group_on_movetoworkspace = {b(s['group_on_movetoworkspace'])}


##======================##
 # GROUP BORDER COLORS  #
##======================##

# Active group border color
col.border_active = {s['col.border_active']}

# Inactive group border color
col.border_inactive = {s['col.border_inactive']}

# Active locked group border color
col.border_locked_active = {s['col.border_locked_active']}

# Inactive locked group border color
col.border_locked_inactive = {s['col.border_locked_inactive']}


##=============##
 # GROUPBAR    #
##=============##

    groupbar {{

# Enable groupbar (bool)
enabled = {b(s['gb_enabled'])}

# Font family
font_family = "{s['gb_font_family']}"

# Font size (int)
font_size = {s['gb_font_size']}

# Font weight for active title
font_weight_active = {s['gb_font_weight_active']}

# Font weight for inactive title
font_weight_inactive = {s['gb_font_weight_inactive']}

# Enable gradient effects (bool)
gradients = {b(s['gb_gradients'])}

# Groupbar height in pixels (int)
height = {s['gb_height']}

# Gap between indicator and title (int)
indicator_gap = {s['gb_indicator_gap']}

# Height of the groupbar indicator (int)
indicator_height = {s['gb_indicator_height']}

# Render groupbar as vertical stack (bool)
stacked = {b(s['gb_stacked'])}

# Decoration priority for groupbars (int)
priority = {s['gb_priority']}

# Render titles in group bar (bool)
render_titles = {b(s['gb_render_titles'])}

# Vertical position adjustment for titles (int)
text_offset = {s['gb_text_offset']}

# Horizontal padding for titles (int)
text_padding = {s['gb_text_padding']}

# Scrolling in groupbar changes active window (bool)
scrolling = {b(s['gb_scrolling'])}

# Indicator rounding (int)
rounding = {s['gb_rounding']}

# Rounding curve [1.0 - 20.0] (float)
rounding_power = {s['gb_rounding_power']:.1f}

# Indicator gradient_rounding (int)
gradient_rounding = {s['gb_gradient_rounding']}

# Rounding gradient_curve [1.0 - 20.0] (float)
gradient_rounding_power = {s['gb_gradient_rounding_power']:.1f}

# Round only indicator edges of entire groupbar (bool)
round_only_edges = {b(s['gb_round_only_edges'])}

# Round only gradient edges of entire groupbar (bool)
gradient_round_only_edges = {b(s['gb_gradient_round_only_edges'])}

# Gap size between gradients (int)
gaps_in = {s['gb_gaps_in']}

# Gap size between gradients and window (int)
gaps_out = {s['gb_gaps_out']}

# Add or remove upper gap (bool)
keep_upper_gap = {b(s['gb_keep_upper_gap'])}

# Blur groupbar indicators and gradients (bool)
blur = {b(s['gb_blur'])}


##========================##
 #    GROUPBAR COLORS     #
##========================##

text_color = {s['gb_text_color']}
col.active = {s['gb_col_active']}
col.inactive = {s['gb_col_inactive']}
col.locked_active = {s['gb_col_locked_active']}
col.locked_inactive = {s['gb_col_locked_inactive']}


    }}


}}
'''
        return config

    def save_config(self):
        """Save configuration to file"""
        try:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

            if CONFIG_PATH.exists():
                backup = CONFIG_PATH.with_suffix('.conf.backup')
                shutil.copy2(CONFIG_PATH, backup)

            CONFIG_PATH.write_text(self.generate_config())
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def reload_hyprland(self):
        """Reload Hyprland configuration"""
        try:
            subprocess.run(['hyprctl', 'reload'], check=True)
            return True
        except Exception as e:
            print(f"Error reloading Hyprland: {e}")
            return False

    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = DEFAULT_SETTINGS.copy()


# =============================================
# WIDGET CLASSES
# =============================================
class SliderRow(Adw.ActionRow):
    """A row with slider for numeric values"""

    def __init__(self, title, subtitle, min_val, max_val, step, value, callback, digits=0):
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
    """A row with dropdown for Nordix color selection with preview"""

    def __init__(self, title, subtitle, current_value, callback):
        super().__init__()
        self.set_title(title)
        self.set_subtitle(subtitle)

        self.callback = callback
        self.color_keys = []

        string_list = Gtk.StringList()
        current_index = 0

        for i, (color_var, color_info) in enumerate(NORDIX_COLORS.items()):
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
        if color_var in NORDIX_COLORS:
            rgba = NORDIX_COLORS[color_var]['rgba']
            match = re.search(r'rgba\(([0-9a-fA-F]{6})', rgba)
            if match:
                return f"#{match.group(1)}"
        return "#000000"

    def _create_color_pixbuf(self, hex_color, width=24, height=24):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        pixels = bytes([r, g, b] * (width * height))
        gbytes = GLib.Bytes.new(pixels)

        return GdkPixbuf.Pixbuf.new_from_bytes(
            gbytes,
            GdkPixbuf.Colorspace.RGB,
            False,
            8,
            width,
            height,
            width * 3
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
        if color_var in self.color_keys:
            index = self.color_keys.index(color_var)
            self.dropdown.set_selected(index)
            self.current_color = self._get_hex_color(color_var)
            self._update_preview()

class DropdownRow(Adw.ActionRow):
    """A row with dropdown for selecting from a list of options"""

    def __init__(self, title, subtitle, options, current_value, callback):
        super().__init__()
        self.set_title(title)
        self.set_subtitle(subtitle)

        self.callback = callback
        self.option_values = [opt['value'] for opt in options]

        string_list = Gtk.StringList()
        current_index = 0

        for i, opt in enumerate(options):
            string_list.append(opt['name'])
            if opt['value'] == current_value:
                current_index = i

        self.dropdown = Gtk.DropDown(model=string_list)
        self.dropdown.set_selected(current_index)
        self.dropdown.connect('notify::selected', self._on_selected)

        self.add_suffix(self.dropdown)

    def _on_selected(self, dropdown, _):
        selected = dropdown.get_selected()
        if selected < len(self.option_values):
            self.callback(self.option_values[selected])

    def set_value(self, value):
        if value in self.option_values:
            index = self.option_values.index(value)
            self.dropdown.set_selected(index)


class TextEntryRow(Adw.ActionRow):
    """A row with text entry field"""

    def __init__(self, title, subtitle, current_value, callback):
        super().__init__()
        self.set_title(title)
        self.set_subtitle(subtitle)

        self.callback = callback

        self.entry = Gtk.Entry()
        self.entry.set_text(current_value)
        self.entry.set_valign(Gtk.Align.CENTER)
        self.entry.set_width_chars(20)
        self.entry.connect('changed', self._on_changed)

        self.add_suffix(self.entry)

    def _on_changed(self, entry):
        self.callback(entry.get_text())

    def set_text(self, text):
        self.entry.set_text(text)


# =============================================
# MAIN WINDOW
# =============================================
class NordixGroupsWindow(Adw.ApplicationWindow):
    """Main window for group settings"""

    def __init__(self, app):
        super().__init__(application=app, title="Yggdrasil Groups Settings")
        self.set_default_size(550, 900)

        self.settings = GroupSettings()
        self.widgets = {}

        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.status_bar = Gtk.Label(label="Ready")
        self.status_bar.add_css_class("dim-label")
        self.status_bar.set_margin_top(6)
        self.status_bar.set_margin_bottom(6)

        # Header bar
        header = Adw.HeaderBar()

        apply_btn = Gtk.Button(label="Apply")
        apply_btn.add_css_class("suggested-action")
        apply_btn.connect("clicked", self.on_apply)
        header.pack_end(apply_btn)

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
        # GROUP BEHAVIOR SECTION
        # =========================================
        behavior_group = Adw.PreferencesGroup(
            title="Group Behavior",
            description="How windows are grouped and merged"
        )

        self.widgets['auto_group'] = SwitchRow(
            "Auto Group", "Automatically group new windows into focused unlocked group",
            self.settings.settings['auto_group'],
            lambda v: self.on_value_changed('auto_group', v)
        )
        behavior_group.add(self.widgets['auto_group'])

        self.widgets['insert_after_current'] = SwitchRow(
            "Insert After Current", "New windows in group spawn after current (off = at tail)",
            self.settings.settings['insert_after_current'],
            lambda v: self.on_value_changed('insert_after_current', v)
        )
        behavior_group.add(self.widgets['insert_after_current'])

        self.widgets['focus_removed_window'] = SwitchRow(
            "Focus Removed Window", "Focus window that was moved out of group",
            self.settings.settings['focus_removed_window'],
            lambda v: self.on_value_changed('focus_removed_window', v)
        )
        behavior_group.add(self.widgets['focus_removed_window'])

        self.widgets['drag_into_group'] = DropdownRow(
            "Drag Into Group", "How dragging windows into groups works",
            [
                {'value': 0, 'name': 'Disabled'},
                {'value': 1, 'name': 'Enabled'},
                {'value': 2, 'name': 'Only via Groupbar'},
            ],
            self.settings.settings['drag_into_group'],
            lambda v: self.on_value_changed('drag_into_group', v)
        )
        behavior_group.add(self.widgets['drag_into_group'])

        self.widgets['merge_groups_on_drag'] = SwitchRow(
            "Merge Groups on Drag", "Window groups can be dragged into other groups",
            self.settings.settings['merge_groups_on_drag'],
            lambda v: self.on_value_changed('merge_groups_on_drag', v)
        )
        behavior_group.add(self.widgets['merge_groups_on_drag'])

        self.widgets['merge_groups_on_groupbar'] = SwitchRow(
            "Merge on Groupbar", "Merge groups when dragged into groupbar",
            self.settings.settings['merge_groups_on_groupbar'],
            lambda v: self.on_value_changed('merge_groups_on_groupbar', v)
        )
        behavior_group.add(self.widgets['merge_groups_on_groupbar'])

        self.widgets['merge_floated_into_tiled_on_groupbar'] = SwitchRow(
            "Float into Tiled Groupbar", "Merge floating window into tiled window groupbar",
            self.settings.settings['merge_floated_into_tiled_on_groupbar'],
            lambda v: self.on_value_changed('merge_floated_into_tiled_on_groupbar', v)
        )
        behavior_group.add(self.widgets['merge_floated_into_tiled_on_groupbar'])

        self.widgets['group_on_movetoworkspace'] = SwitchRow(
            "Group on Move to Workspace", "Merge into workspace solitary group on movetoworkspace",
            self.settings.settings['group_on_movetoworkspace'],
            lambda v: self.on_value_changed('group_on_movetoworkspace', v)
        )
        behavior_group.add(self.widgets['group_on_movetoworkspace'])

        content.append(behavior_group)

        # =========================================
        # GROUP BORDER COLORS SECTION
        # =========================================
        border_group = Adw.PreferencesGroup(
            title="Group Border Colors",
            description="Border colors for grouped windows"
        )

        self.widgets['col.border_active'] = ColorRow(
            "Active Border", "Active group border color",
            self.settings.settings['col.border_active'],
            lambda v: self.on_value_changed('col.border_active', v),

        )
        border_group.add(self.widgets['col.border_active'])

        self.widgets['col.border_inactive'] = ColorRow(
            "Inactive Border", "Inactive group border color",
            self.settings.settings['col.border_inactive'],
            lambda v: self.on_value_changed('col.border_inactive', v),

        )
        border_group.add(self.widgets['col.border_inactive'])

        self.widgets['col.border_locked_active'] = ColorRow(
            "Locked Active Border", "Active locked group border color",
            self.settings.settings['col.border_locked_active'],
            lambda v: self.on_value_changed('col.border_locked_active', v),

        )
        border_group.add(self.widgets['col.border_locked_active'])

        self.widgets['col.border_locked_inactive'] = ColorRow(
            "Locked Inactive Border", "Inactive locked group border color",
            self.settings.settings['col.border_locked_inactive'],
            lambda v: self.on_value_changed('col.border_locked_inactive', v),

        )
        border_group.add(self.widgets['col.border_locked_inactive'])

        content.append(border_group)

        # =========================================
        # GROUPBAR GENERAL SECTION
        # =========================================
        gb_general_group = Adw.PreferencesGroup(
            title="Groupbar",
            description="Appearance and behavior of the group tab bar"
        )

        self.widgets['gb_enabled'] = SwitchRow(
            "Enable Groupbar", "Show the groupbar decoration on grouped windows",
            self.settings.settings['gb_enabled'],
            lambda v: self.on_value_changed('gb_enabled', v)
        )
        gb_general_group.add(self.widgets['gb_enabled'])

        self.widgets['gb_stacked'] = SwitchRow(
            "Stacked Layout", "Render groupbar as a vertical stack",
            self.settings.settings['gb_stacked'],
            lambda v: self.on_value_changed('gb_stacked', v)
        )
        gb_general_group.add(self.widgets['gb_stacked'])

        self.widgets['gb_height'] = SliderRow(
            "Height", "Groupbar height in pixels [10 - 40]",
            10, 40, 1, self.settings.settings['gb_height'],
            lambda v: self.on_value_changed('gb_height', int(v))
        )
        gb_general_group.add(self.widgets['gb_height'])

        self.widgets['gb_render_titles'] = SwitchRow(
            "Render Titles", "Show window titles in the groupbar",
            self.settings.settings['gb_render_titles'],
            lambda v: self.on_value_changed('gb_render_titles', v)
        )
        gb_general_group.add(self.widgets['gb_render_titles'])

        self.widgets['gb_scrolling'] = SwitchRow(
            "Scrolling", "Scroll in groupbar to change active window",
            self.settings.settings['gb_scrolling'],
            lambda v: self.on_value_changed('gb_scrolling', v)
        )
        gb_general_group.add(self.widgets['gb_scrolling'])

        self.widgets['gb_gradients'] = SwitchRow(
            "Gradients", "Enable gradient effects on groupbar",
            self.settings.settings['gb_gradients'],
            lambda v: self.on_value_changed('gb_gradients', v)
        )
        gb_general_group.add(self.widgets['gb_gradients'])

        self.widgets['gb_blur'] = SwitchRow(
            "Blur", "Apply blur to groupbar indicators and gradients",
            self.settings.settings['gb_blur'],
            lambda v: self.on_value_changed('gb_blur', v)
        )
        gb_general_group.add(self.widgets['gb_blur'])

        self.widgets['gb_priority'] = SliderRow(
            "Priority", "Decoration priority for groupbars [0 - 10]",
            0, 10, 1, self.settings.settings['gb_priority'],
            lambda v: self.on_value_changed('gb_priority', int(v))
        )
        gb_general_group.add(self.widgets['gb_priority'])

        content.append(gb_general_group)

        # =========================================
        # GROUPBAR FONT SECTION
        # =========================================
        gb_font_group = Adw.PreferencesGroup(
            title="Groupbar Font",
            description="Font settings for groupbar titles"
        )

        self.widgets['gb_font_family'] = TextEntryRow(
            "Font Family", "Font used for groupbar titles",
            self.settings.settings['gb_font_family'],
            lambda v: self.on_value_changed('gb_font_family', v)
        )
        gb_font_group.add(self.widgets['gb_font_family'])

        self.widgets['gb_font_size'] = SliderRow(
            "Font Size", "Font size in pixels [8 - 24]",
            8, 24, 1, self.settings.settings['gb_font_size'],
            lambda v: self.on_value_changed('gb_font_size', int(v))
        )
        gb_font_group.add(self.widgets['gb_font_size'])

        self.widgets['gb_font_weight_active'] = DropdownRow(
            "Active Font Weight", "Font weight for active groupbar title",
            FONT_WEIGHT_OPTIONS,
            self.settings.settings['gb_font_weight_active'],
            lambda v: self.on_value_changed('gb_font_weight_active', v)
        )
        gb_font_group.add(self.widgets['gb_font_weight_active'])

        self.widgets['gb_font_weight_inactive'] = DropdownRow(
            "Inactive Font Weight", "Font weight for inactive groupbar title",
            FONT_WEIGHT_OPTIONS,
            self.settings.settings['gb_font_weight_inactive'],
            lambda v: self.on_value_changed('gb_font_weight_inactive', v)
        )
        gb_font_group.add(self.widgets['gb_font_weight_inactive'])

        self.widgets['gb_text_offset'] = SliderRow(
            "Text Offset", "Vertical position adjustment for titles [-10 - 10]",
            -10, 10, 1, self.settings.settings['gb_text_offset'],
            lambda v: self.on_value_changed('gb_text_offset', int(v))
        )
        gb_font_group.add(self.widgets['gb_text_offset'])

        self.widgets['gb_text_padding'] = SliderRow(
            "Text Padding", "Horizontal padding for titles [0 - 20]",
            0, 20, 1, self.settings.settings['gb_text_padding'],
            lambda v: self.on_value_changed('gb_text_padding', int(v))
        )
        gb_font_group.add(self.widgets['gb_text_padding'])

        content.append(gb_font_group)

        # =========================================
        # GROUPBAR INDICATOR SECTION
        # =========================================
        gb_indicator_group = Adw.PreferencesGroup(
            title="Groupbar Indicator & Rounding",
            description="Indicator appearance and corner rounding"
        )

        self.widgets['gb_indicator_height'] = SliderRow(
            "Indicator Height", "Height of the groupbar indicator [0 - 10]",
            0, 10, 1, self.settings.settings['gb_indicator_height'],
            lambda v: self.on_value_changed('gb_indicator_height', int(v))
        )
        gb_indicator_group.add(self.widgets['gb_indicator_height'])

        self.widgets['gb_indicator_gap'] = SliderRow(
            "Indicator Gap", "Gap between indicator and title [0 - 10]",
            0, 10, 1, self.settings.settings['gb_indicator_gap'],
            lambda v: self.on_value_changed('gb_indicator_gap', int(v))
        )
        gb_indicator_group.add(self.widgets['gb_indicator_gap'])

        self.widgets['gb_rounding'] = SliderRow(
            "Rounding", "How much to round the indicator [0 - 45]",
            0, 45, 1, self.settings.settings['gb_rounding'],
            lambda v: self.on_value_changed('gb_rounding', int(v))
        )
        gb_indicator_group.add(self.widgets['gb_rounding'])

        self.widgets['gb_rounding_power'] = SliderRow(
            "Rounding Power", "Rounding curve: 1.0 triangle, 2.0 circle, 4.0 squircle [1.0 - 20.0]",
            1.0, 20.0, 0.5, self.settings.settings['gb_rounding_power'],
            lambda v: self.on_value_changed('gb_rounding_power', v),
            digits=1
        )
        gb_indicator_group.add(self.widgets['gb_rounding_power'])

        self.widgets['gb_gradient_rounding'] = SliderRow(
             "Gradient Rounding", "How much to Gradient round the indicator [0 - 45]",
             0, 45, 1, self.settings.settings['gb_gradient_rounding'],
             lambda v: self.on_value_changed('gb_gradient_rounding', int(v))
         )
        gb_indicator_group.add(self.widgets['gb_gradient_rounding'])

        self.widgets['gb_gradient_rounding_power'] = SliderRow(
             "Gradient Rounding Power", "Gradient Rounding curve: 1.0 triangle, 2.0 circle, 4.0 squircle [1.0 - 20.0]",
             1.0, 20.0, 0.5, self.settings.settings['gb_gradient_rounding_power'],
             lambda v: self.on_value_changed('gb_gradient_rounding_power', v),
             digits=1
         )
        gb_indicator_group.add(self.widgets['gb_gradient_rounding_power'])

        self.widgets['gb_round_only_edges'] = SwitchRow(
            "Round Only Edges", "Only round the indicator edges of the entire groupbar",
            self.settings.settings['gb_round_only_edges'],
            lambda v: self.on_value_changed('gb_round_only_edges', v)
        )
        gb_indicator_group.add(self.widgets['gb_round_only_edges'])

        self.widgets['gb_gradient_round_only_edges'] = SwitchRow(
            "Gradient Round Only Edges", "Only round gradient edges of entire groupbar",
            self.settings.settings['gb_gradient_round_only_edges'],
            lambda v: self.on_value_changed('gb_gradient_round_only_edges', v)
        )
        gb_indicator_group.add(self.widgets['gb_gradient_round_only_edges'])

        content.append(gb_indicator_group)

        # =========================================
        # GROUPBAR GAPS SECTION
        # =========================================
        gb_gaps_group = Adw.PreferencesGroup(
            title="Groupbar Gaps",
            description="Spacing within the groupbar"
        )

        self.widgets['gb_gaps_in'] = SliderRow(
            "Inner Gaps", "Gap size between gradients [0 - 10]",
            0, 10, 1, self.settings.settings['gb_gaps_in'],
            lambda v: self.on_value_changed('gb_gaps_in', int(v))
        )
        gb_gaps_group.add(self.widgets['gb_gaps_in'])

        self.widgets['gb_gaps_out'] = SliderRow(
            "Outer Gaps", "Gap size between gradients and window [0 - 10]",
            0, 10, 1, self.settings.settings['gb_gaps_out'],
            lambda v: self.on_value_changed('gb_gaps_out', int(v))
        )
        gb_gaps_group.add(self.widgets['gb_gaps_out'])

        self.widgets['gb_keep_upper_gap'] = SwitchRow(
            "Keep Upper Gap", "Add upper gap above groupbar",
            self.settings.settings['gb_keep_upper_gap'],
            lambda v: self.on_value_changed('gb_keep_upper_gap', v)
        )
        gb_gaps_group.add(self.widgets['gb_keep_upper_gap'])

        content.append(gb_gaps_group)

        # =========================================
        # GROUPBAR COLORS SECTION
        # =========================================
        gb_colors_group = Adw.PreferencesGroup(
            title="Groupbar Colors",
            description="Colors for groupbar elements"
        )

        self.widgets['gb_text_color'] = ColorRow(
            "Text Color", "Color of groupbar title text",
            self.settings.settings['gb_text_color'],
            lambda v: self.on_value_changed('gb_text_color', v),

        )
        gb_colors_group.add(self.widgets['gb_text_color'])

        self.widgets['gb_col_active'] = ColorRow(
            "Active Tab", "Color of the active groupbar tab",
            self.settings.settings['gb_col_active'],
            lambda v: self.on_value_changed('gb_col_active', v),

        )
        gb_colors_group.add(self.widgets['gb_col_active'])

        self.widgets['gb_col_inactive'] = ColorRow(
            "Inactive Tab", "Color of inactive groupbar tabs",
            self.settings.settings['gb_col_inactive'],
            lambda v: self.on_value_changed('gb_col_inactive', v),

        )
        gb_colors_group.add(self.widgets['gb_col_inactive'])

        self.widgets['gb_col_locked_active'] = ColorRow(
            "Locked Active Tab", "Color of active locked groupbar tab",
            self.settings.settings['gb_col_locked_active'],
            lambda v: self.on_value_changed('gb_col_locked_active', v),

        )
        gb_colors_group.add(self.widgets['gb_col_locked_active'])

        self.widgets['gb_col_locked_inactive'] = ColorRow(
            "Locked Inactive Tab", "Color of inactive locked groupbar tab",
            self.settings.settings['gb_col_locked_inactive'],
            lambda v: self.on_value_changed('gb_col_locked_inactive', v),

        )
        gb_colors_group.add(self.widgets['gb_col_locked_inactive'])

        content.append(gb_colors_group)

        scrolled.set_child(content)
        main_box.append(scrolled)

        main_box.append(self.status_bar)

        self.set_content(main_box)

    def on_value_changed(self, key, value):
        """Update a setting"""
        self.settings.settings[key] = value
        self.status_bar.set_text(f"Changed: {key} = {value}")

    def on_apply(self, button):
        """Save and apply changes"""
        if self.settings.save_config():
            if self.settings.reload_hyprland():
                self.status_bar.set_text("Saved and applied successfully!")
            else:
                self.status_bar.set_text("Saved (could not reload Hyprland)")
        else:
            self.status_bar.set_text("Error saving configuration!")

    def on_reset(self, button):
        """Reset to default values"""
        self.settings.reset_to_defaults()
        self.refresh_ui()
        self.status_bar.set_text("Reset to Nordix defaults — click Apply to save")

    def refresh_ui(self):
        """Update all widgets with current values"""
        s = self.settings.settings

        for key, widget in self.widgets.items():
            if key in s:
                if isinstance(widget, SliderRow):
                    widget.set_value(s[key])
                elif isinstance(widget, SwitchRow):
                    widget.set_active(s[key])
                elif isinstance(widget, ColorRow):
                    widget.set_color(s[key])
                elif isinstance(widget, DropdownRow):
                    widget.set_value(s[key])
                elif isinstance(widget, TextEntryRow):
                    widget.set_text(s[key])


# =============================================
# APPLICATION
# =============================================
class NordixGroupsApp(Adw.Application):
    """Main application"""

    def __init__(self):
        super().__init__(
            application_id='com.Nordix.Settings.Groups',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

    def do_activate(self):
        win = NordixGroupsWindow(self)
        win.present()


def main():
    app = NordixGroupsApp()
    return app.run(None)


if __name__ == "__main__":
    main()
