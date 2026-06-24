"""
MCP tools for the macos-sys-assist server.
"""

from .information import (
    get_window_geometry,
)
from .actions import (
    move_window,
    resize_window,
    click_at,
    type_string,
    press_key,
)
from .screenshot import (
    screenshot,
    screenshot_window,
    screenshot_region,
    get_displays,
)

__all__ = [
    # Window tools
    "get_window_geometry",
    # Action tools
    "move_window",
    "resize_window",
    "click_at",
    "type_string",
    "press_key",
    # Screenshot tools
    "screenshot",
    "screenshot_window",
    "screenshot_region",
    "get_displays",
]
