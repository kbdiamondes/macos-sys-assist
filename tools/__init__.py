"""
MCP tools for the macos-sys-assist server.
"""

from .information import (
    get_active_app,
    list_open_apps,
    get_window_geometry,
    get_screen_resolution,
)
from .actions import (
    move_window,
    resize_window,
    click_at,
    type_string,
    press_key,
)
from .filesystem import (
    find_files,
    read_file,
    open_file,
    list_directory,
)
from .screenshot import (
    screenshot,
    screenshot_window,
    screenshot_region,
    get_displays,
)

__all__ = [
    # Information tools
    "get_active_app",
    "list_open_apps",
    "get_window_geometry",
    "get_screen_resolution",
    # Action tools
    "move_window",
    "resize_window",
    "click_at",
    "type_string",
    "press_key",
    # File system tools
    "find_files",
    "read_file",
    "open_file",
    "list_directory",
    # Screenshot tools
    "screenshot",
    "screenshot_window",
    "screenshot_region",
    "get_displays",
]
