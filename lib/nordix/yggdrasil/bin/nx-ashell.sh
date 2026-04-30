#!/bin/bash
killall -SIGUSR2 ashell
exec ashell --config-path ~/.config/ashell/config.toml &