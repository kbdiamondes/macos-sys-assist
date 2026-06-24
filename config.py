"""
Configuration management for macos-sys-assist.
Loads and validates the allowed_apps.json configuration file.
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional


CONFIG_FILE = Path(__file__).parent / "allowed_apps.json"


@dataclass
class AllowedApp:
    """Represents an application that the AI is authorized to interact with."""
    bundle_id: str
    name: str
    allow_actions: bool = True


@dataclass
class GlobalSettings:
    """Global security settings for the MCP server."""
    require_confirmation_for_click: bool = True
    require_confirmation_for_type: bool = True
    require_confirmation_for_key: bool = False
    max_string_length: int = 500
    blocked_key_combinations: List[str] = field(default_factory=list)


@dataclass
class ServerConfig:
    """Main configuration for the MCP server."""
    allowed_apps: List[AllowedApp] = field(default_factory=list)
    global_settings: GlobalSettings = field(default_factory=GlobalSettings)

    def is_app_allowed(self, bundle_id: str) -> bool:
        """Check if a specific app is in the allow-list."""
        return any(app.bundle_id == bundle_id for app in self.allowed_apps)

    def get_app(self, bundle_id: str) -> Optional[AllowedApp]:
        """Get an allowed app by its bundle ID."""
        for app in self.allowed_apps:
            if app.bundle_id == bundle_id:
                return app
        return None

    def is_key_combination_blocked(self, key_combo: str) -> bool:
        """Check if a key combination is explicitly blocked."""
        return key_combo.lower() in [
            k.lower() for k in self.global_settings.blocked_key_combinations
        ]


def load_config(config_path: Optional[Path] = None) -> ServerConfig:
    """Load configuration from the JSON file."""
    path = config_path or CONFIG_FILE
    
    if not path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {path}\n"
            "Please ensure allowed_apps.json exists in the project root."
        )
    
    with open(path, "r") as f:
        data = json.load(f)
    
    # Parse allowed apps
    apps = []
    for app_data in data.get("allowed_apps", []):
        apps.append(AllowedApp(
            bundle_id=app_data["bundle_id"],
            name=app_data["name"],
            allow_actions=app_data.get("allow_actions", True)
        ))
    
    # Parse global settings
    settings_data = data.get("global_settings", {})
    settings = GlobalSettings(
        require_confirmation_for_click=settings_data.get("require_confirmation_for_click", True),
        require_confirmation_for_type=settings_data.get("require_confirmation_for_type", True),
        require_confirmation_for_key=settings_data.get("require_confirmation_for_key", False),
        max_string_length=settings_data.get("max_string_length", 500),
        blocked_key_combinations=settings_data.get("blocked_key_combinations", [])
    )
    
    return ServerConfig(allowed_apps=apps, global_settings=settings)
