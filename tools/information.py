"""
Information-gathering MCP tools (read-only).
These tools query the system state without making any changes.
"""

from typing import Dict, Any

from security import SecurityValidator


def get_active_app(validator: SecurityValidator) -> Dict[str, Any]:
    """
    Get the currently focused (frontmost) application.
    
    Returns:
        {
            "bundle_id": str,
            "name": str,
            "pid": str,
            "is_allowed": bool
        }
    """
    validator.invalidate_cache()
    current = validator.get_current_app()
    
    bundle_id = current.get("bundle_id", "")
    is_allowed = validator.config.is_app_allowed(bundle_id)
    
    return {
        "bundle_id": bundle_id,
        "name": current.get("name", "Unknown"),
        "pid": current.get("pid", "0"),
        "is_allowed": is_allowed
    }


def list_open_apps(validator: SecurityValidator) -> Dict[str, Any]:
    """
    List all running applications that have visible windows.
    
    Returns:
        {
            "apps": [
                {"bundle_id": str, "name": str, "pid": str, "is_allowed": bool}
            ]
        }
    """
    from macos.accessibility import AccessibilityWrapper
    
    accessibility = AccessibilityWrapper()
    apps = accessibility.get_running_apps()
    
    # Enrich with allow-list status
    enriched_apps = []
    for app in apps:
        bundle_id = app.get("bundle_id", "")
        enriched_apps.append({
            **app,
            "is_allowed": validator.config.is_app_allowed(bundle_id)
        })
    
    return {"apps": enriched_apps}


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


def get_screen_resolution(validator: SecurityValidator) -> Dict[str, int]:
    """
    Get the primary screen resolution.
    
    Returns:
        {"width": int, "height": int}
    """
    from macos.accessibility import AccessibilityWrapper
    
    accessibility = AccessibilityWrapper()
    return accessibility.get_screen_resolution()
