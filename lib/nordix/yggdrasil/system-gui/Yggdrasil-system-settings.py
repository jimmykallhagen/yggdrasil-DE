#!/usr/bin/env python3
##=========================================================##
 # SPDX-License-Identifier: GPL-3.0-or-later               #
 # Copyright (c) 2025 Jimmy Källhagen                      #
 # Part of Yggdrasil - Nordix desktop environment          #
##=========================================================##

"""Yggdrasil System Settings
A central launcher for all Nordix system settings GUIs.
Hides while a settings module is open, re-shows when it closes."""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib, Gdk
import subprocess


# =============================================
# SETTINGS MODULES
# =============================================

SETTINGS_MODULES = [
    {
        'category': 'Desktop',
        'entries': [
            {
                'id': 'general',
                'icon': 'preferences-system-symbolic',
                'title': 'General',
                'subtitle': 'General desktop settings',
                'command': '/usr/lib/nordix/yggdrasil/system-gui/yggdrasil-settings-general.py',
            },
            {
                'id': 'monitors',
                'icon': 'preferences-desktop-display-symbolic',
                'title': 'Monitors',
                'subtitle': 'Display configuration and resolution',
                'command': '/usr/lib/nordix/yggdrasil/system-gui/yggdrasil-settings-monitors.py',
            },
            {
                'id': 'decorations',
                'icon': 'preferences-desktop-theme-symbolic',
                'title': 'Decorations',
                'subtitle': 'Window borders, shadows and effects',
                'command': '/usr/lib/nordix/yggdrasil/system-gui/yggdrasil-settings-decorations.py',
            },
            {
                'id': 'layout',
                'icon': 'view-grid-symbolic',
                'title': 'Layout',
                'subtitle': 'Window tiling and workspace layout',
                'command': '/usr/lib/nordix/yggdrasil/system-gui/yggdrasil-settings-layout.py',
            },
            {
                'id': 'groups',
                'icon': 'view-dual-symbolic',
                'title': 'Groups',
                'subtitle': 'Window groups and groupbar appearance',
                'command': '/usr/lib/nordix/yggdrasil/system-gui/yggdrasil-settings-groups.py',
            },
        ],
    },
    {
        'category': 'System',
        'entries': [
            {
                'id': 'environment',
                'icon': 'preferences-other-symbolic',
                'title': 'Environment',
                'subtitle': 'Environment variables, GPU and compatibility',
                'command': '/usr/lib/nordix/yggdrasil/system-gui/yggdrasil-settings-environment.py',
            },
            {
                'id': 'input',
                'icon': 'input-keyboard-symbolic',
                'title': 'Input',
                'subtitle': 'Keyboard, mouse and touchpad settings',
                'command': '/usr/lib/nordix/yggdrasil/system-gui/yggdrasil-settings-input.py',
            },
            {
                'id': 'binds',
                'icon': 'preferences-desktop-keyboard-shortcuts-symbolic',
                'title': 'Keybindings',
                'subtitle': 'Keyboard shortcuts and bindings',
                'command': '/usr/lib/nordix/yggdrasil/system-gui/yggdrasil-settings-binds.py',
            },
            {
                'id': 'default-apps',
                'icon': 'application-x-executable-symbolic',
                'title': 'Default Applications',
                'subtitle': 'Browser, terminal, file manager and more',
                'command': '/usr/lib/nordix/yggdrasil/system-gui/yggdrasil-default-apps.py',
            },
        ],
    },
    {
        'category': 'Advanced',
        'entries': [
            {
                'id': 'advanced',
                'icon': 'system-run-symbolic',
                'title': 'Advanced',
                'subtitle': 'Performance tuning and advanced options',
                'command': '/usr/lib/nordix/yggdrasil/system-gui/yggdrasil-settings-advanced.py',
            },
        ],
    },
]


# =============================================
# CUSTOM CSS
# =============================================
PANEL_CSS = """
.panel-category-label {
    font-weight: bold;
    font-size: 11px;
    color: alpha(currentColor, 0.55);
    letter-spacing: 1px;
    margin-top: 16px;
    margin-bottom: 4px;
    margin-start: 8px;
}
.panel-entry-row {
    min-height: 56px;
    border-radius: 10px;
    margin: 2px 4px;
}
.panel-entry-row:hover {
    background-color: alpha(currentColor, 0.07);
}
.panel-icon {
    color: @accent_color;
}
.panel-status-running {
    color: @success_color;
    font-size: 10px;
    font-weight: bold;
}
.panel-footer {
    font-size: 11px;
    color: alpha(currentColor, 0.45);
}
"""


# =============================================
# MAIN WINDOW
# =============================================
class NordixSystemSettingsWindow(Adw.ApplicationWindow):
    """Main system settings window"""

    def __init__(self, app):
        super().__init__(
            application=app,
            title="Yggdrasil System Settings",
        )
        self.set_default_size(460, 680)

        self.children = {}
        self.status_labels = {}

        self._apply_css()
        self._setup_ui()

    def _apply_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_string(PANEL_CSS)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _setup_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Header bar
        header = Adw.HeaderBar()
        main_box.append(header)

        # Scrollable content
        scrolled = Gtk.ScrolledWindow(vexpand=True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content.set_margin_top(8)
        content.set_margin_bottom(16)
        content.set_margin_start(12)
        content.set_margin_end(12)

        for category_data in SETTINGS_MODULES:
            # Category label
            cat_label = Gtk.Label(
                label=category_data['category'].upper(),
                xalign=0,
            )
            cat_label.add_css_class('panel-category-label')
            content.append(cat_label)

            # Entries group
            group = Adw.PreferencesGroup()

            for entry in category_data['entries']:
                row = self._create_entry_row(entry)
                group.add(row)

            content.append(group)

        # Footer
        footer = Gtk.Label(
            label="Each module opens its own settings window.",
            xalign=0.5,
            wrap=True,
        )
        footer.add_css_class('panel-footer')
        footer.set_margin_top(20)
        content.append(footer)

        scrolled.set_child(content)
        main_box.append(scrolled)
        self.set_content(main_box)

    def _create_entry_row(self, entry):
        row = Adw.ActionRow()
        row.set_title(entry['title'])
        row.set_subtitle(entry['subtitle'])
        row.set_activatable(True)
        row.add_css_class('panel-entry-row')

        # Icon
        icon = Gtk.Image.new_from_icon_name(entry['icon'])
        icon.set_pixel_size(24)
        icon.add_css_class('panel-icon')
        row.add_prefix(icon)

        # Running status (hidden by default)
        status = Gtk.Label(label="Running")
        status.add_css_class('panel-status-running')
        status.set_visible(False)
        status.set_valign(Gtk.Align.CENTER)
        self.status_labels[entry['id']] = status
        row.add_suffix(status)

        # Arrow
        arrow = Gtk.Image.new_from_icon_name('go-next-symbolic')
        arrow.set_valign(Gtk.Align.CENTER)
        arrow.add_css_class('dim-label')
        row.add_suffix(arrow)

        row.connect('activated', self._on_entry_activated, entry)
        return row

    def _on_entry_activated(self, row, entry):
        entry_id = entry['id']
        command = entry['command']

        # Already running — don't launch again
        if entry_id in self.children:
            return

        try:
            proc = subprocess.Popen(
                [command],
                start_new_session=True,
            )
        except Exception as e:
            dialog = Adw.AlertDialog(
                heading="Failed to launch",
                body=f"{command}\n\n{e}",
            )
            dialog.add_response('ok', 'OK')
            dialog.present(self)
            return

        self.children[entry_id] = proc.pid

        if entry_id in self.status_labels:
            self.status_labels[entry_id].set_visible(True)

        # Hide system settings while module is open
        self.hide()

        # Watch for the child to exit
        GLib.child_watch_add(
            GLib.PRIORITY_DEFAULT, proc.pid,
            self._on_child_exited, entry_id
        )

    def _on_child_exited(self, pid, status, entry_id):
        if entry_id in self.children:
            del self.children[entry_id]

        if entry_id in self.status_labels:
            self.status_labels[entry_id].set_visible(False)

        # Re-show when no children are running
        if not self.children:
            self.present()

    def do_close_request(self):
        return False


# =============================================
# APPLICATION
# =============================================
class NordixSystemSettingsApp(Adw.Application):

    def __init__(self):
        super().__init__(
            application_id='com.Nordix.System.Settings',
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )

    def do_activate(self):
        win = NordixSystemSettingsWindow(self)
        win.present()


def main():
    app = NordixSystemSettingsApp()
    return app.run(None)


if __name__ == '__main__':
    main()
