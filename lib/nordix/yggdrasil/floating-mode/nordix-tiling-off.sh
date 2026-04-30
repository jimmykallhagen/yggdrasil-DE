#!/bin/bash
    grep -q 'floating-mode/floating.conf' ~/.config/hypr/hyprland.conf \
    && sed -i 's|^#source = /usr/share/nordix/yggdrasil/floating-mode/floating.conf|source = /usr/share/nordix/yggdrasil/floating-mode/floating.conf|' ~/.config/hypr/hyprland.conf \
    || echo 'source = /usr/share/nordix/yggdrasil/floating-mode/floating.conf' >> ~/.config/hypr/hyprland.conf
