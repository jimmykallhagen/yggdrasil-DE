#!/bin/bash

killall -SIGUSR2 zfs-system-monitor
killall -SIGUSR2 zfs-arc-monitor

exec zfs-arc-monitor &
