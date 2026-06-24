"""
Clipboard MCP tools.
Read and write clipboard contents.
"""

from typing import Dict, Any

from security import SecurityValidator


def get_clipboard(validator: SecurityValidator) -> Dict[str, Any]:
    """
    Get text from clipboard.

    Returns:
        Clipboard contents as text
    """
    from macos.clipboard import ClipboardManager

    cm = ClipboardManager()
    return cm.get_text()


def set_clipboard(validator: SecurityValidator, text: str) -> Dict[str, Any]:
    """
    Set clipboard text.

    Args:
        text: Text to copy to clipboard

    Returns:
        Status of the operation
    """
    from macos.clipboard import ClipboardManager

    cm = ClipboardManager()
    return cm.set_text(text)


def clipboard_has_text(validator: SecurityValidator) -> Dict[str, Any]:
    """
    Check if clipboard contains text.

    Returns:
        Whether clipboard has text content
    """
    from macos.clipboard import ClipboardManager

    cm = ClipboardManager()
    return cm.has_text()
