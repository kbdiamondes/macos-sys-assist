"""
Screenshot MCP tools.
Capture screen, windows, and regions.
"""

from typing import Dict, Any

from security import SecurityValidator


def screenshot(
    validator: SecurityValidator,
    filepath: str = "~/Pictures/screenshot.png",
    display_id: int = 0,
    include_cursor: bool = False
) -> Dict[str, Any]:
    """
    Capture full screen.

    Args:
        filepath: Where to save the screenshot
        display_id: Display to capture (0 = main)
        include_cursor: Include mouse cursor

    Returns:
        Status and filepath
    """
    from macos.screenshot import ScreenshotManager

    sm = ScreenshotManager()
    return sm.screenshot(
        filepath=filepath,
        display_id=display_id,
        include_cursor=include_cursor
    )


def screenshot_window(
    validator: SecurityValidator,
    pid: int,
    filepath: str = "/tmp/window.png"
) -> Dict[str, Any]:
    """
    Capture a specific window by PID.

    Args:
        pid: Process ID of the target window
        filepath: Where to save the screenshot

    Returns:
        Status and filepath
    """
    from macos.screenshot import ScreenshotManager

    sm = ScreenshotManager()
    return sm.screenshot_window(pid=pid, filepath=filepath)


def screenshot_region(
    validator: SecurityValidator,
    x: int,
    y: int,
    width: int,
    height: int,
    filepath: str = "/tmp/region.png"
) -> Dict[str, Any]:
    """
    Capture a specific screen region.

    Args:
        x: X coordinate of top-left corner
        y: Y coordinate of top-left corner
        width: Width of region
        height: Height of region
        filepath: Where to save the screenshot

    Returns:
        Status and filepath
    """
    from macos.screenshot import ScreenshotManager

    sm = ScreenshotManager()
    return sm.screenshot_region(
        x=x, y=y,
        width=width, height=height,
        filepath=filepath
    )


def get_displays(validator: SecurityValidator) -> Dict[str, Any]:
    """
    Get information about connected displays.

    Returns:
        List of displays
    """
    from macos.screenshot import ScreenshotManager

    sm = ScreenshotManager()
    return sm.get_displays()
