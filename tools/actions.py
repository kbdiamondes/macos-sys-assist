"""
Action MCP tools (write operations).
These tools make changes to the system (window manipulation, input simulation).
All actions are validated against the security layer before execution.
"""

from typing import Dict, Any

from security import SecurityValidator


def move_window(
    validator: SecurityValidator,
    x: int,
    y: int
) -> Dict[str, Any]:
    """
    Move the active window to the specified coordinates.
    
    Args:
        x: Target X coordinate (pixels from left).
        y: Target Y coordinate (pixels from top).
    
    Returns:
        {"status": "success", "x": int, "y": int} or {"error": str}
    """
    validation = validator.validate_action("window")
    if not validation["valid"]:
        return {"error": validation["error"]}
    
    if validation["needs_confirmation"]:
        return {
            "status": "needs_confirmation",
            "action": "move_window",
            "target_app": validation["app_name"],
            "params": {"x": x, "y": y},
            "message": f"Move window of '{validation['app_name']}' to ({x}, {y})?"
        }
    
    from macos.window import WindowManager
    
    window_manager = WindowManager()
    result = window_manager.move_window(validation["pid"], x, y)
    return result


def resize_window(
    validator: SecurityValidator,
    width: int,
    height: int
) -> Dict[str, Any]:
    """
    Resize the active window to the specified dimensions.
    
    Args:
        width: Target width in pixels.
        height: Target height in pixels.
    
    Returns:
        {"status": "success", "width": int, "height": int} or {"error": str}
    """
    validation = validator.validate_action("window")
    if not validation["valid"]:
        return {"error": validation["error"]}
    
    if validation["needs_confirmation"]:
        return {
            "status": "needs_confirmation",
            "action": "resize_window",
            "target_app": validation["app_name"],
            "params": {"width": width, "height": height},
            "message": f"Resize window of '{validation['app_name']}' to {width}x{height}?"
        }
    
    from macos.window import WindowManager
    
    window_manager = WindowManager()
    result = window_manager.resize_window(validation["pid"], width, height)
    return result


def click_at(
    validator: SecurityValidator,
    x: int,
    y: int,
    button: str = "left",
    double: bool = False
) -> Dict[str, Any]:
    """
    Simulate a mouse click at the specified screen coordinates.
    
    Args:
        x: Screen X coordinate.
        y: Screen Y coordinate.
        button: "left" or "right".
        double: If True, perform a double-click.
    
    Returns:
        {"status": "success", "x": int, "y": int, "button": str} or {"error": str}
    """
    validation = validator.validate_action("click")
    if not validation["valid"]:
        return {"error": validation["error"]}
    
    if validation["needs_confirmation"]:
        return {
            "status": "needs_confirmation",
            "action": "click_at",
            "target_app": validation["app_name"],
            "params": {"x": x, "y": y, "button": button, "double": double},
            "message": f"Click at ({x}, {y}) on '{validation['app_name']}'?"
        }
    
    from macos.input import InputSimulator
    
    input_sim = InputSimulator()
    
    if double:
        result = input_sim.double_click_at(x, y)
    else:
        result = input_sim.click_at(x, y, button)
    
    return result


def type_string(
    validator: SecurityValidator,
    text: str
) -> Dict[str, Any]:
    """
    Type a string character by character.
    
    Args:
        text: The string to type (max 500 characters by default).
    
    Returns:
        {"status": "success", "length": int} or {"error": str}
    """
    # Validate text length
    text_validation = validator.validate_text_input(text)
    if not text_validation["valid"]:
        return {"error": text_validation["error"]}
    
    # Validate action permission
    validation = validator.validate_action("type")
    if not validation["valid"]:
        return {"error": validation["error"]}
    
    if validation["needs_confirmation"]:
        # Mask the text for security (don't show full content in confirmation)
        preview = text[:20] + "..." if len(text) > 20 else text
        return {
            "status": "needs_confirmation",
            "action": "type_string",
            "target_app": validation["app_name"],
            "params": {"text_preview": preview, "length": len(text)},
            "message": f"Type '{preview}' ({len(text)} chars) in '{validation['app_name']}'?"
        }
    
    from macos.input import InputSimulator
    
    input_sim = InputSimulator()
    result = input_sim.type_string(text)
    return result


def press_key(
    validator: SecurityValidator,
    key_combination: str
) -> Dict[str, Any]:
    """
    Press a key or key combination.
    
    Args:
        key_combination: Key combo string, e.g., "cmd+tab", "ctrl+c", "enter".
    
    Returns:
        {"status": "success", "combination": str} or {"error": str}
    """
    # Validate key combination against blocked list
    key_validation = validator.validate_key_combination(key_combination)
    if not key_validation["valid"]:
        return {"error": key_validation["error"]}
    
    # Validate action permission
    validation = validator.validate_action("key")
    if not validation["valid"]:
        return {"error": validation["error"]}
    
    if validation["needs_confirmation"]:
        return {
            "status": "needs_confirmation",
            "action": "press_key",
            "target_app": validation["app_name"],
            "params": {"key_combination": key_combination},
            "message": f"Press '{key_combination}' in '{validation['app_name']}'?"
        }
    
    from macos.input import InputSimulator
    
    input_sim = InputSimulator()
    result = input_sim.press_key(key_combination)
    return result
