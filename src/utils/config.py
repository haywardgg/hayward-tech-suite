"""
Configuration manager for Hayward Tech Suite.

Loads and manages application configuration from YAML files and environment variables.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from dotenv import load_dotenv

from src.utils.logger import get_logger
from src.utils.resource_path import resource_path

logger = get_logger("config")


class Config:
    """Configuration manager with YAML and environment variable support."""

    _instance: Optional["Config"] = None
    _initialized: bool = False

    def __new__(cls) -> "Config":
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_path: Optional[str] = None) -> None:
        """
        Initialize configuration manager.

        Args:
            config_path: Path to YAML config file
        """
        if not self._initialized:
            self._initialized = True
            self._config: Dict[str, Any] = {}
            self._config_path = Path(config_path or resource_path("config/config.yaml"))
            self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file and environment variables."""
        # Load environment variables from .env file if it exists
        env_file = Path(".env")
        if env_file.exists():
            load_dotenv(env_file)
            logger.info("Loaded environment variables from .env")

        # Load YAML configuration
        if self._config_path.exists():
            try:
                with open(self._config_path, "r", encoding="utf-8") as f:
                    self._config = yaml.safe_load(f) or {}
                logger.info(f"Loaded configuration from {self._config_path}")
            except Exception as e:
                logger.error(f"Failed to load config file: {e}")
                self._config = self._get_default_config()
        else:
            logger.warning(f"Config file not found: {self._config_path}, using defaults")
            self._config = self._get_default_config()

        # Override with environment variables
        self._apply_env_overrides()

    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration.

        Returns:
            Default configuration dictionary
        """
        return {
            "app": {
                "name": "Hayward Tech Suite",
                "version": "1.0.0",
                "debug": False,
            },
            "ui": {
                "theme": "dark",
                "window": {"width": 1200, "height": 800},
            },
            "logging": {
                "level": "INFO",
                "file": "logs/hayward_techsuite.log",
            },
            "monitoring": {
                "cpu_interval": 2,
                "ram_interval": 2,
                "disk_check_interval": 60,
            },
            "system_operations": {
                "command_timeout": 300,
                "require_confirmation": True,
            },
            "security": {
                "audit_logging": True,
                "audit_log_file": "logs/audit.log",
            },
        }

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to configuration."""
        env_mappings = {
            "APP_NAME": ("app", "name"),
            "APP_VERSION": ("app", "version"),
            "DEBUG": ("app", "debug"),
            "LOG_LEVEL": ("logging", "level"),
            "LOG_FILE": ("logging", "file"),
            "DEFAULT_THEME": ("ui", "theme"),
            "COMMAND_TIMEOUT": ("system_operations", "command_timeout"),
            "REQUIRE_ADMIN_CONFIRMATION": ("system_operations", "require_confirmation"),
            "ENABLE_AUDIT_LOG": ("security", "audit_logging"),
            "AUDIT_LOG_FILE": ("security", "audit_log_file"),
        }

        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Type conversion
                if value.lower() in ("true", "false"):
                    value = value.lower() == "true"
                elif value.isdigit():
                    value = int(value)

                # Apply override
                if section not in self._config:
                    self._config[section] = {}
                self._config[section][key] = value
                logger.debug(f"Applied env override: {env_var} = {value}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'app.name' or 'ui.theme')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'app.name')
            value: Value to set
        """
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value
        logger.debug(f"Set config: {key} = {value}")

    def save(self, path: Optional[str] = None) -> None:
        """
        Save configuration to YAML file.

        Args:
            path: Optional custom path to save to
        """
        save_path = Path(path or self._config_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Saved configuration to {save_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()
        logger.info("Configuration reloaded")

    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        logger.info("Resetting configuration to defaults")
        self._config = self._get_default_config()
        self._apply_env_overrides()
        
        # Save defaults to file if config file exists
        if self._config_path.exists() or self._config_path.parent.exists():
            try:
                self._config_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self._config_path, "w", encoding="utf-8") as f:
                    yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)
                logger.info(f"Default configuration saved to {self._config_path}")
            except Exception as e:
                logger.error(f"Failed to save default config: {e}")

    @property
    def all(self) -> Dict[str, Any]:
        """
        Get all configuration.

        Returns:
            Complete configuration dictionary
        """
        return self._config.copy()


# Global config instance
_config_instance = Config()


def get_config() -> Config:
    """
    Get the global configuration instance.

    Returns:
        Config instance
    """
    return _config_instance


# Example usage
if __name__ == "__main__":
    config = get_config()
    print(f"App Name: {config.get('app.name')}")
    print(f"Theme: {config.get('ui.theme')}")
    print(f"Log Level: {config.get('logging.level')}")
    print(f"Command Timeout: {config.get('system_operations.command_timeout')}")
