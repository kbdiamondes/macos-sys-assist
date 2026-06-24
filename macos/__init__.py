"""
macOS native wrappers for system-level automation.
Uses pyobjc to interface directly with macOS frameworks.
"""

from .accessibility import AccessibilityWrapper
from .window import WindowManager
from .input import InputSimulator

__all__ = ["AccessibilityWrapper", "WindowManager", "InputSimulator"]
