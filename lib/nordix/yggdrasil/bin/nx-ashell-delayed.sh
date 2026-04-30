#!/bin/bash
killall -SIGUSR2 ashell

# just because it looks fun when the top bar comes bouncing forward
sleep 1
exec ashell --config-path ~/.config/ashell/config.toml &