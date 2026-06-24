"""
Window management wrapper using pyobjc.
Provides safe window manipulation (move, resize, get geometry).
"""

from typing import Dict, Optional, Tuple

import ApplicationServices as AppServices
from Quartz import (
    CGMainDisplayID,
    CGDisplayBounds,
    CGEventCreateMouseEvent,
    CGEventPost,
    kCGEventLeftMouseDown,
    kCGEventLeftMouseUp,
    kCGHIDEventTap,
    kCGMouseButtonLeft,
)


class WindowManager:
    """
    Manages window operations for macOS applications.
    All operations are scoped to the Accessibility API.
    """

    def __init__(self):
        pass

    def _get_active_window(self, pid: int) -> Optional[object]:
        """
        Get the AXUIElement reference for the active window of an app.
        
        Args:
            pid: The process ID of the target application.
        
        Returns: AXUIElement reference or None.
        """
        try:
            app_ref = AppServices.AXUIElementCreateApplication(pid)
            focused_window = AppServices.AXUIElementCopyAttributeValue(
                app_ref,
                AppServices.kAXFocusedWindowAttribute,
                None
            )[1]
            return focused_window
        except Exception:
            return None

    def _get_main_window(self, pid: int) -> Optional[object]:
        """
        Get the main window of an application (fallback if no focused window).
        
        Args:
            pid: The process ID of the target application.
        
        Returns: AXUIElement reference or None.
        """
        try:
            app_ref = AppServices.AXUIElementCreateApplication(pid)
            main_window = AppServices.AXUIElementCopyAttributeValue(
                app_ref,
                AppServices.kAXMainWindowAttribute,
                None
            )[1]
            return main_window
        except Exception:
            return None

    def get_window_geometry(self, pid: int) -> Dict[str, int]:
        """
        Get the position and size of the active window.
        
        Args:
            pid: The process ID of the target application.
        
        Returns: {"x": int, "y": int, "width": int, "height": int}
        """
        window = self._get_active_window(pid) or self._get_main_window(pid)
        
        if window is None:
            return {"error": "No window found", "x": 0, "y": 0, "width": 0, "height": 0}
        
        try:
            position = AppServices.AXUIElementCopyAttributeValue(
                window,
                AppServices.kAXPositionAttribute,
                None
            )[1]
            
            size = AppServices.AXUIElementCopyAttributeValue(
                window,
                AppServices.kAXSizeAttribute,
                None
            )[1]
            
            x, y = AppServices.AXValueGetValue(position, AppServices.kAXValueCGPointType, None)[1]
            w, h = AppServices.AXValueGetValue(size, AppServices.kAXValueCGSizeType, None)[1]
            
            return {
                "x": int(x),
                "y": int(y),
                "width": int(w),
                "height": int(h),
            }
        except Exception as e:
            return {"error": str(e), "x": 0, "y": 0, "width": 0, "height": 0}

    def move_window(self, pid: int, x: int, y: int) -> Dict[str, str]:
        """
        Move the active window to the specified coordinates.
        
        Args:
            pid: The process ID of the target application.
            x: Target X coordinate.
            y: Target Y coordinate.
        
        Returns: {"status": "success"} or {"error": "..."}
        """
        window = self._get_active_window(pid) or self._get_main_window(pid)
        
        if window is None:
            return {"error": "No window found"}
        
        try:
            # Create the new position value
            new_position = AppServices.AXValueCreate(
                AppServices.kAXValueCGPointType,
                (x, y)
            )
            
            # Set the position
            result = AppServices.AXUIElementSetAttributeValue(
                window,
                AppServices.kAXPositionAttribute,
                new_position
            )
            
            if result == 0:  # kAXErrorSuccess
                return {"status": "success", "x": x, "y": y}
            else:
                return {"error": f"AXError code: {result}"}
        
        except Exception as e:
            return {"error": str(e)}

    def resize_window(self, pid: int, width: int, height: int) -> Dict[str, str]:
        """
        Resize the active window to the specified dimensions.
        
        Args:
            pid: The process ID of the target application.
            width: Target width in pixels.
            height: Target height in pixels.
        
        Returns: {"status": "success"} or {"error": "..."}
        """
        window = self._get_active_window(pid) or self._get_main_window(pid)
        
        if window is None:
            return {"error": "No window found"}
        
        try:
            # Create the new size value
            new_size = AppServices.AXValueCreate(
                AppServices.kAXValueCGSizeType,
                (width, height)
            )
            
            # Set the size
            result = AppServices.AXUIElementSetAttributeValue(
                window,
                AppServices.kAXSizeAttribute,
                new_size
            )
            
            if result == 0:  # kAXErrorSuccess
                return {"status": "success", "width": width, "height": height}
            else:
                return {"error": f"AXError code: {result}"}
        
        except Exception as e:
            return {"error": str(e)}

    def get_window_title(self, pid: int) -> str:
        """
        Get the title of the active window.
        
        Args:
            pid: The process ID of the target application.
        
        Returns: Window title string.
        """
        window = self._get_active_window(pid) or self._get_main_window(pid)
        
        if window is None:
            return "No window"
        
        try:
            title = AppServices.AXUIElementCopyAttributeValue(
                window,
                AppServices.kAXTitleAttribute,
                None
            )[1]
            return str(title) if title else "Untitled"
        except Exception:
            return "Unknown"
