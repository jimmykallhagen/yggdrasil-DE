#!/usr/bin/env python3
##=========================================================##
 # SPDX-License-Identifier: GPL-3.0-or-later               #
 # Copyright (c) 2025 Jimmy Källhagen                      #
 # Part of Yggdrasil - Nordix desktop environment          #
##=========================================================##

"""Yggdrasil Advanced Settings GUI
A graphical settings panel for Hyprland misc, opengl, and render configuration
Handles: misc behaviors, animations, DPMS, fullscreen, session lock, rendering
Note: disable_autoreload is always false and NOT exposed in GUI"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib
import subprocess
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
    '$nordix-pblack': {'name': 'Pure Black', 'rgba': 'rgba(000000ff)'},
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
# DEFAULT SETTINGS
# =============================================
DEFAULT_SETTINGS = {
    # Appearance
    'disable_hyprland_logo': False,
    'disable_splash_rendering': False,
    'disable_scale_notification': False,
    'font_family': 'Comfortaa',
    'splash_font_family': 'Comfortaa',
    'col_splash': '$nordix-mustard',
    'background_color': '$nordix-pblack',
    # DPMS
    'mouse_move_enables_dpms': False,
    'key_press_enables_dpms': False,
    # Animation
    'animate_manual_resizes': True,
    'animate_mouse_windowdragging': True,
    # Mouse & Focus
    'always_follow_on_dnd': True,
    'layers_hog_keyboard_focus': True,
    'mouse_move_focuses_monitor': True,
    'middle_click_paste': True,
    'name_vk_after_proc': True,
    # Fullscreen
    'exit_window_retains_fullscreen': False,
    'on_focus_under_fullscreen': 2,
    # Workspace
    'close_special_on_empty': True,
    'initial_workspace_tracking': 1,
    # Session Lock
    'allow_session_lock_restore': True,
    'session_lock_xray': False,
    'lockdead_screen_delay': 1000,
    # Performance
    'render_unfocused_fps': 15,
    'anr_missed_pings': 10,
    'enable_anr_dialog': True,
    # Advanced
    'size_limits_tiled': False,
    'disable_xdg_env_checks': False,
    'disable_watchdog_warning': False,
    # OpenGL
    'nvidia_anti_flicker': True,
    # Render
    'direct_scanout': False,
}


# =============================================
# FILE PATH
# =============================================
CONFIG_PATH = Path.home() / ".config" / "nordix" / "yggdrasil" / "settings" / "Yggdrasil-advanced.conf"

# =============================================
# SETTINGS HANDLER
# =============================================
class AdvancedSettings:
    """Handles reading and writing of nordix-advanced.conf"""

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

            current_section = None
            brace_depth = 0

            for line in content.split('\n'):
                stripped = line.strip()

                if stripped.startswith('# ') or not stripped:
                    continue

                # Track sections
                if re.match(r'^misc\s*\{', stripped):
                    current_section = 'misc'
                    brace_depth = 1
                    continue
                elif re.match(r'^opengl\s*\{', stripped):
                    current_section = 'opengl'
                    brace_depth = 1
                    continue
                elif re.match(r'^render\s*\{', stripped):
                    current_section = 'render'
                    brace_depth = 1
                    continue

                if '{' in stripped:
                    brace_depth += stripped.count('{')
                if '}' in stripped:
                    brace_depth -= stripped.count('}')
                    if brace_depth <= 0:
                        current_section = None
                        brace_depth = 0
                    continue

                if not current_section:
                    continue

                if '=' in stripped:
                    parts = stripped.split('=', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()

                        if '# ' in value:
                            value = value.split('# ')[0].strip()

                        # Map config key to settings key
                        settings_key = self._map_key(key, current_section)

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

        except Exception as e:
            print(f"Error loading config: {e}")

    def _map_key(self, key, section):
        """Map config file key to internal settings key"""
        if section == 'misc':
            if key == 'col.splash':
                return 'col_splash'
            return key
        elif section == 'opengl':
            return key
        elif section == 'render':
            return key
        return None

    def generate_config(self):
        """Generate config file content"""
        s = self.settings

        def b(val):
            return 'true' if val else 'false'

        config = f'''
##=============================================##
 #       Yggdrasil's -  Advanced Settings      #
 #           Hyprland - Configuration          #
##=============================================##
 # * Generated by Yggdrasil Advanced Settings GUI #
##=============================================###
source = ~/.config/nordix/yggdrasil/color/colors.conf

misc {{


##=================##
 #   APPEARANCE    #
##=================##

# Disable the Hyprland logo / anime girl background (bool)
disable_hyprland_logo = {b(s['disable_hyprland_logo'])}

# Disable the Hyprland splash rendering (bool)
disable_splash_rendering = {b(s['disable_splash_rendering'])}

# Disable notification when monitor fails to set scale (bool)
disable_scale_notification = {b(s['disable_scale_notification'])}

# System font family
font_family = {s['font_family']}

# Splash screen font family
splash_font_family = {s['splash_font_family']}

# Splash text color
col.splash = {s['col_splash']}

# Background color (visible when logo is disabled)
background_color = {s['background_color']}


##=================##
 #      DPMS       #
##=================##

# Wake monitors on mouse move when DPMS is off (bool)
mouse_move_enables_dpms = {b(s['mouse_move_enables_dpms'])}

# Wake monitors on key press when DPMS is off (bool)
key_press_enables_dpms = {b(s['key_press_enables_dpms'])}


##=================##
 #    ANIMATION    #
##=================##

# Animate manual window resizes/moves (bool)
animate_manual_resizes = {b(s['animate_manual_resizes'])}

# Animate windows dragged by mouse (bool)
animate_mouse_windowdragging = {b(s['animate_mouse_windowdragging'])}


##=====================##
 #    MOUSE & FOCUS    #
##=====================##

# Follow window on drag-and-drop (bool)
always_follow_on_dnd = {b(s['always_follow_on_dnd'])}

# Keyboard-interactive layers keep focus on mouse move (bool)
layers_hog_keyboard_focus = {b(s['layers_hog_keyboard_focus'])}

# Mouse moving to different monitor focuses it (bool)
mouse_move_focuses_monitor = {b(s['mouse_move_focuses_monitor'])}

# Enable middle-click paste / primary selection (bool)
middle_click_paste = {b(s['middle_click_paste'])}

# Name virtual keyboards after their process (bool)
name_vk_after_proc = {b(s['name_vk_after_proc'])}


##=====================##
 #     FULLSCREEN      #
##=====================##

# Closing fullscreen window makes next window fullscreen (bool)
exit_window_retains_fullscreen = {b(s['exit_window_retains_fullscreen'])}

# Focus request under fullscreen: 0 = ignore, 1 = take over, 2 = unfullscreen (int)
on_focus_under_fullscreen = {s['on_focus_under_fullscreen']}


##=====================##
 #      WORKSPACE      #
##=====================##

# Close special workspace when last window is removed (bool)
close_special_on_empty = {b(s['close_special_on_empty'])}

# Window workspace tracking: 0 = disabled, 1 = single-shot, 2 = persistent (int)
initial_workspace_tracking = {s['initial_workspace_tracking']}


##=====================##
 #    SESSION LOCK     #
##=====================##

# Allow restarting lockscreen app if it crashes (bool)
allow_session_lock_restore = {b(s['allow_session_lock_restore'])}

# Keep rendering workspaces below lockscreen (bool)
session_lock_xray = {b(s['session_lock_xray'])}

# Delay before lockdead screen appears in ms, max 5000 (int)
lockdead_screen_delay = {s['lockdead_screen_delay']}


##=====================##
 #     PERFORMANCE     #
##=====================##

# Max FPS for unfocused windows in background (int)
render_unfocused_fps = {s['render_unfocused_fps']}

# Missed pings before ANR dialog (int)
anr_missed_pings = {s['anr_missed_pings']}

# Enable app not responding dialog (bool)
enable_anr_dialog = {b(s['enable_anr_dialog'])}


##====================##
 #      ADVANCED      #
##====================##

# Apply min/max size rules to tiled windows (bool)
size_limits_tiled = {b(s['size_limits_tiled'])}

# Disable XDG environment managed warning (bool)
disable_xdg_env_checks = {b(s['disable_xdg_env_checks'])}

# Disable watchdog warning about not using start-hyprland (bool)
disable_watchdog_warning = {b(s['disable_watchdog_warning'])}


 ##=============================================##
  #     SYSTEM REQUIERMENT - DO NOT MODIFY      #
  #  * disable_autoreload must always be false  #
  #  * This enables live config reload for GUI  #
 ##=============================================##
 disable_autoreload = false
 ##=============================================##

}}


opengl {{

# Reduce flickering on Nvidia (may drop frames on low-end GPUs, ignored on non-Nvidia) (bool)
nvidia_anti_flicker = {b(s['nvidia_anti_flicker'])}

}}


render {{

# Direct scanout - must be false for shaders on games and fullscreen (bool)
direct_scanout = {b(s['direct_scanout'])}

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
class NordixAdvancedWindow(Adw.ApplicationWindow):
    """Main window for advanced settings"""

    def __init__(self, app):
        super().__init__(application=app, title="Yggdrasil Advanced Settings")
        self.set_default_size(600, 800)

        self.settings = AdvancedSettings()
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
        # APPEARANCE SECTION
        # =========================================
        appearance_group = Adw.PreferencesGroup(
            title="Appearance",
            description="Splash screen and background settings"
        )

        self.widgets['disable_hyprland_logo'] = SwitchRow(
            "Disable Hyprland Logo",
            "Hide the Hyprland logo / anime girl background",
            self.settings.settings['disable_hyprland_logo'],
            lambda v: self.on_value_changed('disable_hyprland_logo', v)
        )
        appearance_group.add(self.widgets['disable_hyprland_logo'])

        self.widgets['disable_splash_rendering'] = SwitchRow(
            "Disable Splash Rendering",
            "Hide the splash text on startup",
            self.settings.settings['disable_splash_rendering'],
            lambda v: self.on_value_changed('disable_splash_rendering', v)
        )
        appearance_group.add(self.widgets['disable_splash_rendering'])

        self.widgets['disable_scale_notification'] = SwitchRow(
            "Disable Scale Notification",
            "Hide notification when monitor fails to set scale",
            self.settings.settings['disable_scale_notification'],
            lambda v: self.on_value_changed('disable_scale_notification', v)
        )
        appearance_group.add(self.widgets['disable_scale_notification'])

        self.widgets['font_family'] = TextEntryRow(
            "Font Family", "System font used by Hyprland",
            self.settings.settings['font_family'],
            lambda v: self.on_value_changed('font_family', v)
        )
        appearance_group.add(self.widgets['font_family'])

        self.widgets['splash_font_family'] = TextEntryRow(
            "Splash Font Family", "Font used for splash screen text",
            self.settings.settings['splash_font_family'],
            lambda v: self.on_value_changed('splash_font_family', v)
        )
        appearance_group.add(self.widgets['splash_font_family'])

        self.widgets['col_splash'] = ColorRow(
            "Splash Color", "Color of the splash screen text",
            self.settings.settings['col_splash'],
            lambda v: self.on_value_changed('col_splash', v)
        )
        appearance_group.add(self.widgets['col_splash'])

        self.widgets['background_color'] = ColorRow(
            "Background Color", "Desktop background color",
            self.settings.settings['background_color'],
            lambda v: self.on_value_changed('background_color', v)
        )
        appearance_group.add(self.widgets['background_color'])

        content.append(appearance_group)

        # =========================================
        # DPMS SECTION
        # =========================================
        dpms_group = Adw.PreferencesGroup(
            title="DPMS (Display Power)",
            description="Wake monitors from sleep"
        )

        self.widgets['mouse_move_enables_dpms'] = SwitchRow(
            "Mouse Wakes Monitor",
            "Wake monitors from DPMS sleep on mouse movement",
            self.settings.settings['mouse_move_enables_dpms'],
            lambda v: self.on_value_changed('mouse_move_enables_dpms', v)
        )
        dpms_group.add(self.widgets['mouse_move_enables_dpms'])

        self.widgets['key_press_enables_dpms'] = SwitchRow(
            "Key Press Wakes Monitor",
            "Wake monitors from DPMS sleep on key press",
            self.settings.settings['key_press_enables_dpms'],
            lambda v: self.on_value_changed('key_press_enables_dpms', v)
        )
        dpms_group.add(self.widgets['key_press_enables_dpms'])

        content.append(dpms_group)

        # =========================================
        # ANIMATION SECTION
        # =========================================
        anim_group = Adw.PreferencesGroup(
            title="Animation",
            description="Window animation behavior"
        )

        self.widgets['animate_manual_resizes'] = SwitchRow(
            "Animate Manual Resizes",
            "Animate windows when manually resizing or moving",
            self.settings.settings['animate_manual_resizes'],
            lambda v: self.on_value_changed('animate_manual_resizes', v)
        )
        anim_group.add(self.widgets['animate_manual_resizes'])

        self.widgets['animate_mouse_windowdragging'] = SwitchRow(
            "Animate Mouse Dragging",
            "Animate windows being dragged by mouse (may cause issues with some curves)",
            self.settings.settings['animate_mouse_windowdragging'],
            lambda v: self.on_value_changed('animate_mouse_windowdragging', v)
        )
        anim_group.add(self.widgets['animate_mouse_windowdragging'])

        content.append(anim_group)

        # =========================================
        # MOUSE & FOCUS SECTION
        # =========================================
        mouse_group = Adw.PreferencesGroup(
            title="Mouse and Focus",
            description="Mouse and keyboard interaction behavior"
        )

        self.widgets['always_follow_on_dnd'] = SwitchRow(
            "Follow on Drag and Drop",
            "Follow window during drag-and-drop operations",
            self.settings.settings['always_follow_on_dnd'],
            lambda v: self.on_value_changed('always_follow_on_dnd', v)
        )
        mouse_group.add(self.widgets['always_follow_on_dnd'])

        self.widgets['layers_hog_keyboard_focus'] = SwitchRow(
            "Layers Hog Keyboard",
            "Keyboard-interactive layers keep focus on mouse move",
            self.settings.settings['layers_hog_keyboard_focus'],
            lambda v: self.on_value_changed('layers_hog_keyboard_focus', v)
        )
        mouse_group.add(self.widgets['layers_hog_keyboard_focus'])

        self.widgets['mouse_move_focuses_monitor'] = SwitchRow(
            "Mouse Focuses Monitor",
            "Moving mouse to different monitor automatically focuses it",
            self.settings.settings['mouse_move_focuses_monitor'],
            lambda v: self.on_value_changed('mouse_move_focuses_monitor', v)
        )
        mouse_group.add(self.widgets['mouse_move_focuses_monitor'])

        self.widgets['middle_click_paste'] = SwitchRow(
            "Middle Click Paste",
            "Enable middle-click paste (primary selection)",
            self.settings.settings['middle_click_paste'],
            lambda v: self.on_value_changed('middle_click_paste', v)
        )
        mouse_group.add(self.widgets['middle_click_paste'])

        self.widgets['name_vk_after_proc'] = SwitchRow(
            "Name Virtual Keyboards",
            "Name virtual keyboards after their process (e.g. fcitx5)",
            self.settings.settings['name_vk_after_proc'],
            lambda v: self.on_value_changed('name_vk_after_proc', v)
        )
        mouse_group.add(self.widgets['name_vk_after_proc'])

        content.append(mouse_group)

        # =========================================
        # FULLSCREEN SECTION
        # =========================================
        fullscreen_group = Adw.PreferencesGroup(
            title="Fullscreen",
            description="Fullscreen window behavior"
        )

        self.widgets['exit_window_retains_fullscreen'] = SwitchRow(
            "Retain Fullscreen on Close",
            "Next window becomes fullscreen when closing a fullscreen window",
            self.settings.settings['exit_window_retains_fullscreen'],
            lambda v: self.on_value_changed('exit_window_retains_fullscreen', v)
        )
        fullscreen_group.add(self.widgets['exit_window_retains_fullscreen'])

        self.widgets['on_focus_under_fullscreen'] = DropdownRow(
            "Focus Under Fullscreen",
            "What happens when a window requests focus under fullscreen",
            [
                {'value': 0, 'name': 'Ignore (keep fullscreen)'},
                {'value': 1, 'name': 'Take over (replace fullscreen)'},
                {'value': 2, 'name': 'Unfullscreen / Unmaximize'},
            ],
            self.settings.settings['on_focus_under_fullscreen'],
            lambda v: self.on_value_changed('on_focus_under_fullscreen', v)
        )
        fullscreen_group.add(self.widgets['on_focus_under_fullscreen'])

        content.append(fullscreen_group)

        # =========================================
        # WORKSPACE SECTION
        # =========================================
        workspace_group = Adw.PreferencesGroup(
            title="Workspace",
            description="Workspace behavior settings"
        )

        self.widgets['close_special_on_empty'] = SwitchRow(
            "Close Special on Empty",
            "Close special workspace when last window is removed",
            self.settings.settings['close_special_on_empty'],
            lambda v: self.on_value_changed('close_special_on_empty', v)
        )
        workspace_group.add(self.widgets['close_special_on_empty'])

        self.widgets['initial_workspace_tracking'] = DropdownRow(
            "Workspace Tracking",
            "How windows track which workspace they were launched on",
            [
                {'value': 0, 'name': 'Disabled'},
                {'value': 1, 'name': 'Single-shot'},
                {'value': 2, 'name': 'Persistent (all children)'},
            ],
            self.settings.settings['initial_workspace_tracking'],
            lambda v: self.on_value_changed('initial_workspace_tracking', v)
        )
        workspace_group.add(self.widgets['initial_workspace_tracking'])

        content.append(workspace_group)

        # =========================================
        # SESSION LOCK SECTION
        # =========================================
        lock_group = Adw.PreferencesGroup(
            title="Session Lock",
            description="Lock screen behavior"
        )

        self.widgets['allow_session_lock_restore'] = SwitchRow(
            "Allow Lock Restore",
            "Allow restarting lockscreen app if it crashes",
            self.settings.settings['allow_session_lock_restore'],
            lambda v: self.on_value_changed('allow_session_lock_restore', v)
        )
        lock_group.add(self.widgets['allow_session_lock_restore'])

        self.widgets['session_lock_xray'] = SwitchRow(
            "Lock Screen X-Ray",
            "Keep rendering workspaces visible below lockscreen",
            self.settings.settings['session_lock_xray'],
            lambda v: self.on_value_changed('session_lock_xray', v)
        )
        lock_group.add(self.widgets['session_lock_xray'])

        self.widgets['lockdead_screen_delay'] = SliderRow(
            "Lockdead Delay",
            "Milliseconds before lockdead screen appears if lock fails [500 - 5000]",
            500, 5000, 100, self.settings.settings['lockdead_screen_delay'],
            lambda v: self.on_value_changed('lockdead_screen_delay', int(v))
        )
        lock_group.add(self.widgets['lockdead_screen_delay'])

        content.append(lock_group)

        # =========================================
        # PERFORMANCE SECTION
        # =========================================
        perf_group = Adw.PreferencesGroup(
            title="Performance",
            description="Rendering and responsiveness settings"
        )

        self.widgets['render_unfocused_fps'] = SliderRow(
            "Unfocused Window FPS",
            "Max FPS for background windows [1 - 60]",
            1, 60, 1, self.settings.settings['render_unfocused_fps'],
            lambda v: self.on_value_changed('render_unfocused_fps', int(v))
        )
        perf_group.add(self.widgets['render_unfocused_fps'])

        self.widgets['anr_missed_pings'] = SliderRow(
            "ANR Missed Pings",
            "Missed pings before showing App Not Responding dialog [1 - 30]",
            1, 30, 1, self.settings.settings['anr_missed_pings'],
            lambda v: self.on_value_changed('anr_missed_pings', int(v))
        )
        perf_group.add(self.widgets['anr_missed_pings'])

        self.widgets['enable_anr_dialog'] = SwitchRow(
            "Enable ANR Dialog",
            "Show dialog when apps stop responding",
            self.settings.settings['enable_anr_dialog'],
            lambda v: self.on_value_changed('enable_anr_dialog', v)
        )
        perf_group.add(self.widgets['enable_anr_dialog'])

        content.append(perf_group)

        # =========================================
        # RENDERING SECTION (OpenGL + Render)
        # =========================================
        render_group = Adw.PreferencesGroup(
            title="Rendering",
            description="GPU rendering options"
        )

        self.widgets['nvidia_anti_flicker'] = SwitchRow(
            "Nvidia Anti-Flicker",
            "Reduce flickering on Nvidia (may drop frames on low-end GPUs, ignored on non-Nvidia)",
            self.settings.settings['nvidia_anti_flicker'],
            lambda v: self.on_value_changed('nvidia_anti_flicker', v)
        )
        render_group.add(self.widgets['nvidia_anti_flicker'])

        self.widgets['direct_scanout'] = SwitchRow(
            "Direct Scanout",
            "Direct scanout optimization (must be off for shaders on fullscreen/games)",
            self.settings.settings['direct_scanout'],
            lambda v: self.on_value_changed('direct_scanout', v)
        )
        render_group.add(self.widgets['direct_scanout'])

        content.append(render_group)

        # =========================================
        # ADVANCED / SYSTEM SECTION
        # =========================================
        advanced_group = Adw.PreferencesGroup(
            title="System",
            description="Advanced system behavior (change with caution)"
        )

        self.widgets['size_limits_tiled'] = SwitchRow(
            "Size Limits on Tiled",
            "Apply min/max size rules to tiled windows",
            self.settings.settings['size_limits_tiled'],
            lambda v: self.on_value_changed('size_limits_tiled', v)
        )
        advanced_group.add(self.widgets['size_limits_tiled'])

        self.widgets['disable_xdg_env_checks'] = SwitchRow(
            "Disable XDG Env Checks",
            "Disable warning if XDG environment is externally managed",
            self.settings.settings['disable_xdg_env_checks'],
            lambda v: self.on_value_changed('disable_xdg_env_checks', v)
        )
        advanced_group.add(self.widgets['disable_xdg_env_checks'])

        self.widgets['disable_watchdog_warning'] = SwitchRow(
            "Disable Watchdog Warning",
            "Disable warning about not using start-hyprland",
            self.settings.settings['disable_watchdog_warning'],
            lambda v: self.on_value_changed('disable_watchdog_warning', v)
        )
        advanced_group.add(self.widgets['disable_watchdog_warning'])

        content.append(advanced_group)

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
class NordixAdvancedApp(Adw.Application):
    """Main application"""

    def __init__(self):
        super().__init__(
            application_id='com.Nordix.Settings.Advance',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

    def do_activate(self):
        win = NordixAdvancedWindow(self)
        win.present()


def main():
    app = NordixAdvancedApp()
    return app.run(None)


if __name__ == "__main__":
    main()
