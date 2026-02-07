"""Tests for resource_path utility."""

import os
import sys
import pytest
from pathlib import Path
from src.utils.resource_path import resource_path


class TestResourcePath:
    """Test suite for resource_path function."""

    def test_resource_path_returns_string(self):
        """Test that resource_path returns a string."""
        result = resource_path("config/config.yaml")
        assert isinstance(result, str)

    def test_resource_path_uses_cwd_when_not_bundled(self):
        """Test that resource_path uses current working directory when not bundled."""
        # When not running as PyInstaller bundle, should use current directory
        result = resource_path("config/config.yaml")
        expected = os.path.join(os.path.abspath("."), "config/config.yaml")
        assert result == expected

    def test_resource_path_with_nested_paths(self):
        """Test resource_path with nested directory paths."""
        result = resource_path("some/nested/path/file.txt")
        expected = os.path.join(os.path.abspath("."), "some/nested/path/file.txt")
        assert result == expected

    def test_resource_path_uses_meipass_when_available(self, monkeypatch):
        """Test that resource_path uses sys._MEIPASS when available (PyInstaller mode)."""
        # Simulate PyInstaller bundle by setting sys._MEIPASS
        test_meipass = "/tmp/test_bundle"
        monkeypatch.setattr(sys, "_MEIPASS", test_meipass, raising=False)
        
        result = resource_path("config/config.yaml")
        expected = os.path.join(test_meipass, "config/config.yaml")
        assert result == expected

    def test_resource_path_with_absolute_path_components(self):
        """Test resource_path with various path formats."""
        # Test with forward slashes
        result1 = resource_path("images/icon.ico")
        assert "images" in result1
        assert "icon.ico" in result1
        
        # Test with backslashes (on Windows)
        if os.name == 'nt':
            result2 = resource_path("images\\icon.ico")
            assert "images" in result2
            assert "icon.ico" in result2

    def test_actual_config_file_accessible(self):
        """Test that actual config file can be accessed via resource_path."""
        config_path = resource_path("config/config.yaml")
        # File should exist in the repository
        assert Path(config_path).exists(), f"Config file should exist at {config_path}"

    def test_actual_registry_tweaks_file_accessible(self):
        """Test that registry tweaks JSON file can be accessed via resource_path."""
        tweaks_path = resource_path("config/registry_tweaks.json")
        # File should exist in the repository
        assert Path(tweaks_path).exists(), f"Registry tweaks file should exist at {tweaks_path}"
