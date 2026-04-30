#!/usr/bin/env python3
##=========================================================##
 # SPDX-License-Identifier: GPL-3.0-or-later               #
 # Copyright (c) 2025 Jimmy Källhagen                      #
 # Part of Yggdrasil - Nordix desktop environment          #
##=========================================================##

"""Yggdrasil Default Applications GUI
A graphical settings panel for configuring default applications
Handles both MIME desktop associations and system/shortcut app defaults"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib
import subprocess
import os
import re
import glob
import shutil
from pathlib import Path
from configparser import ConfigParser


# =============================================
# MIME CATEGORY DEFINITIONS
# =============================================
# Each category maps to a set of MIME types and
# the default .desktop file for Nordix
MIME_CATEGORIES = {
    'Text/Code Editor': {
        'default': 'dev.zed.Zed.desktop',
        'mime_types': [
            'text/plain',
            'text/x-csrc',
            'text/x-chdr',
            'text/x-c++src',
            'text/x-c++hdr',
            'text/x-java',
            'text/x-python',
            'text/x-shellscript',
            'text/x-script.python',
            'text/x-makefile',
            'text/x-cmake',
            'text/x-meson',
            'text/markdown',
            'text/x-markdown',
            'text/css',
            'text/javascript',
            'text/x-rust',
            'text/x-go',
            'text/x-lua',
            'text/x-perl',
            'text/x-ruby',
            'text/x-php',
            'text/xml',
            'text/csv',
            'text/tab-separated-values',
            'text/x-log',
            'application/json',
            'application/xml',
            'application/x-yaml',
            'application/toml',
            'application/x-shellscript',
            'application/javascript',
            'application/x-perl',
            'application/x-ruby',
            'application/x-php',
        ],
        'filter_categories': ['TextEditor', 'Development', 'IDE'],
        'description': 'Application for opening text files and code',
    },
    'Web Browser': {
        'default': 'firefox.desktop',
        'mime_types': [
            'text/html',
            'application/xhtml+xml',
            'application/x-extension-htm',
            'application/x-extension-html',
            'application/x-extension-shtml',
            'application/x-extension-xhtml',
            'application/x-extension-xht',
            'x-scheme-handler/http',
            'x-scheme-handler/https',
            'x-scheme-handler/about',
            'x-scheme-handler/chrome',
        ],
        'filter_categories': ['WebBrowser'],
        'description': 'Application for browsing the web',
    },
    'Images': {
        'default': 'org.kde.gwenview.desktop',
        'mime_types': [
            'image/png',
            'image/jpeg',
            'image/jpg',
            'image/gif',
            'image/webp',
            'image/avif',
            'image/bmp',
            'image/x-bmp',
            'image/tiff',
            'image/x-tiff',
            'image/svg+xml',
            'image/x-icon',
            'image/vnd.microsoft.icon',
            'image/x-portable-pixmap',
            'image/x-portable-bitmap',
            'image/x-portable-graymap',
            'image/x-xbitmap',
            'image/x-xpixmap',
        ],
        'filter_categories': ['Viewer', 'Graphics'],
        'description': 'Application for viewing images',
    },
    'Video': {
        'default': 'mpv.desktop',
        'mime_types': [
            'video/mp4',
            'video/x-matroska',
            'video/webm',
            'video/x-msvideo',
            'video/avi',
            'video/mpeg',
            'video/x-mpeg',
            'video/mp2t',
            'video/quicktime',
            'video/x-flv',
            'video/x-ms-wmv',
            'video/x-ms-asf',
            'video/ogg',
            'video/3gpp',
            'video/3gpp2',
            'video/x-ogm+ogg',
            'video/divx',
            'video/x-m4v',
        ],
        'filter_categories': ['Video', 'AudioVideo', 'Player'],
        'description': 'Application for playing video files',
    },
    'Audio': {
        'default': 'mpv.desktop',
        'mime_types': [
            'audio/mpeg',
            'audio/mp3',
            'audio/x-mp3',
            'audio/flac',
            'audio/x-flac',
            'audio/ogg',
            'audio/x-vorbis+ogg',
            'audio/opus',
            'audio/x-opus+ogg',
            'audio/wav',
            'audio/x-wav',
            'audio/x-ms-wma',
            'audio/aac',
            'audio/x-aac',
            'audio/mp4',
            'audio/x-m4a',
            'audio/x-matroska',
            'audio/webm',
            'audio/x-ape',
            'audio/x-wavpack',
            'audio/x-musepack',
            'audio/midi',
            'audio/x-midi',
        ],
        'filter_categories': ['Audio', 'AudioVideo', 'Music', 'Player'],
        'description': 'Application for playing audio files',
    },
    'File Manager': {
        'default': 'thunar.desktop',
        'mime_types': [
            'inode/directory',
        ],
        'filter_categories': ['FileManager'],
        'description': 'Application for browsing files and folders',
    },
    'Terminal': {
        'default': 'org.wezfurlong.wezterm.desktop',
        'mime_types': [
            'application/x-terminal-emulator',
        ],
        'filter_categories': ['TerminalEmulator'],
        'description': 'Terminal emulator application',
    },
    'Wine / Windows Executables': {
        'default': 'wine.desktop',
        'mime_types': [
            'application/x-ms-dos-executable',
            'application/x-msdos-program',
            'application/x-msdownload',
            'application/x-exe',
            'application/x-win-exe',
            'application/x-dosexec',
            'application/vnd.microsoft.portable-executable',
        ],
        'filter_categories': ['Emulator'],
        'description': 'Application for running Windows executables',
    },
    'Archives': {
        'default': 'peazip.desktop',
        'mime_types': [
            'application/zip',
            'application/x-tar',
            'application/x-gzip',
            'application/gzip',
            'application/x-bzip2',
            'application/x-xz',
            'application/x-7z-compressed',
            'application/x-rar',
            'application/x-rar-compressed',
            'application/vnd.rar',
            'application/x-compressed-tar',
            'application/x-bzip-compressed-tar',
            'application/x-xz-compressed-tar',
            'application/x-lzip-compressed-tar',
            'application/x-zstd-compressed-tar',
        ],
        'filter_categories': ['Archiving', 'Compression'],
        'description': 'Application for handling compressed archives',
    },
    'PDF / Documents': {
        'default': 'org.kde.okular.desktop',
        'mime_types': [
            'application/pdf',
        ],
        'filter_categories': ['Viewer', 'Office'],
        'description': 'Application for viewing PDF and documents',
    },
    'Torrents': {
        'default': 'org.qbittorrent.qBittorrent.desktop',
        'mime_types': [
            'application/x-bittorrent',
            'x-scheme-handler/magnet',
        ],
        'filter_categories': ['FileTransfer', 'P2P', 'Network'],
        'description': 'Application for downloading torrents',
    },
}


# =============================================
# SYSTEM & SHORTCUT APP DEFINITIONS
# =============================================
# These write to system_defaults.conf using
# Hyprland variable format: $variable = command
SYSTEM_DEFAULTS = {
    'system_browser': {
        'label': 'Web Browser',
        'default': 'firefox',
        'description': 'Default web browser for system and keybinds',
        'filter_categories': ['WebBrowser'],
        'section': 'shortcut',
    },
    'system_visula_editor': {
        'label': 'Visual Text Editor',
        'default': 'Zed',
        'description': 'Default graphical text editor',
        'filter_categories': ['TextEditor', 'Development', 'IDE'],
        'section': 'shortcut',
    },
    'system_pdf_viewer': {
        'label': 'PDF Viewer',
        'default': 'okular',
        'description': 'Default PDF and document viewer',
        'filter_categories': ['Viewer', 'Office'],
        'section': 'system',
    },
    'system_image_viewer': {
        'label': 'Image Viewer',
        'default': 'gwenview',
        'description': 'Default image viewer',
        'filter_categories': ['Viewer', 'Graphics'],
        'section': 'system',
    },
    'system_calculator': {
        'label': 'Calculator',
        'default': 'qalculate-gtk',
        'description': 'Default calculator application',
        'filter_categories': ['Calculator', 'Utility'],
        'section': 'system',
    },
    'system_terminal': {
        'label': 'Primary Terminal',
        'default': 'wezterm',
        'description': 'Default terminal emulator',
        'filter_categories': ['TerminalEmulator'],
        'section': 'shortcut',
    },
    'system_filebrowser': {
        'label': 'File Manager',
        'default': 'thunar',
        'description': 'Default file browser',
        'filter_categories': ['FileManager'],
        'section': 'shortcut',
    },
    'terminal_2': {
        'label': 'Secondary Terminal',
        'default': 'ghostty',
        'description': 'Alternative terminal (keybind shortcut)',
        'filter_categories': ['TerminalEmulator'],
        'section': 'shortcut',
    },
    'translate': {
        'label': 'Translator',
        'default': 'crow',
        'description': 'Translation application (keybind shortcut)',
        'filter_categories': [],
        'section': 'shortcut',
    },
    'youtube': {
        'label': 'YouTube',
        'default': 'nordix-youtube-tauri',
        'description': 'YouTube application (keybind shortcut)',
        'filter_categories': [],
        'section': 'shortcut',
    },
    'emoji': {
        'label': 'Emoji Picker',
        'default': 'smile',
        'description': 'Emoji picker application (keybind shortcut)',
        'filter_categories': [],
        'section': 'shortcut',
    },
}


# =============================================
# FILE PATHS
# =============================================
MIMEAPPS_PATH = Path.home() / ".config" / "mimeapps.list"
SYSTEM_DEFAULTS_PATH = Path.home() / ".config" / "nordix" / "yggdrasil" / "settings" / "nordix-defaults.conf"

# =============================================
# DESKTOP ENTRY SCANNER
# =============================================
class DesktopEntryScanner:
    """Scans and parses .desktop files from standard locations"""

    DESKTOP_DIRS = [
        Path("/usr/share/applications"),
        Path("/usr/local/share/applications"),
        Path.home() / ".local" / "share" / "applications",
        Path("/var/lib/flatpak/exports/share/applications"),
        Path.home() / ".local" / "share" / "flatpak" / "exports" / "share" / "applications",
    ]

    def __init__(self):
        self.entries = {}  # filename -> parsed entry
        self.scan_all()

    def scan_all(self):
        """Scan all desktop entry directories"""
        for directory in self.DESKTOP_DIRS:
            if directory.exists():
                for desktop_file in directory.glob("*.desktop"):
                    try:
                        entry = self._parse_desktop_file(desktop_file)
                        if entry and not entry.get('hidden', False) and not entry.get('no_display', False):
                            # Later directories override earlier ones
                            self.entries[desktop_file.name] = entry
                    except Exception as e:
                        continue

    def _parse_desktop_file(self, path):
        """Parse a single .desktop file"""
        entry = {
            'filename': path.name,
            'path': str(path),
            'name': '',
            'icon': '',
            'exec': '',
            'command': '',
            'mime_types': [],
            'categories': [],
            'hidden': False,
            'no_display': False,
            'type': '',
        }

        try:
            content = path.read_text(errors='replace')
        except Exception:
            return None

        in_desktop_entry = False

        for line in content.split('\n'):
            stripped = line.strip()

            if stripped == '[Desktop Entry]':
                in_desktop_entry = True
                continue
            elif stripped.startswith('[') and stripped.endswith(']'):
                in_desktop_entry = False
                continue

            if not in_desktop_entry or '=' not in stripped:
                continue

            key, _, value = stripped.partition('=')
            key = key.strip()
            value = value.strip()

            if key == 'Name':
                entry['name'] = value
            elif key == 'Icon':
                entry['icon'] = value
            elif key == 'Exec':
                entry['exec'] = value
                # Extract base command (first word, strip % arguments)
                cmd = value.split()[0] if value else ''
                # Remove path prefix if present
                cmd = cmd.rsplit('/', 1)[-1]
                entry['command'] = cmd
            elif key == 'MimeType':
                entry['mime_types'] = [m.strip() for m in value.strip(';').split(';') if m.strip()]
            elif key == 'Categories':
                entry['categories'] = [c.strip() for c in value.strip(';').split(';') if c.strip()]
            elif key == 'Hidden':
                entry['hidden'] = value.lower() == 'true'
            elif key == 'NoDisplay':
                entry['no_display'] = value.lower() == 'true'
            elif key == 'Type':
                entry['type'] = value

        # Only return Application types with a name
        if entry['type'] != 'Application' or not entry['name']:
            return None

        return entry

    def get_apps_for_mime_category(self, mime_types, filter_categories):
        """Get list of apps that can handle given MIME types or belong to categories"""
        matching = {}

        for filename, entry in self.entries.items():
            # Check MIME type overlap
            entry_mimes = set(entry['mime_types'])
            target_mimes = set(mime_types)
            has_mime_match = bool(entry_mimes & target_mimes)

            # Check category overlap
            entry_cats = set(entry['categories'])
            target_cats = set(filter_categories)
            has_cat_match = bool(entry_cats & target_cats)

            if has_mime_match or has_cat_match:
                matching[filename] = entry

        # Sort by name
        return dict(sorted(matching.items(), key=lambda x: x[1]['name'].lower()))

    def get_apps_for_system_category(self, filter_categories):
        """Get list of apps matching category filters for system defaults"""
        if not filter_categories:
            # Return all apps if no filter (for custom/niche apps)
            return dict(sorted(self.entries.items(), key=lambda x: x[1]['name'].lower()))

        matching = {}
        for filename, entry in self.entries.items():
            entry_cats = set(entry['categories'])
            target_cats = set(filter_categories)
            if entry_cats & target_cats:
                matching[filename] = entry

        return dict(sorted(matching.items(), key=lambda x: x[1]['name'].lower()))

    def find_entry_by_command(self, command):
        """Find a desktop entry by its command name"""
        for filename, entry in self.entries.items():
            if entry['command'] == command:
                return filename, entry
        return None, None

    def find_entry_by_filename(self, filename):
        """Find a desktop entry by its .desktop filename"""
        if filename in self.entries:
            return self.entries[filename]
        return None


# =============================================
# MIME SETTINGS HANDLER
# =============================================
class MimeSettings:
    """Handles reading and writing of mimeapps.list"""

    def __init__(self):
        self.associations = {}  # mime_type -> desktop_file
        self.load()

    def load(self):
        """Load current mimeapps.list"""
        self.associations = {}

        if not MIMEAPPS_PATH.exists():
            print(f"mimeapps.list not found, will create with defaults")
            self._create_defaults()
            return

        try:
            content = MIMEAPPS_PATH.read_text()
            in_default = False

            for line in content.split('\n'):
                stripped = line.strip()

                if stripped == '[Default Applications]':
                    in_default = True
                    continue
                elif stripped.startswith('['):
                    in_default = False
                    continue

                if in_default and '=' in stripped and not stripped.startswith('# '):
                    mime_type, _, desktop = stripped.partition('=')
                    mime_type = mime_type.strip()
                    desktop = desktop.strip().rstrip(';')
                    if mime_type and desktop:
                        self.associations[mime_type] = desktop

        except Exception as e:
            print(f"Error loading mimeapps.list: {e}")
            self._create_defaults()

    def _create_defaults(self):
        """Create default MIME associations"""
        for cat_name, cat_data in MIME_CATEGORIES.items():
            for mime_type in cat_data['mime_types']:
                self.associations[mime_type] = cat_data['default']

    def get_app_for_category(self, category_name):
        """Get the current default app for a MIME category"""
        cat_data = MIME_CATEGORIES.get(category_name)
        if not cat_data:
            return cat_data['default']

        # Return the app set for the first MIME type in the category
        first_mime = cat_data['mime_types'][0]
        return self.associations.get(first_mime, cat_data['default'])

    def set_app_for_category(self, category_name, desktop_file):
        """Set the default app for all MIME types in a category"""
        cat_data = MIME_CATEGORIES.get(category_name)
        if not cat_data:
            return

        for mime_type in cat_data['mime_types']:
            self.associations[mime_type] = desktop_file

    def save(self):
        """Save mimeapps.list"""
        try:
            MIMEAPPS_PATH.parent.mkdir(parents=True, exist_ok=True)

            # Create backup
            if MIMEAPPS_PATH.exists():
                backup = MIMEAPPS_PATH.with_suffix('.list.backup')
                shutil.copy2(MIMEAPPS_PATH, backup)

            lines = ['[Default Applications]']

            # Group by category for readability
            written_mimes = set()
            for cat_name, cat_data in MIME_CATEGORIES.items():
                lines.append(f'\n# {cat_name}')
                for mime_type in cat_data['mime_types']:
                    if mime_type in self.associations:
                        lines.append(f'{mime_type}={self.associations[mime_type]}')
                        written_mimes.add(mime_type)

            # Write any remaining associations not in our categories
            remaining = {k: v for k, v in self.associations.items() if k not in written_mimes}
            if remaining:
                lines.append('\n# Other')
                for mime_type, desktop in remaining.items():
                    lines.append(f'{mime_type}={desktop}')

            lines.append('\n[Added Associations]\n')

            MIMEAPPS_PATH.write_text('\n'.join(lines) + '\n')
            return True

        except Exception as e:
            print(f"Error saving mimeapps.list: {e}")
            return False


# =============================================
# SYSTEM DEFAULTS HANDLER
# =============================================
class SystemDefaultsSettings:
    """Handles reading and writing of system_defaults.conf"""

    def __init__(self):
        self.values = {}  # variable_name -> command
        self.load()

    def load(self):
        """Load current system_defaults.conf"""
        # Initialize with defaults
        for key, data in SYSTEM_DEFAULTS.items():
            self.values[key] = data['default']

        if not SYSTEM_DEFAULTS_PATH.exists():
            print(f"system_defaults.conf not found, will create with defaults")
            return

        try:
            content = SYSTEM_DEFAULTS_PATH.read_text()

            for line in content.split('\n'):
                stripped = line.strip()

                if not stripped or stripped.startswith('#'):
                    continue

                # Parse Hyprland variable format: $variable = value
                match = re.match(r'^\$(\w+)\s*=\s*(.+)$', stripped)
                if match:
                    var_name = match.group(1)
                    value = match.group(2).strip()
                    if var_name in SYSTEM_DEFAULTS:
                        self.values[var_name] = value

        except Exception as e:
            print(f"Error loading system_defaults.conf: {e}")

    def save(self):
        """Save system_defaults.conf"""
        try:
            SYSTEM_DEFAULTS_PATH.parent.mkdir(parents=True, exist_ok=True)

            # Create backup
            if SYSTEM_DEFAULTS_PATH.exists():
                backup = SYSTEM_DEFAULTS_PATH.with_suffix('.conf.backup')
                shutil.copy2(SYSTEM_DEFAULTS_PATH, backup)

            lines = [
                '##=========================================================##',
                ' # SPDX-License-Identifier: GPL-3.0-or-later               #',
                ' # Copyright (c) 2025 Jimmy Källhagen                      #',
                ' # Part of Yggdrasil - Nordix desktop environment          #',
                '##=========================================================##',
                '',
                '# ##=========================================##',
                '#  #                Yggdrasils               #',
                '#  #       System Default Applications       #',
                '# ##=========================================##',
                '# ',
                '# Generated by Yggdrasils Default Apps GUI',
                '# This file is sourced by Hyprland for keybinds and env vars',
                '',
                '# Cursor',
                '$system_cursor = Nero-Cyber-Cyan',
                '$cursor_size = 34',
                '',
                '# Top bar',
                '$system_bar = /usr/lib/nordix/yggdrasil/scripts/nordix-ashell.sh',

                '# Applauncher ',
                '$applauncher = /usr/lib/nordix/yggdrasil/bin/launcher-wrapper.sh',
                '',


            ]

            # System defaults section
            lines.append('# System Default Applications')
            for key, data in SYSTEM_DEFAULTS.items():
                if data['section'] == 'system':
                    lines.append(f'${key} = {self.values.get(key, data["default"])}')

            lines.append('')

            # Shortcut apps section
            lines.append('# Shortcut Applications')
            for key, data in SYSTEM_DEFAULTS.items():
                if data['section'] == 'shortcut':
                    lines.append(f'${key} = {self.values.get(key, data["default"])}')

            lines.append('')

            SYSTEM_DEFAULTS_PATH.write_text('\n'.join(lines) + '\n')
            return True

        except Exception as e:
            print(f"Error saving system_defaults.conf: {e}")
            return False


# =============================================
# APP CHOOSER ROW WIDGET
# =============================================
class AppChooserRow(Adw.ActionRow):
    """A row with dropdown for choosing an application, with icon"""

    def __init__(self, title, subtitle, apps_dict, current_value, callback, value_is_command=False):
        """Args:
            title: Row title
            subtitle: Row description
            apps_dict: dict of {filename: entry} from DesktopEntryScanner
            current_value: Current .desktop filename or command name
            callback: Called with new value on change
            value_is_command: If True, values are command names instead of .desktop filenames"""
        super().__init__()
        self.set_title(title)
        self.set_subtitle(subtitle)

        self.callback = callback
        self.value_is_command = value_is_command
        self.app_keys = []  # .desktop filenames or commands in dropdown order

        # Build the model for the dropdown
        self.store = Gtk.StringList()
        current_index = 0

        # Add a "Custom / Not installed" entry first if current not found
        found_current = False

        for filename, entry in apps_dict.items():
            value = entry['command'] if value_is_command else filename
            self.app_keys.append(value)
            self.store.append(entry['name'])

            if value_is_command:
                if entry['command'] == current_value:
                    current_index = len(self.app_keys) - 1
                    found_current = True
            else:
                if filename == current_value:
                    current_index = len(self.app_keys) - 1
                    found_current = True

        # If current value not in list, add it as custom entry
        if not found_current and current_value:
            self.app_keys.insert(0, current_value)
            self.store.splice(0, 0, [f"{current_value} (custom)"])
            current_index = 0

        # Icon display
        self.icon_image = Gtk.Image()
        self.icon_image.set_pixel_size(24)
        self._update_icon(current_value, apps_dict)

        # Dropdown
        self.dropdown = Gtk.DropDown(model=self.store)
        self.dropdown.set_selected(current_index)
        self.dropdown.connect('notify::selected', self._on_selected)

        # Layout
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        box.set_valign(Gtk.Align.CENTER)
        box.append(self.icon_image)
        box.append(self.dropdown)

        self.add_suffix(box)
        self.apps_dict = apps_dict

    def _update_icon(self, value, apps_dict=None):
        """Update the icon display for the selected app"""
        icon_name = None

        if apps_dict:
            for filename, entry in apps_dict.items():
                check_val = entry['command'] if self.value_is_command else filename
                if check_val == value:
                    icon_name = entry.get('icon', '')
                    break

        if icon_name:
            icon_theme = Gtk.IconTheme.get_for_display(
                self.icon_image.get_display() if self.icon_image.get_display()
                else self.icon_image.get_root().get_display() if self.icon_image.get_root()
                else None
            )
            # Try themed icon first, fall back to generic
            if icon_theme and icon_theme.has_icon(icon_name):
                self.icon_image.set_from_icon_name(icon_name)
            else:
                self.icon_image.set_from_icon_name('application-x-executable')
        else:
            self.icon_image.set_from_icon_name('application-x-executable')

    def _on_selected(self, dropdown, _):
        selected = dropdown.get_selected()
        if selected < len(self.app_keys):
            value = self.app_keys[selected]
            self._update_icon(value, self.apps_dict)
            self.callback(value)

    def set_value(self, value):
        """Set the selected value"""
        if value in self.app_keys:
            index = self.app_keys.index(value)
            self.dropdown.set_selected(index)
            self._update_icon(value, self.apps_dict)


# =============================================
# MAIN WINDOW
# =============================================
class NordixDefaultAppsWindow(Adw.ApplicationWindow):
    """Main window for default application settings"""

    def __init__(self, app):
        super().__init__(application=app, title="Yggdrasils Default Applications")
        self.set_default_size(600, 850)

        # Initialize scanner and settings
        self.scanner = DesktopEntryScanner()
        self.mime_settings = MimeSettings()
        self.system_settings = SystemDefaultsSettings()
        self.widgets = {}

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
        # DESKTOP DEFAULT APPS (MIME) SECTION
        # =========================================
        mime_group = Adw.PreferencesGroup(
            title="Desktop Default Applications",
            description="Choose which applications open different file types"
        )

        for cat_name, cat_data in MIME_CATEGORIES.items():
            # Get available apps for this category
            available_apps = self.scanner.get_apps_for_mime_category(
                cat_data['mime_types'],
                cat_data['filter_categories']
            )

            # Get current setting
            current_app = self.mime_settings.get_app_for_category(cat_name)

            widget_key = f"mime_{cat_name}"
            self.widgets[widget_key] = AppChooserRow(
                cat_name,
                cat_data['description'],
                available_apps,
                current_app,
                lambda value, cn=cat_name: self.on_mime_changed(cn, value),
                value_is_command=False
            )
            mime_group.add(self.widgets[widget_key])

        content.append(mime_group)

        # =========================================
        # SYSTEM DEFAULT APPS SECTION
        # =========================================
        system_group = Adw.PreferencesGroup(
            title="System Default Applications",
            description="Default applications used by system keybinds and environment"
        )

        for key, data in SYSTEM_DEFAULTS.items():
            if data['section'] != 'system':
                continue

            available_apps = self.scanner.get_apps_for_system_category(
                data['filter_categories']
            )

            current_cmd = self.system_settings.values.get(key, data['default'])

            widget_key = f"sys_{key}"
            self.widgets[widget_key] = AppChooserRow(
                data['label'],
                data['description'],
                available_apps,
                current_cmd,
                lambda value, k=key: self.on_system_changed(k, value),
                value_is_command=True
            )
            system_group.add(self.widgets[widget_key])

        content.append(system_group)

        # =========================================
        # SHORTCUT APPS SECTION
        # =========================================
        shortcut_group = Adw.PreferencesGroup(
            title="Keyboard Shortcut Applications",
            description="Applications launched via keyboard shortcuts"
        )

        for key, data in SYSTEM_DEFAULTS.items():
            if data['section'] != 'shortcut':
                continue

            available_apps = self.scanner.get_apps_for_system_category(
                data['filter_categories']
            )

            current_cmd = self.system_settings.values.get(key, data['default'])

            widget_key = f"short_{key}"
            self.widgets[widget_key] = AppChooserRow(
                data['label'],
                data['description'],
                available_apps,
                current_cmd,
                lambda value, k=key: self.on_system_changed(k, value),
                value_is_command=True
            )
            shortcut_group.add(self.widgets[widget_key])

        content.append(shortcut_group)

        scrolled.set_child(content)
        main_box.append(scrolled)

        # Status bar
        self.status_bar = Gtk.Label(label="Ready")
        self.status_bar.add_css_class("dim-label")
        self.status_bar.set_margin_top(6)
        self.status_bar.set_margin_bottom(6)
        main_box.append(self.status_bar)

        self.set_content(main_box)

    def on_mime_changed(self, category_name, desktop_file):
        """Called when a MIME category default is changed"""
        self.mime_settings.set_app_for_category(category_name, desktop_file)
        self.status_bar.set_text(f"Changed: {category_name} → {desktop_file}")

    def on_system_changed(self, key, command):
        """Called when a system/shortcut default is changed"""
        self.system_settings.values[key] = command
        label = SYSTEM_DEFAULTS[key]['label']
        self.status_bar.set_text(f"Changed: {label} → {command}")

    def on_apply(self, button):
        """Save and apply all changes"""
        mime_ok = self.mime_settings.save()
        sys_ok = self.system_settings.save()

        if mime_ok and sys_ok:
            # Reload Hyprland to pick up new system defaults
            try:
                subprocess.run(['hyprctl', 'reload'], check=True)
                self.status_bar.set_text("Saved and applied successfully!")
            except Exception:
                self.status_bar.set_text("Saved (could not reload Hyprland)")
        else:
            errors = []
            if not mime_ok:
                errors.append("mimeapps.list")
            if not sys_ok:
                errors.append("system_defaults.conf")
            self.status_bar.set_text(f"Error saving: {', '.join(errors)}")

    def on_reset(self, button):
        """Reset all settings to Nordix defaults"""
        # Reset MIME
        for cat_name, cat_data in MIME_CATEGORIES.items():
            self.mime_settings.set_app_for_category(cat_name, cat_data['default'])

        # Reset system defaults
        for key, data in SYSTEM_DEFAULTS.items():
            self.system_settings.values[key] = data['default']

        # Refresh UI
        self.refresh_ui()
        self.status_bar.set_text("Reset to Yggdrasils defaults - click Apply to save")

    def refresh_ui(self):
        """Update all widgets with current values"""
        for cat_name in MIME_CATEGORIES:
            widget_key = f"mime_{cat_name}"
            if widget_key in self.widgets:
                current = self.mime_settings.get_app_for_category(cat_name)
                self.widgets[widget_key].set_value(current)

        for key, data in SYSTEM_DEFAULTS.items():
            prefix = "sys_" if data['section'] == 'system' else "short_"
            widget_key = f"{prefix}{key}"
            if widget_key in self.widgets:
                self.widgets[widget_key].set_value(
                    self.system_settings.values.get(key, data['default'])
                )


# =============================================
# APPLICATION
# =============================================
class NordixDefaultAppsApp(Adw.Application):
    """Main application"""

    def __init__(self):
        super().__init__(
            application_id='com.Nordix.Settings.Default',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

    def do_activate(self):
        win = NordixDefaultAppsWindow(self)
        win.present()


def main():
    app = NordixDefaultAppsApp()
    return app.run(None)


if __name__ == "__main__":
    main()
