# macos-sys-assist

A focused macOS automation MCP server for **reliable input simulation**, **window management**, and **window-specific screenshots** — the three things AppleScript and bash do poorly.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-purple.svg)](https://modelcontextprotocol.io)

---

## What Is This?

**macos-sys-assist** is a Python-based MCP server that fills the gaps where **bash + Chrome DevTools** fall short. It uses `pyobjc` (native macOS APIs) and **Core Graphics** for low-level input simulation — more reliable than AppleScript's `keystroke`.

### What It Does That bash/CDP Can't

| Capability | Why Not bash/CDP |
|---|---|
| **Core Graphics click/type/key** | AppleScript `keystroke` misses keys or fails silently. This uses `CGEventPost` — the same API macOS uses internally. |
| **Window-specific screenshots** | bash `screencapture` captures the full screen; cropping is tedious. This captures just the window you want. |
| **Precise window geometry** | `osascript` returns position inconsistently. This uses the Accessibility API for accurate pixel-level data. |
| **Multi-app window layouts** | Arrange 3+ apps at specific positions in one command. bash needs multiple chained `osascript` calls. |

### What It Does NOT Do (Use bash Instead)

| Tool | Why Use bash |
|---|---|
| Finding files | `find` / `mdfind` are simpler |
| Reading files | `cat` / `python3 -c` |
| Opening files | `open` command |
| App queries | `osascript -e 'tell app "System Events"...'` |
| Clipboard | `pbpaste` / `pbcopy` |
| Screen resolution | `system_profiler SPDisplaysDataType` |

---

## Quick Start

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/macos-sys-assist.git
cd macos-sys-assist
./setup.sh
```

### Grant Permissions

1. **Accessibility** — System Settings → Privacy & Security → Accessibility → Add Terminal/Python
2. **Screen Recording** (for screenshots) — System Settings → Privacy & Security → Screen Recording → Add Terminal/Python

### Configure Apps

Edit `allowed_apps.json` to control which apps can be automated.

---

## Usage

### Standalone Mode

```bash
./run.sh
```

### OpenCode Integration

Add to `opencode.jsonc`:

```json
"mcp": {
  "macos-sys-assist": {
    "type": "local",
    "command": ["/path/to/macos-sys-assist/run.sh"],
    "enabled": true
  }
}
```

### Direct Python Usage (via bash)

```bash
.venv/bin/python3 -c "
import sys
sys.path.insert(0, '.')
from macos.input import InputSimulator
InputSimulator().click_at(100, 200, 'left')
"
```

---

## Tool Reference

### Input Simulation (Core Graphics)

| Tool | Description | Security |
|------|-------------|----------|
| `click_at(x, y, button, double)` | Click at screen coordinates | ⚠️ Confirmation |
| `type_string(text)` | Type text character by character | ⚠️ Confirmation, max 500 chars |
| `press_key(combination)` | Press key combo (e.g., `cmd+tab`) | ⚠️ Blocked combos enforced |

More reliable than AppleScript — uses `CGEventPost` instead of `keystroke`.

### Window Management

| Tool | Description | Security |
|------|-------------|----------|
| `move_window(x, y)` | Move active window to coords | ⚠️ Confirmation |
| `resize_window(width, height)` | Resize active window | ⚠️ Confirmation |
| `get_window_geometry(pid)` | Get window position/size (Accurate) | Read-only |

Uses Accessibility API for pixel-level accuracy. More reliable than `osascript`.

### Screenshots (Requires Screen Recording Permission)

| Tool | Description |
|------|-------------|
| `screenshot(filepath, display_id)` | Capture full screen |
| `screenshot_window(pid, filepath)` | Capture **specific window only** — no cropping needed |
| `screenshot_region(x, y, w, h, filepath)` | Capture a screen region |
| `get_displays()` | Get all connected displays and resolutions |

---

## When to Use This vs bash

### ✅ Use macos-sys-assist when:

- AppleScript `keystroke` or `click` fails silently
- You need a screenshot of **just one window** without browser chrome
- You're arranging 3+ app windows at specific positions for a workspace
- The task requires **pixel-level coordinate accuracy**

### ❌ Use bash when:

- Finding files (`find`, `mdfind`, `ls`)
- Reading files (`cat`, `python3 -c`)
- Opening files (`open`)
- Basic clipboard (`pbpaste`, `pbcopy`)
- Checking what app is frontmost (`osascript`)
- Launching apps (`open -a`)

### 🔄 Use Chrome DevTools when:

- Interacting with web pages (clicking buttons, filling forms)
- Uploading files to websites (base64 injection into `<input type="file">`)
- Reading page content
- Navigating multi-page web flows

---

## Configuration

### `allowed_apps.json`

Controls which apps can be automated:

```json
{
  "allowed_apps": [
    {
      "bundle_id": "com.brave.Browser",
      "name": "Brave Browser",
      "allow_actions": true
    }
  ],
  "global_settings": {
    "require_confirmation_for_click": true,
    "require_confirmation_for_type": true,
    "max_string_length": 500,
    "blocked_key_combinations": [
      "cmd+q",
      "cmd+delete",
      "ctrl+alt+delete"
    ]
  }
}
```

---

## Project Structure

```
macos-sys-assist/
├── server.py                 # Main MCP server entry point
├── config.py                 # Configuration management
├── security.py               # Security validation layer
├── allowed_apps.json         # Application allow-list
├── requirements.txt          # Python dependencies
├── setup.sh                  # Installation script
├── run.sh                    # Wrapper script
├── macos/                    # Native macOS API wrappers
│   ├── accessibility.py     # App queries, PID lookup
│   ├── window.py            # Window move/resize/geometry
│   ├── input.py             # Core Graphics click/type/key
│   ├── screenshot.py        # Screen capture (full/window/region)
│   └── task_engine.py       # Multi-step task execution
└── tools/                    # MCP tool definitions
    ├── information.py       # get_window_geometry
    ├── actions.py           # click_at, type_string, press_key, move/resize
    └── screenshot.py        # screenshot, screenshot_window, screenshot_region, get_displays
```

---

## Roadmap

### Completed ✅
- [x] Core Graphics input simulation (click, type, key)
- [x] Window management (move, resize, geometry)
- [x] Window-specific screenshots (no cropping)
- [x] Security layer (allow-list, blocked keys, confirmations)

### Planned 📋
- [ ] **Folder Watcher** — Detect new files in Downloads, auto-organize by project
- [ ] **System State** — Battery, WiFi, disk space checks before long automations
- [ ] **Window Layout Presets** — Save/restore multi-app workspaces
- [ ] **Calendar Integration** — Meeting-aware automation scheduling

---

## Security Model

### Design Principles

1. **No Shell Access** — All operations use native macOS APIs
2. **Explicit Allow-List** — Only pre-approved apps can be controlled
3. **Human-in-the-Loop** — Invasive actions require user confirmation
4. **Input Validation** — Text length limits, key combo blocking

### What's Blocked

| Threat | Mitigation |
|--------|------------|
| Unauthorized app control | Application allow-list |
| Destructive key combos | Blocked combinations list |
| Excessive text input | Maximum string length (500) |
| Unconfirmed actions | Confirmation prompts |

---

## Troubleshooting

### "Accessibility permission not granted"

1. System Settings → Privacy & Security → Accessibility
2. Add Terminal.app or `.venv/bin/python3`
3. Ensure toggle is **ON**
4. Restart the server

### "Screen Recording permission required"

1. System Settings → Privacy & Security → Screen Recording
2. Add Terminal.app or `.venv/bin/python3`
3. Ensure toggle is **ON**
4. Restart the server

### "App not in allow-list"

1. Find the app's bundle ID: `osascript -e 'id of app "AppName"'`
2. Add it to `allowed_apps.json`
3. Restart the server

---

## License

MIT License — see [LICENSE](LICENSE)

---

## Acknowledgments

Built for the [OpenCode](https://opencode.ai) AI assistant framework.
Uses the [Model Context Protocol](https://modelcontextprotocol.io) for tool integration.
Powered by `pyobjc` for native macOS API access.
