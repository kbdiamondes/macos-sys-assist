"""
macOS native wrappers for system-level automation.
Uses pyobjc to interface directly with macOS frameworks.
"""

from .accessibility import AccessibilityWrapper
from .window import WindowManager
from .input import InputSimulator
from .filesystem import FileSystemManager
from .app_lifecycle import AppLifecycleManager
from .screenshot import ScreenshotManager
from .clipboard import ClipboardManager
from .task_engine import TaskEngine, TaskStep, TaskResult, PromptParser

__all__ = [
    "AccessibilityWrapper",
    "WindowManager",
    "InputSimulator",
    "FileSystemManager",
    "AppLifecycleManager",
    "ScreenshotManager",
    "ClipboardManager",
    "TaskEngine",
    "TaskStep",
    "TaskResult",
    "PromptParser",
]
