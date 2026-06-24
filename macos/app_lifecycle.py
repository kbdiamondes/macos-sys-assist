"""
Application lifecycle management for macOS.
Launch, quit, focus, and query applications.
"""

import subprocess
from typing import Dict, Optional

import ApplicationServices as AppServices


class AppLifecycleManager:
    """
    Manage application lifecycle on macOS.
    Launch, quit, focus, and get app information.
    """

    def __init__(self):
        pass

    def _get_workspace(self):
        """Get NSWorkspace shared instance."""
        return AppServices.NSWorkspace.sharedWorkspace()

    def _find_running_app(
        self,
        app_name: Optional[str] = None,
        bundle_id: Optional[str] = None
    ):
        """Find a running application by name or bundle ID."""
        workspace = self._get_workspace()
        apps = workspace.runningApplications()

        for app in apps:
            if bundle_id and app.bundleIdentifier() == bundle_id:
                return app
            elif app_name and app.localizedName() == app_name:
                return app

        return None

    def launch_app(
        self,
        app_name: Optional[str] = None,
        bundle_id: Optional[str] = None
    ) -> Dict:
        """
        Launch an application.

        Args:
            app_name: Name of the application (e.g., "Safari")
            bundle_id: Bundle ID (e.g., "com.apple.Safari")

        Returns:
            Status of the launch operation
        """
        try:
            workspace = self._get_workspace()

            if bundle_id:
                workspace.launchApplication_(bundle_id)
                return {
                    "status": "success",
                    "action": "launch",
                    "app": bundle_id,
                }
            elif app_name:
                workspace.launchApplication_(app_name)
                return {
                    "status": "success",
                    "action": "launch",
                    "app": app_name,
                }
            else:
                return {"error": "Must provide app_name or bundle_id"}

        except Exception as e:
            return {"error": str(e)}

    def quit_app(
        self,
        app_name: Optional[str] = None,
        bundle_id: Optional[str] = None,
        force: bool = False
    ) -> Dict:
        """
        Quit an application.

        Args:
            app_name: Name of the application
            bundle_id: Bundle ID
            force: Force quit if True

        Returns:
            Status of the quit operation
        """
        try:
            target_app = self._find_running_app(app_name, bundle_id)

            if not target_app:
                return {
                    "error": f"App not found or not running: {app_name or bundle_id}"
                }

            if force:
                target_app.forceTerminate()
            else:
                target_app.terminate()

            return {
                "status": "success",
                "action": "quit",
                "app": target_app.localizedName(),
                "force": force,
            }

        except Exception as e:
            return {"error": str(e)}

    def focus_app(
        self,
        app_name: Optional[str] = None,
        bundle_id: Optional[str] = None
    ) -> Dict:
        """
        Bring an application to the front.

        Args:
            app_name: Name of the application
            bundle_id: Bundle ID

        Returns:
            Status of the focus operation
        """
        try:
            target_app = self._find_running_app(app_name, bundle_id)

            if not target_app:
                return {
                    "error": f"App not found or not running: {app_name or bundle_id}"
                }

            target_app.activateWithOptions_(
                AppServices.NSApplicationActivateIgnoringOtherApps
            )

            return {
                "status": "success",
                "action": "focus",
                "app": target_app.localizedName(),
                "bundle_id": target_app.bundleIdentifier(),
            }

        except Exception as e:
            return {"error": str(e)}

    def get_app_info(
        self,
        app_name: Optional[str] = None,
        bundle_id: Optional[str] = None
    ) -> Dict:
        """
        Get information about an application.

        Args:
            app_name: Name of the application
            bundle_id: Bundle ID

        Returns:
            Application information
        """
        try:
            target_app = self._find_running_app(app_name, bundle_id)

            if not target_app:
                return {
                    "error": f"App not found or not running: {app_name or bundle_id}"
                }

            return {
                "name": target_app.localizedName(),
                "bundle_id": target_app.bundleIdentifier(),
                "pid": target_app.processIdentifier(),
                "is_active": target_app.isActive(),
                "is_hidden": target_app.isHidden(),
                "is_terminated": target_app.isTerminated(),
            }

        except Exception as e:
            return {"error": str(e)}

    def get_running_apps(self) -> Dict:
        """
        Get all running applications with visible windows.

        Returns:
            List of running applications
        """
        try:
            workspace = self._get_workspace()
            apps = workspace.runningApplications()

            running_apps = []
            for app in apps:
                # Only include apps with regular activation policy (visible apps)
                if app.activationPolicy() == AppServices.NSApplicationActivationPolicyRegular:
                    running_apps.append({
                        "name": app.localizedName() or "Unknown",
                        "bundle_id": app.bundleIdentifier() or "",
                        "pid": app.processIdentifier(),
                        "is_active": app.isActive(),
                    })

            return {
                "apps": running_apps,
                "total": len(running_apps),
            }

        except Exception as e:
            return {"error": str(e)}
