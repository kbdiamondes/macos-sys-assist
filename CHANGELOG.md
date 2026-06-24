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

- File system operations (find, read, open files)
- Screenshot capability
- Clipboard operations (get/set)
- App lifecycle management (launch, quit, focus)
- Multi-monitor support
- Multi-step task engine
- Notification center integration
- Volume/brightness control
