"""Tests for configuration module."""

import pytest
from src.utils.config import Config


class TestConfig:
    """Test suite for Config class."""

    def test_config_singleton(self):
        """Test that Config implements singleton pattern."""
        config1 = Config()
        config2 = Config()
        assert config1 is config2

    def test_get_default_value(self):
        """Test getting default configuration value."""
        config = Config()
        app_name = config.get("app.name")
        assert app_name is not None
        assert isinstance(app_name, str)

    def test_get_with_default(self):
        """Test getting non-existent key with default."""
        config = Config()
        value = config.get("nonexistent.key", "default_value")
        assert value == "default_value"

    def test_set_and_get(self):
        """Test setting and getting a value."""
        config = Config()
        config.set("test.key", "test_value")
        value = config.get("test.key")
        assert value == "test_value"

    def test_nested_get(self):
        """Test getting nested configuration value."""
        config = Config()
        theme = config.get("ui.theme")
        assert theme in ["dark", "light", "system"]
