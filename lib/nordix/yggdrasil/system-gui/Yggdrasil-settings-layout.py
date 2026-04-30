#!/usr/bin/env python3
##=========================================================##
 # SPDX-License-Identifier: GPL-3.0-or-later               #
 # Copyright (c) 2025 Jimmy Källhagen                      #
 # Part of Yggdrasil - Nordix desktop environment          #
##=========================================================##

"""Yggdrasil Layout Settings GUI
A graphical settings panel for Hyprland layout configuration
Handles: Tiling ON/OFF toggle, General layout, Master, Dwindle,
Scrolling layout and Workspace direction settings.

OFF = Traditional desktop mode (dwindle base, floating, dock, decorations)
ON  = Tiling window manager with selectable layout"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib
import subprocess
import re
import shutil
from pathlib import Path

DEFAULT_SETTINGS = {
    # Tiling mode toggle (True = tiling ON, False = traditional desktop)
    'tiling_enabled': True,
    # General
    'g_layout': 'master',
    # Layout (aspect ratio)
    'l_single_window_aspect_ratio': '0 0',
    'l_single_window_aspect_ratio_tolerance': 0.1,
    # Master
    'm_allow_small_split': False, 'm_special_scale_factor': 0.9, 'm_mfact': 0.6,
    'm_new_status': 'master', 'm_new_on_top': False, 'm_new_on_active': 'none',
    'm_orientation': 'left', 'm_slave_count_for_center_master': 0,
    'm_center_master_fallback': 'left', 'm_smart_resizing': True,
    'm_drop_at_cursor': True, 'm_always_keep_position': False,
    # Dwindle
    'd_special_scale_factor': 0.8, 'd_pseudotile': True, 'd_force_split': 0,
    'd_smart_split': True, 'd_preserve_split': True, 'd_smart_resizing': True,
    'd_permanent_direction_override': False, 'd_split_width_multiplier': 1.0,
    'd_use_active_for_splits': True, 'd_default_split_ratio': 1.2,
    'd_split_bias': 1, 'd_precise_mouse_move': True,
    # Scrolling
    's_fullscreen_on_one_column': True, 's_column_width': 0.5,
    's_focus_fit_method': 0, 's_follow_focus': True,
    's_follow_min_visible': 0.4, 's_explicit_column_widths': '0.333, 0.5, 0.667, 1.0',
    's_direction': 'right',
    # Workspace directions (per workspace scroll direction)
    'ws_1_direction': 'right',
    'ws_2_direction': 'left', 'ws_3_direction': 'left', 'ws_4_direction': 'left',
    'ws_5_direction': 'left', 'ws_6_direction': 'left', 'ws_7_direction': 'left',
    'ws_8_direction': 'left', 'ws_9_direction': 'left',
}

CONFIG_PATH = Path.home() / ".config" / "nordix" / "yggdrasil" / "settings" / "Yggdrasil-layout.conf"
TILING_STATE_PATH = Path.home() / ".config" / "nordix" / "yggdrasil" / "settings" / "nordix-tiling-mode.conf"
SCRIPTS_PATH = Path("/usr") / "lib" / "nordix" / "yggdrasil" / "floating-mode"
TILING_ON_SCRIPT = SCRIPTS_PATH / "nordix-tiling-on.sh"
TILING_OFF_SCRIPT = SCRIPTS_PATH / "nordix-tiling-off.sh"


class LayoutSettings:
    def __init__(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.load_tiling_state()
        self.load_config()

    def load_tiling_state(self):
        """Load tiling enabled/disabled state from separate config file."""
        if not TILING_STATE_PATH.exists():
            return
        try:
            for line in TILING_STATE_PATH.read_text().split('\n'):
                stripped = line.strip()
                if stripped.startswith('#') or not stripped:
                    continue
                if '=' in stripped:
                    key, value = stripped.split('=', 1)
                    if key.strip() == 'tiling_enabled':
                        self.settings['tiling_enabled'] = value.strip().lower() == 'true'
        except Exception as e:
            print(f"Error loading tiling state: {e}")

    def save_tiling_state(self):
        """Save tiling enabled/disabled state to separate config file."""
        try:
            TILING_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
            state = 'true' if self.settings['tiling_enabled'] else 'false'
            TILING_STATE_PATH.write_text(
                f"# Nordix tiling mode state\n"
                f"# true = tiling layouts, false = traditional desktop\n"
                f"tiling_enabled = {state}\n"
            )
            return True
        except Exception as e:
            print(f"Error saving tiling state: {e}")
            return False

    def load_config(self):
        if not CONFIG_PATH.exists():
            return
        try:
            content = CONFIG_PATH.read_text()
            current_section = None
            brace_depth = 0
            for line in content.split('\n'):
                stripped = line.strip()
                if stripped.startswith('# ') or not stripped:
                    continue
                # Detect section starts
                if re.match(r'^general\s*\{', stripped):
                    current_section = 'general'; brace_depth = 1; continue
                elif re.match(r'^layout\s*\{', stripped):
                    current_section = 'layout'; brace_depth = 1; continue
                elif re.match(r'^master\s*\{', stripped):
                    current_section = 'master'; brace_depth = 1; continue
                elif re.match(r'^dwindle\s*\{', stripped):
                    current_section = 'dwindle'; brace_depth = 1; continue
                elif re.match(r'^scrolling\s*\{', stripped):
                    current_section = 'scrolling'; brace_depth = 1; continue
                if '{' in stripped: brace_depth += stripped.count('{')
                if '}' in stripped:
                    brace_depth -= stripped.count('}')
                    if brace_depth <= 0: current_section = None; brace_depth = 0
                    continue
                # Workspace direction lines (outside sections)
                if not current_section:
                    ws_match = re.match(r'^workspace\s*=\s*(\d+)\s*,\s*layoutopt:direction:(\w+)', stripped)
                    if ws_match:
                        ws_num = ws_match.group(1)
                        ws_dir = ws_match.group(2)
                        key = f'ws_{ws_num}_direction'
                        if key in self.settings:
                            self.settings[key] = ws_dir
                    continue
                if not current_section: continue
                if '=' in stripped:
                    parts = stripped.split('=', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        if '# ' in value: value = value.split('#')[0].strip()
                        # Map section to prefix
                        prefix_map = {'general': 'g_', 'layout': 'l_', 'master': 'm_', 'dwindle': 'd_', 'scrolling': 's_'}
                        prefix = prefix_map.get(current_section, '')
                        if not prefix: continue
                        settings_key = prefix + key
                        if settings_key in self.settings:
                            current_type = type(self.settings[settings_key])
                            try:
                                if current_type == bool: self.settings[settings_key] = value.lower() == 'true'
                                elif current_type == int: self.settings[settings_key] = int(value)
                                elif current_type == float: self.settings[settings_key] = float(value)
                                else: self.settings[settings_key] = value
                            except ValueError: pass
        except Exception as e:
            print(f"Error loading config: {e}")

    def generate_config(self):
        s = self.settings
        def b(val): return 'true' if val else 'false'

        # When tiling is OFF, force master as the layout (base for traditional desktop)
        active_layout = s['g_layout'] if s['tiling_enabled'] else 'master'

        # Build master section only if master is selected
        master_section = ''
        if active_layout == 'master':
            master_section = f'''

 ##====================##
  #    MASTER LAYOUT   #
 ##====================##

master {{

# Enable additional master windows in horizontal split (bool)
allow_small_split = {b(s['m_allow_small_split'])}

# Scale of special workspace windows [0.0 - 1.0] (float)
special_scale_factor = {s['m_special_scale_factor']:.2f}

# Master window size as percentage of screen [0.0 - 1.0] (float)
mfact = {s['m_mfact']:.2f}

# New window status: master, slave, or inherit (string)
new_status = {s['m_new_status']}

# New window opens on top of stack (bool)
new_on_top = {b(s['m_new_on_top'])}

# Place new window relative to focused: before, after, or none (string)
new_on_active = {s['m_new_on_active']}

# Master area placement: left, right, top, bottom, or center (string)
orientation = {s['m_orientation']}

# Minimum slaves for center orientation, 0 = always center (int)
slave_count_for_center_master = {s['m_slave_count_for_center_master']}

# Fallback for center master: left, right, top, bottom (string)
center_master_fallback = {s['m_center_master_fallback']}

# Resize direction determined by mouse position on window (bool)
smart_resizing = {b(s['m_smart_resizing'])}

# Drag-and-drop puts windows at cursor position (bool)
drop_at_cursor = {b(s['m_drop_at_cursor'])}

# Keep master window in configured position when no slaves (bool)
always_keep_position = {b(s['m_always_keep_position'])}

}}

# Hyprland bug workaround: special_scale_factor only works under dwindle {{}}
dwindle {{
special_scale_factor = {s['m_special_scale_factor']:.2f}
}}'''

        # Build dwindle section only if dwindle is selected
        dwindle_section = ''
        if active_layout == 'dwindle':
            dwindle_section = f'''

##====================##
 #   DWINDLE LAYOUT   #
##====================##

dwindle {{

# Scale of special workspace windows [0.0 - 1.0] (float)
special_scale_factor = {s['d_special_scale_factor']:.2f}

# Enable pseudotiling - pseudotiled windows retain floating size when tiled (bool)
pseudotile = {b(s['d_pseudotile'])}

# Split direction: 0 = follow mouse, 1 = always left/top, 2 = always right/bottom (int)
force_split = {s['d_force_split']}

# Precise split direction based on cursor position in window quadrants (bool)
smart_split = {b(s['d_smart_split'])}

# Keep split side/top regardless of container changes (bool)
preserve_split = {b(s['d_preserve_split'])}

# Resize direction determined by mouse position on window (bool)
smart_resizing = {b(s['d_smart_resizing'])}

# Preselect direction persists until changed (bool)
permanent_direction_override = {b(s['d_permanent_direction_override'])}

# Auto-split width multiplier, useful for widescreen monitors (float)
split_width_multiplier = {s['d_split_width_multiplier']:.1f}

# Prefer active window or mouse position for splits (bool)
use_active_for_splits = {b(s['d_use_active_for_splits'])}

# Default split ratio on window open, 1.0 = even 50/50 [0.1 - 1.9] (float)
default_split_ratio = {s['d_default_split_ratio']:.1f}

# Split ratio target: 0 = directional (top/left), 1 = current window (int)
split_bias = {s['d_split_bias']}

# More precise window drop position on bindm movewindow (bool)
precise_mouse_move = {b(s['d_precise_mouse_move'])}

}}'''

        return f'''
##=============================================##
 #       Yggdrasil's -  Layout Settings        #
 #          Hyprland - Configuration           #
##=============================================##
 # * Generated by Yggdrasil Layout Settings GUI   #
##=============================================##
# * Tiling mode: {'ON' if s['tiling_enabled'] else 'OFF (Traditional Desktop)'}


 ##====================##
  #      GENERAL       #
 ##====================##

general {{

# layout: which layout to use. [dwindle/master/scrolling/monocle]
layout = {active_layout}

}}


 ##====================##
  #       LAYOUT       #
 ##====================##

layout {{

# single_window_aspect_ratio: add padding so single window conforms to aspect ratio
# A value like 4 3 on a 16:9 screen will make it a 4:3 window in the middle
single_window_aspect_ratio = {s['l_single_window_aspect_ratio']}

# single_window_aspect_ratio_tolerance: tolerance before padding is applied [0 - 1]
single_window_aspect_ratio_tolerance = {s['l_single_window_aspect_ratio_tolerance']:.1f}

}}
{master_section}
{dwindle_section}

##====================##
 # SCROLLING LAYOUT   #
##====================##

scrolling {{

# When enabled, a single column on a workspace will always span the entire screen (bool)
fullscreen_on_one_column = {b(s['s_fullscreen_on_one_column'])}

# The default width of a column [0.1 - 1.0] (float)
column_width = {s['s_column_width']:.1f}

# When a column is focused, method to bring it into view. 0 = center, 1 = fit (int)
focus_fit_method = {s['s_focus_fit_method']}

# When a window is focused, move layout to bring it into view automatically (bool)
follow_focus = {b(s['s_follow_focus'])}

# Require at least this fraction visible for focus to follow [0.0 - 1.0] (float)
follow_min_visible = {s['s_follow_min_visible']:.1f}

# Comma-separated list of preconfigured widths for colresize +conf/-conf (string)
explicit_column_widths = {s['s_explicit_column_widths']}

# Direction in which new windows appear and layout scrolls: left/right/down/up (string)
direction = {s['s_direction']}

}}


##============================##
 # WORKSPACE SCROLL DIRECTION #
##============================##

# Per-workspace scroll direction overrides
# Monitor left
workspace = 1, layoutopt:direction:{s['ws_1_direction']}

# Monitor right
workspace = 2, layoutopt:direction:{s['ws_2_direction']}
workspace = 3, layoutopt:direction:{s['ws_3_direction']}
workspace = 4, layoutopt:direction:{s['ws_4_direction']}
workspace = 5, layoutopt:direction:{s['ws_5_direction']}
workspace = 6, layoutopt:direction:{s['ws_6_direction']}
workspace = 7, layoutopt:direction:{s['ws_7_direction']}
workspace = 8, layoutopt:direction:{s['ws_8_direction']}
workspace = 9, layoutopt:direction:{s['ws_9_direction']}
'''

    def save_config(self):
        try:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            if CONFIG_PATH.exists():
                shutil.copy2(CONFIG_PATH, CONFIG_PATH.with_suffix('.conf.backup'))
            CONFIG_PATH.write_text(self.generate_config())
            self.save_tiling_state()
            return True
        except Exception as e:
            print(f"Error saving config: {e}"); return False

    def run_tiling_script(self, enable):
        """Run the appropriate on/off script for tiling mode switch."""
        script = TILING_ON_SCRIPT if enable else TILING_OFF_SCRIPT
        if script.exists():
            try:
                subprocess.Popen(['bash', str(script)])
                return True
            except Exception as e:
                print(f"Error running script {script}: {e}")
                return False
        else:
            print(f"Script not found: {script}")
            return False

    def reload_hyprland(self):
        try: subprocess.run(['hyprctl', 'reload'], check=True); return True
        except Exception: return False

    def reset_to_defaults(self):
        self.settings = DEFAULT_SETTINGS.copy()


class SliderRow(Adw.ActionRow):
    def __init__(self, title, subtitle, min_val, max_val, step, value, callback, digits=0):
        super().__init__(); self.set_title(title); self.set_subtitle(subtitle)
        self.callback = callback
        self.adjustment = Gtk.Adjustment(value=value, lower=min_val, upper=max_val,
            step_increment=step, page_increment=step * 10)
        self.scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL,
            adjustment=self.adjustment, draw_value=True, digits=digits, hexpand=True)
        self.scale.set_size_request(200, -1)
        self.scale.connect('value-changed', self._on_value_changed)
        self.add_suffix(self.scale)
    def _on_value_changed(self, scale): self.callback(scale.get_value())
    def set_value(self, value): self.adjustment.set_value(value)


class SwitchRow(Adw.ActionRow):
    def __init__(self, title, subtitle, active, callback):
        super().__init__(); self.set_title(title); self.set_subtitle(subtitle)
        self.set_activatable(True); self.callback = callback
        self.switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        self.switch.set_active(active)
        self.switch.connect('notify::active', self._on_toggled)
        self.add_suffix(self.switch); self.set_activatable_widget(self.switch)
    def _on_toggled(self, switch, _): self.callback(switch.get_active())
    def set_active(self, active): self.switch.set_active(active)


class DropdownRow(Adw.ActionRow):
    def __init__(self, title, subtitle, options, current_value, callback):
        super().__init__(); self.set_title(title); self.set_subtitle(subtitle)
        self.callback = callback
        self.option_values = [opt['value'] for opt in options]
        string_list = Gtk.StringList(); current_index = 0
        for i, opt in enumerate(options):
            string_list.append(opt['name'])
            if opt['value'] == current_value: current_index = i
        self.dropdown = Gtk.DropDown(model=string_list)
        self.dropdown.set_selected(current_index)
        self.dropdown.connect('notify::selected', self._on_selected)
        self.add_suffix(self.dropdown)
    def _on_selected(self, dropdown, _):
        selected = dropdown.get_selected()
        if selected < len(self.option_values): self.callback(self.option_values[selected])
    def set_value(self, value):
        if value in self.option_values:
            self.dropdown.set_selected(self.option_values.index(value))


class EntryRow(Adw.ActionRow):
    """A row with a text entry field for string values like aspect ratios or column widths."""
    def __init__(self, title, subtitle, value, callback):
        super().__init__(); self.set_title(title); self.set_subtitle(subtitle)
        self.callback = callback
        self.entry = Gtk.Entry(text=str(value), valign=Gtk.Align.CENTER, hexpand=True)
        self.entry.set_size_request(180, -1)
        self.entry.connect('changed', self._on_changed)
        self.add_suffix(self.entry)
    def _on_changed(self, entry): self.callback(entry.get_text())
    def set_text(self, text): self.entry.set_text(text)


class NordixLayoutWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Yggdrasil Layout Settings")
        self.set_default_size(550, 1000)
        self.settings = LayoutSettings(); self.widgets = {}
        self.tiling_sections = []  # Track sections to show/hide
        self.master_sections = []  # Master-specific sections
        self.dwindle_sections = []  # Dwindle-specific sections
        self.setup_ui()

    def setup_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        header = Adw.HeaderBar()
        apply_btn = Gtk.Button(label="Apply"); apply_btn.add_css_class("suggested-action")
        apply_btn.connect("clicked", self.on_apply); header.pack_end(apply_btn)
        reset_btn = Gtk.Button(label="Reset to Default")
        reset_btn.connect("clicked", self.on_reset); header.pack_start(reset_btn)
        main_box.append(header)

        scrolled = Gtk.ScrolledWindow(vexpand=True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        content.set_margin_top(12); content.set_margin_bottom(12)
        content.set_margin_start(12); content.set_margin_end(12)

        # =========================================
        # TILING MODE TOGGLE
        # =========================================
        mode_group = Adw.PreferencesGroup(
            title="Window Management Mode",
            description="Switch between a range of exotic window managers or choose traditional desktop window management")

        self.widgets['tiling_enabled'] = SwitchRow(
            "Window Manager",
            "ON = Tiling layouts (Master, Dwindle, Scrolling, Monocle) · OFF = Traditional desktop",
            self.settings.settings['tiling_enabled'],
            lambda v: self.on_tiling_toggled(v))
        mode_group.add(self.widgets['tiling_enabled'])

        content.append(mode_group)

        # =========================================
        # LAYOUT SELECTION (only visible when tiling ON)
        # =========================================
        general_group = Adw.PreferencesGroup(
            title="Tiling Layout", description="Select which tiling layout to use")

        self.widgets['g_layout'] = DropdownRow(
            "Layout", "Which tiling layout to use",
            [{'value': 'master', 'name': 'Master'},
             {'value': 'dwindle', 'name': 'Dwindle'},
             {'value': 'scrolling', 'name': 'Scrolling'},
             {'value': 'monocle', 'name': 'Monocle'}],
            self.settings.settings['g_layout'],
            lambda v: self.on_value_changed('g_layout', v))
        general_group.add(self.widgets['g_layout'])

        content.append(general_group)
        self.tiling_sections.append(general_group)

        # =========================================
        # LAYOUT (aspect ratio settings)
        # =========================================
        layout_group = Adw.PreferencesGroup(
            title="Layout", description="Single window aspect ratio padding settings")

        self.widgets['l_single_window_aspect_ratio'] = EntryRow(
            "Single Window Aspect Ratio",
            "Aspect ratio padding for single window (e.g. '16 9', '4 3', '3 2', or '0 0' to disable)",
            self.settings.settings['l_single_window_aspect_ratio'],
            lambda v: self.on_value_changed('l_single_window_aspect_ratio', v))
        layout_group.add(self.widgets['l_single_window_aspect_ratio'])

        self.widgets['l_single_window_aspect_ratio_tolerance'] = SliderRow(
            "Aspect Ratio Tolerance",
            "Tolerance before padding is applied, smaller = more strict [0.0 - 1.0]",
            0.0, 1.0, 0.05, self.settings.settings['l_single_window_aspect_ratio_tolerance'],
            lambda v: self.on_value_changed('l_single_window_aspect_ratio_tolerance', v), digits=2)
        layout_group.add(self.widgets['l_single_window_aspect_ratio_tolerance'])

        content.append(layout_group)
        self.tiling_sections.append(layout_group)

        # =========================================
        # MASTER LAYOUT - MAIN
        # =========================================
        master_group = Adw.PreferencesGroup(
            title="Master Layout", description="Settings for the master-stack tiling layout")

        self.widgets['m_orientation'] = DropdownRow(
            "Orientation", "Placement of the master area",
            [{'value': 'left', 'name': 'Left'}, {'value': 'right', 'name': 'Right'},
             {'value': 'top', 'name': 'Top'}, {'value': 'bottom', 'name': 'Bottom'},
             {'value': 'center', 'name': 'Center'}],
            self.settings.settings['m_orientation'],
            lambda v: self.on_value_changed('m_orientation', v))
        master_group.add(self.widgets['m_orientation'])

        self.widgets['m_mfact'] = SliderRow(
            "Master Factor", "Master window size as percentage of screen [0.1 - 0.9]",
            0.1, 1.0, 0.05, self.settings.settings['m_mfact'],
            lambda v: self.on_value_changed('m_mfact', v), digits=2)
        master_group.add(self.widgets['m_mfact'])

        self.widgets['m_new_status'] = DropdownRow(
            "New Window Status", "Where new windows are placed",
            [{'value': 'master', 'name': 'Master'}, {'value': 'slave', 'name': 'Slave'},
             {'value': 'inherit', 'name': 'Inherit from focused'}],
            self.settings.settings['m_new_status'],
            lambda v: self.on_value_changed('m_new_status', v))
        master_group.add(self.widgets['m_new_status'])

        self.widgets['m_new_on_active'] = DropdownRow(
            "New Window Placement", "Place new window relative to focused window",
            [{'value': 'none', 'name': 'None (use new_on_top)'},
             {'value': 'before', 'name': 'Before focused'},
             {'value': 'after', 'name': 'After focused'}],
            self.settings.settings['m_new_on_active'],
            lambda v: self.on_value_changed('m_new_on_active', v))
        master_group.add(self.widgets['m_new_on_active'])

        self.widgets['m_new_on_top'] = SwitchRow(
            "New on Top", "New windows open at top of stack",
            self.settings.settings['m_new_on_top'],
            lambda v: self.on_value_changed('m_new_on_top', v))
        master_group.add(self.widgets['m_new_on_top'])

        self.widgets['m_special_scale_factor'] = SliderRow(
            "Special Scale", "Scale of special workspace windows [0.1 - 1.0]",
            0.1, 1.0, 0.05, self.settings.settings['m_special_scale_factor'],
            lambda v: self.on_value_changed('m_special_scale_factor', v), digits=2)
        master_group.add(self.widgets['m_special_scale_factor'])

        self.widgets['m_allow_small_split'] = SwitchRow(
            "Allow Small Split", "Enable additional master windows in horizontal split",
            self.settings.settings['m_allow_small_split'],
            lambda v: self.on_value_changed('m_allow_small_split', v))
        master_group.add(self.widgets['m_allow_small_split'])

        content.append(master_group)
        self.tiling_sections.append(master_group)
        self.master_sections.append(master_group)
        # =========================================
        master_center = Adw.PreferencesGroup(
            title="Master Center Options", description="Settings for center orientation mode")

        self.widgets['m_slave_count_for_center_master'] = SliderRow(
            "Center Min Slaves", "Minimum slave windows for center mode, 0 = always center [0 - 10]",
            0, 10, 1, self.settings.settings['m_slave_count_for_center_master'],
            lambda v: self.on_value_changed('m_slave_count_for_center_master', int(v)))
        master_center.add(self.widgets['m_slave_count_for_center_master'])

        self.widgets['m_center_master_fallback'] = DropdownRow(
            "Center Fallback", "Fallback when too few slaves for center mode",
            [{'value': 'left', 'name': 'Left'}, {'value': 'right', 'name': 'Right'},
             {'value': 'top', 'name': 'Top'}, {'value': 'bottom', 'name': 'Bottom'}],
            self.settings.settings['m_center_master_fallback'],
            lambda v: self.on_value_changed('m_center_master_fallback', v))
        master_center.add(self.widgets['m_center_master_fallback'])

        content.append(master_center)
        self.tiling_sections.append(master_center)
        self.master_sections.append(master_center)
        # =========================================
        master_interact = Adw.PreferencesGroup(
            title="Master Interaction", description="Resize and drag behavior")

        self.widgets['m_smart_resizing'] = SwitchRow(
            "Smart Resizing", "Resize direction based on mouse position on window",
            self.settings.settings['m_smart_resizing'],
            lambda v: self.on_value_changed('m_smart_resizing', v))
        master_interact.add(self.widgets['m_smart_resizing'])

        self.widgets['m_drop_at_cursor'] = SwitchRow(
            "Drop at Cursor", "Drag-and-drop places windows at cursor position",
            self.settings.settings['m_drop_at_cursor'],
            lambda v: self.on_value_changed('m_drop_at_cursor', v))
        master_interact.add(self.widgets['m_drop_at_cursor'])

        self.widgets['m_always_keep_position'] = SwitchRow(
            "Always Keep Position", "Keep master in configured position when no slaves",
            self.settings.settings['m_always_keep_position'],
            lambda v: self.on_value_changed('m_always_keep_position', v))
        master_interact.add(self.widgets['m_always_keep_position'])

        content.append(master_interact)
        self.tiling_sections.append(master_interact)
        self.master_sections.append(master_interact)
        # =========================================
        dwindle_group = Adw.PreferencesGroup(
            title="Dwindle Layout", description="Settings for the dwindle (binary split) tiling layout")

        self.widgets['d_force_split'] = DropdownRow(
            "Split Direction", "How new windows are split",
            [{'value': 0, 'name': 'Follow mouse'}, {'value': 1, 'name': 'Always left / top'},
             {'value': 2, 'name': 'Always right / bottom'}],
            self.settings.settings['d_force_split'],
            lambda v: self.on_value_changed('d_force_split', v))
        dwindle_group.add(self.widgets['d_force_split'])

        self.widgets['d_default_split_ratio'] = SliderRow(
            "Default Split Ratio", "Split ratio on open, 1.0 = even 50/50 [0.1 - 1.9]",
            0.1, 1.9, 0.1, self.settings.settings['d_default_split_ratio'],
            lambda v: self.on_value_changed('d_default_split_ratio', v), digits=1)
        dwindle_group.add(self.widgets['d_default_split_ratio'])

        self.widgets['d_split_bias'] = DropdownRow(
            "Split Bias", "Which window receives the split ratio",
            [{'value': 0, 'name': 'Directional (top/left window)'},
             {'value': 1, 'name': 'Current window'}],
            self.settings.settings['d_split_bias'],
            lambda v: self.on_value_changed('d_split_bias', v))
        dwindle_group.add(self.widgets['d_split_bias'])

        self.widgets['d_split_width_multiplier'] = SliderRow(
            "Width Multiplier", "Auto-split width multiplier, useful for widescreen [0.5 - 2.0]",
            0.5, 2.0, 0.1, self.settings.settings['d_split_width_multiplier'],
            lambda v: self.on_value_changed('d_split_width_multiplier', v), digits=1)
        dwindle_group.add(self.widgets['d_split_width_multiplier'])

        self.widgets['d_special_scale_factor'] = SliderRow(
            "Special Scale", "Scale of special workspace windows [0.1 - 1.0]",
            0.1, 1.0, 0.05, self.settings.settings['d_special_scale_factor'],
            lambda v: self.on_value_changed('d_special_scale_factor', v), digits=2)
        dwindle_group.add(self.widgets['d_special_scale_factor'])

        self.widgets['d_pseudotile'] = SwitchRow(
            "Pseudotile", "Pseudotiled windows retain floating size when tiled",
            self.settings.settings['d_pseudotile'],
            lambda v: self.on_value_changed('d_pseudotile', v))
        dwindle_group.add(self.widgets['d_pseudotile'])

        content.append(dwindle_group)
        self.tiling_sections.append(dwindle_group)
        self.dwindle_sections.append(dwindle_group)
        # =========================================
        dwindle_split = Adw.PreferencesGroup(
            title="Dwindle Split Behavior", description="How splits are created and preserved")

        self.widgets['d_smart_split'] = SwitchRow(
            "Smart Split", "Precise split direction based on cursor position in window",
            self.settings.settings['d_smart_split'],
            lambda v: self.on_value_changed('d_smart_split', v))
        dwindle_split.add(self.widgets['d_smart_split'])

        self.widgets['d_preserve_split'] = SwitchRow(
            "Preserve Split", "Keep split direction regardless of container changes",
            self.settings.settings['d_preserve_split'],
            lambda v: self.on_value_changed('d_preserve_split', v))
        dwindle_split.add(self.widgets['d_preserve_split'])

        self.widgets['d_permanent_direction_override'] = SwitchRow(
            "Permanent Direction", "Preselect direction persists until changed",
            self.settings.settings['d_permanent_direction_override'],
            lambda v: self.on_value_changed('d_permanent_direction_override', v))
        dwindle_split.add(self.widgets['d_permanent_direction_override'])

        self.widgets['d_use_active_for_splits'] = SwitchRow(
            "Use Active for Splits", "Prefer active window over mouse position for splits",
            self.settings.settings['d_use_active_for_splits'],
            lambda v: self.on_value_changed('d_use_active_for_splits', v))
        dwindle_split.add(self.widgets['d_use_active_for_splits'])

        content.append(dwindle_split)
        self.tiling_sections.append(dwindle_split)
        self.dwindle_sections.append(dwindle_split)
        # =========================================
        dwindle_interact = Adw.PreferencesGroup(
            title="Dwindle Interaction", description="Resize and move behavior")

        self.widgets['d_smart_resizing'] = SwitchRow(
            "Smart Resizing", "Resize direction based on mouse position on window",
            self.settings.settings['d_smart_resizing'],
            lambda v: self.on_value_changed('d_smart_resizing', v))
        dwindle_interact.add(self.widgets['d_smart_resizing'])

        self.widgets['d_precise_mouse_move'] = SwitchRow(
            "Precise Mouse Move", "More precise window drop position on bindm movewindow",
            self.settings.settings['d_precise_mouse_move'],
            lambda v: self.on_value_changed('d_precise_mouse_move', v))
        dwindle_interact.add(self.widgets['d_precise_mouse_move'])

        content.append(dwindle_interact)
        self.tiling_sections.append(dwindle_interact)
        self.dwindle_sections.append(dwindle_interact)
        # =========================================
        scrolling_group = Adw.PreferencesGroup(
            title="Scrolling Layout",
            description="Windows positioned on an infinitely growing tape")

        self.widgets['s_fullscreen_on_one_column'] = SwitchRow(
            "Fullscreen on One Column",
            "A single column on a workspace always spans the entire screen",
            self.settings.settings['s_fullscreen_on_one_column'],
            lambda v: self.on_value_changed('s_fullscreen_on_one_column', v))
        scrolling_group.add(self.widgets['s_fullscreen_on_one_column'])

        self.widgets['s_column_width'] = SliderRow(
            "Column Width", "Default width of a column [0.1 - 1.0]",
            0.1, 1.0, 0.05, self.settings.settings['s_column_width'],
            lambda v: self.on_value_changed('s_column_width', v), digits=2)
        scrolling_group.add(self.widgets['s_column_width'])

        self.widgets['s_focus_fit_method'] = DropdownRow(
            "Focus Fit Method", "How focused column is brought into view",
            [{'value': 0, 'name': 'Center'}, {'value': 1, 'name': 'Fit'}],
            self.settings.settings['s_focus_fit_method'],
            lambda v: self.on_value_changed('s_focus_fit_method', v))
        scrolling_group.add(self.widgets['s_focus_fit_method'])

        self.widgets['s_follow_focus'] = SwitchRow(
            "Follow Focus", "Automatically move layout to show focused window",
            self.settings.settings['s_follow_focus'],
            lambda v: self.on_value_changed('s_follow_focus', v))
        scrolling_group.add(self.widgets['s_follow_focus'])

        self.widgets['s_follow_min_visible'] = SliderRow(
            "Follow Min Visible",
            "Minimum fraction visible for focus to follow [0.0 - 1.0]",
            0.0, 1.0, 0.05, self.settings.settings['s_follow_min_visible'],
            lambda v: self.on_value_changed('s_follow_min_visible', v), digits=2)
        scrolling_group.add(self.widgets['s_follow_min_visible'])

        self.widgets['s_explicit_column_widths'] = EntryRow(
            "Explicit Column Widths",
            "Comma-separated list of widths for colresize +conf/-conf",
            self.settings.settings['s_explicit_column_widths'],
            lambda v: self.on_value_changed('s_explicit_column_widths', v))
        scrolling_group.add(self.widgets['s_explicit_column_widths'])

        self.widgets['s_direction'] = DropdownRow(
            "Default Direction", "Direction new windows appear and layout scrolls",
            [{'value': 'right', 'name': 'Right'}, {'value': 'left', 'name': 'Left'},
             {'value': 'up', 'name': 'Up'}, {'value': 'down', 'name': 'Down'}],
            self.settings.settings['s_direction'],
            lambda v: self.on_value_changed('s_direction', v))
        scrolling_group.add(self.widgets['s_direction'])

        content.append(scrolling_group)
        self.tiling_sections.append(scrolling_group)

        # =========================================
        # WORKSPACE SCROLL DIRECTION
        # =========================================
        ws_group = Adw.PreferencesGroup(
            title="Workspace Scroll Direction",
            description="Per-workspace scroll direction override (left/right monitor)")

        direction_options = [
            {'value': 'left', 'name': 'Left'}, {'value': 'right', 'name': 'Right'},
            {'value': 'up', 'name': 'Up'}, {'value': 'down', 'name': 'Down'}]

        # Workspace 1 = monitor left
        self.widgets['ws_1_direction'] = DropdownRow(
            "Workspace 1 (Monitor Left)", "Scroll direction for workspace 1",
            direction_options,
            self.settings.settings['ws_1_direction'],
            lambda v: self.on_value_changed('ws_1_direction', v))
        ws_group.add(self.widgets['ws_1_direction'])

        # Workspaces 2-9 = monitor right
        for ws_num in range(2, 10):
            key = f'ws_{ws_num}_direction'
            self.widgets[key] = DropdownRow(
                f"Workspace {ws_num} (Monitor Right)",
                f"Scroll direction for workspace {ws_num}",
                direction_options,
                self.settings.settings[key],
                lambda v, k=key: self.on_value_changed(k, v))
            ws_group.add(self.widgets[key])

        content.append(ws_group)
        self.tiling_sections.append(ws_group)

        scrolled.set_child(content)
        main_box.append(scrolled)

        self.status_bar = Gtk.Label(label="Ready")
        self.status_bar.add_css_class("dim-label")
        self.status_bar.set_margin_top(6); self.status_bar.set_margin_bottom(6)
        main_box.append(self.status_bar)
        self.set_content(main_box)

        # Set initial visibility based on tiling state
        self.update_tiling_visibility(self.settings.settings['tiling_enabled'])
        # Set initial visibility based on selected layout (only matters when tiling is ON)
        if self.settings.settings['tiling_enabled']:
            self.update_layout_visibility(self.settings.settings['g_layout'])

    def on_tiling_toggled(self, enabled):
        """Handle tiling mode toggle — show/hide tiling sections."""
        self.settings.settings['tiling_enabled'] = enabled
        self.update_tiling_visibility(enabled)
        # Re-apply layout-specific visibility (master/dwindle) after showing all tiling sections
        if enabled:
            self.update_layout_visibility(self.settings.settings['g_layout'])
            self.status_bar.set_text("Tiling mode ON — select a layout and click Apply")
        else:
            self.status_bar.set_text("Traditional desktop mode — click Apply to switch")

    def update_tiling_visibility(self, enabled):
        """Show or hide all tiling-related sections."""
        for section in self.tiling_sections:
            section.set_visible(enabled)

    #def on_value_changed(self, key, value):
    #    self.settings.settings[key] = value
    #    self.status_bar.set_text(f"Changed: {key} = {value}")
    def on_value_changed(self, key, value):
        self.settings.settings[key] = value
        sync_pairs = {
            'm_special_scale_factor': 'd_special_scale_factor',
            'd_special_scale_factor': 'm_special_scale_factor',
            'm_smart_resizing': 'd_smart_resizing',
            'd_smart_resizing': 'm_smart_resizing',
        }
        if key in sync_pairs:
            partner = sync_pairs[key]
            self.settings.settings[partner] = value
            if partner in self.widgets:
                widget = self.widgets[partner]
                if isinstance(widget, SliderRow): widget.set_value(value)
                elif isinstance(widget, SwitchRow): widget.set_active(value)
        # Update layout-specific section visibility when layout changes
        if key == 'g_layout':
            self.update_layout_visibility(value)
        self.status_bar.set_text(f"Changed: {key} = {value}")

    def update_layout_visibility(self, layout):
        """Show only the GUI sections for the currently selected layout.
        Master sections visible only when layout=master,
        Dwindle sections visible only when layout=dwindle.
        Scrolling and workspace directions are always visible."""
        for section in self.master_sections:
            section.set_visible(layout == 'master')
        for section in self.dwindle_sections:
            section.set_visible(layout == 'dwindle')

    def on_apply(self, button):
        tiling_enabled = self.settings.settings['tiling_enabled']

        # Save config
        if self.settings.save_config():
            # Run the appropriate on/off script
            script_ok = self.settings.run_tiling_script(tiling_enabled)

            # Reload hyprland
            reload_ok = self.settings.reload_hyprland()

            if script_ok and reload_ok:
                mode = "Tiling" if tiling_enabled else "Traditional Desktop"
                self.status_bar.set_text(f"{mode} mode — saved and applied!")
            elif script_ok:
                self.status_bar.set_text("Saved (could not reload Hyprland)")
            elif reload_ok:
                mode = "Tiling" if tiling_enabled else "Traditional Desktop"
                self.status_bar.set_text(f"{mode} mode — saved (script not found, reload OK)")
            else:
                self.status_bar.set_text("Saved config (script not found, could not reload)")
        else:
            self.status_bar.set_text("Error saving configuration!")

    def on_reset(self, button):
        self.settings.reset_to_defaults(); self.refresh_ui()
        self.status_bar.set_text("Reset to Nordix defaults — click Apply to save")

    def refresh_ui(self):
        s = self.settings.settings
        for key, widget in self.widgets.items():
            if key in s:
                if isinstance(widget, SliderRow): widget.set_value(s[key])
                elif isinstance(widget, SwitchRow): widget.set_active(s[key])
                elif isinstance(widget, DropdownRow): widget.set_value(s[key])
                elif isinstance(widget, EntryRow): widget.set_text(str(s[key]))
        self.update_tiling_visibility(s['tiling_enabled'])
        if s['tiling_enabled']:
            self.update_layout_visibility(s['g_layout'])


class NordixLayoutApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id='com.Nordix.Settings.Layout', flags=Gio.ApplicationFlags.FLAGS_NONE)
    def do_activate(self):
        win = NordixLayoutWindow(self); win.present()

def main():
    app = NordixLayoutApp(); return app.run(None)

if __name__ == "__main__":
    main()
