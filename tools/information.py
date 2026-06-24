"""
Information-gathering MCP tools (read-only).
These tools query the system state without making any changes.
"""

from typing import Dict, Any

from security import SecurityValidator


def get_window_geometry(validator: SecurityValidator, pid: int) -> Dict[str, Any]:
    """
    Get the position and size of the active window for a specific app.
    
    Args:
        pid: The process ID of the target application.
    
    Returns:
        {"x": int, "y": int, "width": int, "height": int}
    """
    from macos.window import WindowManager
    
    # Validate against the specific PID, not the frontmost app
    validation = validator.validate_action_for_pid("info", pid)
    if not validation["valid"]:
        return {"error": validation["error"]}
    
    window_manager = WindowManager()
    return window_manager.get_window_geometry(pid)
