#!/usr/bin/env python3
##=========================================================##
 # SPDX-License-Identifier: GPL-3.0-or-later               #
 # Copyright (c) 2025 Jimmy Källhagen                      #
 # Part of Yggdrasil - Nordix desktop environment          #
##=========================================================##

"""Yggdrasil Environment GUI
A graphical settings panel for Hyprland environment variables
Handles language, GPU selection, gaming options, and compatibility"""

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
# FILE PATH
# =============================================
ENV_CONFIG_PATH = Path.home() / ".config" / "nordix" / "yggdrasil" / "settings" / "Yggdrasil-environment.conf"

# =============================================
# LANGUAGE / LOCALE OPTIONS
# =============================================
LOCALE_OPTIONS = [
    ('en_US.UTF-8', 'English (US)'),
    ('en_GB.UTF-8', 'English (UK)'),
    ('sv_SE.UTF-8', 'Swedish'),
    ('de_DE.UTF-8', 'German'),
    ('fr_FR.UTF-8', 'French'),
    ('es_ES.UTF-8', 'Spanish'),
    ('it_IT.UTF-8', 'Italian'),
    ('pt_BR.UTF-8', 'Portuguese (Brazil)'),
    ('pt_PT.UTF-8', 'Portuguese (Portugal)'),
    ('nl_NL.UTF-8', 'Dutch'),
    ('da_DK.UTF-8', 'Danish'),
    ('nb_NO.UTF-8', 'Norwegian'),
    ('fi_FI.UTF-8', 'Finnish'),
    ('pl_PL.UTF-8', 'Polish'),
    ('cs_CZ.UTF-8', 'Czech'),
    ('hu_HU.UTF-8', 'Hungarian'),
    ('ro_RO.UTF-8', 'Romanian'),
    ('ru_RU.UTF-8', 'Russian'),
    ('uk_UA.UTF-8', 'Ukrainian'),
    ('ja_JP.UTF-8', 'Japanese'),
    ('ko_KR.UTF-8', 'Korean'),
    ('zh_CN.UTF-8', 'Chinese (Simplified)'),
    ('zh_TW.UTF-8', 'Chinese (Traditional)'),
    ('ar_SA.UTF-8', 'Arabic'),
    ('tr_TR.UTF-8', 'Turkish'),
    ('el_GR.UTF-8', 'Greek'),
    ('th_TH.UTF-8', 'Thai'),
    ('vi_VN.UTF-8', 'Vietnamese'),
    ('hi_IN.UTF-8', 'Hindi'),
]


# =============================================
# GPU VENDOR DEFINITIONS
# =============================================
# Each GPU vendor has a set of env vars that can be toggled
# 'active' means uncommented in the config file

GPU_AMD_OPTIONS = {
    'AMD_VULKAN_ICD': {
        'label': 'Vulkan ICD',
        'description': 'Vulkan driver selection',
        'default': 'RADV',
        'choices': ['RADV', 'AMDVLK'],
        'type': 'choice',
    },
    'LIBVA_DRIVER_NAME': {
        'label': 'Video Acceleration',
        'description': 'VA-API driver for hardware video decoding',
        'default': 'radeonsi',
        'choices': ['radeonsi'],
        'type': 'fixed',
    },
    'VDPAU_DRIVER': {
        'label': 'Video Decoding (VDPAU)',
        'description': 'VDPAU driver for video decoding',
        'default': 'radeonsi',
        'choices': ['radeonsi'],
        'type': 'fixed',
    },
}

GPU_NVIDIA_OPTIONS = {
    'LIBVA_DRIVER_NAME': {
        'label': 'Video Acceleration',
        'description': 'VA-API driver for hardware video decoding',
        'default': 'nvidia',
        'choices': ['nvidia'],
        'type': 'fixed',
    },
    'VDPAU_DRIVER': {
        'label': 'Video Decoding (VDPAU)',
        'description': 'VDPAU driver for video decoding',
        'default': 'nvidia',
        'choices': ['nvidia'],
        'type': 'fixed',
    },
    'GBM_BACKEND': {
        'label': 'GBM Backend',
        'description': 'Force GBM as backend for NVIDIA',
        'default': 'nvidia-drm',
        'choices': ['nvidia-drm'],
        'type': 'toggle',
    },
    '__GLX_VENDOR_LIBRARY_NAME': {
        'label': 'GLX Vendor Library',
        'description': 'Force NVIDIA GLX vendor library',
        'default': 'nvidia',
        'choices': ['nvidia'],
        'type': 'toggle',
    },
    '__GL_GSYNC_ALLOWED': {
        'label': 'G-Sync',
        'description': 'Allow G-Sync on compatible monitors',
        'default': '1',
        'choices': ['0', '1'],
        'type': 'toggle',
    },
    '__GL_VRR_ALLOWED': {
        'label': 'Variable Refresh Rate',
        'description': 'Adaptive sync (may cause issues in some games)',
        'default': '0',
        'choices': ['0', '1'],
        'type': 'toggle',
    },
    '__GL_THREADED_OPTIMIZATIONS': {
        'label': 'Threaded Optimizations',
        'description': 'NVIDIA threaded rendering optimizations',
        'default': '1',
        'choices': ['0', '1'],
        'type': 'toggle',
    },
    '__GL_SYNC_DISPLAY_DEVICE': {
        'label': 'Sync Display Device',
        'description': 'Display for sync (e.g. DP-1, HDMI-A-1). Helps with multi-monitor tearing',
        'default': '',
        'choices': [],
        'type': 'text',
    },
}

GPU_INTEL_OPTIONS = {
    'LIBVA_DRIVER_NAME': {
        'label': 'Video Acceleration',
        'description': 'VA-API driver for hardware video decoding',
        'default': 'intel',
        'choices': ['intel', 'iHD'],
        'type': 'choice',
    },
    'VDPAU_DRIVER': {
        'label': 'Video Decoding (VDPAU)',
        'description': 'VDPAU driver for video decoding',
        'default': 'intel',
        'choices': ['intel'],
        'type': 'fixed',
    },
}

GPU_VENDORS = {
    'amd': {'label': 'AMD', 'options': GPU_AMD_OPTIONS},
    'nvidia': {'label': 'NVIDIA', 'options': GPU_NVIDIA_OPTIONS},
    'intel': {'label': 'Intel', 'options': GPU_INTEL_OPTIONS},
}


# =============================================
# GAMING OPTIONS
# =============================================
GAMING_OPTIONS = {
    'SDL_VIDEODRIVER': {
        'label': 'SDL Video Driver',
        'description': 'Video driver for SDL games. Wayland recommended, X11 for older games',
        'default': 'wayland',
        'choices': ['wayland', 'x11'],
        'type': 'choice',
    },
}


# =============================================
# WEBKIT COMPATIBILITY
# =============================================
WEBKIT_OPTIONS = {
    'WEBKIT_DISABLE_COMPOSITING_MODE': {
        'label': 'Disable Compositing Mode',
        'description': 'Fix for apps with rendering issues (WebKit-based apps)',
        'default': '1',
        'type': 'toggle',
        'active_default': False,
    },
    'WEBKIT_DISABLE_DMABUF_RENDERER': {
        'label': 'Disable DMA-BUF Renderer',
        'description': 'Fix for apps with DMA-BUF rendering problems',
        'default': '1',
        'type': 'toggle',
        'active_default': False,
    },
    'WEBKIT_FORCE_COMPOSITING_MODE': {
        'label': 'Force Compositing Mode',
        'description': 'Full GPU acceleration (AMD/Intel recommended, NVIDIA may vary)',
        'default': '1',
        'type': 'toggle',
        'active_default': False,
    },
}


# =============================================
# ENVIRONMENT SETTINGS HANDLER
# =============================================
class EnvironmentSettings:
    """Handles reading and writing of environment.conf"""

    def __init__(self):
        self.config_path = ENV_CONFIG_PATH

        # Current values
        self.locale = 'en_US.UTF-8'
        self.language = 'en_US'
        self.active_gpu = None  # 'amd', 'nvidia', 'intel', or None
        self.gpu_values = {}    # env_var -> value for active GPU options
        self.gpu_active = {}    # env_var -> bool (is uncommented)
        self.gaming_values = {} # env_var -> value
        self.webkit_active = {} # env_var -> bool
        self.raw_lines = []     # Preserve full file for faithful rewriting

        # Ensure config exists before loading
        self._ensure_config_exists()
        self.load()

    def _ensure_config_exists(self):
        """Ensure config directory and file exist - fail-safe initialization"""
        try:
            # Create parent directories if they don't exist
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # If config file doesn't exist, create it with defaults
            if not self.config_path.exists():
                print(f"Config not found: {self.config_path}")
                print("Creating config directory and file with default settings...")
                self._create_failsafe()
                self._write_default_config()
                print(f"Created: {self.config_path}")
        except PermissionError as e:
            print(f"Permission denied creating config: {e}")
            print("Will use default settings in memory.")
            self._create_failsafe()
        except Exception as e:
            print(f"Error ensuring config exists: {e}")
            print("Will use default settings in memory.")
            self._create_failsafe()

    def _write_default_config(self):
        """Write default configuration to file"""
        try:
            config_content = self._generate_config()
            self.config_path.write_text(config_content)
            return True
        except Exception as e:
            print(f"Error writing default config: {e}")
            return False

    def load(self):
        """Load current environment.conf with fail-safe handling"""
        if not self.config_path.exists():
            print(f"Config file not found, using defaults: {self.config_path}")
            self._create_failsafe()
            return

        try:
            content = self.config_path.read_text()
            self.raw_lines = content.split('\n')
            self._parse_content(content)
            print(f"Config loaded successfully: {self.config_path}")
        except PermissionError as e:
            print(f"Permission denied reading config: {e}")
            print("Using default settings.")
            self._create_failsafe()
        except Exception as e:
            print(f"Error loading environment.conf: {e}")
            print("Using default settings.")
            self._create_failsafe()

    def _parse_content(self, content):
        """Parse the environment config file"""
        # Detect active GPU vendor
        self.active_gpu = None
        self.gpu_values = {}
        self.gpu_active = {}
        self.gaming_values = {}
        self.webkit_active = {}

        for line in content.split('\n'):
            stripped = line.strip()

            # Parse both active and commented env lines
            is_commented = False
            parse_line = stripped

            if parse_line.startswith('# '):
                is_commented = True
                # Remove leading # and whitespace
                parse_line = parse_line.lstrip('# ').strip()

            # Match env = KEY,VALUE pattern
            match = re.match(r'^env\s*=\s*(\S+?)\s*,\s*(.+)$', parse_line)
            if not match:
                continue

            key = match.group(1).strip()
            value = match.group(2).strip()

            # Remove inline comments from value
            if '# ' in value:
                value = value.split('# ')[0].strip()

            # Language
            if key == 'LANG' and not is_commented:
                self.locale = value
            elif key == 'LANGUAGE' and not is_commented:
                self.language = value

            # Detect GPU vendor from active (uncommented) lines
            if not is_commented:
                if key == 'AMD_VULKAN_ICD':
                    self.active_gpu = 'amd'
                elif key in ('GBM_BACKEND', '__GLX_VENDOR_LIBRARY_NAME',
                             '__GL_GSYNC_ALLOWED', '__GL_THREADED_OPTIMIZATIONS',
                             '__GL_SYNC_DISPLAY_DEVICE'):
                    self.active_gpu = 'nvidia'
                elif key == 'LIBVA_DRIVER_NAME':
                    if value == 'radeonsi':
                        self.active_gpu = 'amd'
                    elif value == 'nvidia':
                        self.active_gpu = 'nvidia'
                    elif value in ('intel', 'iHD'):
                        self.active_gpu = 'intel'

            # Store GPU-related values
            all_gpu_keys = set()
            for vendor_data in GPU_VENDORS.values():
                all_gpu_keys.update(vendor_data['options'].keys())

            if key in all_gpu_keys:
                self.gpu_values[key] = value
                self.gpu_active[key] = not is_commented

            # Gaming
            if key in GAMING_OPTIONS:
                self.gaming_values[key] = value

            # Webkit
            if key in WEBKIT_OPTIONS:
                self.webkit_active[key] = not is_commented

        # Set defaults for gaming options not found
        for key, opt in GAMING_OPTIONS.items():
            if key not in self.gaming_values:
                self.gaming_values[key] = opt['default']

        # Set defaults for webkit options not found
        for key, opt in WEBKIT_OPTIONS.items():
            if key not in self.webkit_active:
                self.webkit_active[key] = opt.get('active_default', False)

    def save(self):
        """Save configuration back to file with fail-safe handling"""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Backup existing config
            if self.config_path.exists():
                backup = self.config_path.with_suffix('.conf.backup')
                try:
                    shutil.copy2(self.config_path, backup)
                except Exception as e:
                    print(f"Warning: Could not create backup: {e}")

            config_text = self._generate_config()
            self.config_path.write_text(config_text)
            return True

        except PermissionError as e:
            print(f"Permission denied saving config: {e}")
            return False
        except Exception as e:
            print(f"Error saving environment.conf: {e}")
            return False

    def _generate_config(self):
        """Generate the full environment.conf"""
        lang_short = self.locale.split('.')[0] if '.' in self.locale else self.locale

        # Helper to format env line (commented or not)
        def env(key, value, active=True, comment=''):
            prefix = '  env' if active else '# env'
            c = f'  {comment}' if comment else ''
            return f'{prefix} = {key},{value}{c}'

        # GPU states
        is_nvidia = self.active_gpu == 'nvidia'
        is_amd = self.active_gpu == 'amd'
        is_intel = self.active_gpu == 'intel'

        # GPU values with defaults
        sdl_val = self.gaming_values.get('SDL_VIDEODRIVER', 'wayland')
        nv_sync = self.gpu_values.get('__GL_SYNC_DISPLAY_DEVICE', '')
        nv_gsync = self.gpu_values.get('__GL_GSYNC_ALLOWED', '1')
        nv_threaded = self.gpu_values.get('__GL_THREADED_OPTIMIZATIONS', '1')
        nv_vrr = self.gpu_values.get('__GL_VRR_ALLOWED', '0')
        amd_icd = self.gpu_values.get('AMD_VULKAN_ICD', 'RADV')
        intel_libva = self.gpu_values.get('LIBVA_DRIVER_NAME', 'intel') if is_intel else 'intel'

        # Webkit states
        wk_comp = self.webkit_active.get('WEBKIT_DISABLE_COMPOSITING_MODE', False)
        wk_dma = self.webkit_active.get('WEBKIT_DISABLE_DMABUF_RENDERER', False)
        wk_force = self.webkit_active.get('WEBKIT_FORCE_COMPOSITING_MODE', False)

        # NVIDIA active helpers
        def nv_active(key):
            return is_nvidia and self.gpu_active.get(key, False)

        config = f'''
##=========================================================##
 # SPDX-License-Identifier: GPL-3.0-or-later               #
 # Copyright (c) 2025 Jimmy Källhagen                      #
 # Part of Yggdrasil - Nordix desktop environment          #
##=========================================================##
source = ~/.config/nordix/yggdrasil/settings/Yggdrasil-defaults.conf

##=============================================##
 #            Yggdrasil -  Environment         #
##=============================================##
 # * Generated by Nordix Environment GUI       #
##=============================================###


##==================================================##
 #                   LANGUAGE                       #
##==================================================##
#
##=========================##
{env('LANG', self.locale)}
{env('LC_ALL', self.locale)}
{env('LANGUAGE', lang_short)}
##========================##
#
#

##==================================================##
 #                  Icon - Theme                    #
##==================================================##
#
##=================================##
{env('ICON_THEME', 'Cosmic')}
{env('QT_ICON_THEME_FALLBACK', 'Pop')}
##=================================##
#
#

##==================================================##
 #                QT & GTK - Theme                  #
##==================================================##
#
##===========================================##
# {env('GTK_THEME', 'adw-gtk3-dark')}
{env('QT_QPA_PLATFORMTHEME', 'hyprqt6engine')}
##===========================================##
#
#

##==================================================##
 #       Disable QT - Window Decorations            #
##==================================================##
#
##===========================================##
{env('QT_WAYLAND_DISABLE_WINDOWDECORATION', '1')}
##===========================================##
#
#

##==================================================##
 #              DESKTOP COMPATIBILITY               #
##==================================================##
##
##====================================##
{env('XDG_CURRENT_DESKTOP', 'Hyprland')}
{env('XDG_SESSION_TYPE', 'wayland')}
{env('XDG_SESSION_DESKTOP', 'Hyprland')}
{env('QT_AUTO_SCREEN_SCALE_FACTOR', '1')}
{env('QT_QPA_PLATFORM', 'wayland;xcb')}
{env('GDK_SCALE', '1')}
{env('QT_SCALE_FACTOR', '1')}
{env('BEMENU_BACKEND', 'wayland')}
##====================================##
#
#

##==================================================##
 #              STANDARD APPLICATIONS               #
##==================================================##
#
##===========================================##
  env = BROWSER,$system_browser
  env = EDITOR,$system_editor
  env = VISUAL,$system_visual_editor
  env = TERMINAL,$system_filebrowser
  env = FILE_MANAGER,$system_filebrowser
  env = PAGER,less
  env = IMAGEVIEWER,$system_image_viewer
  env = CALCULATOR,$system_calculator
  env = PDFVIEWER,$system_pdf_viewer
  env = DSV_PDFVIEWER,$system_pdf_viewer
##===========================================##
#
#

##==================================================##
 #                CURSOR SETTINGS                   #
##==================================================##
#
##===================================##
  env = XCURSOR_THEME,$system_cursor
  env = XCURSOR_SIZE,$cursor_size
  env = QT_CURSOR_SIZE,$cursor_size
  env = HYPRCURSOR_SIZE,$cursor_size
##===================================##
#
#

##==================================================##
 #        WEB BROWSER, OZON & ELECTRON APPS         #
##==================================================##
#
##========================================##
{env('ELECTRON_OZONE_PLATFORM_HINT', 'auto')}
{env('NIXOS_OZONE_WL', '1')}
##========================================##
#
#

##=================================================##
# set only if you have problems with specific apps #
##=================================================##
#
##=======================================##
{env('WEBKIT_DISABLE_COMPOSITING_MODE', '1', active=wk_comp)}
{env('WEBKIT_DISABLE_DMABUF_RENDERER', '1', active=wk_dma)}
##=======================================##

##=================================================##
#  AMD/Intel: FULL GPU-acceleration,
#  For NVIDA - hit and miss
##=================================================##
#
##=====================================##
{env('WEBKIT_FORCE_COMPOSITING_MODE', '1', active=wk_force)}
##=====================================##
#

##=====================================##
# Only affects Firefox, not other apps  #
##=====================================##
{env('MOZ_ENABLE_WAYLAND', '1')}
{env('MOZ_GTK_TITLEBAR_DECORATION', '0')}
##=====================================##

##==================================================##
 #                SDL VIDEODRIVERS                  #
##==================================================##

# Hardcoding SDL_VIDEODRIVER can prevent some programs
# and old SDL games from starting.
# Therefore, it's recommended to set this per app instead of globally.
#
#  * I've tested SDL_VIDEODRIVER=wayland globally for months \\
#    on Nordix-Desktop (pure Wayland) without any issues.
#
#  * Some older games might expect X11. If you encounter problems: \\
#    Set SDL_VIDEODRIVER=x11 per app (Steam/Heroic/Lutris) \\
#    or create a wrapper script for that specific game.
#
#  * But for 99.9% of Wayland-native usage? \\
#    This just works.
#
##==================================##
{env('SDL_VIDEODRIVER', sdl_val)}
##==================================##

##==================================================##
 #                   GDK BACKEND                    #
##==================================================##

## this can prevent programs from starting
## (e.g. chromium and electron apps).
## Therefore, it's recommended to set this per app instead of globally.
##
## Nordix set these on Wayland as default, read the comment below
#
##==================================##
{env('GTK_USE_PORTAL', '1')}
{env('GDK_BACKEND', 'wayland,x11,*')}
##==================================##

##==================================================##
 #                    Clutter                       #
##==================================================##

# Clutter is an older graphics toolkit for animated UIs.
# Some older GNOME apps (Cheese, GNOME Videos) use it.
#
# CLUTTER_BACKEND=wayland forces these apps to use Wayland
# instead of falling back to X11.
#
#   * This is generally safe
#   * But if an ancient Clutter app refuses to start, you know why:
#
#     - Remove or comment out this line
#     - Or set per app if needed
#
#  * In modern GNOME (Mutter), this is ignored
#  * In daily driving Nordix, no problems
#
##==================================##
{env('CLUTTER_BACKEND', 'wayland')}
##==================================##
#
#

##==================================================##
 #             Hyprland Environment                 #
##==================================================##
#
#  --Debug
##=======================================================================##
 #env = HYPRLAND_TRACE=1          # Enables more verbose logging
 #env = HYPRLAND_NO_RT=1          # Disables realtime priority
 #env = HYPRLAND_NO_SD_NOTIFY=1   # if systemd, disables the sd_notify calls
 #env = HYPRLAND_NO_SD_VARS=1     # Disables management of variables in systemd and dbus activation environments.
##=======================================================================##
#

##==================================================##
 #             Aquamarine Environment               #
##==================================================##
#
#  --Debug  & NVIDIA Fix
##=======================================================================##
 #env = AQ_TRACE=1              # Enables more verbose logging
 #env = AQ_FORCE_LINEAR_BLIT=0  # potentially workaround Nvidia issues.
 #env = AQ_MGPU_NO_EXPLICIT=1   # Disables explicit syncing on mgpu buffers.
 #env = AQ_NO_MODIFIERS=1       # Disables modifiers for DRM buffers.
##=======================================================================##

#
#
##==================================================##
 #             DEVELOPER & DEBUGGING                #
##==================================================##
#
##=======================================================================##
 # env = HYPRLAND_LOG_WLR,1                  # WLR logging
 # env = HYPRLAND_LOG_DAMAGE,1               # Damage tracking logs
 # env = QT_LOGGING_RULES,*.debug=false      # QT logging control
 #
 # env = DEBUG,*                             # Activatea debug logging
 # env = MESA_DEBUG,1                        # GPU debugging
 # env = RUST_BACKTRACE,full                 # Full Rust backtrace logging
 # env = RUST_BACKTRACE,1                    # Rust backtrace logging
##=======================================================================##

#
#
##==================================================##
 #                JAVA Environment                   #
##==================================================##
#
##=======================================================================##
{env('_JAVA_AWT_WM_NONREPARENTING', '1')}
{env('NO_AT_BRIDGE', '1')}
{env('_JAVA_OPTIONS', '"-Dawt.useSystemAAFontSettings=on -Dswing.aatext=true -Dswing.defaultlaf=com.sun.java.swing.plaf.gtk.GTKLookAndFeel -Dswing.crossplatformlaf=com.sun.java.swing.plaf.gtk.GTKLookAndFeel"')}
{env('JAVA_FONTS', '/usr/share/fonts/TTF')}
##=======================================================================##

##==================================================##
 #                 ELEMENTARY                       #
##==================================================##
#
##==================================##
{env('ECORE_EVAS_ENGINE', 'wayland-egl')}
{env('ELM_ENGINE', 'wayland_egl')}
{env('ELM_DISPLAY', 'wl')}
{env('ELM_ACCEL', 'gl')}
##==================================##
#


##==================================================##
 #                NVIDIA SPECIFIC                    #
##==================================================##
#
# Only applies if you have NVIDIA GPU
# Helps with screen tearing on multi-monitor setups
#
#   * Find your display name with: xrandr
#   * Replace with your port
#
#   * HDMI-A-1, HDMI-A-2, HDMI-A-3
#   * DP-1, DP-2, DP-3
#
##====================================##
{env('__GL_SYNC_DISPLAY_DEVICE', nv_sync if nv_sync else 'DP-3', active=nv_active('__GL_SYNC_DISPLAY_DEVICE'))}
##====================================##

##==================================================##
 #    Controls if G-Sync capable monitors should    #
 #    use Variable Refresh Rate (VRR)               #
##==================================================##
{env('__GL_GSYNC_ALLOWED', nv_gsync, active=nv_active('__GL_GSYNC_ALLOWED'))}
##====================================##

#
##===================================================================##
# To force GBM as a backend, set the following environment variables:
##===================================================================##
{env('GBM_BACKEND', 'nvidia-drm', active=nv_active('GBM_BACKEND'))}
{env('__GLX_VENDOR_LIBRARY_NAME', 'nvidia', active=nv_active('__GLX_VENDOR_LIBRARY_NAME'))}
##===================================================================##

#
##======================================##
#  Hardware acceleration on NVIDIA GPUs #
##======================================##
{env('LIBVA_DRIVER_NAME', 'nvidia', active=is_nvidia)}
##======================================##

#
##======================================##
#          NVIDIA performance           #
##======================================##
{env('__GL_THREADED_OPTIMIZATIONS', nv_threaded, active=nv_active('__GL_THREADED_OPTIMIZATIONS'))}
##======================================##

#
##======================================##
#         NVIDIA video decoding         #
##======================================##
{env('VDPAU_DRIVER', 'nvidia', active=is_nvidia)}
##======================================##
#

##===================================================================##
 # Controls if Adaptive Sync should be used.                         #
 # Recommended to set as "0" to avoid having problems on some games. #
##===================================================================##
{env('__GL_VRR_ALLOWED', nv_vrr, active=nv_active('__GL_VRR_ALLOWED'))}
##======================================##

#
##==========================================================##
 # use legacy DRM interface instead of atomic mode setting. #
 # NOT recommended.                                         #
##==========================================================##
  # env = AQ_NO_ATOMIC,1
##======================##

#
#
##==================================================##
 #                  AMD SPECIFIC                    #
##==================================================##
#
##==================================================##
{env('AMD_VULKAN_ICD', amd_icd, active=is_amd)}
{env('LIBVA_DRIVER_NAME', 'radeonsi', active=is_amd, comment='# AMD Video acceleration')}
{env('VDPAU_DRIVER', 'radeonsi', active=is_amd, comment='# AMD video decoding')}
##==================================================================##
#
#   * "minimizes video decoding latency but results
#      in higher GPU power consumption.
#      Not enabled by default due to increased power usage." *
#
#   * Some says it unlock more performance - for me, it unlocks login crash. 
#   * Do you dare to try?
#
##=============================##
#  env = AMD_DEBUG=lowlatencydec   #  <-- Try
##=============================##
#
#

##======================================##
#             INTEL - GPU               #
##======================================##
#
##===========================================================##
{env('LIBVA_DRIVER_NAME', intel_libva, active=is_intel, comment='# Intel Video acceleration')}
{env('VDPAU_DRIVER', 'intel', active=is_intel, comment='# Intel video decoding')}
##===========================================================##
#
#

##======================================##
#               GPU MISC                #
##======================================##
#
##==================================================##
env = AQ_DRM_DEVICES,/dev/dri/card1:/dev/dri/card0
{env('WLR_DRM_NO_ATOMIC', '0')}
{env('WLR_RENDERER_ALLOW_SOFTWARE', '1')}
##===================================================##
#

##======================================##
#             OLD GPU SUPPORT           #
##======================================##

#
##===================================================##
# env = WLR_DRM_NO_MODIFIERS,1
# env = WLR_NO_HARDWARE_CURSORS,1     Software cursors (fix for some GPUs)
##===================================================##
'''
        return config

    def _create_failsafe(self):
        """Create a failsafe environment.conf with sensible defaults (no theme/icon)"""
        self.locale = 'en_US.UTF-8'
        self.language = 'en_US'
        self.active_gpu = None
        self.gpu_values = {}
        self.gpu_active = {}
        self.gaming_values = {'SDL_VIDEODRIVER': 'wayland'}
        self.webkit_active = {
            'WEBKIT_DISABLE_COMPOSITING_MODE': False,
            'WEBKIT_DISABLE_DMABUF_RENDERER': False,
            'WEBKIT_FORCE_COMPOSITING_MODE': False,
        }

    def reload_hyprland(self):
        """Reload Hyprland configuration"""
        try:
            subprocess.run(['hyprctl', 'reload'], check=True)
            return True
        except Exception:
            return False


# =============================================
# CUSTOM WIDGETS
# =============================================
class DropdownRow(Adw.ActionRow):
    """A row with a dropdown selector"""

    def __init__(self, title, subtitle, options, current_value, callback):
        """Args:
            options: list of (value, display_name) tuples
            current_value: the currently selected value
            callback: called with new value"""
        super().__init__()
        self.set_title(title)
        self.set_subtitle(subtitle)

        self.callback = callback
        self.values = [v for v, _ in options]
        self.names = [n for _, n in options]

        string_list = Gtk.StringList()
        current_index = 0
        for i, (value, name) in enumerate(options):
            string_list.append(name)
            if value == current_value:
                current_index = i

        self.dropdown = Gtk.DropDown(model=string_list)
        self.dropdown.set_selected(current_index)
        self.dropdown.set_valign(Gtk.Align.CENTER)
        self.dropdown.connect('notify::selected', self._on_selected)

        self.add_suffix(self.dropdown)

    def _on_selected(self, dropdown, _):
        selected = dropdown.get_selected()
        if selected < len(self.values):
            self.callback(self.values[selected])

    def set_value(self, value):
        if value in self.values:
            self.dropdown.set_selected(self.values.index(value))


class ToggleRow(Adw.ActionRow):
    """A row with a switch for boolean toggles"""

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


class TextEntryRow(Adw.ActionRow):
    """A row with a text entry field"""

    def __init__(self, title, subtitle, current_value, callback):
        super().__init__()
        self.set_title(title)
        self.set_subtitle(subtitle)

        self.callback = callback

        self.entry = Gtk.Entry(valign=Gtk.Align.CENTER)
        self.entry.set_text(current_value or '')
        self.entry.set_placeholder_text('e.g. DP-1, HDMI-A-1')
        self.entry.set_width_chars(16)
        self.entry.connect('changed', self._on_changed)

        self.add_suffix(self.entry)

    def _on_changed(self, entry):
        self.callback(entry.get_text())

    def set_text(self, text):
        self.entry.set_text(text or '')


# =============================================
# MAIN WINDOW
# =============================================
class NordixEnvironmentWindow(Adw.ApplicationWindow):
    """Main window for environment settings"""

    def __init__(self, app):
        super().__init__(application=app, title="Yggdrasil Environment")
        self.set_default_size(600, 850)

        # Initialize settings with fail-safe handling
        try:
            self.settings = EnvironmentSettings()
        except Exception as e:
            print(f"Critical error initializing settings: {e}")
            print("Starting with default settings...")
            self.settings = EnvironmentSettings.__new__(EnvironmentSettings)
            self.settings.config_path = ENV_CONFIG_PATH
            self.settings._create_failsafe()

        self.widgets = {}
        self.gpu_options_box = {}  # vendor -> Gtk.Box for GPU options
        self.gpu_buttons = {}     # vendor -> Gtk.ToggleButton

        self.setup_ui()

    def setup_ui(self):
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
            title="Language & Locale",
            description="System language settings"
        )

        self.widgets['locale'] = DropdownRow(
            "System Language",
            "Language for the desktop environment",
            LOCALE_OPTIONS,
            self.settings.locale,
            self.on_locale_changed
        )
        lang_group.add(self.widgets['locale'])

        content.append(lang_group)

        # =========================================
        # GPU SELECTION SECTION
        # =========================================
        gpu_group = Adw.PreferencesGroup(
            title="GPU Configuration",
            description="Select your GPU vendor — only one can be active at a time"
        )

        # GPU toggle buttons row
        gpu_button_row = Adw.ActionRow(
            title="GPU Vendor",
            subtitle="Deselect current GPU before selecting a new one"
        )

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.set_valign(Gtk.Align.CENTER)

        for vendor_key, vendor_data in GPU_VENDORS.items():
            btn = Gtk.ToggleButton(label=vendor_data['label'])
            btn.set_active(self.settings.active_gpu == vendor_key)
            btn.connect('toggled', self._on_gpu_toggled, vendor_key)
            self.gpu_buttons[vendor_key] = btn
            button_box.append(btn)

        gpu_button_row.add_suffix(button_box)
        gpu_group.add(gpu_button_row)

        content.append(gpu_group)

        # =========================================
        # GPU OPTIONS SECTIONS (one per vendor)
        # =========================================
        for vendor_key, vendor_data in GPU_VENDORS.items():
            options_group = Adw.PreferencesGroup(
                title=f"{vendor_data['label']} Options",
                description=f"Configuration for {vendor_data['label']} GPUs"
            )

            for opt_key, opt_data in vendor_data['options'].items():
                widget_key = f"gpu_{vendor_key}_{opt_key}"
                current_val = self.settings.gpu_values.get(opt_key, opt_data['default'])
                is_active = self.settings.gpu_active.get(opt_key, False)

                if opt_data['type'] == 'choice':
                    choices = [(c, c) for c in opt_data['choices']]
                    self.widgets[widget_key] = DropdownRow(
                        opt_data['label'],
                        opt_data['description'],
                        choices,
                        current_val,
                        lambda v, k=opt_key: self._on_gpu_option_changed(k, v)
                    )
                elif opt_data['type'] == 'toggle':
                    self.widgets[widget_key] = ToggleRow(
                        opt_data['label'],
                        opt_data['description'],
                        is_active and self.settings.active_gpu == vendor_key,
                        lambda v, k=opt_key: self._on_gpu_toggle_changed(k, v)
                    )
                elif opt_data['type'] == 'text':
                    self.widgets[widget_key] = TextEntryRow(
                        opt_data['label'],
                        opt_data['description'],
                        current_val if is_active else '',
                        lambda v, k=opt_key: self._on_gpu_option_changed(k, v)
                    )
                elif opt_data['type'] == 'fixed':
                    # Show as info row, not editable
                    row = Adw.ActionRow(
                        title=opt_data['label'],
                        subtitle=opt_data['description']
                    )
                    label = Gtk.Label(label=opt_data['default'])
                    label.add_css_class("dim-label")
                    label.set_valign(Gtk.Align.CENTER)
                    row.add_suffix(label)
                    self.widgets[widget_key] = row

                options_group.add(self.widgets[widget_key])

            self.gpu_options_box[vendor_key] = options_group
            content.append(options_group)

            # Show/hide based on current GPU
            options_group.set_visible(self.settings.active_gpu == vendor_key)

        # =========================================
        # GAMING SECTION
        # =========================================
        gaming_group = Adw.PreferencesGroup(
            title="Gaming",
            description="Options that affect game compatibility"
        )

        sdl_choices = [('wayland', 'Wayland (recommended)'), ('x11', 'X11 (compatibility)')]
        self.widgets['sdl'] = DropdownRow(
            "SDL Video Driver",
            "Video driver for SDL games. Use X11 if older games have issues",
            sdl_choices,
            self.settings.gaming_values.get('SDL_VIDEODRIVER', 'wayland'),
            lambda v: self._on_gaming_changed('SDL_VIDEODRIVER', v)
        )
        gaming_group.add(self.widgets['sdl'])

        content.append(gaming_group)

        # =========================================
        # WEBKIT COMPATIBILITY SECTION
        # =========================================
        webkit_group = Adw.PreferencesGroup(
            title="WebKit Compatibility",
            description="Fixes for WebKit-based applications (enable only if needed)"
        )

        for key, opt in WEBKIT_OPTIONS.items():
            widget_key = f"webkit_{key}"
            self.widgets[widget_key] = ToggleRow(
                opt['label'],
                opt['description'],
                self.settings.webkit_active.get(key, False),
                lambda v, k=key: self._on_webkit_changed(k, v)
            )
            webkit_group.add(self.widgets[widget_key])

        content.append(webkit_group)

        # =========================================
        # DEBUG INFO SECTION
        # =========================================
        debug_group = Adw.PreferencesGroup(
            title="Advanced and Debug Options",
            description="For Advance Options and For Hyprland, Aquamarine, Mesa, and Rust debugging — edit the config file directly"
        )

        config_path_row = Adw.ActionRow()
        config_path_row.set_title("Open Config File")
        config_path_row.set_subtitle(str(ENV_CONFIG_PATH))
        
        open_btn = Gtk.Button(label="Open")
        open_btn.set_valign(Gtk.Align.CENTER)
        open_btn.connect("clicked", self._on_open_config)
        config_path_row.add_suffix(open_btn)
        config_path_row.set_activatable(False)
        debug_group.add(config_path_row)

        content.append(debug_group)

        scrolled.set_child(content)
        main_box.append(scrolled)

        # Status bar
        self.status_bar = Gtk.Label(label="Ready")
        self.status_bar.add_css_class("dim-label")
        self.status_bar.set_margin_top(6)
        self.status_bar.set_margin_bottom(6)
        main_box.append(self.status_bar)

        self.set_content(main_box)

    # ---- GPU TOGGLE LOGIC ----
    def _on_gpu_toggled(self, button, vendor_key):
        """Handle GPU vendor toggle with mutual exclusion"""
        if button.get_active():
            # Check if another GPU is already active
            if self.settings.active_gpu is not None and self.settings.active_gpu != vendor_key:
                # Block activation — must deselect current first
                button.set_active(False)
                current_label = GPU_VENDORS[self.settings.active_gpu]['label']
                self.status_bar.set_text(
                    f"Deselect {current_label} before selecting {GPU_VENDORS[vendor_key]['label']}"
                )
                return

            # Activate this vendor
            self.settings.active_gpu = vendor_key
            self.gpu_options_box[vendor_key].set_visible(True)
            self.status_bar.set_text(f"GPU: {GPU_VENDORS[vendor_key]['label']} selected")

            # Set default active states for this vendor's toggle options
            for opt_key, opt_data in GPU_VENDORS[vendor_key]['options'].items():
                if opt_data['type'] in ('fixed', 'choice'):
                    self.settings.gpu_active[opt_key] = True
                    if opt_key not in self.settings.gpu_values:
                        self.settings.gpu_values[opt_key] = opt_data['default']

        else:
            # Deactivate this vendor
            if self.settings.active_gpu == vendor_key:
                self.settings.active_gpu = None
                self.gpu_options_box[vendor_key].set_visible(False)

                # Deactivate all GPU options for this vendor
                for opt_key in GPU_VENDORS[vendor_key]['options']:
                    self.settings.gpu_active[opt_key] = False

                self.status_bar.set_text(f"GPU: {GPU_VENDORS[vendor_key]['label']} deselected")

    def _on_gpu_option_changed(self, key, value):
        """Handle GPU option value change"""
        self.settings.gpu_values[key] = value
        self.settings.gpu_active[key] = True
        self.status_bar.set_text(f"Changed: {key} = {value}")

    def _on_gpu_toggle_changed(self, key, active):
        """Handle GPU toggle option change"""
        self.settings.gpu_active[key] = active
        self.status_bar.set_text(f"{'Enabled' if active else 'Disabled'}: {key}")

    # OTHER CALLBACKS
    def on_locale_changed(self, locale):
        self.settings.locale = locale
        self.settings.language = locale.split('.')[0] if '.' in locale else locale
        self.status_bar.set_text(f"Language: {locale}")

    def _on_gaming_changed(self, key, value):
        self.settings.gaming_values[key] = value
        self.status_bar.set_text(f"Changed: {key} = {value}")

    def _on_webkit_changed(self, key, active):
        self.settings.webkit_active[key] = active
        self.status_bar.set_text(f"{'Enabled' if active else 'Disabled'}: {key}")

    def _on_open_config(self, button):
        """Open config file in default text editor"""
        try:
            # Try xdg-open first (works on most Linux desktops)
            subprocess.Popen(['xdg-open', str(ENV_CONFIG_PATH)])
            self.status_bar.set_text(f"Opening config file...")
        except Exception as e:
            # Fallback: try common editors
            for editor in ['gedit', 'kate', 'xed', 'pluma', 'mousepad', 'nano', 'vim']:
                try:
                    subprocess.Popen([editor, str(ENV_CONFIG_PATH)])
                    self.status_bar.set_text(f"Opening config in {editor}...")
                    return
                except FileNotFoundError:
                    continue
            self.status_bar.set_text(f"Could not open config file: {e}")

    def on_apply(self, button):
        """Save and apply"""
        if self.settings.save():
            if self.settings.reload_hyprland():
                self.status_bar.set_text("✓ Saved and applied successfully!")
            else:
                self.status_bar.set_text("✓ Saved (could not reload Hyprland)")
        else:
            self.status_bar.set_text("✗ Error saving configuration!")

    def on_reset(self, button):
        """Reset to defaults"""
        self.settings._create_failsafe()

        # Reset GPU buttons
        for vendor_key, btn in self.gpu_buttons.items():
            btn.set_active(False)
            self.gpu_options_box[vendor_key].set_visible(False)

        # Reset locale
        self.widgets['locale'].set_value('en_US.UTF-8')

        # Reset SDL
        self.widgets['sdl'].set_value('wayland')

        # Reset webkit
        for key in WEBKIT_OPTIONS:
            widget_key = f"webkit_{key}"
            if widget_key in self.widgets:
                self.widgets[widget_key].set_active(False)

        self.status_bar.set_text("Reset to defaults — click Apply to save")


# =============================================
# APPLICATION
# =============================================
class NordixEnvironmentApp(Adw.Application):
    """Main application"""

    def __init__(self):
        super().__init__(
            application_id='com.Nordix.Settings.Environment',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

    def do_activate(self):
        win = NordixEnvironmentWindow(self)
        win.present()


def main():
    app = NordixEnvironmentApp()
    return app.run(None)


if __name__ == "__main__":
    main()
