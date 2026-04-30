#!/usr/bin/env python3
##=========================================================##
 # SPDX-License-Identifier: GPL-3.0-or-later               #
 # Copyright (c) 2025 Jimmy Källhagen                      #
 # Part of Yggdrasil - Nordix desktop environment          #
##=========================================================##

"""Yggdrasil General Settings GUI
A graphical settings panel for Hyprland general configuration
Handles: locale, borders, gaps, colors, snap, tearing, resize"""

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
    '$subl-light-gray': {'name': 'Sublime Light Gray', 'rgba': 'rgba(4f565eee)'},
    '$subl-white-gray': {'name': 'Sublime White Gray', 'rgba': 'rgba(696f75ee)'},
    '$cosmic-gray': {'name': 'Cosmic Gray', 'rgba': 'rgba(8d9199ee)'},
}


# =============================================
# COMMON LOCALE OPTIONS
# =============================================
LOCALE_OPTIONS = [
    {'value': '', 'name': 'System Default'},
    {'value': 'en_US', 'name': 'English (US)'},
    {'value': 'en_GB', 'name': 'English (UK)'},
    {'value': 'sv_SE', 'name': 'Svenska (Swedish)'},
    {'value': 'nb_NO', 'name': 'Norsk Bokmål (Norwegian)'},
    {'value': 'nn_NO', 'name': 'Norsk Nynorsk'},
    {'value': 'da_DK', 'name': 'Dansk (Danish)'},
    {'value': 'fi_FI', 'name': 'Suomi (Finnish)'},
    {'value': 'is_IS', 'name': 'Íslenska (Icelandic)'},
    {'value': 'de_DE', 'name': 'Deutsch (German)'},
    {'value': 'de_AT', 'name': 'Deutsch (Austria)'},
    {'value': 'de_CH', 'name': 'Deutsch (Switzerland)'},
    {'value': 'fr_FR', 'name': 'Français (French)'},
    {'value': 'fr_CA', 'name': 'Français (Canada)'},
    {'value': 'fr_CH', 'name': 'Français (Switzerland)'},
    {'value': 'es_ES', 'name': 'Español (Spain)'},
    {'value': 'es_MX', 'name': 'Español (Mexico)'},
    {'value': 'es_AR', 'name': 'Español (Argentina)'},
    {'value': 'pt_BR', 'name': 'Português (Brazil)'},
    {'value': 'pt_PT', 'name': 'Português (Portugal)'},
    {'value': 'it_IT', 'name': 'Italiano (Italian)'},
    {'value': 'nl_NL', 'name': 'Nederlands (Dutch)'},
    {'value': 'nl_BE', 'name': 'Nederlands (Belgium)'},
    {'value': 'pl_PL', 'name': 'Polski (Polish)'},
    {'value': 'cs_CZ', 'name': 'Čeština (Czech)'},
    {'value': 'sk_SK', 'name': 'Slovenčina (Slovak)'},
    {'value': 'hu_HU', 'name': 'Magyar (Hungarian)'},
    {'value': 'ro_RO', 'name': 'Română (Romanian)'},
    {'value': 'bg_BG', 'name': 'Български (Bulgarian)'},
    {'value': 'hr_HR', 'name': 'Hrvatski (Croatian)'},
    {'value': 'sl_SI', 'name': 'Slovenščina (Slovenian)'},
    {'value': 'sr_RS', 'name': 'Српски (Serbian)'},
    {'value': 'el_GR', 'name': 'Ελληνικά (Greek)'},
    {'value': 'tr_TR', 'name': 'Türkçe (Turkish)'},
    {'value': 'ru_RU', 'name': 'Русский (Russian)'},
    {'value': 'uk_UA', 'name': 'Українська (Ukrainian)'},
    {'value': 'ja_JP', 'name': '日本語 (Japanese)'},
    {'value': 'ko_KR', 'name': '한국어 (Korean)'},
    {'value': 'zh_CN', 'name': '中文 简体 (Chinese Simplified)'},
    {'value': 'zh_TW', 'name': '中文 繁體 (Chinese Traditional)'},
    {'value': 'ar_SA', 'name': 'العربية (Arabic)'},
    {'value': 'he_IL', 'name': 'עברית (Hebrew)'},
    {'value': 'hi_IN', 'name': 'हिन्दी (Hindi)'},
    {'value': 'th_TH', 'name': 'ไทย (Thai)'},
    {'value': 'vi_VN', 'name': 'Tiếng Việt (Vietnamese)'},
    {'value': 'id_ID', 'name': 'Bahasa Indonesia'},
    {'value': 'ms_MY', 'name': 'Bahasa Melayu (Malay)'},
]


# =============================================
# DEFAULT SETTINGS
# =============================================
DEFAULT_SETTINGS = {
    # Locale
    'locale': '',
    # Tearing
    'allow_tearing': True,
    # Borders
    'border_size': 1,
    # Gaps
    'gaps_in': 3,
    'gaps_out': 5,
    'float_gaps': 0,
    'gaps_workspaces': 5,
    # Focus
    'no_focus_fallback': True,
    # Resize
    'resize_on_border': False,
    'extend_border_grab_area': 15,
    'hover_icon_on_border': True,
    'resize_corner': 0,
    # Modal
    'modal_parent_blocking': True,
    # Colors
    'col.active_border': '$nordix-hyprblue',
    'col.inactive_border': '$nordix-artic',
    'col.nogroup_border': '$nordix-blue',
    'col.nogroup_border_active': '$nordix-hyprblue',
    # Snap
    'snap_enabled': True,
    'snap_window_gap': 10,
    'snap_monitor_gap': 10,
    'snap_border_overlap': True,
    'snap_respect_gaps': True,
}


# =============================================
# FILE PATH
# =============================================
CONFIG_PATH = Path.home() / ".config" / "nordix" / "yggdrasil" / "settings" / "Yggdrasil-general.conf"


# =============================================
# SETTINGS HANDLER
# =============================================
class GeneralSettings:
    """Handles reading and writing of nordix-general.conf"""

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

            in_snap = False
            in_general = False
            brace_depth = 0

            for line in content.split('\n'):
                stripped = line.strip()

                if stripped.startswith('# ') or not stripped:
                    continue

                # Track sections
                if 'general' in stripped and '{' in stripped:
                    in_general = True
                    brace_depth = 1
                    continue
                elif 'snap' in stripped and '{' in stripped:
                    in_snap = True
                    brace_depth += 1
                    continue

                if '{' in stripped:
                    brace_depth += stripped.count('{')
                if '}' in stripped:
                    brace_depth -= stripped.count('}')
                    if brace_depth <= 1 and in_snap:
                        in_snap = False
                    if brace_depth <= 0:
                        in_general = False
                        in_snap = False
                        brace_depth = 0
                    continue

                if not in_general:
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

                        self._set_value(key, value, in_snap)

        except Exception as e:
            print(f"Error loading config: {e}")

    def _set_value(self, key, value, in_snap):
        """Set a setting value based on key and section"""
        if in_snap:
            key_map = {
                'enabled': 'snap_enabled',
                'window_gap': 'snap_window_gap',
                'monitor_gap': 'snap_monitor_gap',
                'border_overlap': 'snap_border_overlap',
                'respect_gaps': 'snap_respect_gaps',
            }
            settings_key = key_map.get(key)
        else:
            # Direct mapping for general section
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
        config = f'''
##=============================================##
 #       Yggdrasil's -  General Settings       #
 #          Hyprland - Configuration           #
##=============================================##
 # Generated by Yggdrasil General Settings GUI #
##=============================================##
source = ~/.config/nordix/yggdrasil/color/colors.conf

general {{


##===========##
 # LANGUAGE  #
##===========##

# Override system locale (e.g. en_US, sv_SE) - leave empty for system default
locale = {s['locale']}


##===========##
 #  TEARING  #
##===========##

# Master switch for allowing tearing to occur (bool)
allow_tearing = {'true' if s['allow_tearing'] else 'false'}


##===========##
 #  BORDERS  #
##===========##

# Size of the border around windows (int)
border_size = {s['border_size']}


##========##
 #  GAPS  #
##========##

# Gaps between windows (int)
gaps_in = {s['gaps_in']}

# Gaps between windows and monitor edges (int)
gaps_out = {s['gaps_out']}

# Gaps for floating windows, -1 means default (int)
float_gaps = {s['float_gaps']}

# Gaps between workspaces, stacks with gaps_out (int)
gaps_workspaces = {s['gaps_workspaces']}


##=========##
 #  FOCUS  #
##=========##

# Will not fall back to next window when moving focus where no window exists (bool)
no_focus_fallback = {'true' if s['no_focus_fallback'] else 'false'}


##==========##
 #  RESIZE  #
##==========##

# Resize windows by clicking and dragging on borders and gaps (bool)
resize_on_border = {'true' if s['resize_on_border'] else 'false'}

# Extend area around border for click and drag (int)
extend_border_grab_area = {s['extend_border_grab_area']}

# Show cursor icon when hovering over borders (bool)
hover_icon_on_border = {'true' if s['hover_icon_on_border'] else 'false'}

# Force floating windows to use specific corner for resize, 0 to disable (int)
resize_corner = {s['resize_corner']}


##=========##
 #  MODAL #
##=========##

# Whether parent windows of modals will be interactive (bool)
modal_parent_blocking = {'true' if s['modal_parent_blocking'] else 'false'}


##===================##
 #   BORDER COLORS   #
##===================##

# Active window border color
col.active_border = {s['col.active_border']}

# Inactive window border color
col.inactive_border = {s['col.inactive_border']}

# Inactive border for windows that cannot be added to a group
col.nogroup_border = {s['col.nogroup_border']}

# Active border for windows that cannot be added to a group
col.nogroup_border_active = {s['col.nogroup_border_active']}


##========##
 #  SNAP  #
##========##

    snap {{

# Enable snapping for floating windows (bool)
enabled = {'true' if s['snap_enabled'] else 'false'}

# Minimum gap in pixels between windows before snapping (int)
window_gap = {s['snap_window_gap']}

# Minimum gap in pixels between window and monitor edges before snapping (int)
monitor_gap = {s['snap_monitor_gap']}

# Snap so only one border width of space between windows (bool)
border_overlap = {'true' if s['snap_border_overlap'] else 'false'}

# Respect gaps_in setting when snapping (bool)
respect_gaps = {'true' if s['snap_respect_gaps'] else 'false'}

    }}


}}
'''
        return config

    def save_config(self):
        """Save configuration to file"""
        try:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

            # Create backup
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
        """Convert Nordix color variable to hex"""
        if color_var in NORDIX_COLORS:
            rgba = NORDIX_COLORS[color_var]['rgba']
            match = re.search(r'rgba\(([0-9a-fA-F]{6})', rgba)
            if match:
                return f"#{match.group(1)}"
        return "#000000"

    def _create_color_pixbuf(self, hex_color, width=24, height=24):
        """Create a pixbuf with exact color - immune to themes"""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        pixels = bytes([r, g, b] * (width * height))

        return GdkPixbuf.Pixbuf.new_from_data(
            pixels,
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
        """Set selected color"""
        if color_var in self.color_keys:
            index = self.color_keys.index(color_var)
            self.dropdown.set_selected(index)
            self.current_color = self._get_hex_color(color_var)
            self._update_preview()

class DropdownRow(Adw.ActionRow):
    """A row with dropdown for selecting from a list of options"""

    def __init__(self, title, subtitle, options, current_value, callback):
        """Args:
            options: list of {'value': str, 'name': str}
            current_value: current value string
            callback: called with new value"""
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


# =============================================
# MAIN WINDOW
# =============================================
class NordixGeneralWindow(Adw.ApplicationWindow):
    """Main window for general settings"""

    def __init__(self, app):
        super().__init__(application=app, title="Yggdrasil General Settings")
        self.set_default_size(550, 850)

        self.settings = GeneralSettings()
        self.widgets = {}

        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

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
        # LANGUAGE SECTION
        # =========================================
        lang_group = Adw.PreferencesGroup(
            title="Language",
            description="Override system locale for Hyprland"
        )

        self.widgets['locale'] = DropdownRow(
            "Locale", "Language and region setting",
            LOCALE_OPTIONS,
            self.settings.settings['locale'],
            lambda v: self.on_value_changed('locale', v)
        )
        lang_group.add(self.widgets['locale'])

        content.append(lang_group)

        # =========================================
        # BORDERS SECTION
        # =========================================
        border_group = Adw.PreferencesGroup(
            title="Window Borders",
            description="Border size and colors for windows"
        )

        self.widgets['border_size'] = SliderRow(
            "Border Size", "Size of border around windows [0 - 10]",
            0, 10, 1, self.settings.settings['border_size'],
            lambda v: self.on_value_changed('border_size', int(v))
        )
        border_group.add(self.widgets['border_size'])

        self.widgets['col.active_border'] = ColorRow(
            "Active Border Color", "Border color for the focused window",
            self.settings.settings['col.active_border'],
            lambda v: self.on_value_changed('col.active_border', v)
        )
        border_group.add(self.widgets['col.active_border'])

        self.widgets['col.inactive_border'] = ColorRow(
            "Inactive Border Color", "Border color for unfocused windows",
            self.settings.settings['col.inactive_border'],
            lambda v: self.on_value_changed('col.inactive_border', v)
        )
        border_group.add(self.widgets['col.inactive_border'])

        self.widgets['col.nogroup_border'] = ColorRow(
            "No-Group Border", "Inactive border for ungroupable windows",
            self.settings.settings['col.nogroup_border'],
            lambda v: self.on_value_changed('col.nogroup_border', v)
        )
        border_group.add(self.widgets['col.nogroup_border'])

        self.widgets['col.nogroup_border_active'] = ColorRow(
            "No-Group Border Active", "Active border for ungroupable windows",
            self.settings.settings['col.nogroup_border_active'],
            lambda v: self.on_value_changed('col.nogroup_border_active', v)
        )
        border_group.add(self.widgets['col.nogroup_border_active'])

        content.append(border_group)

        # =========================================
        # GAPS SECTION
        # =========================================
        gaps_group = Adw.PreferencesGroup(
            title="Gaps",
            description="Spacing between windows and edges"
        )

        self.widgets['gaps_in'] = SliderRow(
            "Gaps Between Windows", "Space between tiled windows [0 - 30]",
            0, 30, 1, self.settings.settings['gaps_in'],
            lambda v: self.on_value_changed('gaps_in', int(v))
        )
        gaps_group.add(self.widgets['gaps_in'])

        self.widgets['gaps_out'] = SliderRow(
            "Gaps to Monitor Edges", "Space between windows and screen edges [0 - 30]",
            0, 30, 1, self.settings.settings['gaps_out'],
            lambda v: self.on_value_changed('gaps_out', int(v))
        )
        gaps_group.add(self.widgets['gaps_out'])

        self.widgets['float_gaps'] = SliderRow(
            "Floating Window Gaps", "Gaps for floating windows, -1 for default [-1 - 30]",
            -1, 30, 1, self.settings.settings['float_gaps'],
            lambda v: self.on_value_changed('float_gaps', int(v))
        )
        gaps_group.add(self.widgets['float_gaps'])

        self.widgets['gaps_workspaces'] = SliderRow(
            "Workspace Gaps", "Gaps between workspaces [0 - 30]",
            0, 30, 1, self.settings.settings['gaps_workspaces'],
            lambda v: self.on_value_changed('gaps_workspaces', int(v))
        )
        gaps_group.add(self.widgets['gaps_workspaces'])

        content.append(gaps_group)

        # =========================================
        # GAMING SECTION
        # =========================================
        gaming_group = Adw.PreferencesGroup(
            title="Gaming",
            description="Settings that affect gaming performance"
        )

        self.widgets['allow_tearing'] = SwitchRow(
            "Allow Tearing", "Allow screen tearing for reduced input lag in games",
            self.settings.settings['allow_tearing'],
            lambda v: self.on_value_changed('allow_tearing', v)
        )
        gaming_group.add(self.widgets['allow_tearing'])

        content.append(gaming_group)

        # =========================================
        # RESIZE & INTERACTION SECTION
        # =========================================
        resize_group = Adw.PreferencesGroup(
            title="Resize & Interaction",
            description="How windows can be resized and interact"
        )

        self.widgets['resize_on_border'] = SwitchRow(
            "Resize on Border", "Resize windows by dragging their borders",
            self.settings.settings['resize_on_border'],
            lambda v: self.on_resize_border_changed(v)
        )
        resize_group.add(self.widgets['resize_on_border'])

        self.widgets['extend_border_grab_area'] = SliderRow(
            "Border Grab Area", "Pixel area around border for click and drag [0 - 30]",
            0, 30, 1, self.settings.settings['extend_border_grab_area'],
            lambda v: self.on_value_changed('extend_border_grab_area', int(v))
        )
        resize_group.add(self.widgets['extend_border_grab_area'])

        self.widgets['hover_icon_on_border'] = SwitchRow(
            "Hover Cursor on Border", "Show resize cursor when hovering over borders",
            self.settings.settings['hover_icon_on_border'],
            lambda v: self.on_value_changed('hover_icon_on_border', v)
        )
        resize_group.add(self.widgets['hover_icon_on_border'])

        self.widgets['resize_corner'] = SliderRow(
            "Resize Corner", "Force resize from corner (0 = disabled, 1-4 clockwise from top-left)",
            0, 4, 1, self.settings.settings['resize_corner'],
            lambda v: self.on_value_changed('resize_corner', int(v))
        )
        resize_group.add(self.widgets['resize_corner'])

        self.widgets['no_focus_fallback'] = SwitchRow(
            "No Focus Fallback", "Don't fall back to next window when moving focus to empty area",
            self.settings.settings['no_focus_fallback'],
            lambda v: self.on_value_changed('no_focus_fallback', v)
        )
        resize_group.add(self.widgets['no_focus_fallback'])

        self.widgets['modal_parent_blocking'] = SwitchRow(
            "Modal Parent Blocking", "Whether parent windows of modal dialogs are interactive",
            self.settings.settings['modal_parent_blocking'],
            lambda v: self.on_value_changed('modal_parent_blocking', v)
        )
        resize_group.add(self.widgets['modal_parent_blocking'])

        content.append(resize_group)

        # =========================================
        # SNAP SECTION
        # =========================================
        snap_group = Adw.PreferencesGroup(
            title="Window Snapping",
            description="Snap floating windows to edges and other windows"
        )

        self.widgets['snap_enabled'] = SwitchRow(
            "Enable Snapping", "Snap floating windows to nearby edges",
            self.settings.settings['snap_enabled'],
            lambda v: self.on_value_changed('snap_enabled', v)
        )
        snap_group.add(self.widgets['snap_enabled'])

        self.widgets['snap_window_gap'] = SliderRow(
            "Window Snap Gap", "Minimum pixels between windows before snapping [0 - 50]",
            0, 50, 1, self.settings.settings['snap_window_gap'],
            lambda v: self.on_value_changed('snap_window_gap', int(v))
        )
        snap_group.add(self.widgets['snap_window_gap'])

        self.widgets['snap_monitor_gap'] = SliderRow(
            "Monitor Snap Gap", "Minimum pixels between window and monitor edge [0 - 50]",
            0, 50, 1, self.settings.settings['snap_monitor_gap'],
            lambda v: self.on_value_changed('snap_monitor_gap', int(v))
        )
        snap_group.add(self.widgets['snap_monitor_gap'])

        self.widgets['snap_border_overlap'] = SwitchRow(
            "Border Overlap", "Snap with only one border width between windows",
            self.settings.settings['snap_border_overlap'],
            lambda v: self.on_value_changed('snap_border_overlap', v)
        )
        snap_group.add(self.widgets['snap_border_overlap'])

        self.widgets['snap_respect_gaps'] = SwitchRow(
            "Respect Gaps", "Respect gap settings when snapping",
            self.settings.settings['snap_respect_gaps'],
            lambda v: self.on_value_changed('snap_respect_gaps', v)
        )
        snap_group.add(self.widgets['snap_respect_gaps'])

        content.append(snap_group)

        # =========================================
        # GAP PRESETS
        # =========================================
        presets_group = Adw.PreferencesGroup(
            title="Gap Presets",
            description="Quick gap configurations"
        )

        for preset_name, preset_values in {
            'No Gaps': {'gaps_in': 0, 'gaps_out': 0, 'gaps_workspaces': 0},
            'Tight': {'gaps_in': 2, 'gaps_out': 3, 'gaps_workspaces': 3},
            'Nordix Default': {'gaps_in': 3, 'gaps_out': 5, 'gaps_workspaces': 5},
            'Comfortable': {'gaps_in': 5, 'gaps_out': 8, 'gaps_workspaces': 8},
            'Spacious': {'gaps_in': 8, 'gaps_out': 12, 'gaps_workspaces': 12},
            'Ultra Wide': {'gaps_in': 12, 'gaps_out': 20, 'gaps_workspaces': 15},
        }.items():
            row = Adw.ActionRow(title=preset_name)
            btn = Gtk.Button(label="Apply", valign=Gtk.Align.CENTER)
            btn.connect("clicked", lambda _, pv=preset_values: self.apply_gap_preset(pv))
            row.add_suffix(btn)
            presets_group.add(row)

        content.append(presets_group)

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
        """Update a setting"""
        self.settings.settings[key] = value
        self.status_bar.set_text(f"Changed: {key} = {value}")

    def on_resize_border_changed(self, value):
        """Handle resize_on_border toggle with dependent settings"""
        self.settings.settings['resize_on_border'] = value
        # Update sensitivity of dependent widgets
        self.widgets['extend_border_grab_area'].set_sensitive(value)
        self.widgets['hover_icon_on_border'].set_sensitive(value)
        self.status_bar.set_text(f"Changed: resize_on_border = {value}")

    def apply_gap_preset(self, preset_values):
        """Apply a gap preset"""
        for key, value in preset_values.items():
            self.settings.settings[key] = value
        self.refresh_ui()
        self.status_bar.set_text("Gap preset applied — click Apply to save")

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

        # Update dependent sensitivity
        resize_active = s['resize_on_border']
        self.widgets['extend_border_grab_area'].set_sensitive(resize_active)
        self.widgets['hover_icon_on_border'].set_sensitive(resize_active)


# =============================================
# APPLICATION
# =============================================
class NordixGeneralApp(Adw.Application):
    """Main application"""

    def __init__(self):
        super().__init__(
            application_id='com.Nordix.Settings.General',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

    def do_activate(self):
        win = NordixGeneralWindow(self)
        win.present()


def main():
    app = NordixGeneralApp()
    return app.run(None)


if __name__ == "__main__":
    main()
