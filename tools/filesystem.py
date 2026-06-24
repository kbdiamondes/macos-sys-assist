"""
File system MCP tools.
Safe, constrained file operations.
"""

from typing import Dict, Any

from security import SecurityValidator


def find_files(
    validator: SecurityValidator,
    directory: str = "~/Downloads",
    pattern: str = "*",
    recursive: bool = False
) -> Dict[str, Any]:
    """
    Find files matching a pattern in a directory.

    Args:
        directory: Directory to search in (default: ~/Downloads)
        pattern: Glob pattern to match (e.g., "*.md", "Readme*")
        recursive: Search subdirectories

    Returns:
        List of matching files
    """
    from macos.filesystem import FileSystemManager

    fs = FileSystemManager()
    return fs.find_files(
        directory=directory,
        pattern=pattern,
        recursive=recursive
    )


def read_file(
    validator: SecurityValidator,
    filepath: str,
    max_lines: int = 100
) -> Dict[str, Any]:
    """
    Read text file contents.

    Args:
        filepath: Path to the file
        max_lines: Maximum lines to read

    Returns:
        File contents with metadata
    """
    from macos.filesystem import FileSystemManager

    fs = FileSystemManager()
    return fs.read_file(filepath=filepath, max_lines=max_lines)


def open_file(
    validator: SecurityValidator,
    filepath: str
) -> Dict[str, Any]:
    """
    Open file with default application.

    Args:
        filepath: Path to the file

    Returns:
        Status of the open operation
    """
    validation = validator.validate_action("open_file")
    if not validation["valid"]:
        return {"error": validation["error"]}

    from macos.filesystem import FileSystemManager

    fs = FileSystemManager()
    return fs.open_file(filepath=filepath)


def list_directory(
    validator: SecurityValidator,
    directory: str = "~/Downloads"
) -> Dict[str, Any]:
    """
    List directory contents.

    Args:
        directory: Directory to list

    Returns:
        Directory contents
    """
    from macos.filesystem import FileSystemManager

    fs = FileSystemManager()
    return fs.list_directory(directory=directory)
