## Yggdrasil's Theme - Nordix Dynamic Theme

Yggdrasil comes with a theme system based on pywal, Nordix Dynamic Theme.

Nordix Dynamic Theme is a python script that uses a number of tools and nordix templates to set color and theme on:

- GTK-3
- GTK-4
- QT
- Firefox/Librewolf

Nordix Dynamic Theme consists of:
- nordix-wallpaper-loop.sh
- nordix-dynamic-theme

**You can configure Nordix Dynamic Theme in these config files:**
 - ~/.config/nordix/nordix-theme/nordix-wallpaper-loop.conf
 - ~/.config/nordix/nordix-theme/nordix-dynamic-theme.conf

It works like this, nordix-wallpaper-loop.sh is a loop that changes wallpaper for you automatically, it chooses random wallpaper in ~/Pictures/wallpaper. nordix-wallpapper-loop.sh works with these backends:
- awww
- mpvpaper

However, it is only with awww that it automatically changes wallpaper, if you use mpvpaper you have to manually stop the current wallpaper and start a new one from the waypaper GUI.

nordix-dynamic-theme.py is triggered by waypaper.ini, so every time waypaper changes wallpaper, nordix-dynamic-theme.py runs and takes color samples from the new wallpaper and applies this to gtk3, gtk4, qt, firefox/librewolf and also has a small own section in the theme for thunar

you can choose how long nordix-wallpaper-loop.sh should have for interval in its config file, you can also turn off the loop and only have a constant wallpaper. 
Config for nordix-dynamic-theme.py you can adjust: 
- gtk/qt theme variables
- pywal backend
- font
- cursor
- Icon theme

Nordix template for GTK-3 is based on the adw-gtk-theme-dark theme

You find the original sorcecode for adw-gtk-theme here:
- [**adw-gtk3**](https://github.com/lassekongo83/adw-gtk3)
  
