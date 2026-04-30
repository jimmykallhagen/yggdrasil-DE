#!/usr/bin/env python3
##=========================================================##
 # SPDX-License-Identifier: GPL-3.0-or-later               #
 # Copyright (c) 2025 Jimmy Källhagen                      #
 # Part of Yggdrasil - Nordix desktop environment          #
##=========================================================##

"""Yggdrasil Keybinds Overlay
A fullscreen transparent overlay showing all keybinds
Press ESC or ALT+H to close"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gtk4LayerShell', '1.0')
from gi.repository import Gtk, Gdk, Pango, GLib
from gi.repository import Gtk4LayerShell as LayerShell

# =============================================================================
# KEYBINDS DATA - Hardcoded for Yggdrasil
# =============================================================================

KEYBINDS = {
    "Disable/Enable Keybinds": [
        ("ALT + Scroll Lock", "Disable all keybinds"),
        ("Scroll Lock", "Enable all keybinds"),
    ],
    
    "SpecialWorkspace": [
        ("ALT + S", "Move to Special: 1 ❄️ Yggdrasil"),
        ("SUPER + S", "Move back to regular Workspace"),
        ("SUPER + 1", "Toggle Special: 1 ❄️ Yggdrasil"),
        ("SUPER + 2", "Toggle Special: 2 ❄️ Game"),
        ("SUPER + 3", "Toggle Special: System Settings (3 ⚙️)"),
        ("SUPER + 4", "Toggle Special: Flatpak Store (4 🏛️)"),
    ],
    
    "Standard Apps": [
        ("ALT + E", "File Manager"),
        ("ALT + Q", "Close Window"),
        ("ALT + W", "Web Browser"),
        ("ALT + Y", "YouTube"),
        ("ALT + H", "Keybinds Help"),
        ("ALT + Space", "App Launcher"),
        ("SUPER + Space", "App Search/Launcher"),
        ("ALT + U", "Emoji Picker"),
        ("ALT + B", "Flatpak Store - Bazaar"),
    ],
    
    "Second Layer Apps": [
        ("ALT + SHIFT + E", "Visual Editor"),
        ("ALT + SHIFT + U", "Character Map (Unicode)"),
        ("ALT + SHIFT + P", "Color Picker"),
        ("ALT + SHIFT + T", "Translate"),

    ],
    
    "Third Layer Functions": [
        ("SUPER + H", "Reload Hyprland"),
        ("SUPER + F", "Fullscreen"),
        ("SUPER + A", "Restart Bar"),
        ("SUPER + X", "Toggle XWayland Scale"),
        ("SUPER + P", "Pin Window"),
    ],
    
    "Shaders": [
        ("ALT + Caps", "Toggle Shaders"),
        ("SUPER + Caps", "Shaders Off"),
    ],
    
    "Terminal": [
        ("ALT + Return", "Terminal"),
        ("ALT + T", "Terminal"),
        ("SUPER + Return", "Terminal 2"),
        ("SUPER + T", "Terminal 2"),
    ],
    
    "Nordix Settings": [
        ("SUPER + N", "Nordix: Yggdrasil-Settings"),
    ],
    
    "Window Mode": [
        ("ALT + C", "Toggle Floating"),
        ("SUPER + C", "Toggle Pseudo Tile"),
    ],
    
    "Zoom": [
        ("ALT + CTRL + LMB", "Zoom In"),
        ("ALT + CTRL + RMB", "Zoom Reset"),
    ],
    
    "Screenshots": [
        ("Print", "Screenshot Monitor"),
        ("CTRL + Print", "Screenshot to Clipboard"),
        ("SHIFT + Print", "Screenshot Selected Area"),
        ("ALT + Print", "Screenshot Active Window"),
    ],
    
    "Groups": [
        ("ALT + G", "Create/Release Group"),
        ("ALT + SHIFT + G", "Toggle Grouped Windows"),
    ],
    
    "Toggle Gaps": [
        ("ALT + SHIFT + D", "Small Gaps"),
        ("SUPER + SHIFT + D", "Big Gaps"),
        ("SUPER + D", "Default Gaps (Reload Hyprland)"),
    ],
    
    "Playback Control": [
        ("XF86 AudioPlay", "Toggle Play/Pause"),
        ("XF86 AudioNext", "Next Track"),
        ("XF86 AudioPrev", "Previous Track"),
    ],
    
    "Screen Brightness": [
        ("XF86 BrightnessUp", "Brightness +5%"),
        ("XF86 BrightnessDown", "Brightness -5%"),
    ],
    
    "Lock Screen": [
        ("ALT + L", "Lock Screen"),
    ],
    
    "Window Actions - Mouse": [
        ("ALT + LMB", "Move Window"),
        ("ALT + RMB", "Resize Window"),
    ],
    
    "Move Window (Direction)": [
        ("ALT + SHIFT + Left", "Move Window Left"),
        ("ALT + SHIFT + Right", "Move Window Right"),
        ("ALT + SHIFT + Up", "Move Window Up"),
        ("ALT + SHIFT + Down", "Move Window Down"),
    ],
    
    "Move Focus": [
        ("ALT + Left", "Focus Left"),
        ("ALT + Right", "Focus Right"),
        ("ALT + Up", "Focus Up"),
        ("ALT + Down", "Focus Down"),
        ("ALT + Scroll Down", "Focus Left"),
        ("ALT + Scroll Up", "Focus Right"),
        ("ALT + Scroll Up", "Focus Up"),
        ("ALT + Scroll Down", "Focus Down"),

    ],
    
    "Resize Mode (SUPER + R)": [
        ("ALT + R", "Enter Resize Mode"),
        ("Right / L", "Resize Right"),
        ("Left / H", "Resize Left"),
        ("Up / K", "Resize Up"),
        ("Down / J", "Resize Down"),
        ("ESC", "Exit Resize Mode"),
    ],
    
    "Quick Resize": [
        ("ALT + CTRL + SHIFT + Right", "Resize Right"),
        ("ALT + CTRL + SHIFT + Left", "Resize Left"),
        ("ALT + CTRL + SHIFT + Up", "Resize Up"),
        ("ALT + CTRL + SHIFT + Down", "Resize Down"),
        ("ALT + CTRL + SHIFT + L", "Resize Right"),
        ("ALT + CTRL + SHIFT + H", "Resize Left"),
        ("ALT + CTRL + SHIFT + K", "Resize Up"),
        ("ALT + CTRL + SHIFT + J", "Resize Down"),
    ],
    
    "Move + Switch Workspace": [
        ("ALT + CTRL + 1", "Move + Switch WS 1"),
        ("ALT + CTRL + 2", "Move + Switch WS 2"),
        ("ALT + CTRL + 3", "Move + Switch WS 3"),
        ("ALT + CTRL + 4", "Move + Switch WS 4"),
        ("ALT + CTRL + 5", "Move + Switch WS 5"),
        ("ALT + CTRL + 6", "Move + Switch WS 6"),
        ("ALT + CTRL + 7", "Move + Switch WS 7"),
        ("ALT + CTRL + 8", "Move + Switch WS 8"),
        ("ALT + CTRL + 9", "Move + Switch WS 9"),
        ("ALT + CTRL + 0", "Move + Switch WS 10"),
        ("ALT + CTRL + Left", "Move + Switch Prev WS"),
        ("ALT + CTRL + Right", "Move + Switch Next WS"),
    ],
    
    "Move Silent (No Switch)": [
        ("ALT + SHIFT + 1", "Move Silent WS 1"),
        ("ALT + SHIFT + 2", "Move Silent WS 2"),
        ("ALT + SHIFT + 3", "Move Silent WS 3"),
        ("ALT + SHIFT + 4", "Move Silent WS 4"),
        ("ALT + SHIFT + 5", "Move Silent WS 5"),
        ("ALT + SHIFT + 6", "Move Silent WS 6"),
        ("ALT + SHIFT + 7", "Move Silent WS 7"),
        ("ALT + SHIFT + 8", "Move Silent WS 8"),
        ("ALT + SHIFT + 9", "Move Silent WS 9"),
        ("ALT + SHIFT + 0", "Move Silent WS 10"),
    ],
    
    "Switch Workspace": [
        ("ALT + 1", "Workspace 1"),
        ("ALT + 2", "Workspace 2"),
        ("ALT + 3", "Workspace 3"),
        ("ALT + 4", "Workspace 4"),
        ("ALT + 5", "Workspace 5"),
        ("ALT + 6", "Workspace 6"),
        ("ALT + 7", "Workspace 7"),
        ("ALT + 8", "Workspace 8"),
        ("ALT + 9", "Workspace 9"),
        ("ALT + 0", "Workspace 10"),
    ],
    
    "Workspace Navigation": [
        ("ALT + .", "Next Workspace"),
        ("ALT + ,", "Prev Workspace"),
        ("ALT + /", "Previous Workspace"),
        ("SUPER + Scroll Down", "Next Workspace"),
        ("SUPER + Scroll Up", "Prev Workspace"),
        ("SUPER + Right", "Next Workspace"),
        ("SUPER + Left", "Prev Workspace"),
    ],
}

# Color scheme
COLORS = {
    'bg': 'rgba(10, 15, 20, 0.85)',
    'title': '#00d2ff',
    'key': '#9ce6ff',
    'desc': '#d2ffff',
    'category': '#13abc6',
    'border': 'rgba(0, 210, 255, 0.3)',
}


class KeybindsOverlay(Gtk.Window):
    def __init__(self, app):
        super().__init__(application=app)
        
        # Setup layer shell
        LayerShell.init_for_window(self)
        LayerShell.set_layer(self, LayerShell.Layer.OVERLAY)
        LayerShell.set_anchor(self, LayerShell.Edge.TOP, True)
        LayerShell.set_anchor(self, LayerShell.Edge.BOTTOM, True)
        LayerShell.set_anchor(self, LayerShell.Edge.LEFT, True)
        LayerShell.set_anchor(self, LayerShell.Edge.RIGHT, True)
        LayerShell.set_keyboard_mode(self, LayerShell.KeyboardMode.EXCLUSIVE)
        
        # Make it closeable with ESC
        controller = Gtk.EventControllerKey()
        controller.connect('key-pressed', self.on_key_press)
        self.add_controller(controller)
        
        # Click to close
        click = Gtk.GestureClick()
        click.connect('pressed', lambda *_: self.close())
        self.add_controller(click)
        
        self.setup_ui()
        self.apply_css()
    
    def on_key_press(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape or keyval == Gdk.KEY_h or keyval == Gdk.KEY_q:
            self.close()
            return True
        return False
    
    def apply_css(self):
        css = f'''
            window {{
                background-color: {COLORS['bg']};
            }}
            .title {{
                font-size: 32px;
                font-weight: bold;
                color: {COLORS['title']};
            }}
            .subtitle {{
                font-size: 14px;
                color: {COLORS['desc']};
                opacity: 0.7;
            }}
            .category-title {{
                font-size: 14px;
                font-weight: bold;
                color: {COLORS['category']};
                padding: 8px 0 4px 0;
            }}
            .keybind-key {{
                font-size: 12px;
                font-weight: bold;
                font-family: monospace;
                color: {COLORS['key']};
                min-width: 180px;
            }}
            .keybind-desc {{
                font-size: 12px;
                color: {COLORS['desc']};
            }}
            .category-box {{
                padding: 12px;
                border-radius: 8px;
                background-color: rgba(0, 0, 0, 0.3);
                border: 1px solid {COLORS['border']};
            }}
            .close-hint {{
                font-size: 12px;
                color: {COLORS['desc']};
                opacity: 0.5;
            }}
        '''
        
        provider = Gtk.CssProvider()
        provider.load_from_string(css)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def setup_ui(self):
        # Scroll container for responsiveness
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        main_box.set_margin_top(10)
        main_box.set_margin_bottom(10)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)
        
        # FlowBox adapts to available width
        grid = Gtk.FlowBox()
        grid.set_valign(Gtk.Align.START)
        grid.set_halign(Gtk.Align.FILL)
        grid.set_hexpand(True)
        grid.set_selection_mode(Gtk.SelectionMode.NONE)
        grid.set_homogeneous(False)
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        
        # Add categories
        for category, binds in KEYBINDS.items():
            cat_box = self.create_category_box(category, binds)
            grid.append(cat_box)
        
        main_box.append(grid)
        
        # Close hint
        hint = Gtk.Label(label="Press ESC, Q, or click anywhere to close")
        hint.add_css_class("close-hint")
        main_box.append(hint)
        
        scroll.set_child(main_box)
        self.set_child(scroll)
    
    def create_category_box(self, title, binds):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.add_css_class("category-box")
        
        # Category title
        title_label = Gtk.Label(label=title, xalign=0)
        title_label.add_css_class("category-title")
        box.append(title_label)
        
        # Keybinds
        for key, desc in binds:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            
            key_label = Gtk.Label(label=key, xalign=0)
            key_label.add_css_class("keybind-key")
            row.append(key_label)
            
            desc_label = Gtk.Label(label=desc, xalign=0)
            desc_label.add_css_class("keybind-desc")
            row.append(desc_label)
            
            box.append(row)
        
        return box


class KeybindsApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='com.nordix.yggdrasil.keybinds')
    
    def do_activate(self):
        win = KeybindsOverlay(self)
        win.present()


def main():
    app = KeybindsApp()
    return app.run(None)


if __name__ == "__main__":
    main()
