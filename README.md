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
- **Multi-Step Task Engine** — Parse complex prompts into executable chains of actions
- **File System** — Find, read, and open files safely
- **Screenshots** — Capture full screen, windows, or regions
- **Clipboard** — Read and write clipboard contents
- **App Lifecycle** — Launch, quit, and focus applications
- **Window Management** — Move, resize, snap to halves/quarters
- **Input Simulation** — Click, type, press key combinations

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
from macos.accessibility import AccessibilityWrapper
a = AccessibilityWrapper()
print(a.get_frontmost_app())
"
```

---

## Complete Tool Reference

### App Intelligence (Read-Only)

| Tool | Description | Returns |
|------|-------------|---------|
| `get_active_app` | Get currently focused application | name, bundle_id, pid |
| `list_open_apps` | List all running apps with windows | name, bundle_id, pid |
| `get_app_info(name/bundle_id)` | Info about a specific app | name, bundle_id, pid, active |
| `get_screen_resolution` | Get primary display resolution | width, height |
| `get_displays` | Get all connected displays | list of displays |

### File System (Read-Only)

| Tool | Description | Returns |
|------|-------------|---------|
| `find_files(directory, pattern, recursive)` | Search files by name/pattern | file list with paths, sizes |
| `read_file(filepath, max_lines)` | Read text file contents | content, lines, size |
| `list_directory(directory)` | List directory contents | files, folders, counts |
| `open_file(filepath)` | Open file in default app | status, filename |
| `get_clipboard()` | Read clipboard text | content, length |
| `clipboard_has_text()` | Check clipboard state | boolean, length |

### Input Simulation

| Tool | Description | Security |
|------|-------------|----------|
| `click_at(x, y, button, double)` | Click at screen coordinates | ⚠️ Confirmation |
| `type_string(text)` | Type text character by character | ⚠️ Confirmation |
| `press_key(combination)` | Press key combo (e.g., `cmd+tab`) | ⚠️ Blocked combos |
| `set_clipboard(text)` | Write text to clipboard | ⚠️ Confirmation |

### Window Management

| Tool | Description | Security |
|------|-------------|----------|
| `move_window(x, y)` | Move active window to coords | ⚠️ Confirmation |
| `resize_window(width, height)` | Resize active window | ⚠️ Confirmation |
| `get_window_geometry(pid)` | Get window position/size | Read-only |

### App Lifecycle

| Tool | Description | Security |
|------|-------------|----------|
| `launch_app(name/bundle_id)` | Launch an application | ⚠️ Allow-list |
| `quit_app(name/bundle_id, force)` | Quit an application | ⚠️ Allow-list |
| `focus_app(name/bundle_id)` | Bring app to front | ⚠️ Allow-list |

### Screenshots (Requires Screen Recording Permission)

| Tool | Description |
|------|-------------|
| `screenshot(filepath, display_id)` | Capture full screen |
| `screenshot_window(pid, filepath)` | Capture specific window |
| `screenshot_region(x, y, w, h, filepath)` | Capture screen region |

---

## Multi-Step Task Engine

### How It Works

The task engine decomposes complex natural language prompts into executable steps. Each step's output can be chained into the next step's input.

### Supported Prompt Patterns

| Pattern | Example |
|---------|---------|
| `find X in Y and open it` | "Find readme.md in Downloads and open it" |
| `open X in Y folder` | "Open data.csv in downloads folder" |
| `find and open X` | "Find and open report.pdf" |
| `open X` (filename) | "Open notes.txt" (auto-searches Downloads) |
| `launch X` | "Launch Safari" |
| `list X` | "List Downloads" |
| `find X in Y` | "Find all .pdf files in Documents" |
| `what app is focused` | "What app is currently focused?" |

### Example: Find and Open File

```python
from macos.task_engine import PromptParser, TaskEngine
from macos.filesystem import FileSystemManager
from macos.app_lifecycle import AppLifecycleManager
from macos.window import WindowManager
from macos.input import InputSimulator
from macos.accessibility import AccessibilityWrapper

# Parse the prompt
steps = PromptParser.parse("Find readme.md in Downloads and open it")
# Output:
#   Step 1: find_files(directory="~/Downloads", pattern="readme.md")
#   Step 2: open_file(filepath=<result_of_step_1>)

# Execute
engine = TaskEngine(
    FileSystemManager(),
    AppLifecycleManager(),
    WindowManager(),
    InputSimulator(),
    AccessibilityWrapper()
)
result = engine.execute(steps)
print(result.final_output)
# Output:
#   ✅ Find 'readme.md' in ~/Downloads: Found 1 items
#   ✅ Open the found file
```

---

## Configuration

### `allowed_apps.json`

Controls which apps can be automated and what actions are allowed:

```json
{
  "allowed_apps": [
    {
      "bundle_id": "com.apple.Safari",
      "name": "Safari",
      "allow_actions": true
    },
    {
      "bundle_id": "com.microsoft.VSCode",
      "name": "Visual Studio Code",
      "allow_actions": true
    }
  ],
  "global_settings": {
    "require_confirmation_for_click": true,
    "require_confirmation_for_type": true,
    "require_confirmation_for_key": false,
    "max_string_length": 500,
    "blocked_key_combinations": [
      "cmd+q",
      "cmd+delete",
      "ctrl+alt+delete"
    ]
  }
}
```

### Finding Bundle IDs

```bash
osascript -e 'id of app "Safari"'
# Output: com.apple.Safari
```

### Common Bundle IDs

| App | Bundle ID |
|-----|-----------|
| Safari | `com.apple.Safari` |
| Google Chrome | `com.google.Chrome` |
| Brave Browser | `com.brave.Browser` |
| Visual Studio Code | `com.microsoft.VSCode` |
| Terminal | `com.apple.Terminal` |
| Finder | `com.apple.finder` |

---

## Security Model

### Design Principles

1. **Least Privilege** — Only minimum necessary capabilities exposed
2. **No Shell Access** — All operations use native macOS APIs
3. **Explicit Allow-List** — Only pre-approved apps can be controlled
4. **Human-in-the-Loop** — Invasive actions require user confirmation
5. **Input Validation** — Text length limits, key combo blocking

### 6-Layer Security

```
1. Application Allow-List    → Only approved bundle IDs pass
2. Action Permission Check   → Per-app allow_actions flag
3. Input Validation          → Text length, key combo validation
4. Blocked Operations        → Destructive shortcuts rejected
5. Confirmation Prompts      → User approval for invasive actions
6. Native API Only           → No shell, no AppleScript
```

### What's Blocked

| Threat | Mitigation |
|--------|------------|
| Arbitrary command execution | No `subprocess` or shell access |
| Unauthorized app control | Application allow-list |
| Destructive key combos | Blocked combinations list |
| Excessive text input | Maximum string length (500) |
| Unconfirmed actions | Confirmation prompts |

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
│   ├── accessibility.py     # App queries, screen info
│   ├── window.py            # Window move/resize
│   ├── input.py             # Mouse/keyboard simulation
│   ├── filesystem.py        # File search, read, open
│   ├── app_lifecycle.py     # Launch, quit, focus apps
│   ├── screenshot.py        # Screen capture
│   ├── clipboard.py         # Clipboard read/write
│   └── task_engine.py       # Multi-step task execution
└── tools/                    # MCP tool definitions
    ├── information.py       # Read-only app/screen tools
    ├── actions.py           # Input/window action tools
    ├── filesystem.py        # File system tools
    ├── screenshot.py        # Screenshot tools
    └── clipboard.py         # Clipboard tools
```

---

## Roadmap

### Completed ✅
- [x] Base MCP server with app intelligence and input simulation
- [x] Window management (move, resize, snap)
- [x] Application lifecycle (launch, quit, focus)
- [x] File system operations (find, read, open, list)
- [x] Screenshot capability (full screen, window, region)
- [x] Clipboard operations (read, write, check)
- [x] Multi-step task engine with prompt parser

### Planned 📋
- [ ] Push to GitHub as public repository
- [ ] Notification center integration
- [ ] Volume/brightness control
- [ ] Multi-monitor window management
- [ ] Drag and drop simulation

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

### MCP tools not appearing in OpenCode UI

**Known OpenCode bug.** The server loads correctly but tools don't appear in the UI. Use the bash fallback method:

```bash
.venv/bin/python3 -c "import sys; sys.path.insert(0, '.'); from macos.accessibility import AccessibilityWrapper; print(AccessibilityWrapper().get_frontmost_app())"
```

---

## License

MIT License — see [LICENSE](LICENSE)

---

## Acknowledgments

Built for the [OpenCode](https://opencode.ai) AI assistant framework.
Uses the [Model Context Protocol](https://modelcontextprotocol.io) for tool integration.
Powered by `pyobjc` for native macOS API access.
