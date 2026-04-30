#!/usr/bin/env python3
##=========================================================##
 # SPDX-License-Identifier: GPL-3.0-or-later               #
 # Copyright (c) 2025 Jimmy Källhagen                      #
 # Part of Yggdrasil - Nordix desktop environment          #
##=========================================================##

"""Yggdrasil Hyprland Monitor GUI
A graphical settings panel for Hyprland monitor configuration
Supports HDR, 10-bit color, VRR, and dual monitor workspace management"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib
import subprocess
import json
import os
import re
from pathlib import Path

# Config path
CONFIG_PATH = Path.home() / ".config" / "nordix" / "yggdrasil" / "settings" / "Yggdrasil-monitors.conf"

# Available options
SCALE_OPTIONS = [
    ('1.0 (100%)', 1.0),
    ('1.25 (125%)', 1.25),
    ('1.5 (150%)', 1.5),
    ('1.67 (167%)', 1.67),
    ('2.0 (200%)', 2.0),
]

TRANSFORM_OPTIONS = [
    ('Normal (0)', 0),
    ('90 degrees (1)', 1),
    ('180 degrees (2)', 2),
    ('270 degrees (3)', 3),
    ('Flipped (4)', 4),
    ('Flipped + 90 (5)', 5),
    ('Flipped + 180 (6)', 6),
    ('Flipped + 270 (7)', 7),
]

VRR_OPTIONS = [
    ('Off', 0),
    ('On', 1),
    ('Fullscreen only', 2),
    ('Fullscreen + content type', 3),
]

COLOR_MANAGEMENT_OPTIONS = [
    ('auto - 8-bit sRGB', 'auto'),
    ('srgb - sRGB primaries (8-bit)', 'srgb'),
    ('wide - 10-bit BT2020 (required for 10-bit)', 'wide'),
    ('hdr - HDR with PQ transfer (requires 10-bit)', 'hdr'),
    ('hdredid - HDR with EDID primaries', 'hdredid'),
    ('dcip3 - DCI P3 primaries', 'dcip3'),
    ('dp3 - Apple P3 primaries', 'dp3'),
    ('adobe - Adobe RGB primaries', 'adobe'),
    ('edid - From monitor EDID', 'edid'),
]

SDR_EOTF_OPTIONS = [
    ('Follow render setting (0)', 0),
    ('sRGB (1)', 1),
    ('Gamma 2.2 (2)', 2),
]

BITDEPTH_OPTIONS = [
    ('8-bit', 8),
    ('10-bit', 10),
]

PREFER_HDR_OPTIONS = [
    ('Off', 0),
    ('Always', 1),
    ('Gamescope only', 2),
]

CM_FS_PASSTHROUGH_OPTIONS = [
    ('Off', 0),
    ('Always', 1),
    ('HDR only', 2),
]

# Default monitor settings
DEFAULT_MONITOR_SETTINGS = {
    'output': '',
    'mode': '1920x1080@60',
    'position': '0x0',
    'scale': 1.0,
    'transform': 0,
    'bitdepth': 8,
    'vrr': 2,
    'cm': 'auto',
    'sdr_eotf': 0,
    'supports_wide_color': 0,  # int: 0=auto, 1=on, -1=off
    'supports_hdr': 0,         # int: 0=auto, 1=on, -1=off
    'sdr_min_luminance': 0.005,  # float - true black
    'sdr_max_luminance': 200,    # int - recommended 200-250
    'min_luminance': 0.0,        # float
    'max_avg_luminance': 15,     # int
    'max_luminance': 100,        # int
    'sdrbrightness': 1.0,
    'sdrsaturation': 1.0,
}

# Default global settings
DEFAULT_GLOBAL_SETTINGS = {
    'wine_hdr_enable': True,
    'enable_hdr_wsi': True,
    'dxvk_hdr': True,
    'xx_color_management_v4': True,
    'prefer_hdr': 1,
    'full_cm_proto': True,
    'cm_enabled': True,
    'cm_fs_passthrough': 1,
    'cm_sdr_eotf': 1,
    'secondary_scrolling_layout': True,
}


class MonitorDetector:
    """Detects connected monitors using hyprctl"""
    
    @staticmethod
    def get_monitors():
        """Returns list of connected monitors with their capabilities"""
        try:
            # Use text output and parse it (more reliable than JSON for modes)
            result = subprocess.run(
                ['hyprctl', 'monitors'],
                capture_output=True, text=True, check=True
            )
            
            monitors = []
            current_monitor = None
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                
                # New monitor starts with "Monitor NAME"
                if line.startswith('Monitor '):
                    if current_monitor:
                        monitors.append(current_monitor)
                    
                    parts = line.split()
                    name = parts[1] if len(parts) > 1 else 'Unknown'
                    current_monitor = {
                        'name': name,
                        'availableModes': [],
                        'currentMode': '',
                        'description': '',
                        'make': '',
                        'model': '',
                        'scale': 1.0,
                    }
                
                elif current_monitor:
                    if line.startswith('availableModes:'):
                        modes_str = line.replace('availableModes:', '').strip()
                        modes = modes_str.split()
                        current_monitor['availableModes'] = modes
                    
                    elif line.startswith('description:'):
                        current_monitor['description'] = line.replace('description:', '').strip()
                    
                    elif line.startswith('make:'):
                        current_monitor['make'] = line.replace('make:', '').strip()
                    
                    elif line.startswith('model:'):
                        current_monitor['model'] = line.replace('model:', '').strip()
                    
                    elif line.startswith('scale:'):
                        try:
                            current_monitor['scale'] = float(line.replace('scale:', '').strip())
                        except:
                            pass
                    
                    elif '@' in line and 'at' in line and not line.startswith('availableModes'):
                        # Current mode line like "3840x2160@119.99900 at 0x0"
                        mode_part = line.split(' at ')[0].strip()
                        current_monitor['currentMode'] = mode_part
            
            # Don't forget the last monitor
            if current_monitor:
                monitors.append(current_monitor)
            
            return monitors
            
        except Exception as e:
            print(f"Error detecting monitors: {e}")
            return []
    
    @staticmethod
    def get_available_modes(monitor_name):
        """Get available modes for a specific monitor"""
        monitors = MonitorDetector.get_monitors()
        for mon in monitors:
            if mon.get('name') == monitor_name:
                return mon.get('availableModes', [])
        return []


class MonitorSettings:
    """Handles reading and writing of monitors.conf"""
    
    def __init__(self, config_path=None):
        self.config_path = Path(config_path) if config_path else CONFIG_PATH
        
        self.setup_mode = 'single'  # 'single' or 'dual'
        self.primary_monitor = DEFAULT_MONITOR_SETTINGS.copy()
        self.secondary_monitor = DEFAULT_MONITOR_SETTINGS.copy()
        self.global_settings = DEFAULT_GLOBAL_SETTINGS.copy()
        self.detected_monitors = []
        self.config_loaded = False  # Track if config was loaded
        
        self.detect_monitors()
        self.load_config()
    
    def detect_monitors(self):
        """Detect connected monitors"""
        self.detected_monitors = MonitorDetector.get_monitors()
        
        if len(self.detected_monitors) >= 2:
            self.setup_mode = 'dual'
        else:
            self.setup_mode = 'single'
    
    def load_config(self):
        """Load current configuration from file"""
        if not self.config_path.exists():
            self.config_loaded = False
            return
        
        try:
            content = self.config_path.read_text()
            self._parse_config(content)
            self.config_loaded = True
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config_loaded = False
    
    def _parse_config(self, content):
        """Parse monitors.conf content and populate settings"""
        
        # Parse monitorv2 blocks
        monitors_parsed = self._parse_monitorv2_blocks(content)
        
        # Parse workspace assignments to determine which monitor is secondary
        workspace_assignments = self._parse_workspace_assignments(content)
        
        # Parse global settings
        self._parse_global_settings(content)
        
        # Parse scrolling layout setting
        self._parse_scrolling_layout(content)
        
        # Assign parsed monitors to primary/secondary
        if monitors_parsed:
            # Check if we have workspace 1 assigned (indicates dual setup with secondary)
            secondary_output = workspace_assignments.get(1)
            
            if len(monitors_parsed) >= 2 and secondary_output:
                self.setup_mode = 'dual'
                # Assign monitors based on workspace 1 assignment
                for mon in monitors_parsed:
                    if mon.get('output') == secondary_output:
                        self._apply_parsed_monitor(mon, self.secondary_monitor)
                    else:
                        self._apply_parsed_monitor(mon, self.primary_monitor)
            elif len(monitors_parsed) >= 2:
                # Dual setup without workspace assignments - use position hints
                self.setup_mode = 'dual'
                for i, mon in enumerate(monitors_parsed):
                    if i == 0:
                        self._apply_parsed_monitor(mon, self.primary_monitor)
                    elif i == 1:
                        self._apply_parsed_monitor(mon, self.secondary_monitor)
            else:
                # Single monitor setup
                self.setup_mode = 'single'
                self._apply_parsed_monitor(monitors_parsed[0], self.primary_monitor)
    
    def _parse_monitorv2_blocks(self, content):
        """Parse all monitorv2 { ... } blocks from config"""
        monitors = []
        
        # Find all monitorv2 blocks
        # Pattern matches "monitorv2 {" followed by content until "}"
        pattern = r'monitorv2\s*\{([^}]*)\}'
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        
        for block_content in matches:
            mon = self._parse_monitor_block(block_content)
            if mon.get('output'):  # Only add if we got an output name
                monitors.append(mon)
        
        return monitors
    
    def _parse_monitor_block(self, block_content):
        """Parse a single monitorv2 block content"""
        mon = {}
        
        # Key-value patterns for different types
        # String values
        string_keys = ['output', 'mode', 'position', 'cm']
        # Integer values
        int_keys = ['transform', 'bitdepth', 'vrr', 'sdr_eotf', 'supports_wide_color', 
                    'supports_hdr', 'sdr_max_luminance', 'max_avg_luminance', 'max_luminance']
        # Float values  
        float_keys = ['scale', 'sdr_min_luminance', 'min_luminance', 'sdrbrightness', 'sdrsaturation']
        
        for line in block_content.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse key = value
            if '=' in line:
                parts = line.split('=', 1)
                key = parts[0].strip()
                value = parts[1].strip()
                
                # Remove inline comments
                if '#' in value:
                    value = value.split('#')[0].strip()
                
                if key in string_keys:
                    mon[key] = value
                elif key in int_keys:
                    try:
                        mon[key] = int(float(value))  # Handle "200.0" -> 200
                    except ValueError:
                        pass
                elif key in float_keys:
                    try:
                        mon[key] = float(value)
                    except ValueError:
                        pass
        
        return mon
    
    def _parse_workspace_assignments(self, content):
        """Parse workspace = N, monitor:OUTPUT lines"""
        assignments = {}
        
        # Pattern: workspace = 1, monitor:DP-1, ...
        pattern = r'workspace\s*=\s*(\d+)\s*,\s*monitor:([^,\s]+)'
        matches = re.findall(pattern, content)
        
        for ws_num, monitor_name in matches:
            try:
                assignments[int(ws_num)] = monitor_name
            except ValueError:
                pass
        
        return assignments
    
    def _parse_scrolling_layout(self, content):
        """Parse scrolling layout setting for secondary monitor"""
        # Check if scrolling layout line exists and if it's commented out
        # Pattern matches both: "workspace = 1, layout:scrolling" and "# workspace = 1, layout:scrolling"
        pattern = r'^(\s*#?\s*)workspace\s*=\s*1\s*,\s*layout:scrolling'
        
        for line in content.split('\n'):
            match = re.match(pattern, line)
            if match:
                # If the line starts with #, it's disabled
                prefix = match.group(1)
                self.global_settings['secondary_scrolling_layout'] = '#' not in prefix
                return
        
        # If not found in config, keep default (True)
    
    def _parse_global_settings(self, content):
        """Parse global environment and setting lines"""
        
        # Parse env = KEY,VALUE lines
        env_pattern = r'env\s*=\s*(\w+)\s*,\s*(\d+)'
        for match in re.finditer(env_pattern, content):
            key = match.group(1).upper()
            value = int(match.group(2))
            
            if key == 'WINE_HDR_ENABLE':
                self.global_settings['wine_hdr_enable'] = bool(value)
            elif key == 'ENABLE_HDR_WSI':
                self.global_settings['enable_hdr_wsi'] = bool(value)
            elif key == 'DXVK_HDR':
                self.global_settings['dxvk_hdr'] = bool(value)
        
        # Parse boolean settings (key = true/false)
        bool_settings = {
            'xx_color_management_v4': 'xx_color_management_v4',
            'full_cm_proto': 'full_cm_proto',
            'cm_enabled': 'cm_enabled',
        }
        
        for config_key, settings_key in bool_settings.items():
            pattern = rf'{config_key}\s*=\s*(true|false)'
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                self.global_settings[settings_key] = match.group(1).lower() == 'true'
        
        # Parse integer settings
        int_settings = {
            'prefer_hdr': 'prefer_hdr',
            'cm_fs_passthrough': 'cm_fs_passthrough',
            'cm_sdr_eotf': 'cm_sdr_eotf',
        }
        
        for config_key, settings_key in int_settings.items():
            pattern = rf'{config_key}\s*=\s*(\d+)'
            match = re.search(pattern, content)
            if match:
                self.global_settings[settings_key] = int(match.group(1))
    
    def _apply_parsed_monitor(self, parsed, target):
        """Apply parsed monitor values to target monitor settings dict"""
        for key, value in parsed.items():
            if key in target:
                target[key] = value
    
    def generate_config(self):
        """Generate the monitors.conf content"""
        pm = self.primary_monitor
        sm = self.secondary_monitor
        gs = self.global_settings
        
        config = '''
##=========================================================##
 # SPDX-License-Identifier: GPL-3.0-or-later               #
 # Copyright (c) 2025 Jimmy Källhagen                      #
 # Part of Yggdrasil - Nordix desktop environment          #
##=========================================================##

# ##==================================================##
#  #              Yggdrasil - Monitors                #
#  #             Hyprland Configuration               #
# ##==================================================##
#  * HDR, 10-BIT support
#  * Generated by Yggdrasil Monitor GUI
#  * Full HDR configuration with color management
#  * Based on Hyprland monitorv2 syntax
#  * Documentation: https://wiki.hyprland.org/Configuring/Monitors/#monitor-v2
#
##==============================================================##

##==============================================================##
 #                       *** TIP HDR ***                        #
##==============================================================##
 # * Run "wlr-randr" in the terminal to see your monitor spec   #
 #                                                              #
 # Steam:                                                       #
 #  * DXVK_HDR=1 gamescope -f --hdr-enabled -- %command%        #
 #                                                              # 
 # Proton:                                                      #
 # For Displayport 1, 2 or 3 (DP-1,DP-2,DP-3...):               #
 # * ENABLE_HDR_WSI=1 DXVK_HDR=1 DISPLAY=DP-3   %command%       #
 #                                                              #
 # For HDMI (HDMI-A-1,HDMI-A-2,HDMI-A-3.-):                     #
 # * ENABLE_HDR_WSI=1 DXVK_HDR=1 DISPLAY=HDMI-A-1 %command%     #
 #                                                              #
 # Non-steam Displayport:                                       #
 # * ENABLE_HDR_WSI=1 DXVK_HDR=1 WINE_HDR_ENABLE=1 DISPLAY=DP-3 #
 #                                                              #
 # For HDMI:                                                    #
 # * ENABLE_HDR_WSI=1 DXVK_HDR=1 WINE_HDR_ENABLE=1 HDMI-A-1     #
 #                                                              #
 # Video:                                                       #
 # * ENABLE_HDR_WSI=1 mpv --vo=gpu-next \                       #
 # --target-colorspace-hint --gpu-api=vulkan \                  #
 # --gpu-context=waylandvk "filename"                           #
##==============================================================##

##==============================================================##
 #                       Transform list                         #
##==============================================================##
# 0 -> normal (no transforms)
# 1 -> 90 degrees
# 2 -> 180 degrees
# 3 -> 270 degrees
# 4 -> flipped
# 5 -> flipped + 90 degrees
# 6 -> flipped + 180 degrees 
# 7 -> flipped + 270 degrees
##==============================================================##

'''
        
        if self.setup_mode == 'dual':
            # Generate scrolling layout line (commented or not based on setting)
            scrolling_prefix = '' if gs.get('secondary_scrolling_layout', True) else '# '
            
            config += f'''
 ##==================================================##
  #                  2 - monitors                    #
 ##==================================================##
 
 
 # Secondary monitor (left) locked to workspace 1
 # Primary monitor (right) gets workspaces 2-10
 # This prevents unwanted workspace jumping between monitors

 # Scrolling layout for secondary monitor workspace
{scrolling_prefix}workspace = 1, layout:scrolling
 
workspace = 1, monitor:{sm['output']}
workspace = 2, monitor:{pm['output']}, default:true, persistent:true
workspace = 3, monitor:{pm['output']}
workspace = 4, monitor:{pm['output']}
workspace = 5, monitor:{pm['output']}
workspace = 6, monitor:{pm['output']}
workspace = 7, monitor:{pm['output']}
workspace = 8, monitor:{pm['output']}
workspace = 9, monitor:{pm['output']}
workspace = 10, monitor:{pm['output']}

'''
        
        # Primary monitor config
        config += f'''
 ##==================================================##
  #    Primary Monitor - {pm['output']}              # 
 ##==================================================##


monitorv2 {{

  output = {pm['output']}
  mode = {pm['mode']}
  position = {pm['position']}
  transform = {pm['transform']}
  scale = {pm['scale']:.2f}
  bitdepth = {pm['bitdepth']}
  vrr = {pm['vrr']}
  cm = {pm['cm']}
  sdr_eotf = {pm['sdr_eotf']}
'''
        
        if pm['supports_hdr'] != 0 or pm['supports_wide_color'] != 0:
            config += f'''
  # HDR Settings
  supports_wide_color = {pm['supports_wide_color']}
  supports_hdr = {pm['supports_hdr']}
  sdr_min_luminance = {pm['sdr_min_luminance']}
  sdr_max_luminance = {int(pm['sdr_max_luminance'])}
  min_luminance = {pm['min_luminance']}
  max_avg_luminance = {int(pm['max_avg_luminance'])}
  max_luminance = {int(pm['max_luminance'])}
  sdrbrightness = {pm['sdrbrightness']:.2f}
  sdrsaturation = {pm['sdrsaturation']:.2f}
'''
        
        config += '}\n'
        
        # Secondary monitor config (if dual setup)
        if self.setup_mode == 'dual':
            config += f'''

 ##=======================================================##
  # Secondary Monitor - {sm['output']} (Left side, Workspace 1)     #
 ##=======================================================##

monitorv2 {{

  output = {sm['output']}
  mode = {sm['mode']}
  position = auto-left
  transform = {sm['transform']}
  scale = {sm['scale']:.2f}
  bitdepth = {sm['bitdepth']}
  vrr = {sm['vrr']}
  cm = {sm['cm']}
  sdr_eotf = {sm['sdr_eotf']}
'''
            
            if sm['supports_hdr'] != 0 or sm['supports_wide_color'] != 0:
                config += f'''
  # HDR Settings
  supports_wide_color = {sm['supports_wide_color']}
  supports_hdr = {sm['supports_hdr']}
'''
            
            config += '}\n'
        
        # Global HDR settings
        config += f'''

##==================================================##
 #     Global environment HDR support for Wine      # 
##==================================================##

env = WINE_HDR_ENABLE,{1 if gs['wine_hdr_enable'] else 0}
env = ENABLE_HDR_WSI,{1 if gs['enable_hdr_wsi'] else 0}
env = DXVK_HDR,{1 if gs['dxvk_hdr'] else 0}


##==================================================##
 #            HDR support protocol                  #
##==================================================##

xx_color_management_v4 = {'true' if gs['xx_color_management_v4'] else 'false'}

# * Report HDR mode as preferred. 0 - off, 1 - always, 2 - gamescope only
prefer_hdr = {gs['prefer_hdr']}

# * Claims support for all cm proto features (requires restart)
full_cm_proto = {'true' if gs['full_cm_proto'] else 'false'}

# * Whether the color management pipeline should be enabled (requires restart)
cm_enabled = {'true' if gs['cm_enabled'] else 'false'}

#  * Passthrough color settings for fullscreen apps. 0 - off, 1 - always, 2 - hdr only
cm_fs_passthrough = {gs['cm_fs_passthrough']}

# Default transfer function for SDR apps. 0 - sRGB, 1 - Gamma 2.2, 2 - sRGB as Gamma 2.2
cm_sdr_eotf = {gs['cm_sdr_eotf']}
'''
        
        return config
    
    def save_config(self):
        """Save configuration to file"""
        try:
            # Create backup
            if self.config_path.exists():
                backup_path = self.config_path.with_suffix('.conf.backup')
                import shutil
                shutil.copy2(self.config_path, backup_path)
            
            # Write new config
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.config_path.write_text(self.generate_config())
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
        self.primary_monitor = DEFAULT_MONITOR_SETTINGS.copy()
        self.secondary_monitor = DEFAULT_MONITOR_SETTINGS.copy()
        self.global_settings = DEFAULT_GLOBAL_SETTINGS.copy()


class DropdownRow(Adw.ActionRow):
    """A row with dropdown for selection"""
    
    def __init__(self, title, subtitle, options, current_value, callback):
        super().__init__()
        self.set_title(title)
        self.set_subtitle(subtitle)
        
        self.options = options
        self.callback = callback
        
        string_list = Gtk.StringList()
        current_index = 0
        
        for i, (label, value) in enumerate(options):
            string_list.append(label)
            if value == current_value:
                current_index = i
        
        self.dropdown = Gtk.DropDown(model=string_list)
        self.dropdown.set_selected(current_index)
        self.dropdown.connect('notify::selected', self._on_selected)
        
        self.add_suffix(self.dropdown)
    
    def _on_selected(self, dropdown, _):
        selected = dropdown.get_selected()
        if selected < len(self.options):
            _, value = self.options[selected]
            self.callback(value)
    
    def set_value(self, value):
        for i, (_, v) in enumerate(self.options):
            if v == value:
                self.dropdown.set_selected(i)
                break


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
        self.scale.set_size_request(180, -1)
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


class MonitorPanel(Gtk.Box):
    """Panel for configuring a single monitor"""
    
    def __init__(self, title, monitor_settings, detected_monitors, on_change, is_secondary=False):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        self.monitor_settings = monitor_settings
        self.detected_monitors = detected_monitors
        self.on_change = on_change
        self.is_secondary = is_secondary
        self.widgets = {}
        self.mode_group = None  # Reference to update modes dynamically
        
        self.setup_ui(title)
    
    def setup_ui(self, title):
        # Main group
        group = Adw.PreferencesGroup(title=title)
        self.mode_group = group
        
        if self.is_secondary:
            group.set_description("Left side, locked to Workspace 1")
        else:
            group.set_description("Right side, Workspaces 2-10")
        
        # Monitor output selection
        monitor_options = []
        for m in self.detected_monitors:
            name = m.get('name', 'Unknown')
            model = m.get('model', '')
            label = f"{name} ({model})" if model else name
            monitor_options.append((label, name))
        
        if not monitor_options:
            monitor_options = [('No monitors detected', '')]
        
        # Set default output to first detected monitor if not set
        if not self.monitor_settings.get('output') and self.detected_monitors:
            self.monitor_settings['output'] = self.detected_monitors[0].get('name', '')
        
        self.widgets['output'] = DropdownRow(
            "Output", "Select monitor",
            monitor_options,
            self.monitor_settings.get('output', ''),
            lambda v: self._on_output_changed(v)
        )
        group.add(self.widgets['output'])
        
        # Resolution/Mode - populated based on selected monitor
        mode_options = self._get_mode_options()
        current_mode = self.monitor_settings.get('mode', '')
        
        # Always set mode from available options if we have them
        if mode_options:
            if not current_mode or current_mode == '1920x1080@60':
                # Use highest resolution available
                current_mode = mode_options[0][1]
            self.monitor_settings['mode'] = current_mode
            self.on_change('mode', current_mode)
        
        self.widgets['mode'] = DropdownRow(
            "Resolution", "Resolution and refresh rate",
            mode_options if mode_options else [('No modes available', '')],
            current_mode,
            lambda v: self._update('mode', v)
        )
        group.add(self.widgets['mode'])
        
        # Scale
        self.widgets['scale'] = DropdownRow(
            "Scale", "Display scaling factor",
            SCALE_OPTIONS,
            self.monitor_settings.get('scale', 1.0),
            lambda v: self._update('scale', v)
        )
        group.add(self.widgets['scale'])
        
        # Transform
        self.widgets['transform'] = DropdownRow(
            "Rotation", "Display rotation/transform",
            TRANSFORM_OPTIONS,
            self.monitor_settings.get('transform', 0),
            lambda v: self._update('transform', v)
        )
        group.add(self.widgets['transform'])
        
        # Bitdepth
        self.widgets['bitdepth'] = DropdownRow(
            "Bit Depth", "Color depth (10-bit for HDR)",
            BITDEPTH_OPTIONS,
            self.monitor_settings.get('bitdepth', 8),
            lambda v: self._update('bitdepth', v)
        )
        group.add(self.widgets['bitdepth'])
        
        # VRR
        self.widgets['vrr'] = DropdownRow(
            "VRR (Adaptive Sync)", "Variable refresh rate",
            VRR_OPTIONS,
            self.monitor_settings.get('vrr', 2),
            lambda v: self._update('vrr', v)
        )
        group.add(self.widgets['vrr'])
        
        # Color Management
        self.widgets['cm'] = DropdownRow(
            "Color Management", "Color space preset",
            COLOR_MANAGEMENT_OPTIONS,
            self.monitor_settings.get('cm', 'auto'),
            lambda v: self._update('cm', v)
        )
        group.add(self.widgets['cm'])
        
        # SDR EOTF
        self.widgets['sdr_eotf'] = DropdownRow(
            "SDR Transfer Function", "EOTF for SDR content",
            SDR_EOTF_OPTIONS,
            self.monitor_settings.get('sdr_eotf', 0),
            lambda v: self._update('sdr_eotf', v)
        )
        group.add(self.widgets['sdr_eotf'])
        
        self.append(group)
        
        # HDR Settings (expandable)
        hdr_expander = Adw.ExpanderRow(title="Advanced HDR Settings")
        hdr_expander.set_subtitle("Luminance and HDR configuration")
        
        # HDR Enable - now dropdown with -1, 0, 1
        hdr_force_options = [
            ('Auto (0)', 0),
            ('Force On (1)', 1),
            ('Force Off (-1)', -1),
        ]
        
        self.widgets['supports_hdr'] = DropdownRow(
            "HDR Support", "Force HDR support (requires wide color)",
            hdr_force_options,
            self.monitor_settings.get('supports_hdr', 0),
            lambda v: self._update('supports_hdr', v)
        )
        hdr_expander.add_row(self.widgets['supports_hdr'])
        
        self.widgets['supports_wide_color'] = DropdownRow(
            "Wide Color Gamut", "Force wide color gamut support",
            hdr_force_options,
            self.monitor_settings.get('supports_wide_color', 0),
            lambda v: self._update('supports_wide_color', v)
        )
        hdr_expander.add_row(self.widgets['supports_wide_color'])
        
        # HDR Luminance settings
        self.widgets['sdr_min_luminance'] = SliderRow(
            "SDR Min Luminance", "SDR minimum for HDR mapping (0.005 for true black)",
            0.001, 0.5, 0.001, self.monitor_settings.get('sdr_min_luminance', 0.005),
            lambda v: self._update('sdr_min_luminance', v),
            digits=3
        )
        hdr_expander.add_row(self.widgets['sdr_min_luminance'])
        
        self.widgets['sdr_max_luminance'] = SliderRow(
            "SDR Max Luminance", "SDR brightness for HDR mapping (recommended 200-250)",
            80, 400, 10, self.monitor_settings.get('sdr_max_luminance', 200),
            lambda v: self._update('sdr_max_luminance', int(v)),
            digits=0
        )
        hdr_expander.add_row(self.widgets['sdr_max_luminance'])
        
        self.widgets['min_luminance'] = SliderRow(
            "Monitor Min Luminance", "Monitor's minimum luminance",
            0.0, 10.0, 0.1, self.monitor_settings.get('min_luminance', 0.0),
            lambda v: self._update('min_luminance', v),
            digits=2
        )
        hdr_expander.add_row(self.widgets['min_luminance'])
        
        self.widgets['max_avg_luminance'] = SliderRow(
            "Monitor Avg Luminance", "Monitor's average luminance per frame",
            1, 500, 5, self.monitor_settings.get('max_avg_luminance', 15),
            lambda v: self._update('max_avg_luminance', int(v)),
            digits=0
        )
        hdr_expander.add_row(self.widgets['max_avg_luminance'])
        
        self.widgets['max_luminance'] = SliderRow(
            "Monitor Max Luminance", "Monitor's maximum possible luminance",
            100, 2000, 50, self.monitor_settings.get('max_luminance', 100),
            lambda v: self._update('max_luminance', int(v)),
            digits=0
        )
        hdr_expander.add_row(self.widgets['max_luminance'])
        
        self.widgets['sdrbrightness'] = SliderRow(
            "SDR Brightness in HDR", "SDR content brightness when HDR active",
            0.5, 2.0, 0.1, self.monitor_settings.get('sdrbrightness', 1.0),
            lambda v: self._update('sdrbrightness', v),
            digits=1
        )
        hdr_expander.add_row(self.widgets['sdrbrightness'])
        
        self.widgets['sdrsaturation'] = SliderRow(
            "SDR Saturation in HDR", "SDR content saturation when HDR active",
            0.5, 2.0, 0.1, self.monitor_settings.get('sdrsaturation', 1.0),
            lambda v: self._update('sdrsaturation', v),
            digits=1
        )
        hdr_expander.add_row(self.widgets['sdrsaturation'])
        
        group.add(hdr_expander)
    
    def _get_mode_options(self):
        """Get available modes for current monitor as dropdown options"""
        output = self.monitor_settings.get('output', '')
        modes = MonitorDetector.get_available_modes(output)
        
        if not modes:
            return [('1920x1080@60Hz', '1920x1080@60')]
        
        # Sort modes by resolution (highest first) then by refresh rate
        def sort_key(mode):
            try:
                res_part = mode.split('@')[0]
                hz_part = mode.split('@')[1].replace('Hz', '')
                width = int(res_part.split('x')[0])
                height = int(res_part.split('x')[1])
                hz = float(hz_part)
                return (-width, -height, -hz)
            except:
                return (0, 0, 0)
        
        sorted_modes = sorted(modes, key=sort_key)
        
        mode_options = []
        for mode in sorted_modes:
            # Convert "3840x2160@120.00Hz" to display and value
            display = mode
            # Value format for hyprland: "3840x2160@120"
            value = mode.replace('Hz', '').strip()
            # Round the Hz value
            if '@' in value:
                parts = value.split('@')
                try:
                    hz = float(parts[1])
                    value = f"{parts[0]}@{hz:.6f}"
                except:
                    pass
            mode_options.append((display, value))
        
        return mode_options
    
    def _on_output_changed(self, output):
        """Handle monitor output change - update available modes"""
        self.monitor_settings['output'] = output
        self.on_change('output', output)
        
        # Update mode dropdown with new monitor's available modes
        new_modes = self._get_mode_options()
        if new_modes:
            # Set to highest resolution mode
            self.monitor_settings['mode'] = new_modes[0][1]
            self.on_change('mode', new_modes[0][1])
            
            # Rebuild the mode dropdown
            if 'mode' in self.widgets:
                old_widget = self.widgets['mode']
                
                # Update the options list so callback returns correct value
                old_widget.options = new_modes
                
                # Update the dropdown model
                string_list = Gtk.StringList()
                for label, _ in new_modes:
                    string_list.append(label)
                old_widget.dropdown.set_model(string_list)
                old_widget.dropdown.set_selected(0)
    
    def _update(self, key, value):
        self.monitor_settings[key] = value
        self.on_change(key, value)
    
    def refresh(self):
        """Refresh all widgets with current values"""
        for key, widget in self.widgets.items():
            if key in self.monitor_settings:
                value = self.monitor_settings[key]
                if isinstance(widget, SliderRow):
                    widget.set_value(value)
                elif isinstance(widget, SwitchRow):
                    widget.set_active(value)
                elif isinstance(widget, DropdownRow):
                    widget.set_value(value)


class NordixMonitorWindow(Adw.ApplicationWindow):
    """Main window for monitor configuration"""
    
    def __init__(self, app):
        super().__init__(application=app, title="Yggdrasil Monitor Settings")
        self.set_default_size(650, 850)
        
        self.settings = MonitorSettings()
        self.setup_ui()
    
    def setup_ui(self):
        # Create status_bar early so callbacks can use it
        if self.settings.config_loaded:
            status_text = f"Loaded settings from {self.settings.config_path}"
        else:
            status_text = "No existing config found - using defaults"
        self.status_bar = Gtk.Label(label=status_text)
        self.status_bar.add_css_class("dim-label")
        self.status_bar.set_margin_top(6)
        self.status_bar.set_margin_bottom(6)
        
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Header bar
        header = Adw.HeaderBar()
        
        # Apply button
        apply_btn = Gtk.Button(label="Apply")
        apply_btn.add_css_class("suggested-action")
        apply_btn.connect("clicked", self.on_apply)
        header.pack_end(apply_btn)
        
        # Detect button
        detect_btn = Gtk.Button(label="Detect Monitors")
        detect_btn.connect("clicked", self.on_detect)
        header.pack_start(detect_btn)
        
        # Reset button
        reset_btn = Gtk.Button(label="Reset")
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
        
        # Setup mode info
        info_group = Adw.PreferencesGroup(title="Monitor Setup")
        
        detected_count = len(self.settings.detected_monitors)
        detected_names = [m.get('name', 'Unknown') for m in self.settings.detected_monitors]
        
        info_row = Adw.ActionRow(
            title=f"Detected: {detected_count} monitor(s)",
            subtitle=", ".join(detected_names) if detected_names else "No monitors detected"
        )
        info_group.add(info_row)
        
        # Setup mode selection
        mode_options = [
            ('Single Monitor', 'single'),
            ('Dual Monitor', 'dual'),
        ]
        self.setup_mode_row = DropdownRow(
            "Setup Mode", "Choose your monitor configuration",
            mode_options,
            self.settings.setup_mode,
            self.on_setup_mode_changed
        )
        info_group.add(self.setup_mode_row)
        
        # Scrolling Layout switch for secondary monitor (only visible in dual mode)
        self.scrolling_layout_row = SwitchRow(
            "Secondary Monitor - Scrolling Layout",
            "Enable scrolling layout for workspace 1 on secondary monitor",
            self.settings.global_settings.get('secondary_scrolling_layout', True),
            lambda v: self.on_global_changed('secondary_scrolling_layout', v)
        )
        info_group.add(self.scrolling_layout_row)
        
        # Set initial visibility based on setup mode
        self.scrolling_layout_row.set_visible(self.settings.setup_mode == 'dual')
        """
        # Recommendation note for dual
        if detected_count >= 2:
            rec_row = Adw.ActionRow(
                title="Dual Monitor Recommendation",
                subtitle="Secondary monitor on LEFT (workspace 1), Primary on RIGHT (workspaces 2-10)"
            )
            rec_row.add_css_class("dim-label")
            info_group.add(rec_row)
        """
        content.append(info_group)
        
        # Primary monitor panel
        self.primary_panel = MonitorPanel(
            "Primary Monitor (Right)",
            self.settings.primary_monitor,
            self.settings.detected_monitors,
            lambda k, v: self.on_monitor_changed('primary', k, v),
            is_secondary=False
        )
        content.append(self.primary_panel)
        
        # Secondary monitor panel (for dual setup)
        self.secondary_panel = MonitorPanel(
            "Secondary Monitor (Left - Workspace 1)",
            self.settings.secondary_monitor,
            self.settings.detected_monitors,
            lambda k, v: self.on_monitor_changed('secondary', k, v),
            is_secondary=True
        )
        content.append(self.secondary_panel)
        
        # Update visibility based on setup mode
        self.secondary_panel.set_visible(self.settings.setup_mode == 'dual')
        
        # Global HDR Settings
        global_group = Adw.PreferencesGroup(
            title="Global HDR Settings",
            description="Environment variables and protocol settings"
        )
        
        self.widgets = {}
        
        self.widgets['wine_hdr_enable'] = SwitchRow(
            "Wine HDR Enable", "WINE_HDR_ENABLE environment variable",
            self.settings.global_settings['wine_hdr_enable'],
            lambda v: self.on_global_changed('wine_hdr_enable', v)
        )
        global_group.add(self.widgets['wine_hdr_enable'])
        
        self.widgets['enable_hdr_wsi'] = SwitchRow(
            "Enable HDR WSI", "ENABLE_HDR_WSI environment variable",
            self.settings.global_settings['enable_hdr_wsi'],
            lambda v: self.on_global_changed('enable_hdr_wsi', v)
        )
        global_group.add(self.widgets['enable_hdr_wsi'])
        
        self.widgets['dxvk_hdr'] = SwitchRow(
            "DXVK HDR", "DXVK_HDR environment variable",
            self.settings.global_settings['dxvk_hdr'],
            lambda v: self.on_global_changed('dxvk_hdr', v)
        )
        global_group.add(self.widgets['dxvk_hdr'])
        
        self.widgets['cm_enabled'] = SwitchRow(
            "Color Management Enabled", "Enable color management pipeline (requires restart)",
            self.settings.global_settings['cm_enabled'],
            lambda v: self.on_global_changed('cm_enabled', v)
        )
        global_group.add(self.widgets['cm_enabled'])
        
        self.widgets['xx_color_management_v4'] = SwitchRow(
            "Color Management v4 Protocol", "Enable xx_color_management_v4",
            self.settings.global_settings['xx_color_management_v4'],
            lambda v: self.on_global_changed('xx_color_management_v4', v)
        )
        global_group.add(self.widgets['xx_color_management_v4'])
        
        self.widgets['full_cm_proto'] = SwitchRow(
            "Full CM Protocol", "Claim support for all CM features (requires restart)",
            self.settings.global_settings['full_cm_proto'],
            lambda v: self.on_global_changed('full_cm_proto', v)
        )
        global_group.add(self.widgets['full_cm_proto'])
        
        self.widgets['prefer_hdr'] = DropdownRow(
            "Prefer HDR Mode", "Report HDR as preferred",
            PREFER_HDR_OPTIONS,
            self.settings.global_settings['prefer_hdr'],
            lambda v: self.on_global_changed('prefer_hdr', v)
        )
        global_group.add(self.widgets['prefer_hdr'])
        
        self.widgets['cm_fs_passthrough'] = DropdownRow(
            "Fullscreen Passthrough", "Color passthrough for fullscreen apps",
            CM_FS_PASSTHROUGH_OPTIONS,
            self.settings.global_settings['cm_fs_passthrough'],
            lambda v: self.on_global_changed('cm_fs_passthrough', v)
        )
        global_group.add(self.widgets['cm_fs_passthrough'])
        
        self.widgets['cm_sdr_eotf'] = DropdownRow(
            "Global SDR EOTF", "Default transfer function for SDR apps",
            SDR_EOTF_OPTIONS,
            self.settings.global_settings['cm_sdr_eotf'],
            lambda v: self.on_global_changed('cm_sdr_eotf', v)
        )
        global_group.add(self.widgets['cm_sdr_eotf'])
        
        content.append(global_group)
        
        # Tips section (expandable)
        tips_group = Adw.PreferencesGroup(title="HDR Tips")
        
        tips_expander = Adw.ExpanderRow(title="Steam and Wine HDR Commands")
        tips_expander.set_subtitle("Copy these commands for HDR gaming")
        
        tip1 = Adw.ActionRow(title="Steam (Gamescope)")
        tip1.set_subtitle("DXVK_HDR=1 gamescope -f --hdr-enabled -- %command%")
        tips_expander.add_row(tip1)
        
        tip2 = Adw.ActionRow(title="Steam (Wayland Proton)")
        tip2.set_subtitle("ENABLE_HDR_WSI=1 DXVK_HDR=1 %command%")
        tips_expander.add_row(tip2)
        
        tip3 = Adw.ActionRow(title="Non-Steam Wine")
        tip3.set_subtitle("ENABLE_HDR_WSI=1 DXVK_HDR=1 WINE_HDR_ENABLE=1 wine game.exe")
        tips_expander.add_row(tip3)
        
        tip4 = Adw.ActionRow(title="MPV Video Player")
        tip4.set_subtitle("mpv --vo=gpu-next --target-colorspace-hint --gpu-api=vulkan")
        tips_expander.add_row(tip4)
        
        tip5 = Adw.ActionRow(title="Check Monitor Info")
        tip5.set_subtitle("Run 'wlr-randr' in terminal to see monitor specs")
        tips_expander.add_row(tip5)
        
        tips_group.add(tips_expander)
        content.append(tips_group)
        
        # Advanced setup info
        advanced_group = Adw.PreferencesGroup()
        
        advanced_row = Adw.ActionRow(
            title="3+ Monitors or Advanced Setups",
            subtitle="For complex multi-monitor configurations, see the Hyprland wiki"
        )
        
        wiki_btn = Gtk.Button(label="Open Wiki", valign=Gtk.Align.CENTER)
        wiki_btn.connect("clicked", self.on_open_wiki)
        advanced_row.add_suffix(wiki_btn)
        advanced_group.add(advanced_row)
        
        content.append(advanced_group)
        
        scrolled.set_child(content)
        main_box.append(scrolled)
        
        # Add status bar (created at start of setup_ui)
        main_box.append(self.status_bar)
        
        self.set_content(main_box)
    
    def on_setup_mode_changed(self, mode):
        self.settings.setup_mode = mode
        self.secondary_panel.set_visible(mode == 'dual')
        # Show/hide scrolling layout option based on mode
        self.scrolling_layout_row.set_visible(mode == 'dual')
        self.status_bar.set_text(f"Setup mode: {mode}")
    
    def on_monitor_changed(self, monitor_type, key, value):
        if monitor_type == 'primary':
            self.settings.primary_monitor[key] = value
        else:
            self.settings.secondary_monitor[key] = value
        
        # Only update status bar if it exists (not during initial setup)
        if hasattr(self, 'status_bar') and self.status_bar:
            # Better feedback for scale changes
            if key == 'scale':
                self.status_bar.set_text(f"Changed: {monitor_type} scale = {value:.2f} - Click Apply to save")
            else:
                self.status_bar.set_text(f"Changed: {monitor_type} {key} = {value}")
    
    def on_global_changed(self, key, value):
        self.settings.global_settings[key] = value
        self.status_bar.set_text(f"Changed: {key} = {value}")
    
    def on_detect(self, button):
        self.settings.detect_monitors()
        detected_count = len(self.settings.detected_monitors)
        detected_names = [m.get('name', 'Unknown') for m in self.settings.detected_monitors]
        self.status_bar.set_text(f"Detected {detected_count} monitor(s): {', '.join(detected_names)}")
    
    def on_apply(self, button):
        if self.settings.save_config():
            if self.settings.reload_hyprland():
                self.status_bar.set_text("Saved and applied successfully!")
            else:
                self.status_bar.set_text("Saved (could not reload Hyprland)")
        else:
            self.status_bar.set_text("Error saving configuration!")
    
    def on_reset(self, button):
        self.settings.reset_to_defaults()
        self.primary_panel.refresh()
        self.secondary_panel.refresh()
        # Also reset the scrolling layout switch
        self.scrolling_layout_row.set_active(True)
        self.status_bar.set_text("Reset to defaults - click Apply to save")
    
    def on_open_wiki(self, button):
        """Open Hyprland wiki in browser"""
        try:
            subprocess.run(['xdg-open', 'https://wiki.hyprland.org/Configuring/Monitors/'], check=False)
            self.status_bar.set_text("Opening Hyprland wiki...")
        except Exception as e:
            self.status_bar.set_text("Could not open browser")


class NordixMonitorApp(Adw.Application):
    """Main application"""
    
    def __init__(self):
        super().__init__(
            application_id='com.Nordix.Settings.Monitors',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
    
    def do_activate(self):
        win = NordixMonitorWindow(self)
        win.present()


def main():
    app = NordixMonitorApp()
    return app.run(None)


if __name__ == "__main__":
    main()
