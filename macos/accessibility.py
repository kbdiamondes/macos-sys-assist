"""
Accessibility wrapper using pyobjc.
Provides read-only access to the macOS Accessibility API for querying app state.
"""

import sys
from typing import Dict, List, Optional, Any

# Import pyobjc frameworks
import ApplicationServices as AppServices
from CoreFoundation import (
    CFArrayGetCount,
    CFArrayGetValueAtIndex,
    CFRelease,
    CFRetain,
    kCFAllocatorDefault,
)
from Foundation import NSDictionary, NSArray


class AccessibilityWrapper:
    """
    Wraps the macOS Accessibility API for safe, read-only queries.
    No mutation or action commands are exposed here.
    """

    def __init__(self):
        self._check_accessibility_permission()

    def _check_accessibility_permission(self) -> bool:
        """
        Check if the process has Accessibility permissions.
        Returns True if permission is granted, False otherwise.
        """
        options = {AppServices.kAXTrustedCheckOptionPrompt: False}
        is_trusted = AppServices.AXIsProcessTrustedWithOptions(options)
        
        if not is_trusted:
            print(
                "WARNING: Accessibility permission not granted.\n"
                "Please go to System Settings > Privacy & Security > Accessibility\n"
                "and add this application to the allowed list.",
                file=sys.stderr
            )
        return is_trusted

    def get_frontmost_app(self) -> Dict[str, str]:
        """
        Get the currently focused (frontmost) application.
        Returns: {"bundle_id": "...", "name": "...", "pid": "..."}
        """
        workspace = AppServices.NSWorkspace.sharedWorkspace()
        front_app = workspace.frontmostApplication()
        
        if front_app is None:
            return {"bundle_id": "", "name": "None", "pid": "0"}
        
        return {
            "bundle_id": front_app.bundleIdentifier() or "",
            "name": front_app.localizedName() or "Unknown",
            "pid": str(front_app.processIdentifier()),
        }

    def get_running_apps(self) -> List[Dict[str, str]]:
        """
        Get a list of all running applications with visible UI.
        Returns: [{"bundle_id": "...", "name": "...", "pid": "..."}]
        """
        workspace = AppServices.NSWorkspace.sharedWorkspace()
        running_apps = workspace.runningApplications()
        
        apps = []
        for app in running_apps:
            # Only include apps that have a regular UI (non-background agents)
            # Removed isActive() check — it only returned the frontmost app
            if app.activationPolicy() == AppServices.NSApplicationActivationPolicyRegular:
                apps.append({
                    "bundle_id": app.bundleIdentifier() or "",
                    "name": app.localizedName() or "Unknown",
                    "pid": str(app.processIdentifier()),
                })
        
        return apps

    def get_app_by_pid(self, pid: int) -> Optional[Dict[str, str]]:
        """
        Look up a running app's bundle_id and name by its PID.
        Returns: {"bundle_id": "...", "name": "...", "pid": "..."} or None if not found.
        """
        workspace = AppServices.NSWorkspace.sharedWorkspace()
        
        for app in workspace.runningApplications():
            if app.processIdentifier() == pid:
                return {
                    "bundle_id": app.bundleIdentifier() or "",
                    "name": app.localizedName() or "Unknown",
                    "pid": str(pid),
                }
        
        return None

    def get_all_running_apps(self) -> List[Dict[str, str]]:
        """
        Get ALL running applications (including background processes).
        Returns: [{"bundle_id": "...", "name": "...", "pid": "..."}]
        """
        workspace = AppServices.NSWorkspace.sharedWorkspace()
        running_apps = workspace.runningApplications()
        
        apps = []
        for app in running_apps:
            apps.append({
                "bundle_id": app.bundleIdentifier() or "",
                "name": app.localizedName() or "Unknown",
                "pid": str(app.processIdentifier()),
            })
        
        return apps

    def get_element_attributes(self, pid: int) -> Dict[str, Any]:
        """
        Get accessibility attributes for the focused element of an application.
        This is a safe, read-only query.
        
        Args:
            pid: The process ID of the target application.
        
        Returns: Dictionary of accessibility attributes.
        """
        try:
            app_ref = AppServices.AXUIElementCreateApplication(pid)
            focused_element = AppServices.AXUIElementCopyAttributeValue(
                app_ref,
                AppServices.kAXFocusedUIElementAttribute,
                None
            )[1]
            
            if focused_element is None:
                return {"error": "No focused element found"}
            
            # Get role and title
            role = AppServices.AXUIElementCopyAttributeValue(
                focused_element,
                AppServices.kAXRoleAttribute,
                None
            )[1]
            
            title = AppServices.AXUIElementCopyAttributeValue(
                focused_element,
                AppServices.kAXTitleAttribute,
                None
            )[1]
            
            value = AppServices.AXUIElementCopyAttributeValue(
                focused_element,
                AppServices.kAXValueAttribute,
                None
            )[1]
            
            return {
                "role": str(role) if role else "Unknown",
                "title": str(title) if title else "Unknown",
                "value": str(value) if value else "",
            }
        
        except Exception as e:
            return {"error": str(e)}

    def get_screen_resolution(self) -> Dict[str, int]:
        """
        Get the primary screen resolution.
        Returns: {"width": int, "height": int}
        """
        from Quartz import (
            CGMainDisplayID,
            CGDisplayBounds,
        )
        
        main_display = CGMainDisplayID()
        bounds = CGDisplayBounds(main_display)
        
        return {
            "width": int(bounds.size.width),
            "height": int(bounds.size.height),
        }
