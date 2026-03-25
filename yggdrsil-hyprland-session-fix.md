# Yggdrasil Hyprland Session Fix

## The Problem

Hyprland's `start-hyprland` binary uses `fork()` to spawn the Hyprland compositor. When launched via `greetd` (or any login manager), `start-hyprland` itself is correctly placed in the logind session scope (e.g. `session-3.scope`), but the forked Hyprland process — and all of its children — land in the root cgroup (`0::/`).

This means **every process in your desktop session** (terminals, polkit agents, file managers, etc.) exists outside of your logind session as far as systemd is concerned.

### What breaks

- **Polkit authentication fails silently.** `pkexec` and graphical polkit agents cannot determine which session a process belongs to, so authentication is always denied — even with the correct password.
- **Any software relying on logind session tracking** may behave unexpectedly.

### Affected setup

- Hyprland ≥ 0.52.0 using `start-hyprland`
- Any login manager (greetd, SDDM, etc.)
- systemd-logind for session management

### Root cause

In [`start/src/core/Instance.cpp`](https://github.com/hyprwm/Hyprland/blob/main/start/src/core/Instance.cpp), the `runHyprlandThread()` method does a plain `fork() + execvp()` without any systemd scope or cgroup placement. The child process breaks out of the session scope and lands in the root cgroup.

`start-hyprland` is essentially a crash-recovery watchdog — it restarts Hyprland in safe mode if it crashes. It performs **no session management or cgroup handling**.

### Verification

You can verify the issue on your system:

```bash
# start-hyprland sits in the correct scope
cat /proc/$(pgrep -x start-hyprland)/cgroup
# Example output: 0::/user.slice/user-1000.slice/session-3.scope

# But Hyprland and everything it spawns is in root cgroup
cat /proc/$(pgrep -x Hyprland)/cgroup
# Output: 0::/

# Your shell is also orphaned
cat /proc/self/cgroup
# Output: 0::/
```

## The Fix

This workaround uses a systemd socket-activated service running as root. After Hyprland and its child processes have started, the service moves all misplaced processes from `0::/` back into the correct session scope.

### How it works

1. Hyprland starts via `start-hyprland` (cgroup broken as usual)
2. Hyprland's autostart runs the trigger script after a short delay
3. The trigger sends a message to a Unix socket
4. A systemd service (running as root) activates and:
   - Finds `start-hyprland`'s PID (which is in the correct scope)
   - Reads the correct session scope from its cgroup
   - Moves all user-owned processes stuck in `0::/` into that scope
5. Polkit and session tracking work correctly

### Files

| File | Location | Purpose |
|------|----------|---------|
| `nordix-cgroup-fix.socket` | `/etc/systemd/system/` | Socket unit listening for trigger |
| `nordix-cgroup-fix.service` | `/etc/systemd/system/` | Service that performs the cgroup fix |
| `nordix-cgroup-fix` | `/usr/lib/nordix/yggdrasil/session/` | Script that moves processes to correct scope |
| `nordix-cgroup-trigger` | `/usr/lib/nordix/yggdrasil/session/` | Trigger script called from Hyprland autostart |

### Installation

```bash
# Copy systemd units
sudo cp nordix-cgroup-fix.socket nordix-cgroup-fix.service /etc/systemd/system/

# Copy scripts
sudo mkdir -p /usr/lib/nordix/yggdrasil/session
sudo cp nordix-cgroup-fix /usr/lib/nordix/yggdrasil/session/
sudo cp nordix-cgroup-trigger /usr/lib/nordix/yggdrasil/session/
sudo chmod +x /usr/lib/nordix/yggdrasil/session/nordix-cgroup-*

# Enable the socket
sudo systemctl daemon-reload
sudo systemctl enable --now nordix-cgroup-fix.socket
```

Add to your Hyprland autostart config:

```
exec-once = /usr/lib/nordix/yggdrasil/session/nordix-cgroup-trigger &
```

### Dependencies

- `socat` — used by the trigger script to communicate with the socket
- `systemd` — for socket activation and cgroup management

### After reboot

Verify the fix is working:

```bash
# Check that your shell is in a session scope
cat /proc/self/cgroup
# Expected: 0::/user.slice/user-1000.slice/session-X.scope

# Polkit should now work
pkexec whoami
# Expected: prompts for password and returns "root"
```

## Notes

- This is a **workaround**, not a permanent solution. The proper fix belongs in `start-hyprland` upstream - it should either use `systemd-run --scope` when forking Hyprland, or place the child process in the correct cgroup explicitly.
- The 3-second delay in the trigger script ensures most autostart processes have been spawned before the fix runs. If you have slow-starting applications, you may want to increase this delay or run the trigger a second time.
- This fix is part of [Nordix Linux](https://github.com/nordix) - Yggdrasil desktop environment.

## License

 * SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0                            
 * [**Nordix - license**](https://polyformproject.org/licenses/noncommercial/1.0.0) 
 * Copyright (c) 2025 Jimmy Källhagen                                               
 * Part of Nordix - https://github.com/jimmykallhagen/Nordix                        
 * Nordix and Yggdrasil are trademarks of Jimmy Källhagen 
