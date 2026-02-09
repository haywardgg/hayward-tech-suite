"""Tests for monitoring service."""

import pytest
from src.core.monitoring import MonitoringService


class TestMonitoringService:
    """Test suite for MonitoringService class."""

    def test_init(self):
        """Test MonitoringService initialization."""
        service = MonitoringService()
        assert service is not None
        assert service.cpu_interval > 0

    def test_get_cpu_info(self):
        """Test getting CPU information."""
        service = MonitoringService()
        info = service.get_cpu_info()
        assert "percent" in info
        assert isinstance(info["percent"], (int, float))

    def test_get_ram_info(self):
        """Test getting RAM information."""
        service = MonitoringService()
        info = service.get_ram_info()
        assert "total" in info
        assert "percent" in info
        assert info["total"] > 0

    def test_get_disk_info(self):
        """Test getting disk information."""
        service = MonitoringService()
        info = service.get_disk_info()
        assert "disks" in info
        assert isinstance(info["disks"], list)

    def test_register_callback(self):
        """Test callback registration."""
        service = MonitoringService()

        callback_called = []

        def test_callback(data):
            callback_called.append(data)

        service.register_callback("cpu", test_callback)
        assert "cpu" in service._callbacks
