## Yggdrasil's Theme - Nordix Dynamic Theme

**Yggdrasil comes with a theme system based on pywal, Nordix Dynamic Theme.**

---

Nordix Dynamic Theme consists of:
- nordix-wallpaper-loop.sh
- nordix-dynamic-theme

---

**Nordix Dynamic Theme is a python script that uses a number of tools and nordix templates to set color and theme on:**

- GTK-3
- GTK-4
- QT
- Firefox/Librewolf

---

**You can configure Nordix Dynamic Theme in these config files:**
 - ~/.config/nordix/nordix-theme/nordix-wallpaper-loop.conf
 - ~/.config/nordix/nordix-theme/nordix-dynamic-theme.conf

---

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

---

## MPV/MPVPaper

 Norrdix-Yggdrasil Comes with Nordix MPV Config, so that the different video technologies are correctly selected for a very good default and to make sure mpv runs on GPU and not CPU

---

**Nordix template for GTK-3 is based on the adw-gtk-theme-dark theme**

You find the original sorcecode here:
- [**adw-gtk3**](https://github.com/lassekongo83/adw-gtk3)
- [**Pywal16**](https://github.com/eylles/pywal16)
- [**Waypaper**](https://github.com/anufrievroman/waypaper)
- [**AWWW**](https://codeberg.org/LGFae/awww)
- [**MPVPaper**](https://github.com/GhostNaN/mpvpaper)
- [**PywalFox**](https://github.com/frewacom/pywalfox)

Yggdrasil comes with Swengine default as wallpaper store:
- [**Swengine**](https://github.com/saverinonrails/swengine)

  
