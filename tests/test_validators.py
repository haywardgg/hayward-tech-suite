"""Tests for validators module."""

import pytest
from src.utils.validators import Validators, ValidationError


class TestValidators:
    """Test suite for Validators class."""

    def test_validate_path_valid(self):
        """Test path validation with valid path."""
        validator = Validators()
        assert validator.validate_path("C:\\Windows") is True

    def test_validate_path_with_traversal(self):
        """Test path validation rejects path traversal."""
        validator = Validators()
        with pytest.raises(ValidationError):
            validator.validate_path("C:\\Windows\\..\\..\\sensitive")

    def test_validate_command_valid(self):
        """Test command validation with valid command."""
        validator = Validators()
        assert validator.validate_command("ipconfig /all") is True

    def test_validate_command_with_injection(self):
        """Test command validation rejects injection attempts."""
        validator = Validators()
        with pytest.raises(ValidationError):
            validator.validate_command("ipconfig; rm -rf /")

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        validator = Validators()
        result = validator.sanitize_filename("test<file>name*.txt")
        assert "<" not in result
        assert ">" not in result
        assert "*" not in result

    def test_validate_port_valid(self):
        """Test port validation with valid port."""
        validator = Validators()
        assert validator.validate_port(8080) is True

    def test_validate_port_invalid(self):
        """Test port validation with invalid port."""
        validator = Validators()
        with pytest.raises(ValidationError):
            validator.validate_port(70000)

    def test_validate_timeout(self):
        """Test timeout validation."""
        validator = Validators()
        assert validator.validate_timeout(30) is True

    def test_validate_timeout_invalid(self):
        """Test timeout validation with invalid value."""
        validator = Validators()
        with pytest.raises(ValidationError):
            validator.validate_timeout(5000)

    def test_validate_powershell_command_with_pipes(self):
        """Test PowerShell command validation with pipes."""
        validator = Validators()
        # Should pass with allow_shell=True
        assert validator.validate_command(
            'powershell -Command "Get-Process | Select-Object Name"',
            allow_shell=True
        ) is True

    def test_validate_powershell_command_with_quotes_and_parens(self):
        """Test PowerShell command validation with quotes and parentheses."""
        validator = Validators()
        # Should pass with allow_shell=True
        assert validator.validate_command(
            'powershell -Command "(Get-ItemProperty HKLM:\\SOFTWARE).Value"',
            allow_shell=True
        ) is True

    def test_validate_command_with_net_command(self):
        """Test validation of net command."""
        validator = Validators()
        # Should pass with net in whitelist
        assert validator.validate_command("net share", ["net"]) is True

    def test_validate_command_injection_still_blocked(self):
        """Test that dangerous command injection is still blocked."""
        validator = Validators()
        with pytest.raises(ValidationError):
            # Semicolon should still be blocked even with allow_shell
            validator.validate_command("ipconfig; del /f /s /q C:\\Windows", allow_shell=True)

    def test_validate_command_pipes_blocked_without_allow_shell(self):
        """Test that pipes are blocked when allow_shell=False."""
        validator = Validators()
        with pytest.raises(ValidationError):
            # Pipes should be blocked for non-PowerShell commands
            validator.validate_command("ipconfig | findstr", allow_shell=False)

    def test_validate_powershell_command_with_commas(self):
        """Test PowerShell command validation with commas."""
        validator = Validators()
        # Should pass with allow_shell=True for PowerShell commands with commas
        assert validator.validate_command(
            'powershell -Command "Get-MpComputerStatus | Select-Object AntivirusEnabled, RealTimeProtectionEnabled"',
            allow_shell=True
        ) is True

    def test_validate_powershell_command_with_special_chars(self):
        """Test PowerShell command validation with various special characters."""
        validator = Validators()
        # Should pass with allow_shell=True for PowerShell with brackets, backslashes, etc.
        assert validator.validate_command(
            'powershell -Command "$UpdateSession = New-Object -ComObject Microsoft.Update.Session"',
            allow_shell=True
        ) is True

