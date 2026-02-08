"""
System Tools Installer Module.

Provides functionality for installing common developer tools via winget
and PowerShell commands with status checking and progress tracking.
"""

import subprocess
import json
import threading
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Callable, Any
from datetime import datetime
from enum import Enum

from src.utils.logger import get_logger
from src.utils.resource_path import resource_path
from src.utils.admin_state import AdminState

logger = get_logger("system_tools_installer")

# Get CREATE_NO_WINDOW flag for Windows to prevent console flickering
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


class ToolCategory(Enum):
    """Tool category enumeration."""

    DEVELOPMENT_TOOLS = "Development Tools"
    DEVELOPMENT_ENVIRONMENT = "Development Environment"
    TERMINAL_SHELL = "Terminal & Shell"
    PACKAGE_MANAGERS = "Package Managers"


class SystemToolsInstallerError(Exception):
    """Custom exception for system tools installer errors."""

    pass


class SystemTool:
    """Represents a single system tool."""

    def __init__(
        self,
        tool_id: str,
        name: str,
        description: str,
        category: ToolCategory,
        install_commands: List[str],
        check_command: Optional[str] = None,
        requires_admin: bool = False,
        requires_restart: bool = False,
        post_install_message: Optional[str] = None,
    ) -> None:
        """
        Initialize a system tool.

        Args:
            tool_id: Unique tool identifier
            name: Display name
            description: Tool description
            category: Tool category
            install_commands: List of PowerShell commands to install the tool
            check_command: PowerShell command to check if tool is installed
            requires_admin: Whether admin privileges are required
            requires_restart: Whether system restart is required after installation
            post_install_message: Message to show after successful installation
        """
        self.id = tool_id
        self.name = name
        self.description = description
        self.category = category
        self.install_commands = install_commands
        self.check_command = check_command
        self.requires_admin = requires_admin
        self.requires_restart = requires_restart
        self.post_install_message = post_install_message

    def __repr__(self) -> str:
        """String representation."""
        return f"SystemTool(id='{self.id}', name='{self.name}', category='{self.category.value}')"


class SystemToolsInstaller:
    """System tools installer with PowerShell command execution."""

    def __init__(self) -> None:
        """Initialize system tools installer."""
        self.tools: Dict[str, SystemTool] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load system tools configuration from JSON file."""
        try:
            config_path = Path(resource_path("config/system_tools.json"))

            if not config_path.exists():
                logger.error(f"System tools config not found: {config_path}")
                raise SystemToolsInstallerError("Configuration file not found")

            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Category mapping for robust conversion
            category_mapping = {
                "Development Tools": ToolCategory.DEVELOPMENT_TOOLS,
                "Development Environment": ToolCategory.DEVELOPMENT_ENVIRONMENT,
                "Terminal & Shell": ToolCategory.TERMINAL_SHELL,
                "Package Managers": ToolCategory.PACKAGE_MANAGERS,
            }

            # Parse and create SystemTool objects
            for tool_data in config.get("tools", []):
                try:
                    category = category_mapping.get(tool_data["category"])
                    if not category:
                        logger.error(
                            f"Unknown category '{tool_data['category']}' for tool {tool_data.get('id', 'unknown')}"
                        )
                        continue

                    tool = SystemTool(
                        tool_id=tool_data["id"],
                        name=tool_data["name"],
                        description=tool_data["description"],
                        category=category,
                        install_commands=tool_data["install_commands"],
                        check_command=tool_data.get("check_command"),
                        requires_admin=tool_data.get("requires_admin", False),
                        requires_restart=tool_data.get("requires_restart", False),
                        post_install_message=tool_data.get("post_install_message"),
                    )

                    self.tools[tool.id] = tool

                except Exception as e:
                    logger.error(f"Failed to parse tool {tool_data.get('id', 'unknown')}: {e}")

            logger.info(f"Loaded {len(self.tools)} system tools from config")

        except Exception as e:
            logger.error(f"Failed to load system tools config: {e}")
            raise SystemToolsInstallerError(f"Failed to load configuration: {e}")

    def get_tools_by_category(self, category: ToolCategory) -> List[SystemTool]:
        """
        Get all tools in a category.

        Args:
            category: Category to filter by

        Returns:
            List of system tools
        """
        return [tool for tool in self.tools.values() if tool.category == category]

    def get_all_tools(self) -> List[SystemTool]:
        """Get all system tools."""
        return list(self.tools.values())

    def get_all_categories(self) -> List[ToolCategory]:
        """Get all unique categories from loaded tools."""
        categories = set(tool.category for tool in self.tools.values())
        return sorted(list(categories), key=lambda c: c.value)

    def execute_powershell(
        self, command: str, timeout: int = 600, check: bool = False, suppress_warnings: bool = False
    ) -> Tuple[bool, str, str]:
        """
        Execute a PowerShell command.

        Args:
            command: PowerShell command to execute
            timeout: Command timeout in seconds (default 600 for installations)
            check: Whether to check if command exists before running
            suppress_warnings: Whether to suppress warning logs for failed commands

        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            # Build PowerShell command
            ps_command = [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                command,
            ]

            logger.debug(f"Executing PowerShell: {command[:100]}...")

            result = subprocess.run(
                ps_command,
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=CREATE_NO_WINDOW,
            )

            success = result.returncode == 0
            stdout = result.stdout.strip() if result.stdout else ""
            stderr = result.stderr.strip() if result.stderr else ""

            if success:
                logger.debug(f"PowerShell command succeeded")
            else:
                # Only log warnings if not suppressed (e.g., during status checks)
                if not suppress_warnings:
                    logger.warning(f"PowerShell command failed with code {result.returncode}")
                    if stderr:
                        logger.debug(f"Error output: {stderr[:200]}")
                else:
                    logger.debug(
                        f"PowerShell command failed with code {result.returncode} (expected for status check)"
                    )

            return success, stdout, stderr

        except subprocess.TimeoutExpired:
            logger.error(f"PowerShell command timed out after {timeout}s")
            return False, "", f"Command timed out after {timeout} seconds"

        except Exception as e:
            logger.error(f"PowerShell execution failed: {e}")
            return False, "", str(e)

    def check_tool_status(self, tool_id: str) -> Tuple[bool, str]:
        """
        Check if a tool is already installed.

        Args:
            tool_id: Tool identifier

        Returns:
            Tuple of (is_installed, status_message)
        """
        if tool_id not in self.tools:
            return False, "Tool not found"

        tool = self.tools[tool_id]

        if not tool.check_command:
            return False, "No check command available"

        try:
            success, stdout, stderr = self.execute_powershell(
                tool.check_command, timeout=30, suppress_warnings=True
            )

            if success and stdout:
                # Tool is installed
                return True, f"Installed: {stdout[:100]}"
            else:
                # Tool is not installed
                return False, "Not installed"

        except Exception as e:
            logger.error(f"Failed to check tool status for {tool_id}: {e}")
            return False, "Status check failed"

    def install_tool(
        self, tool_id: str, progress_callback: Optional[Callable[[str], None]] = None
    ) -> Tuple[bool, str]:
        """
        Install a system tool.

        Args:
            tool_id: Tool identifier
            progress_callback: Optional callback for progress updates

        Returns:
            Tuple of (success, message)
        """
        if tool_id not in self.tools:
            return False, "Tool not found"

        tool = self.tools[tool_id]

        # Check admin requirements
        if tool.requires_admin and not AdminState.is_admin():
            return False, "Administrator privileges required"

        try:
            if progress_callback:
                progress_callback(f"Installing {tool.name}...")

            logger.info(f"Installing tool: {tool.name}")

            # Execute installation commands
            for i, command in enumerate(tool.install_commands):
                if progress_callback:
                    progress_callback(f"Executing command {i+1}/{len(tool.install_commands)}...")

                logger.debug(f"Executing installation command: {command[:100]}...")
                success, stdout, stderr = self.execute_powershell(command, timeout=600)

                if progress_callback:
                    if stdout:
                        progress_callback(stdout)
                    if stderr:
                        progress_callback(f"Warning: {stderr}")

                if not success:
                    error_msg = f"Installation failed at command {i+1}: {stderr or 'Unknown error'}"
                    logger.error(error_msg)
                    return False, error_msg

            logger.info(f"Successfully installed: {tool.name}")

            # Return post-install message if available
            if tool.post_install_message:
                return True, tool.post_install_message
            else:
                return True, f"{tool.name} installed successfully!"

        except Exception as e:
            logger.error(f"Failed to install {tool.name}: {e}")
            return False, f"Installation failed: {e}"

    def check_winget_available(self) -> bool:
        """
        Check if winget is available.

        Returns:
            True if winget is available
        """
        try:
            result = subprocess.run(
                ["winget", "--version"],
                capture_output=True,
                timeout=10,
                creationflags=CREATE_NO_WINDOW,
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Winget check failed: {e}")
            return False

    def check_powershell_available(self) -> bool:
        """
        Check if PowerShell is available.

        Returns:
            True if PowerShell is available
        """
        try:
            result = subprocess.run(
                ["powershell.exe", "-Command", "echo test"],
                capture_output=True,
                timeout=10,
                creationflags=CREATE_NO_WINDOW,
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"PowerShell check failed: {e}")
            return False
