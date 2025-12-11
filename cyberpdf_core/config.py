"""
Configuration management for CYBER PDF
"""
import os
from pathlib import Path
from typing import Any, Dict
import yaml


class Config:
    """Application configuration manager"""
    
    DEFAULT_CONFIG = {
        "general": {
            "theme": "dark",
            "language": "en",
            "check_updates": True,
        },
        "performance": {
            "enable_gpu": "auto",
            "thumbnail_cache_size": 500,
            "max_memory_mb": 1024,
        },
        "security": {
            "secure_mode": False,
            "auto_cleanup_temp": True,
        },
        "ocr": {
            "default_language": "eng",
            "quality": "medium",
        },
        "plugins": {
            "enabled": True,
            "auto_update": False,
        },
        "ui": {
            "thumbnail_size": 200,
            "grid_columns": "auto",
            "show_page_numbers": True,
        },
    }
    
    def __init__(self) -> None:
        self.config_dir = Path.home() / ".config" / "cyberpdf"
        self.config_file = self.config_dir / "config.yaml"
        self.cache_dir = Path("/tmp/cyberpdf")
        self.plugin_dir = self.config_dir / "plugins"
        
        self._config: Dict[str, Any] = {}
        self._ensure_directories()
        self.load()
    
    def _ensure_directories(self) -> None:
        """Create necessary directories if they don't exist"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> None:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                self._config = yaml.safe_load(f) or {}
        else:
            self._config = self.DEFAULT_CONFIG.copy()
            self.save()
    
    def save(self) -> None:
        """Save configuration to file"""
        with open(self.config_file, "w") as f:
            yaml.dump(self._config, f, default_flow_style=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        Example: config.get('general.theme')
        """
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation
        Example: config.set('general.theme', 'light')
        """
        keys = key.split(".")
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save()
    
    def reset(self) -> None:
        """Reset configuration to defaults"""
        self._config = self.DEFAULT_CONFIG.copy()
        self.save()


# Global configuration instance
config = Config()
