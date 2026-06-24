"""
File system operations for macOS.
Safe, constrained file operations for the MCP server.
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


class FileSystemManager:
    """
    Safe file system operations for macOS.
    All operations are constrained to prevent destructive actions.
    """

    # Restricted paths (cannot be accessed)
    RESTRICTED_PATHS = [
        "/System",
        "/Library/Keychains",
        "~/.ssh",
        "~/.gnupg",
        "/private/var/db",
    ]

    # Maximum file size for reading (1MB)
    MAX_READ_SIZE = 1_000_000

    # Maximum lines to read
    MAX_READ_LINES = 1000

    def __init__(self):
        pass

    def _is_restricted(self, path: Path) -> bool:
        """Check if a path is restricted."""
        resolved = path.expanduser().resolve()
        for restricted in self.RESTRICTED_PATHS:
            restricted_path = Path(restricted).expanduser().resolve()
            try:
                resolved.relative_to(restricted_path)
                return True
            except ValueError:
                continue
        return False

    def find_files(
        self,
        directory: str = "~/Downloads",
        pattern: str = "*",
        recursive: bool = False,
        max_results: int = 50
    ) -> Dict:
        """
        Find files matching a pattern in a directory.

        Args:
            directory: Directory to search in (default: ~/Downloads)
            pattern: Glob pattern to match (e.g., "*.md", "Readme*")
            recursive: Search subdirectories
            max_results: Maximum number of results

        Returns:
            List of matching files with metadata
        """
        try:
            dir_path = Path(directory).expanduser()

            if not dir_path.exists():
                return {"error": f"Directory not found: {directory}"}

            if not dir_path.is_dir():
                return {"error": f"Not a directory: {directory}"}

            if self._is_restricted(dir_path):
                return {"error": "Access to this directory is restricted"}

            # Find files (case-insensitive)
            if recursive:
                files = list(dir_path.rglob(pattern))
            else:
                files = list(dir_path.glob(pattern))

            # If no results, try case-insensitive search
            if not files:
                # Try case-insensitive by listing all files and filtering
                all_files = list(dir_path.iterdir()) if not recursive else list(dir_path.rglob("*"))
                pattern_lower = pattern.lower()
                files = [
                    f for f in all_files
                    if pattern_lower in f.name.lower() or f.match(pattern)
                ]

            # Filter and limit results
            results = []
            for f in files[:max_results]:
                if f.exists():
                    results.append({
                        "name": f.name,
                        "path": str(f),
                        "size": f.stat().st_size if f.is_file() else 0,
                        "is_file": f.is_file(),
                        "is_dir": f.is_dir(),
                        "extension": f.suffix if f.is_file() else "",
                    })

            return {
                "files": results,
                "total": len(results),
                "search_dir": str(dir_path),
                "pattern": pattern,
            }

        except Exception as e:
            return {"error": str(e)}

    def read_file(
        self,
        filepath: str,
        max_lines: int = 100
    ) -> Dict:
        """
        Read text file contents (safe, limited).

        Args:
            filepath: Path to the file
            max_lines: Maximum lines to read

        Returns:
            File contents with metadata
        """
        try:
            path = Path(filepath).expanduser()

            if not path.exists():
                return {"error": f"File not found: {filepath}"}

            if not path.is_file():
                return {"error": f"Not a file: {filepath}"}

            if self._is_restricted(path):
                return {"error": "Access to this file is restricted"}

            # Check file size
            file_size = path.stat().st_size
            if file_size > self.MAX_READ_SIZE:
                return {
                    "error": f"File too large ({file_size} bytes). Maximum: {self.MAX_READ_SIZE} bytes"
                }

            # Read file
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line)

            content = "".join(lines)

            return {
                "content": content,
                "lines": len(lines),
                "size": file_size,
                "filepath": str(path),
                "truncated": len(lines) >= max_lines,
            }

        except UnicodeDecodeError:
            return {"error": "Binary file, cannot read as text"}
        except Exception as e:
            return {"error": str(e)}

    def open_file(self, filepath: str) -> Dict:
        """
        Open file with default application.

        Args:
            filepath: Path to the file

        Returns:
            Status of the open operation
        """
        try:
            path = Path(filepath).expanduser()

            if not path.exists():
                return {"error": f"File not found: {filepath}"}

            if self._is_restricted(path):
                return {"error": "Access to this file is restricted"}

            # Use macOS open command
            result = subprocess.run(
                ["open", str(path)],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return {
                    "status": "success",
                    "filepath": str(path),
                    "filename": path.name,
                }
            else:
                return {"error": result.stderr or "Failed to open file"}

        except subprocess.TimeoutExpired:
            return {"error": "Open command timed out"}
        except Exception as e:
            return {"error": str(e)}

    def list_directory(
        self,
        directory: str = "~/Downloads",
        show_hidden: bool = False
    ) -> Dict:
        """
        List directory contents.

        Args:
            directory: Directory to list
            show_hidden: Include hidden files (starting with .)

        Returns:
            Directory contents with metadata
        """
        try:
            dir_path = Path(directory).expanduser()

            if not dir_path.exists():
                return {"error": f"Directory not found: {directory}"}

            if not dir_path.is_dir():
                return {"error": f"Not a directory: {directory}"}

            if self._is_restricted(dir_path):
                return {"error": "Access to this directory is restricted"}

            files = []
            folders = []

            for item in sorted(dir_path.iterdir()):
                # Skip hidden files if not requested
                if not show_hidden and item.name.startswith('.'):
                    continue

                item_info = {
                    "name": item.name,
                    "path": str(item),
                    "size": item.stat().st_size if item.is_file() else 0,
                    "extension": item.suffix if item.is_file() else "",
                }

                if item.is_file():
                    files.append(item_info)
                elif item.is_dir():
                    folders.append(item_info)

            return {
                "directory": str(dir_path),
                "files": files,
                "folders": folders,
                "total_files": len(files),
                "total_folders": len(folders),
            }

        except Exception as e:
            return {"error": str(e)}

    def get_file_info(self, filepath: str) -> Dict:
        """
        Get detailed file information.

        Args:
            filepath: Path to the file

        Returns:
            File metadata
        """
        try:
            path = Path(filepath).expanduser()

            if not path.exists():
                return {"error": f"File not found: {filepath}"}

            stat = path.stat()

            return {
                "name": path.name,
                "path": str(path),
                "size": stat.st_size,
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
                "extension": path.suffix,
                "modified": stat.st_mtime,
                "created": stat.st_ctime,
            }

        except Exception as e:
            return {"error": str(e)}
