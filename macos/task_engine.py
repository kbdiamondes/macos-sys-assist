"""
Multi-step task execution engine for macOS automation.
Decomposes complex prompts into executable steps.
"""

import re
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class TaskStep:
    """Single step in a task."""
    action: str
    params: Dict[str, Any]
    description: str = ""
    depends_on: Optional[int] = None  # Step index this depends on
    extract_from: Optional[str] = None  # Path to extract value from previous result


@dataclass
class TaskResult:
    """Result of a task execution."""
    status: str  # "success", "failed", "partial"
    steps_completed: int
    total_steps: int
    results: List[Dict]
    error: Optional[str] = None
    final_output: Optional[str] = None


class TaskEngine:
    """
    Execute multi-step tasks on macOS.
    Chains together actions to accomplish complex prompts.
    """

    def __init__(
        self,
        filesystem,
        app_lifecycle,
        window_manager,
        input_simulator,
        accessibility
    ):
        self.fs = filesystem
        self.app = app_lifecycle
        self.wm = window_manager
        self.input = input_simulator
        self.accessibility = accessibility

        # Register available actions
        self.actions: Dict[str, Callable] = {
            # File system actions
            "find_files": self._find_files,
            "read_file": self._read_file,
            "open_file": self._open_file,
            "list_directory": self._list_directory,

            # App lifecycle actions
            "launch_app": self._launch_app,
            "quit_app": self._quit_app,
            "focus_app": self._focus_app,

            # Window actions
            "get_active_app": self._get_active_app,
            "move_window": self._move_window,
            "resize_window": self._resize_window,

            # Input actions
            "type_string": self._type_string,
            "press_key": self._press_key,
            "click_at": self._click_at,

            # Information actions
            "get_screen_resolution": self._get_screen_resolution,
        }

    def _extract_value(self, result: Dict, path: str) -> Any:
        """
        Extract a value from a result using dot notation.
        Example: "files[0].path" extracts result["files"][0]["path"]
        """
        try:
            # Handle array indexing
            match = re.match(r'(\w+)\[(\d+)\]\.(\w+)', path)
            if match:
                key, index, field = match.groups()
                return result[key][int(index)][field]

            # Handle simple dot notation
            parts = path.split('.')
            value = result
            for part in parts:
                if '[' in part:
                    key, idx = part.split('[')
                    idx = int(idx.rstrip(']'))
                    value = value[key][idx]
                else:
                    value = value[part]
            return value

        except (KeyError, IndexError, TypeError):
            return None

    # Action implementations

    def _find_files(self, directory: str = "~/Downloads", pattern: str = "*", **kwargs) -> Dict:
        return self.fs.find_files(directory=directory, pattern=pattern, **kwargs)

    def _read_file(self, filepath: str, max_lines: int = 100, **kwargs) -> Dict:
        return self.fs.read_file(filepath=filepath, max_lines=max_lines)

    def _open_file(self, filepath: str, **kwargs) -> Dict:
        return self.fs.open_file(filepath=filepath)

    def _list_directory(self, directory: str = "~/Downloads", **kwargs) -> Dict:
        return self.fs.list_directory(directory=directory, **kwargs)

    def _launch_app(self, app_name: str = None, bundle_id: str = None, **kwargs) -> Dict:
        return self.app.launch_app(app_name=app_name, bundle_id=bundle_id)

    def _quit_app(self, app_name: str = None, bundle_id: str = None, force: bool = False, **kwargs) -> Dict:
        return self.app.quit_app(app_name=app_name, bundle_id=bundle_id, force=force)

    def _focus_app(self, app_name: str = None, bundle_id: str = None, **kwargs) -> Dict:
        return self.app.focus_app(app_name=app_name, bundle_id=bundle_id)

    def _get_active_app(self, **kwargs) -> Dict:
        return self.accessibility.get_frontmost_app()

    def _move_window(self, x: int = 0, y: int = 0, pid: int = None, **kwargs) -> Dict:
        if pid is None:
            app = self.accessibility.get_frontmost_app()
            pid = int(app.get('pid', 0))
        return self.wm.move_window(pid, x, y)

    def _resize_window(self, width: int = 800, height: int = 600, pid: int = None, **kwargs) -> Dict:
        if pid is None:
            app = self.accessibility.get_frontmost_app()
            pid = int(app.get('pid', 0))
        return self.wm.resize_window(pid, width, height)

    def _type_string(self, text: str = "", **kwargs) -> Dict:
        return self.input.type_string(text)

    def _press_key(self, key_combination: str = "", **kwargs) -> Dict:
        return self.input.press_key(key_combination)

    def _click_at(self, x: int = 0, y: int = 0, **kwargs) -> Dict:
        return self.input.click_at(x, y)

    def _get_screen_resolution(self, **kwargs) -> Dict:
        return self.accessibility.get_screen_resolution()

    def execute(self, steps: List[TaskStep]) -> TaskResult:
        """
        Execute a sequence of steps.

        Args:
            steps: List of TaskStep objects to execute

        Returns:
            TaskResult with status and results
        """
        results = []
        completed_steps = 0

        for i, step in enumerate(steps):
            # Check if action exists
            if step.action not in self.actions:
                return TaskResult(
                    status="failed",
                    steps_completed=completed_steps,
                    total_steps=len(steps),
                    results=results,
                    error=f"Unknown action: {step.action}"
                )

            # Resolve dependencies
            params = step.params.copy()
            if step.extract_from and step.depends_on is not None:
                if step.depends_on < len(results):
                    prev_result = results[step.depends_on].get("result", {})
                    extracted = self._extract_value(prev_result, step.extract_from)
                    if extracted is not None:
                        # Find the first parameter that looks like it should receive this value
                        for key in params:
                            if params[key] is None or params[key] == "":
                                params[key] = extracted
                                break
                        # Special handling for filepath parameter
                        if "filepath" in params and params["filepath"] is None:
                            params["filepath"] = extracted

            # Execute the action
            try:
                result = self.actions[step.action](**params)
                results.append({
                    "step": i + 1,
                    "action": step.action,
                    "description": step.description,
                    "params": params,
                    "result": result,
                })
                completed_steps += 1

                # Check for errors
                if "error" in result:
                    return TaskResult(
                        status="failed",
                        steps_completed=completed_steps,
                        total_steps=len(steps),
                        results=results,
                        error=f"Step {i + 1} failed: {result['error']}"
                    )

            except Exception as e:
                return TaskResult(
                    status="failed",
                    steps_completed=completed_steps,
                    total_steps=len(steps),
                    results=results,
                    error=f"Step {i + 1} exception: {str(e)}"
                )

        return TaskResult(
            status="success",
            steps_completed=completed_steps,
            total_steps=len(steps),
            results=results,
            final_output=self._generate_summary(results)
        )

    def _generate_summary(self, results: List[Dict]) -> str:
        """Generate a human-readable summary of the task execution."""
        if not results:
            return "No steps executed."

        summaries = []
        for r in results:
            action = r["action"]
            desc = r.get("description", action)
            result = r["result"]

            if "error" in result:
                summaries.append(f"❌ {desc}: {result['error']}")
            elif "status" in result and result["status"] == "success":
                summaries.append(f"✅ {desc}")
            elif "files" in result:
                summaries.append(f"✅ {desc}: Found {result.get('total', 0)} items")
            elif "content" in result:
                summaries.append(f"✅ {desc}: Read {result.get('lines', 0)} lines")
            else:
                summaries.append(f"✅ {desc}")

        return "\n".join(summaries)


class PromptParser:
    """
    Parse natural language prompts into task steps.
    Converts user intent into executable TaskStep objects.
    """

    # Common patterns
    PATTERNS = {
        "find_file": [
            r"find (.+?) (?:in|on|from) (.+)",
            r"search (?:for )?(.+?) (?:in|on|from) (.+)",
            r"look for (.+?) (?:in|on|from) (.+)",
        ],
        "open_file": [
            r"open (.+)",
            r"launch (.+)",
        ],
        "list_folder": [
            r"list (?:the )?(?:contents of )?(.+)",
            r"show me (.+)",
            r"what's in (.+)",
        ],
    }

    # Common directory aliases
    DIRECTORY_ALIASES = {
        "downloads": "~/Downloads",
        "desktop": "~/Desktop",
        "documents": "~/Documents",
        "home": "~",
        "pictures": "~/Pictures",
        "music": "~/Music",
        "movies": "~/Movies",
    }

    @classmethod
    def parse(cls, prompt: str) -> List[TaskStep]:
        """
        Parse a natural language prompt into task steps.

        Args:
            prompt: User's natural language prompt

        Returns:
            List of TaskStep objects
        """
        prompt_lower = prompt.lower().strip()
        steps = []

        # Check for "find X in Y and open it"
        find_and_open = re.search(
            r"find (.+?) (?:in|on|from) (.+?) (?:and|then) open (?:it|the file|the result)",
            prompt_lower
        )
        if find_and_open:
            filename = find_and_open.group(1).strip()
            directory = cls._resolve_directory(find_and_open.group(2).strip())

            steps.append(TaskStep(
                action="find_files",
                params={"directory": directory, "pattern": filename},
                description=f"Find '{filename}' in {directory}"
            ))

            steps.append(TaskStep(
                action="open_file",
                params={"filepath": None},  # Will be resolved from previous step
                description="Open the found file",
                depends_on=0,
                extract_from="files[0].path"
            ))

            return steps

        # Check for "find and open X"
        find_open = re.search(
            r"(?:find|search for|locate) and open (.+?)(?:\s+in\s+(.+))?$",
            prompt_lower
        )
        if find_open:
            filename = find_open.group(1).strip()
            directory = cls._resolve_directory(
                find_open.group(2).strip() if find_open.group(2) else "~/Downloads"
            )

            steps.append(TaskStep(
                action="find_files",
                params={"directory": directory, "pattern": filename},
                description=f"Find '{filename}' in {directory}"
            ))

            steps.append(TaskStep(
                action="open_file",
                params={"filepath": None},
                description="Open the found file",
                depends_on=0,
                extract_from="files[0].path"
            ))

            return steps

        # Check for "find X in Y"
        find_match = re.search(
            r"(?:find|search for|look for) (.+?) (?:in|on|from) (.+)",
            prompt_lower
        )
        if find_match:
            filename = find_match.group(1).strip()
            directory = cls._resolve_directory(find_match.group(2).strip())

            steps.append(TaskStep(
                action="find_files",
                params={"directory": directory, "pattern": filename},
                description=f"Find '{filename}' in {directory}"
            ))

            return steps

        # Check for "open X in Y folder"
        open_in_folder = re.search(
            r"open (.+?) (?:in|from|on) (.+?) (?:folder|directory)?",
            prompt_lower
        )
        if open_in_folder:
            filename = open_in_folder.group(1).strip()
            directory = cls._resolve_directory(open_in_folder.group(2).strip())

            # Find the file first
            steps.append(TaskStep(
                action="find_files",
                params={"directory": directory, "pattern": filename},
                description=f"Find '{filename}' in {directory}"
            ))

            # Open the found file
            steps.append(TaskStep(
                action="open_file",
                params={"filepath": None},
                description="Open the found file",
                depends_on=0,
                extract_from="files[0].path"
            ))

            return steps

        # Check for "open X" (simple case)
        open_match = re.search(r"(?:open|launch) (.+)", prompt_lower)
        if open_match:
            target = open_match.group(1).strip()

            # Check if it's a file path (contains / or .)
            if '/' in target or '.' in target:
                # Check if it looks like a filename (has extension)
                if '.' in target and not target.startswith('.'):
                    # Try to find it in Downloads first
                    steps.append(TaskStep(
                        action="find_files",
                        params={"directory": "~/Downloads", "pattern": target},
                        description=f"Find '{target}' in Downloads"
                    ))

                    steps.append(TaskStep(
                        action="open_file",
                        params={"filepath": None},
                        description="Open the found file",
                        depends_on=0,
                        extract_from="files[0].path"
                    ))
                else:
                    steps.append(TaskStep(
                        action="open_file",
                        params={"filepath": target},
                        description=f"Open {target}"
                    ))
            else:
                # Assume it's an app name
                steps.append(TaskStep(
                    action="launch_app",
                    params={"app_name": target.title()},
                    description=f"Launch {target}"
                ))

            return steps

        # Check for "list X"
        list_match = re.search(
            r"(?:list|show me|what's in) (?:the )?(?:contents of )?(.+)",
            prompt_lower
        )
        if list_match:
            directory = cls._resolve_directory(list_match.group(1).strip())

            steps.append(TaskStep(
                action="list_directory",
                params={"directory": directory},
                description=f"List contents of {directory}"
            ))

            return steps

        # Check for "what app is focused"
        if "what app" in prompt_lower and "focused" in prompt_lower:
            steps.append(TaskStep(
                action="get_active_app",
                params={},
                description="Get currently focused app"
            ))

            return steps

        # Check for "arrange windows side by side"
        if "side by side" in prompt_lower or "split" in prompt_lower:
            steps.append(TaskStep(
                action="get_screen_resolution",
                params={},
                description="Get screen resolution"
            ))
            # Would need more complex logic for actual window arrangement
            return steps

        # Default: return empty list (unrecognized prompt)
        return steps

    @classmethod
    def _resolve_directory(cls, directory: str) -> str:
        """Resolve directory aliases to actual paths."""
        dir_lower = directory.lower().strip()

        # Check aliases
        for alias, path in cls.DIRECTORY_ALIASES.items():
            if alias in dir_lower:
                return path

        # Return as-is if not an alias
        return directory
