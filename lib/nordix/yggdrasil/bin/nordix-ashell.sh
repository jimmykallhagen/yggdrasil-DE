#!/bin/bash
##========================================================##
 # SPDX-License-Identifier: GPL-3.0-or-later              #
 # Copyright (c) 2025 Jimmy Källhagen                     #
 # Part of Yggdrasil - Nordix desktop environment         #
 # Nordix and Yggdrasil are trademarks of Jimmy Källhagen #
##========================================================##

# * Restart top bar (ashell) with Nordix ashell theme
killall -SIGUSR2 ashell
exec ashell --config-path ~/.config/nordix/yggdrasil/nordix-ashell-theme/nordix-ashell-theme.toml &
