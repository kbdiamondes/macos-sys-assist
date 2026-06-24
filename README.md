# macos-sys-assist

A secure, constraint-based macOS OS-level automation MCP server for AI assistants.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-purple.svg)](https://modelcontextprotocol.io)

---

## What Is This?

**macos-sys-assist** is a Python-based MCP (Model Context Protocol) server that enables AI assistants to safely interact with macOS at the system level. It uses **native macOS Accessibility APIs** via `pyobjc`, eliminating the risks associated with shell execution.

### Key Features

- **No Shell Execution** — All operations use native macOS APIs, never `os.system()` or `subprocess`
- **Application Allow-List** — Only pre-approved apps can be interacted with
- **Confirmation Prompts** — Invasive actions require user approval
- **Input Validation** — Text length limits and key combination blocking
- **Window Management** — Move, resize, snap to halves/quarters
- **Input Simulation** — Click, type, press key combinations
- **App Intelligence** — Query focused app, list running apps

---

## Quick Start

### Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/macos-sys-assist.git
cd macos-sys-assist

# Run setup script
./setup.sh
```

### Grant Accessibility Permissions

1. Open **System Settings** → **Privacy & Security** → **Accessibility**
2. Click the **+** button
3. Add Terminal.app or the Python interpreter from `.venv/bin/python3`
4. Ensure the toggle is **ON**

### Configure Allowed Apps

Edit `allowed_apps.json` to add apps you want to control:

```json
{
  "allowed_apps": [
    {
      "bundle_id": "com.apple.Safari",
      "name": "Safari",
      "allow_actions": true
    }
  ]
}
```

---

## Usage

### Running the Server

```bash
./run.sh
```

### OpenCode Integration

Add to your `opencode.jsonc`:

```json
"mcp": {
  "macos-sys-assist": {
    "type": "local",
    "command": ["/path/to/macos-sys-assist/run.sh"],
    "enabled": true
  }
}
```

### Available Tools

#### Information Tools (Read-Only)

| Tool | Description |
|------|-------------|
| `get_active_app` | Get the currently focused application |
| `list_open_apps` | List all running applications with visible windows |
| `get_window_geometry` | Get position and size of a window |
| `get_screen_resolution` | Get primary screen resolution |

#### Action Tools (Require Confirmation)

| Tool | Description |
|------|-------------|
| `move_window` | Move the active window to specified coordinates |
| `resize_window` | Resize the active window to specified dimensions |
| `click_at` | Simulate a mouse click at screen coordinates |
| `type_string` | Type a string character by character |
| `press_key` | Press a key or key combination |

---

## Examples

### Get Focused App

```python
# Via Python
from macos.accessibility import AccessibilityWrapper
a = AccessibilityWrapper()
print(a.get_frontmost_app())
# {'bundle_id': 'com.brave.Browser', 'name': 'Brave Browser', 'pid': '634'}
```

### Move Window to Left Half

```python
from macos.accessibility import AccessibilityWrapper
from macos.window import WindowManager

a = AccessibilityWrapper()
wm = WindowManager()

app = a.get_frontmost_app()
pid = int(app['pid'])
screen = a.get_screen_resolution()

wm.resize_window(pid, screen['width'] // 2, screen['height'])
wm.move_window(pid, 0, 0)
```

### Type Text

```python
from macos.input import InputSimulator
inp = InputSimulator()
inp.type_string("Hello, World!")
```

---

## Security Model

### Design Principles

1. **Least Privilege** — Only minimum necessary capabilities exposed
2. **No Shell Access** — All operations use native macOS APIs
3. **Explicit Allow-List** — Only pre-approved apps can be controlled
4. **Human-in-the-Loop** — Invasive actions require user confirmation

### What's Blocked

| Threat | Mitigation |
|--------|------------|
| Arbitrary command execution | No `subprocess`, `os.system`, or shell access |
| Unauthorized app control | Application allow-list enforcement |
| Destructive key combos | Blocked combinations list |
| Excessive text input | Maximum string length limit |

---

## Configuration

### `allowed_apps.json`

```json
{
  "allowed_apps": [
    {
      "bundle_id": "com.apple.Safari",
      "name": "Safari",
      "allow_actions": true
    }
  ],
  "global_settings": {
    "require_confirmation_for_click": true,
    "require_confirmation_for_type": true,
    "require_confirmation_for_key": false,
    "max_string_length": 500,
    "blocked_key_combinations": ["cmd+q", "cmd+delete"]
  }
}
```

### Finding Bundle IDs

```bash
osascript -e 'id of app "Safari"'
# Output: com.apple.Safari
```

---

## Project Structure

```
macos-sys-assist/
├── server.py              # Main MCP server entry point
├── config.py              # Configuration management
├── security.py            # Security validation layer
├── allowed_apps.json      # Application allow-list
├── requirements.txt       # Python dependencies
├── setup.sh               # Installation script
├── run.sh                 # Wrapper script
├── macos/                 # Native macOS API wrappers
│   ├── accessibility.py   # Accessibility API
│   ├── window.py          # Window management
│   └── input.py           # Input simulation
└── tools/                 # MCP tool definitions
    ├── information.py     # Read-only tools
    └── actions.py         # Action tools
```

---

## Roadmap

See [IMPROVEMENT_PLAN.md](IMPROVEMENT_PLAN.md) for the full roadmap.

**Upcoming features:**
- File system operations (find, read, open files)
- Screenshot capability
- Clipboard operations
- App launch/quit/focus
- Multi-step task engine

---

## Contributing

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## License

MIT License - see [LICENSE](LICENSE)

---

## Acknowledgments

Built for the [OpenCode](https://opencode.ai) AI assistant framework.
Uses the [Model Context Protocol](https://modelcontextprotocol.io) for tool integration.
