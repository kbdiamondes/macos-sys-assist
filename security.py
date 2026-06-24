"""
Security layer for macos-sys-assist.
Enforces allow-lists, validates inputs, and manages confirmation requirements.
"""

from typing import Optional, Dict, Any
from config import ServerConfig, load_config
from macos.accessibility import AccessibilityWrapper


class SecurityValidator:
    """
    Validates all tool calls against the security configuration.
    Ensures no unauthorized apps or blocked operations are executed.
    """

    def __init__(self, config: Optional[ServerConfig] = None):
        self.config = config or load_config()
        self.accessibility = AccessibilityWrapper()
        self._current_app_cache: Optional[Dict[str, str]] = None

    def get_current_app(self) -> Dict[str, str]:
        """Get the currently focused application (cached per validation cycle)."""
        if self._current_app_cache is None:
            self._current_app_cache = self.accessibility.get_frontmost_app()
        return self._current_app_cache

    def invalidate_cache(self):
        """Clear the cached app state (call before a new validation cycle)."""
        self._current_app_cache = None

    def validate_action(self, action_type: str, require_pid: bool = True) -> Dict[str, Any]:
        """
        Validate that an action is allowed based on the current app context.
        
        Args:
            action_type: The type of action ("click", "type", "key", "window", "info").
            require_pid: Whether the action requires a valid PID.
        
        Returns:
            {
                "valid": True/False,
                "pid": int or None,
                "app_name": str,
                "error": str or None,
                "needs_confirmation": bool
            }
        """
        self.invalidate_cache()
        current = self.get_current_app()
        
        bundle_id = current.get("bundle_id", "")
        pid_str = current.get("pid", "0")
        app_name = current.get("name", "Unknown")
        
        # Check if we have a valid PID
        try:
            pid = int(pid_str)
        except (ValueError, TypeError):
            pid = 0
        
        # Validate PID is reasonable
        if pid <= 0:
            return {
                "valid": False,
                "pid": None,
                "app_name": app_name,
                "error": "No valid application PID found",
                "needs_confirmation": False
            }
        
        # Check if app is in allow-list
        if not self.config.is_app_allowed(bundle_id):
            return {
                "valid": False,
                "pid": pid,
                "app_name": app_name,
                "error": (
                    f"App '{app_name}' (bundle_id: {bundle_id}) is not in the "
                    f"allowed applications list. Add it to allowed_apps.json to "
                    f"grant access."
                ),
                "needs_confirmation": False
            }
        
        # Check if actions are allowed for this app
        app_config = self.config.get_app(bundle_id)
        if action_type in ("click", "type", "key", "window") and not app_config.allow_actions:
            return {
                "valid": False,
                "pid": pid,
                "app_name": app_name,
                "error": (
                    f"Actions are not allowed for '{app_name}'. "
                    f"Set allow_actions to true in allowed_apps.json."
                ),
                "needs_confirmation": False
            }
        
        # Determine if confirmation is needed
        needs_confirmation = False
        settings = self.config.global_settings
        
        if action_type == "click" and settings.require_confirmation_for_click:
            needs_confirmation = True
        elif action_type == "type" and settings.require_confirmation_for_type:
            needs_confirmation = True
        elif action_type == "key" and settings.require_confirmation_for_key:
            needs_confirmation = True
        
        return {
            "valid": True,
            "pid": pid,
            "app_name": app_name,
            "error": None,
            "needs_confirmation": needs_confirmation
        }

    def validate_text_input(self, text: str) -> Dict[str, Any]:
        """
        Validate text input against security constraints.
        
        Args:
            text: The text to validate.
        
        Returns:
            {"valid": True/False, "error": str or None}
        """
        settings = self.config.global_settings
        
        if len(text) > settings.max_string_length:
            return {
                "valid": False,
                "error": (
                    f"Text length ({len(text)}) exceeds maximum allowed "
                    f"({settings.max_string_length})."
                )
            }
        
        return {"valid": True, "error": None}

    def validate_key_combination(self, key_combo: str) -> Dict[str, Any]:
        """
        Validate a key combination against blocked list.
        
        Args:
            key_combo: The key combination to validate.
        
        Returns:
            {"valid": True/False, "error": str or None}
        """
        if self.config.is_key_combination_blocked(key_combo):
            return {
                "valid": False,
                "error": (
                    f"Key combination '{key_combo}' is blocked by security policy. "
                    f"Blocked combinations: {self.config.global_settings.blocked_key_combinations}"
                )
            }
        
        return {"valid": True, "error": None}
