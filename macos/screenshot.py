"""
Screenshot capabilities for macOS.
Capture screen, windows, and regions using native screencapture.
"""

import subprocess
from pathlib import Path
from typing import Dict, Optional


class ScreenshotManager:
    """
    Capture screenshots on macOS using the native screencapture command.
    Supports full screen, window, and region captures.
    """

    def __init__(self):
        pass

    def _check_permissions(self) -> Dict:
        """Check if Screen Recording permission is available."""
        try:
            result = subprocess.run(
                ["screencapture", "-x", "-t", "png", "/tmp/screenshot_test.png"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Clean up test file
                Path("/tmp/screenshot_test.png").unlink(missing_ok=True)
                return {"status": "ok"}
            else:
                return {
                    "error": "Screen Recording permission required",
                    "instructions": [
                        "Open System Settings → Privacy & Security → Screen Recording",
                        "Click the + button",
                        "Add Terminal.app or the Python interpreter",
                        "Ensure the toggle is ON",
                        "Restart the application"
                    ]
                }
        except Exception as e:
            return {"error": str(e)}

    def screenshot(
        self,
        filepath: str = "~/Pictures/screenshot.png",
        display_id: int = 0,
        include_cursor: bool = False,
        format: str = "png"
    ) -> Dict:
        """
        Capture full screen.

        Args:
            filepath: Where to save the screenshot
            display_id: Display to capture (0 = main, 1 = second, etc.)
            include_cursor: Include mouse cursor in capture
            format: Image format (png, jpg, pdf)

        Returns:
            Status and filepath of the captured screenshot
        """
        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)

            # Build command
            cmd = ["screencapture"]

            # Quiet mode (no sound)
            cmd.append("-x")

            # Format
            if format == "jpg":
                cmd.extend(["-t", "jpg"])
            elif format == "pdf":
                cmd.extend(["-t", "pdf"])
            else:
                cmd.extend(["-t", "png"])

            # Display ID
            if display_id > 0:
                cmd.extend(["-D", str(display_id)])

            # Include cursor
            if include_cursor:
                cmd.append("-C")

            # Output file
            cmd.append(str(path))

            # Execute
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                file_size = path.stat().st_size if path.exists() else 0
                return {
                    "status": "success",
                    "filepath": str(path),
                    "size": file_size,
                    "format": format,
                }
            else:
                # Check if it's a permission issue
                error_msg = result.stderr or "Screenshot failed"
                if "could not create image" in error_msg.lower():
                    return self._check_permissions()
                return {"error": error_msg}

        except subprocess.TimeoutExpired:
            return {"error": "Screenshot timed out"}
        except Exception as e:
            return {"error": str(e)}

    def screenshot_window(
        self,
        pid: int,
        filepath: str = "/tmp/window.png",
        format: str = "png"
    ) -> Dict:
        """
        Capture a specific window by PID.

        Args:
            pid: Process ID of the target window
            filepath: Where to save the screenshot
            format: Image format

        Returns:
            Status and filepath
        """
        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)

            # Build command
            cmd = ["screencapture", "-x"]

            # Format
            if format == "jpg":
                cmd.extend(["-t", "jpg"])
            elif format == "pdf":
                cmd.extend(["-t", "pdf"])
            else:
                cmd.extend(["-t", "png"])

            # Window ID (using -l flag with PID)
            cmd.extend(["-l", str(pid)])

            # Output file
            cmd.append(str(path))

            # Execute
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                file_size = path.stat().st_size if path.exists() else 0
                return {
                    "status": "success",
                    "filepath": str(path),
                    "size": file_size,
                    "pid": pid,
                }
            else:
                return {"error": result.stderr or "Window capture failed"}

        except subprocess.TimeoutExpired:
            return {"error": "Screenshot timed out"}
        except Exception as e:
            return {"error": str(e)}

    def screenshot_region(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        filepath: str = "/tmp/region.png",
        format: str = "png"
    ) -> Dict:
        """
        Capture a specific screen region.

        Args:
            x: X coordinate of top-left corner
            y: Y coordinate of top-left corner
            width: Width of region
            height: Height of region
            filepath: Where to save the screenshot
            format: Image format

        Returns:
            Status and filepath
        """
        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)

            # Build command
            cmd = ["screencapture", "-x"]

            # Format
            if format == "jpg":
                cmd.extend(["-t", "jpg"])
            elif format == "pdf":
                cmd.extend(["-t", "pdf"])
            else:
                cmd.extend(["-t", "png"])

            # Region (-R x,y,width,height)
            cmd.extend(["-R", f"{x},{y},{width},{height}"])

            # Output file
            cmd.append(str(path))

            # Execute
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                file_size = path.stat().st_size if path.exists() else 0
                return {
                    "status": "success",
                    "filepath": str(path),
                    "size": file_size,
                    "region": {"x": x, "y": y, "width": width, "height": height},
                }
            else:
                return {"error": result.stderr or "Region capture failed"}

        except subprocess.TimeoutExpired:
            return {"error": "Screenshot timed out"}
        except Exception as e:
            return {"error": str(e)}

    def screenshot_interactive(self) -> Dict:
        """
        Open interactive screenshot mode (user selects area).
        This launches the macOS screenshot UI.

        Returns:
            Status
        """
        try:
            # screencapture -i opens interactive mode
            result = subprocess.run(
                ["screencapture", "-i", "/tmp/interactive_screenshot.png"],
                capture_output=True,
                text=True,
                timeout=60  # Give user time to select
            )

            if result.returncode == 0:
                path = Path("/tmp/interactive_screenshot.png")
                if path.exists():
                    return {
                        "status": "success",
                        "filepath": str(path),
                        "size": path.stat().st_size,
                    }
                else:
                    return {"error": "No screenshot taken"}
            else:
                return {"error": "Interactive capture cancelled or failed"}

        except subprocess.TimeoutExpired:
            return {"error": "Interactive capture timed out"}
        except Exception as e:
            return {"error": str(e)}

    def get_displays(self) -> Dict:
        """
        Get information about connected displays.

        Returns:
            List of displays with their properties
        """
        try:
            # Use system_profiler to get display info
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Parse the output (basic parsing)
                displays = []
                current_display = {}

                for line in result.stdout.split('\n'):
                    if 'Display Type:' in line or 'Resolution:' in line:
                        if 'Resolution:' in line:
                            # Extract resolution
                            import re
                            match = re.search(r'(\d+)\s*x\s*(\d+)', line)
                            if match:
                                current_display['width'] = int(match.group(1))
                                current_display['height'] = int(match.group(2))
                    elif 'Display' in line and ':' in line:
                        if current_display:
                            displays.append(current_display)
                        current_display = {'name': line.strip()}

                if current_display:
                    displays.append(current_display)

                return {
                    "displays": displays,
                    "count": len(displays),
                }
            else:
                return {"error": "Failed to get display info"}

        except Exception as e:
            return {"error": str(e)}
