"""
Clipboard operations for macOS.
Read/write clipboard contents using native pbcopy/pbpaste.
"""

import subprocess
from pathlib import Path
from typing import Dict, Optional


class ClipboardManager:
    """
    Manage clipboard contents on macOS.
    Uses native pbcopy and pbpaste commands.
    """

    def __init__(self):
        pass

    def get_text(self) -> Dict:
        """
        Get text from clipboard.

        Returns:
            Clipboard contents as text
        """
        try:
            result = subprocess.run(
                ["pbpaste"],
                capture_output=True,
                text=True,
                timeout=5,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                text = result.stdout
                return {
                    "status": "success",
                    "content": text,
                    "length": len(text),
                    "type": "text",
                }
            else:
                return {"error": "Failed to read clipboard"}

        except subprocess.TimeoutExpired:
            return {"error": "Clipboard read timed out"}
        except Exception as e:
            return {"error": str(e)}

    def set_text(self, text: str) -> Dict:
        """
        Set clipboard text.

        Args:
            text: Text to copy to clipboard

        Returns:
            Status of the operation
        """
        try:
            result = subprocess.run(
                ["pbcopy"],
                input=text,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return {
                    "status": "success",
                    "action": "copied",
                    "length": len(text),
                    "preview": text[:100] + ("..." if len(text) > 100 else ""),
                }
            else:
                return {"error": "Failed to set clipboard"}

        except subprocess.TimeoutExpired:
            return {"error": "Clipboard write timed out"}
        except Exception as e:
            return {"error": str(e)}

    def get_image(self, filepath: str = "/tmp/clipboard_image.png") -> Dict:
        """
        Save clipboard image to file if available.

        Args:
            filepath: Where to save the image

        Returns:
            Status and filepath
        """
        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)

            # Use osascript to check if clipboard has an image
            check_script = '''
            use framework "AppKit"
            use scripting additions

            set pb to current application's NSPasteboard's generalPasteboard()
            set classes to current application's NSArray's arrayWithObject:(current application's NSPasteboardTypePNG)
            set options to missing value
            set canRead to pb's canReadObjectForClasses:classes options:options

            if canRead then
                set imageData to pb's dataForType:(current application's NSPasteboardTypePNG)
                if imageData is not missing value then
                    set filePath to (current application's NSString's stringWithString:"%s")
                    set success to imageData's writeToFile:filePath atomically:false
                    if success then
                        return "success"
                    else
                        return "error: could not write file"
                    end if
                else
                    return "error: no image data"
                end if
            else
                return "error: clipboard does not contain an image"
            end if
            ''' % str(path)

            result = subprocess.run(
                ["osascript", "-e", check_script],
                capture_output=True,
                text=True,
                timeout=10
            )

            output = result.stdout.strip() if result.stdout else ""

            if output == "success" and path.exists():
                return {
                    "status": "success",
                    "filepath": str(path),
                    "size": path.stat().st_size,
                    "type": "image",
                }
            else:
                return {"error": output or "Clipboard does not contain an image"}

        except subprocess.TimeoutExpired:
            return {"error": "Image extraction timed out"}
        except Exception as e:
            return {"error": str(e)}

    def has_text(self) -> Dict:
        """
        Check if clipboard contains text.

        Returns:
            Whether clipboard has text content
        """
        try:
            result = subprocess.run(
                ["pbpaste"],
                capture_output=True,
                text=True,
                timeout=3,
                encoding='utf-8',
                errors='replace'
            )

            has_content = result.returncode == 0 and len(result.stdout.strip()) > 0

            return {
                "has_text": has_content,
                "length": len(result.stdout) if has_content else 0,
            }

        except Exception:
            return {"has_text": False, "length": 0}

    def clear(self) -> Dict:
        """
        Clear clipboard contents.

        Returns:
            Status of the operation
        """
        try:
            result = subprocess.run(
                ["pbcopy"],
                input="",
                capture_output=True,
                text=True,
                timeout=3
            )

            if result.returncode == 0:
                return {"status": "success", "action": "cleared"}
            else:
                return {"error": "Failed to clear clipboard"}

        except Exception as e:
            return {"error": str(e)}
