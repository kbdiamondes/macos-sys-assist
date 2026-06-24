# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-24

### Added

- Initial release
- MCP server with stdio transport
- Application allow-list security
- Window management (move, resize)
- Input simulation (click, type, keys)
- App intelligence (get focused app, list running apps)
- Screen resolution queries
- Confirmation prompts for invasive actions
- Blocked key combinations
- Input validation and length limits
- Wrapper script for directory handling
- Setup script for easy installation
- Comprehensive documentation

### Security

- No shell execution (all operations via native macOS APIs)
- Application allow-list enforcement
- Confirmation prompts for click, type, and window operations
- Blocked destructive key combinations (cmd+q, cmd+delete, etc.)
- Maximum string length limits
- Restricted path access in file operations

---

## [Unreleased]

### Planned

- Multi-monitor support
- Notification center integration
- Volume/brightness control
- Drag and drop simulation
- Window snapping presets (thirds, quarters)

---

## [1.1.0] - 2026-06-24

### Added

- **File System Operations**: `find_files`, `read_file`, `open_file`, `list_directory`
- **App Lifecycle Management**: `launch_app`, `quit_app`, `focus_app`, `get_app_info`
- **Screenshot Capability**: `screenshot`, `screenshot_window`, `screenshot_region`, `get_displays`
- **Clipboard Operations**: `get_clipboard`, `set_clipboard`, `clipboard_has_text`
- **Multi-Step Task Engine**: `TaskEngine` with dependency resolution and result chaining
- **Prompt Parser**: Natural language prompt → task steps decomposition
- **Case-Insensitive File Search**: Automatic fallback for case-mismatched searches
- **Wrapper Script**: `run.sh` for proper directory context

### Changed

- Updated server.py with 10 new MCP tool definitions
- Updated tools/__init__.py with all new tool exports
- Updated macos/__init__.py with all new module exports
- Comprehensive README documentation for all features

### Security

- Restricted path access for file operations
- File size limits (1MB max) for read operations
- Permission checking for screenshot operations
