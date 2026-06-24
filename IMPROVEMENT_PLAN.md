# macOS System Assistant — Improvement Plan

**Goal:** Transform macos-sys-assist from a basic automation tool into a **complex task execution engine** capable of handling multi-step prompts like:

> "Find Readme.md on Downloads Folder and open it"

---

## Target Capabilities

### End Goal Examples

| Prompt | Expected Behavior |
|--------|-------------------|
| "Find Readme.md on Downloads Folder and open it" | Search Downloads → Locate file → Open in default app |
| "Take a screenshot and save it to Desktop" | Capture screen → Save to ~/Desktop/screenshot.png |
| "Copy the text from this window and paste it into Notes" | Read clipboard → Switch to Notes → Paste |
| "Open Safari, go to google.com, and search for 'AI news'" | Launch Safari → Navigate → Type query → Submit |
| "Arrange my windows side by side" | Left half: current app, Right half: Finder |
| "What's my battery status?" | Query system → Return battery info |

---

## Improvement Roadmap

### Phase 0: GitHub Repository Setup (PRIORITY #1)

**Objective:** Push the complete macos-sys-assist MCP server to GitHub

#### Checklist

- [ ] **Prepare repository**
  - [ ] Create new GitHub repo: `macos-sys-assist`
  - [ ] Add `.gitignore` (exclude `.venv/`, `__pycache__/`, `.DS_Store`)
  - [ ] Add `LICENSE` (MIT recommended)

- [ ] **Clean up codebase**
  - [ ] Remove any hardcoded user paths
  - [ ] Add environment variable support for paths
  - [ ] Ensure all imports are correct
  - [ ] Add type hints throughout

- [ ] **Documentation**
  - [ ] Update `README.md` with installation instructions
  - [ ] Add `CONTRIBUTING.md`
  - [ ] Add `CHANGELOG.md`
  - [ ] Create GitHub Actions CI (optional)

- [ ] **Publish**
  - [ ] Push to GitHub
  - [ ] Create release v1.0.0
  - [ ] Add badges (Python version, license)

---

### Phase 1: File System Operations

**Objective:** Enable file discovery, reading, and opening

#### New Tools

```python
# 1. Find files by name/pattern
find_files(
    directory: str = "~/Downloads",
    pattern: str = "*.md",
    recursive: bool = False
) -> List[Dict]

# Returns: [{"name": "Readme.md", "path": "/Users/.../Downloads/Readme.md", "size": 1234}]

# 2. Read file contents (safe, text files only)
read_file(
    filepath: str,
    max_lines: int = 100
) -> Dict

# Returns: {"content": "...", "lines": 42, "size": 1234}

# 3. Open file with default app
open_file(
    filepath: str
) -> Dict

# Returns: {"status": "success", "app": "TextEdit"}

# 4. List directory contents
list_directory(
    filepath: str = "~/Downloads",
    show_hidden: bool = False
) -> Dict

# Returns: {"files": [...], "folders": [...], "total": 42}
```

#### Implementation

```python
# macos/filesystem.py

import os
import glob
from pathlib import Path
from typing import List, Dict

class FileSystemManager:
    """Safe file system operations for macOS."""
    
    # Restricted paths (cannot be accessed)
    RESTRICTED_PATHS = [
        "/System",
        "/Library/Keychains",
        "~/.ssh",
        "~/.gnupg",
    ]
    
    def find_files(self, directory: str, pattern: str, recursive: bool = False) -> List[Dict]:
        """Find files matching a pattern."""
        dir_path = Path(directory).expanduser()
        
        if recursive:
            files = dir_path.rglob(pattern)
        else:
            files = dir_path.glob(pattern)
        
        return [
            {
                "name": f.name,
                "path": str(f),
                "size": f.stat().st_size if f.exists() else 0,
                "is_file": f.is_file(),
            }
            for f in files
            if f.exists()
        ]
    
    def read_file(self, filepath: str, max_lines: int = 100) -> Dict:
        """Read text file contents (safe, limited)."""
        path = Path(filepath).expanduser()
        
        if not path.exists():
            return {"error": "File not found"}
        
        if not path.is_file():
            return {"error": "Not a file"}
        
        # Check file size (max 1MB)
        if path.stat().st_size > 1_000_000:
            return {"error": "File too large (max 1MB)"}
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = [next(f) for _ in range(max_lines)]
            return {
                "content": "".join(lines),
                "lines": len(lines),
                "size": path.stat().st_size,
            }
        except UnicodeDecodeError:
            return {"error": "Binary file, cannot read as text"}
    
    def open_file(self, filepath: str) -> Dict:
        """Open file with default application."""
        import subprocess
        
        path = Path(filepath).expanduser()
        
        if not path.exists():
            return {"error": "File not found"}
        
        # Use open command (macOS native)
        result = subprocess.run(
            ["open", str(path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return {"status": "success", "filepath": str(path)}
        else:
            return {"error": result.stderr}
    
    def list_directory(self, directory: str = "~/Downloads", show_hidden: bool = False) -> Dict:
        """List directory contents."""
        dir_path = Path(directory).expanduser()
        
        if not dir_path.exists():
            return {"error": "Directory not found"}
        
        if not dir_path.is_dir():
            return {"error": "Not a directory"}
        
        files = []
        folders = []
        
        for item in dir_path.iterdir():
            if not show_hidden and item.name.startswith('.'):
                continue
            
            item_info = {
                "name": item.name,
                "path": str(item),
                "size": item.stat().st_size if item.is_file() else 0,
            }
            
            if item.is_file():
                files.append(item_info)
            elif item.is_dir():
                folders.append(item_info)
        
        return {
            "files": sorted(files, key=lambda x: x["name"]),
            "folders": sorted(folders, key=lambda x: x["name"]),
            "total_files": len(files),
            "total_folders": len(folders),
        }
```

---

### Phase 2: Application Lifecycle Management

**Objective:** Complete control over app lifecycle

#### New Tools

```python
# 1. Launch an app
launch_app(
    app_name: str = None,
    bundle_id: str = None
) -> Dict

# 2. Quit an app
quit_app(
    app_name: str = None,
    bundle_id: str = None,
    force: bool = False
) -> Dict

# 3. Focus/activate an app
focus_app(
    app_name: str = None,
    bundle_id: str = None
) -> Dict

# 4. Get app info
get_app_info(
    app_name: str = None,
    bundle_id: str = None
) -> Dict
```

#### Implementation

```python
# macos/app_lifecycle.py

import subprocess
import ApplicationServices as AppServices

class AppLifecycleManager:
    """Manage application lifecycle on macOS."""
    
    def launch_app(self, app_name: str = None, bundle_id: str = None) -> Dict:
        """Launch an application."""
        workspace = AppServices.NSWorkspace.sharedWorkspace()
        
        if bundle_id:
            workspace.launchApplication_(bundle_id)
        elif app_name:
            workspace.launchApplication_(app_name)
        else:
            return {"error": "Must provide app_name or bundle_id"}
        
        return {"status": "success", "launched": app_name or bundle_id}
    
    def quit_app(self, app_name: str = None, bundle_id: str = None, force: bool = False) -> Dict:
        """Quit an application."""
        workspace = AppServices.NSWorkspace.sharedWorkspace()
        
        # Find the app
        apps = workspace.runningApplications()
        target_app = None
        
        for app in apps:
            if bundle_id and app.bundleIdentifier() == bundle_id:
                target_app = app
                break
            elif app_name and app.localizedName() == app_name:
                target_app = app
                break
        
        if not target_app:
            return {"error": "App not found or not running"}
        
        if force:
            target_app.forceTerminate()
        else:
            target_app.terminate()
        
        return {"status": "success", "quit": app_name or bundle_id}
    
    def focus_app(self, app_name: str = None, bundle_id: str = None) -> Dict:
        """Bring app to front."""
        workspace = AppServices.NSWorkspace.sharedWorkspace()
        apps = workspace.runningApplications()
        
        for app in apps:
            if bundle_id and app.bundleIdentifier() == bundle_id:
                app.activateWithOptions_(AppServices.NSApplicationActivateIgnoringOtherApps)
                return {"status": "success", "focused": app.localizedName()}
            elif app_name and app.localizedName() == app_name:
                app.activateWithOptions_(AppServices.NSApplicationActivateIgnoringOtherApps)
                return {"status": "success", "focused": app_name}
        
        return {"error": "App not found"}
```

---

### Phase 3: Visual Feedback (Screenshots)

**Objective:** Capture screen for verification and debugging

#### New Tools

```python
# 1. Capture full screen
screenshot(
    filepath: str = "/tmp/screenshot.png",
    display_id: int = 0
) -> Dict

# 2. Capture specific window
screenshot_window(
    pid: int,
    filepath: str = "/tmp/window.png"
) -> Dict

# 3. Capture region
screenshot_region(
    x: int, y: int,
    width: int, height: int,
    filepath: str = "/tmp/region.png"
) -> Dict
```

#### Implementation

```python
# macos/screenshot.py

import subprocess
from pathlib import Path

class ScreenshotManager:
    """Capture screenshots on macOS."""
    
    def screenshot(self, filepath: str = "/tmp/screenshot.png", display_id: int = 0) -> Dict:
        """Capture full screen."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use screencapture command (macOS native)
        cmd = ["screencapture", "-x", str(path)]
        
        if display_id > 0:
            cmd.extend(["-D", str(display_id)])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return {
                "status": "success",
                "filepath": str(path),
                "size": path.stat().st_size,
            }
        else:
            return {"error": result.stderr}
    
    def screenshot_window(self, pid: int, filepath: str = "/tmp/window.png") -> Dict:
        """Capture specific window by PID."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use screencapture with -l flag for window ID
        result = subprocess.run(
            ["screencapture", "-l", str(pid), "-x", str(path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return {"status": "success", "filepath": str(path)}
        else:
            return {"error": result.stderr}
```

---

### Phase 4: Clipboard Operations

**Objective:** Read/write clipboard contents

#### New Tools

```python
# 1. Get clipboard text
get_clipboard() -> Dict

# 2. Set clipboard text
set_clipboard(text: str) -> Dict

# 3. Get clipboard image (if available)
get_clipboard_image(filepath: str = "/tmp/clipboard.png") -> Dict
```

---

### Phase 5: Multi-Step Task Engine

**Objective:** Execute complex, multi-step prompts

#### Task Definition Format

```python
# macos/task_engine.py

from typing import List, Dict, Callable

class TaskStep:
    """Single step in a task."""
    def __init__(self, action: str, params: Dict, description: str = ""):
        self.action = action
        self.params = params
        self.description = description

class TaskEngine:
    """Execute multi-step tasks."""
    
    def __init__(self):
        self.actions: Dict[str, Callable] = {
            "find_files": self.fs.find_files,
            "open_file": self.fs.open_file,
            "launch_app": self.app.launch_app,
            "focus_app": self.app.focus_app,
            "type_string": self.input.type_string,
            "press_key": self.input.press_key,
            "click_at": self.input.click_at,
            "screenshot": self.screenshot.screenshot,
            # ... more actions
        }
    
    def execute(self, steps: List[TaskStep]) -> Dict:
        """Execute a sequence of steps."""
        results = []
        
        for i, step in enumerate(steps):
            if step.action not in self.actions:
                return {"error": f"Unknown action: {step.action}"}
            
            result = self.actions[step.action](**step.params)
            results.append({
                "step": i + 1,
                "action": step.action,
                "description": step.description,
                "result": result,
            })
            
            if "error" in result:
                return {
                    "status": "failed",
                    "failed_at_step": i + 1,
                    "results": results,
                }
        
        return {"status": "success", "results": results}
```

#### Example: "Find Readme.md on Downloads Folder and open it"

```python
# AI would generate these steps:
task_steps = [
    TaskStep(
        action="find_files",
        params={"directory": "~/Downloads", "pattern": "Readme.md"},
        description="Find Readme.md in Downloads"
    ),
    TaskStep(
        action="open_file",
        params={"filepath": "$result[0].path"},  # Reference previous result
        description="Open the found file"
    ),
]

# Execute
result = task_engine.execute(task_steps)
# Output: {"status": "success", "results": [...]}
```

---

## Implementation Priority

| Priority | Phase | Effort | Impact |
|----------|-------|--------|--------|
| 🔴 P0 | GitHub Setup | 1 hour | Foundation |
| 🔴 P1 | File System Operations | 2-3 hours | High |
| 🟠 P2 | App Lifecycle | 1-2 hours | High |
| 🟠 P3 | Screenshots | 2 hours | Medium |
| 🟡 P4 | Clipboard | 1 hour | Medium |
| 🟡 P5 | Task Engine | 4-6 hours | Very High |

---

## Testing Strategy

### Unit Tests
```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_filesystem.py
```

### Integration Tests
```python
# Test: "Find Readme.md and open it"
def test_find_and_open():
    steps = [
        TaskStep("find_files", {"directory": "~/Downloads", "pattern": "Readme.md"}),
        TaskStep("open_file", {"filepath": "$result[0].path"}),
    ]
    result = task_engine.execute(steps)
    assert result["status"] == "success"
```

### Manual Testing
1. Find a file in Downloads
2. Open it with the default app
3. Verify the app launched correctly

---

## Success Criteria

- [ ] Server pushed to GitHub with proper documentation
- [ ] Can find files by name/pattern
- [ ] Can open files with default app
- [ ] Can launch/quit/focus apps
- [ ] Can capture screenshots
- [ ] Can read/write clipboard
- [ ] Can execute multi-step tasks
- [ ] All tools have input validation
- [ ] Security: No shell injection, restricted paths

---

## Next Steps

1. **Start with Phase 0** — Push to GitHub
2. **Then Phase 1** — Add file system operations
3. **Test with target prompt** — "Find Readme.md on Downloads Folder and open it"

---

*Plan created: 2026-06-24*
*Last updated: 2026-06-24*
