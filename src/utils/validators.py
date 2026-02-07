"""
Input validation utilities for Ghost Toolz Evolved.

Provides validation functions for user inputs, system paths, and command arguments.
"""

import os
import re
from pathlib import Path
from typing import List, Optional, Tuple
import string

from src.utils.logger import get_logger

logger = get_logger("validators")


class ValidationError(Exception):
    """Custom exception for validation errors."""

    pass


class Validators:
    """Collection of validation utilities."""

    # Allowed characters for different input types
    SAFE_PATH_CHARS = set(string.ascii_letters + string.digits + r":\/-_. ()")
    SAFE_COMMAND_CHARS = set(string.ascii_letters + string.digits + r":\/-_. ")

    @staticmethod
    def validate_path(path: str, must_exist: bool = False, must_be_dir: bool = False) -> bool:
        """
        Validate a file system path.

        Args:
            path: Path to validate
            must_exist: Whether path must exist
            must_be_dir: Whether path must be a directory

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        if not path:
            raise ValidationError("Path cannot be empty")

        # Check for dangerous patterns
        if ".." in path:
            raise ValidationError("Path traversal not allowed")

        # Convert to Path object for validation
        try:
            path_obj = Path(path)
        except Exception as e:
            raise ValidationError(f"Invalid path format: {e}")

        # Check if path exists when required
        if must_exist and not path_obj.exists():
            raise ValidationError(f"Path does not exist: {path}")

        # Check if it's a directory when required
        if must_be_dir and path_obj.exists() and not path_obj.is_dir():
            raise ValidationError(f"Path is not a directory: {path}")

        # Check for unsafe characters
        path_str = str(path)
        unsafe_chars = set(path_str) - Validators.SAFE_PATH_CHARS
        if unsafe_chars:
            raise ValidationError(f"Path contains unsafe characters: {unsafe_chars}")

        logger.debug(f"Path validated: {path}")
        return True

    @staticmethod
    def validate_command(command: str, allowed_commands: Optional[List[str]] = None, allow_shell: bool = False) -> bool:
        """
        Validate a system command.

        Args:
            command: Command to validate
            allowed_commands: Optional whitelist of allowed commands
            allow_shell: If True, allow shell metacharacters for PowerShell commands

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        if not command:
            raise ValidationError("Command cannot be empty")

        # Check if this is a PowerShell command
        is_powershell = command.strip().lower().startswith(('powershell', 'pwsh'))

        # Check for command injection patterns (relaxed for PowerShell)
        if not (allow_shell and is_powershell):
            dangerous_patterns = [
                r"[;&|`]",  # Command chaining/injection including pipes
                r"\$\(",  # Command substitution
                r">\s*/",  # Writing to system paths
                r"<\s*/",  # Reading from system paths
            ]

            for pattern in dangerous_patterns:
                if re.search(pattern, command):
                    raise ValidationError(f"Command contains dangerous pattern: {pattern}")

        # Check whitelist if provided
        if allowed_commands:
            command_base = command.split()[0] if command.split() else ""
            if command_base not in allowed_commands:
                raise ValidationError(f"Command not in whitelist: {command_base}")

        # Check for unsafe characters (more permissive for PowerShell)
        if allow_shell and is_powershell:
            # Allow only necessary characters for PowerShell commands
            safe_chars = Validators.SAFE_COMMAND_CHARS | {"|", ">", "<", '"', "'", "(", ")", "=", "-", ",", "{", "}", "[", "]", "\\", "@", "$", ".", "?"}
        else:
            safe_chars = Validators.SAFE_COMMAND_CHARS | {"|", ">", "<"}
        
        unsafe_chars = set(command) - safe_chars
        if unsafe_chars:
            raise ValidationError(f"Command contains unsafe characters: {unsafe_chars}")

        logger.debug(f"Command validated: {command[:50]}...")
        return True

    @staticmethod
    def validate_port(port: int) -> bool:
        """
        Validate a network port number.

        Args:
            port: Port number to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(port, int):
            raise ValidationError("Port must be an integer")

        if port < 1 or port > 65535:
            raise ValidationError(f"Port must be between 1 and 65535, got {port}")

        logger.debug(f"Port validated: {port}")
        return True

    @staticmethod
    def validate_timeout(timeout: int, min_value: int = 1, max_value: int = 3600) -> bool:
        """
        Validate a timeout value in seconds.

        Args:
            timeout: Timeout in seconds
            min_value: Minimum allowed value
            max_value: Maximum allowed value

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(timeout, int):
            raise ValidationError("Timeout must be an integer")

        if timeout < min_value or timeout > max_value:
            raise ValidationError(f"Timeout must be between {min_value} and {max_value}")

        logger.debug(f"Timeout validated: {timeout}")
        return True

    @staticmethod
    def sanitize_filename(filename: str, replacement: str = "_") -> str:
        """
        Sanitize a filename by removing/replacing unsafe characters.

        Args:
            filename: Original filename
            replacement: Character to replace unsafe chars with

        Returns:
            Sanitized filename
        """
        # Remove path separators and other dangerous chars
        dangerous_chars = r'[<>:"/\\|?*\x00-\x1f]'
        sanitized = re.sub(dangerous_chars, replacement, filename)

        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(". ")

        # Ensure not empty
        if not sanitized:
            sanitized = "unnamed"

        # Limit length
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            max_name_len = 255 - len(ext)
            sanitized = name[:max_name_len] + ext

        logger.debug(f"Filename sanitized: {filename} -> {sanitized}")
        return sanitized

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate an email address format.

        Args:
            email: Email address to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(email_pattern, email):
            raise ValidationError(f"Invalid email format: {email}")

        logger.debug(f"Email validated: {email}")
        return True

    @staticmethod
    def validate_disk_drive(drive: str) -> bool:
        """
        Validate a Windows disk drive letter.

        Args:
            drive: Drive letter (e.g., 'C:', 'D:')

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        drive_pattern = r"^[A-Za-z]:$"

        if not re.match(drive_pattern, drive):
            raise ValidationError(f"Invalid drive format: {drive}. Expected format: 'C:'")

        logger.debug(f"Drive validated: {drive}")
        return True

    @staticmethod
    def validate_ip_address(ip: str) -> Tuple[bool, str]:
        """
        Validate an IPv4 address.

        Args:
            ip: IP address string

        Returns:
            Tuple of (is_valid, version) where version is 'ipv4' or 'ipv6'

        Raises:
            ValidationError: If validation fails
        """
        # IPv4 pattern
        ipv4_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"

        if re.match(ipv4_pattern, ip):
            # Validate each octet
            octets = ip.split(".")
            for octet in octets:
                if int(octet) > 255:
                    raise ValidationError(f"Invalid IPv4 address: {ip}")
            logger.debug(f"IPv4 address validated: {ip}")
            return True, "ipv4"

        # Basic IPv6 pattern (simplified)
        ipv6_pattern = r"^([0-9a-fA-F]{0,4}:){7}[0-9a-fA-F]{0,4}$"
        if re.match(ipv6_pattern, ip):
            logger.debug(f"IPv6 address validated: {ip}")
            return True, "ipv6"

        raise ValidationError(f"Invalid IP address: {ip}")


# Example usage
if __name__ == "__main__":
    validators = Validators()

    # Test path validation
    try:
        validators.validate_path("C:\\Windows\\System32")
        print("✓ Path validation passed")
    except ValidationError as e:
        print(f"✗ Path validation failed: {e}")

    # Test command validation
    try:
        validators.validate_command("ipconfig /all")
        print("✓ Command validation passed")
    except ValidationError as e:
        print(f"✗ Command validation failed: {e}")

    # Test filename sanitization
    unsafe_name = 'test<file>name*.txt'
    safe_name = validators.sanitize_filename(unsafe_name)
    print(f"Sanitized filename: {unsafe_name} -> {safe_name}")
