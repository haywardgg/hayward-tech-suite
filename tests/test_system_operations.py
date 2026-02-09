"""Tests for system operations module."""

import pytest
import sys
from unittest.mock import Mock, patch
from src.core.system_operations import SystemOperations, ValidationError


class TestSystemOperations:
    """Test suite for SystemOperations class."""

    def test_init(self):
        """Test SystemOperations initialization."""
        ops = SystemOperations()
        assert ops is not None
        assert ops.timeout > 0

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    @patch('src.core.system_operations.ctypes.windll.shell32.IsUserAnAdmin')
    def test_is_admin(self, mock_admin):
        """Test admin check."""
        mock_admin.return_value = 1
        ops = SystemOperations()
        assert ops.is_admin() is True

    def test_execute_command_with_invalid_command(self):
        """Test command execution with invalid command."""
        ops = SystemOperations()
        with pytest.raises(ValidationError):
            ops.execute_command("rm -rf /", audit=False)

    def test_flush_dns_mock(self):
        """Test DNS flush (mocked)."""
        ops = SystemOperations()
        with patch.object(ops, 'execute_command') as mock_exec:
            mock_exec.return_value = (True, "Success", "")
            result = ops.flush_dns()
            assert result is True
            mock_exec.assert_called_once()
