"""
Configuration service for managing user settings.
"""
import os
import json
import sys
from typing import Dict, Any, Optional

# Ensure project root is in path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Local imports
from utils.logger import get_logger

logger = get_logger(__name__)

class ConfigService:
    """Service for managing user configuration and settings."""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize the configuration service with a config file path."""
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self._load_config()
        logger.info(f"ConfigService initialized with file: {config_file}")
    
    def _load_config(self) -> None:
        """Load configuration from file or create with defaults if it doesn't exist."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                    logger.info("Configuration loaded from file")
            else:
                self._create_default_config()
                logger.info("Created default configuration")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self._create_default_config()
    
    def _create_default_config(self) -> None:
        """Create default configuration settings."""
        self.config = {
            "theme": "dark",  # 'dark' or 'light'
            "language": "de",  # 'de' or 'en'
            "auto_save": True,
            "window": {
                "width": 900,
                "height": 650,
                "maximized": False
            },
            "recent_projects": []
        }
        self._save_config()
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            logger.info("Configuration saved to file")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key with optional default."""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value by key."""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the nested dictionary location
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save the updated configuration
        self._save_config()
        logger.info(f"Configuration updated: {key} = {value}")
    
    def add_recent_project(self, project_id: int, project_name: str) -> None:
        """Add a project to the recent projects list."""
        recent_projects = self.config.get("recent_projects", [])
        
        # Remove if already exists to avoid duplicates
        recent_projects = [p for p in recent_projects if p.get("id") != project_id]
        
        # Add to beginning of list
        recent_projects.insert(0, {"id": project_id, "name": project_name})
        
        # Limit to 10 recent projects
        self.config["recent_projects"] = recent_projects[:10]
        self._save_config()
        logger.info(f"Added project to recent list: {project_name} (ID: {project_id})")
    
    def get_recent_projects(self) -> list:
        """Get the list of recent projects."""
        return self.config.get("recent_projects", [])
    
    def clear_recent_projects(self) -> None:
        """Clear the recent projects list."""
        self.config["recent_projects"] = []
        self._save_config()
        logger.info("Cleared recent projects list")
    
    def get_window_settings(self) -> Dict[str, Any]:
        """Get window settings."""
        return self.config.get("window", {
            "width": 900,
            "height": 650,
            "maximized": False
        })
    
    def save_window_settings(self, width: int, height: int, maximized: bool) -> None:
        """Save window settings."""
        self.config["window"] = {
            "width": width,
            "height": height,
            "maximized": maximized
        }
        self._save_config()
        logger.info(f"Saved window settings: {width}x{height}, maximized={maximized}")
