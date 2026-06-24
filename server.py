"""
macos-sys-assist MCP Server
============================

A secure macOS OS-level automation server for the Model Context Protocol.
Provides safe, constrained access to system-level operations through a
strict allow-list and confirmation-based action model.

Security Features:
- Application allow-list (only approved apps can be interacted with)
- No terminal/shell execution (all operations use native macOS APIs)
- Confirmation prompts for invasive actions (click, type, window manipulation)
- Blocked key combinations for destructive shortcuts
- Input validation and length limits

Usage:
    python server.py
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, Optional

from mcp.server import Server
from mcp.types import (
    TextContent,
    Tool,
)

from config import load_config, ServerConfig
from security import SecurityValidator
from tools.information import (
    get_active_app,
    list_open_apps,
    get_window_geometry,
    get_screen_resolution,
)
from tools.actions import (
    move_window,
    resize_window,
    click_at,
    type_string,
    press_key,
)
from tools.filesystem import (
    find_files,
    read_file,
    open_file,
    list_directory,
)
from tools.screenshot import (
    screenshot,
    screenshot_window,
    screenshot_region,
    get_displays,
)
from tools.clipboard import (
    get_clipboard,
    set_clipboard,
    clipboard_has_text,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("macos-sys-assist")

# Tool definitions (what the AI can call)
TOOLS = [
    # Information tools (read-only)
    Tool(
        name="get_active_app",
        description="Get the currently focused application. Returns bundle_id, name, pid, and whether it's in the allow-list.",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="list_open_apps",
        description="List all running applications with visible windows. Shows which apps are allowed.",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="get_window_geometry",
        description="Get the position and size of the active window for a specific application.",
        inputSchema={
            "type": "object",
            "properties": {
                "pid": {
                    "type": "integer",
                    "description": "Process ID of the target application"
                }
            },
            "required": ["pid"]
        }
    ),
    Tool(
        name="get_screen_resolution",
        description="Get the primary screen resolution in pixels.",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    # Action tools (write operations - require confirmation)
    Tool(
        name="move_window",
        description="Move the active window to specified coordinates. Requires user confirmation.",
        inputSchema={
            "type": "object",
            "properties": {
                "x": {
                    "type": "integer",
                    "description": "Target X coordinate (pixels from left)"
                },
                "y": {
                    "type": "integer",
                    "description": "Target Y coordinate (pixels from top)"
                }
            },
            "required": ["x", "y"]
        }
    ),
    Tool(
        name="resize_window",
        description="Resize the active window to specified dimensions. Requires user confirmation.",
        inputSchema={
            "type": "object",
            "properties": {
                "width": {
                    "type": "integer",
                    "description": "Target width in pixels"
                },
                "height": {
                    "type": "integer",
                    "description": "Target height in pixels"
                }
            },
            "required": ["width", "height"]
        }
    ),
    Tool(
        name="click_at",
        description="Simulate a mouse click at specified screen coordinates. Requires user confirmation.",
        inputSchema={
            "type": "object",
            "properties": {
                "x": {
                    "type": "integer",
                    "description": "Screen X coordinate"
                },
                "y": {
                    "type": "integer",
                    "description": "Screen Y coordinate"
                },
                "button": {
                    "type": "string",
                    "description": "Mouse button: 'left' (default) or 'right'",
                    "enum": ["left", "right"]
                },
                "double": {
                    "type": "boolean",
                    "description": "If true, perform a double-click"
                }
            },
            "required": ["x", "y"]
        }
    ),
    Tool(
        name="type_string",
        description="Type a string character by character. Max 500 characters. Requires user confirmation.",
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to type"
                }
            },
            "required": ["text"]
        }
    ),
    Tool(
        name="press_key",
        description="Press a key or key combination (e.g., 'cmd+tab', 'ctrl+c', 'enter'). Blocked combinations are rejected.",
        inputSchema={
            "type": "object",
            "properties": {
                "key_combination": {
                    "type": "string",
                    "description": "Key combination to press. Modifiers: cmd, alt/option, ctrl, shift. Keys: letters, numbers, return, tab, space, delete, escape, arrows, f1-f12."
                }
            },
            "required": ["key_combination"]
        }
    ),
    # File system tools
    Tool(
        name="find_files",
        description="Find files matching a pattern in a directory. Returns file names, paths, and sizes.",
        inputSchema={
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory to search in (default: ~/Downloads)"
                },
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern to match (e.g., '*.md', 'Readme*')"
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Search subdirectories recursively"
                }
            },
            "required": []
        }
    ),
    Tool(
        name="read_file",
        description="Read text file contents. Returns file content with metadata. Max 1MB file size.",
        inputSchema={
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the file to read"
                },
                "max_lines": {
                    "type": "integer",
                    "description": "Maximum lines to read (default: 100)"
                }
            },
            "required": ["filepath"]
        }
    ),
    Tool(
        name="open_file",
        description="Open a file with the default application. Requires user confirmation.",
        inputSchema={
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the file to open"
                }
            },
            "required": ["filepath"]
        }
    ),
    Tool(
        name="list_directory",
        description="List contents of a directory. Returns files and folders with metadata.",
        inputSchema={
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory to list (default: ~/Downloads)"
                }
            },
            "required": []
        }
    ),
    # Screenshot tools
    Tool(
        name="screenshot",
        description="Capture full screen. Requires Screen Recording permission.",
        inputSchema={
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Where to save the screenshot (default: /tmp/screenshot.png)"
                },
                "display_id": {
                    "type": "integer",
                    "description": "Display to capture (0 = main, 1 = second, etc.)"
                },
                "include_cursor": {
                    "type": "boolean",
                    "description": "Include mouse cursor in capture"
                }
            },
            "required": []
        }
    ),
    Tool(
        name="screenshot_window",
        description="Capture a specific window by PID. Requires Screen Recording permission.",
        inputSchema={
            "type": "object",
            "properties": {
                "pid": {
                    "type": "integer",
                    "description": "Process ID of the target window"
                },
                "filepath": {
                    "type": "string",
                    "description": "Where to save the screenshot"
                }
            },
            "required": ["pid"]
        }
    ),
    Tool(
        name="screenshot_region",
        description="Capture a specific screen region. Requires Screen Recording permission.",
        inputSchema={
            "type": "object",
            "properties": {
                "x": {
                    "type": "integer",
                    "description": "X coordinate of top-left corner"
                },
                "y": {
                    "type": "integer",
                    "description": "Y coordinate of top-left corner"
                },
                "width": {
                    "type": "integer",
                    "description": "Width of region"
                },
                "height": {
                    "type": "integer",
                    "description": "Height of region"
                },
                "filepath": {
                    "type": "string",
                    "description": "Where to save the screenshot"
                }
            },
            "required": ["x", "y", "width", "height"]
        }
    ),
    Tool(
        name="get_displays",
        description="Get information about connected displays.",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    # Clipboard tools
    Tool(
        name="get_clipboard",
        description="Get text from clipboard.",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="set_clipboard",
        description="Set clipboard text.",
        inputSchema={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to copy to clipboard"
                }
            },
            "required": ["text"]
        }
    ),
    Tool(
        name="clipboard_has_text",
        description="Check if clipboard contains text.",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
]


class MacOSAssistServer:
    """
    MCP Server for macOS system-level automation.
    """

    def __init__(self):
        self.server = Server("macos-sys-assist")
        self.config: Optional[ServerConfig] = None
        self.validator: Optional[SecurityValidator] = None
        self._setup_handlers()

    def _setup_handlers(self):
        """Set up MCP protocol handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """Return the list of available tools."""
            return TOOLS

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool execution requests."""
            logger.info(f"Tool call: {name}({json.dumps(arguments, indent=2)})")

            # Ensure validator is initialized
            if self.validator is None:
                self.validator = SecurityValidator(self.config)

            try:
                result = self._execute_tool(name, arguments)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": str(e)}, indent=2)
                )]

    def _execute_tool(self, name: str, arguments: dict) -> Dict[str, Any]:
        """
        Execute a tool with the given arguments.
        
        Args:
            name: Tool name.
            arguments: Tool arguments.
        
        Returns:
            Tool execution result.
        """
        # Information tools (read-only)
        if name == "get_active_app":
            return get_active_app(self.validator)

        elif name == "list_open_apps":
            return list_open_apps(self.validator)

        elif name == "get_window_geometry":
            pid = arguments.get("pid")
            if pid is None:
                return {"error": "pid is required"}
            return get_window_geometry(self.validator, pid)

        elif name == "get_screen_resolution":
            return get_screen_resolution(self.validator)

        # Action tools (write operations)
        elif name == "move_window":
            x = arguments.get("x")
            y = arguments.get("y")
            if x is None or y is None:
                return {"error": "x and y are required"}
            return move_window(self.validator, x, y)

        elif name == "resize_window":
            width = arguments.get("width")
            height = arguments.get("height")
            if width is None or height is None:
                return {"error": "width and height are required"}
            return resize_window(self.validator, width, height)

        elif name == "click_at":
            x = arguments.get("x")
            y = arguments.get("y")
            if x is None or y is None:
                return {"error": "x and y are required"}
            button = arguments.get("button", "left")
            double = arguments.get("double", False)
            return click_at(self.validator, x, y, button, double)

        elif name == "type_string":
            text = arguments.get("text")
            if text is None:
                return {"error": "text is required"}
            return type_string(self.validator, text)

        elif name == "press_key":
            key_combination = arguments.get("key_combination")
            if key_combination is None:
                return {"error": "key_combination is required"}
            return press_key(self.validator, key_combination)

        # File system tools
        elif name == "find_files":
            directory = arguments.get("directory", "~/Downloads")
            pattern = arguments.get("pattern", "*")
            recursive = arguments.get("recursive", False)
            return find_files(self.validator, directory, pattern, recursive)

        elif name == "read_file":
            filepath = arguments.get("filepath")
            if filepath is None:
                return {"error": "filepath is required"}
            max_lines = arguments.get("max_lines", 100)
            return read_file(self.validator, filepath, max_lines)

        elif name == "open_file":
            filepath = arguments.get("filepath")
            if filepath is None:
                return {"error": "filepath is required"}
            return open_file(self.validator, filepath)

        elif name == "list_directory":
            directory = arguments.get("directory", "~/Downloads")
            return list_directory(self.validator, directory)

        # Screenshot tools
        elif name == "screenshot":
            filepath = arguments.get("filepath", "/tmp/screenshot.png")
            display_id = arguments.get("display_id", 0)
            include_cursor = arguments.get("include_cursor", False)
            return screenshot(self.validator, filepath, display_id, include_cursor)

        elif name == "screenshot_window":
            pid = arguments.get("pid")
            if pid is None:
                return {"error": "pid is required"}
            filepath = arguments.get("filepath", "/tmp/window.png")
            return screenshot_window(self.validator, pid, filepath)

        elif name == "screenshot_region":
            x = arguments.get("x")
            y = arguments.get("y")
            width = arguments.get("width")
            height = arguments.get("height")
            if None in (x, y, width, height):
                return {"error": "x, y, width, and height are required"}
            filepath = arguments.get("filepath", "/tmp/region.png")
            return screenshot_region(self.validator, x, y, width, height, filepath)

        elif name == "get_displays":
            return get_displays(self.validator)

        # Clipboard tools
        elif name == "get_clipboard":
            return get_clipboard(self.validator)

        elif name == "set_clipboard":
            text = arguments.get("text")
            if text is None:
                return {"error": "text is required"}
            return set_clipboard(self.validator, text)

        elif name == "clipboard_has_text":
            return clipboard_has_text(self.validator)

        else:
            return {"error": f"Unknown tool: {name}"}

    def run(self):
        """Run the MCP server using stdio transport."""
        logger.info("Starting macos-sys-assist MCP server...")

        # Load configuration
        try:
            self.config = load_config()
            logger.info(f"Loaded {len(self.config.allowed_apps)} allowed apps")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)

        # Initialize security validator
        self.validator = SecurityValidator(self.config)
        logger.info("Security validator initialized")

        # Run the server
        import mcp.server.stdio as stdio

        async def run_server():
            async with stdio.stdio_server() as (read_stream, write_stream):
                logger.info("Server running on stdio transport")
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )

        asyncio.run(run_server())


def main():
    """Entry point for the MCP server."""
    server = MacOSAssistServer()
    server.run()


if __name__ == "__main__":
    main()
