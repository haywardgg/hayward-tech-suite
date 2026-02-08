"""
System operations module for Ghosty Toolz Evolved.

Provides safe, audited system operations with proper privilege management,
input validation, and error handling.
"""

import subprocess
import ctypes
import os
import sys
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime

from src.utils.logger import get_logger, get_audit_logger
from src.utils.config import get_config
from src.utils.validators import Validators, ValidationError

logger = get_logger("system_operations")
audit_logger = get_audit_logger()
config = get_config()
validators = Validators()

# Get CREATE_NO_WINDOW flag for Windows to prevent console flickering
# On Windows, this prevents subprocess from creating a visible console window
CREATE_NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


class SystemOperationError(Exception):
    """Custom exception for system operation errors."""

    pass


class PrivilegeError(Exception):
    """Custom exception for privilege-related errors."""

    pass


class SystemOperations:
    """Safe, audited system operations with privilege management."""

    # Whitelist of allowed commands
    ALLOWED_COMMANDS = [
        "ipconfig",
        "sfc",
        "DISM",
        "chkdsk",
        "defrag",
        "gpupdate",
        "wmic",
        "powercfg",
        "netsh",
        "vssadmin",
        "wbadmin",
        "powershell",
        "cmd",
        "net",
        "ping",
        "tracert",
    ]

    def __init__(self) -> None:
        """Initialize system operations manager."""
        self.timeout = config.get("system_operations.command_timeout", 300)
        self.require_confirmation = config.get("system_operations.require_confirmation", True)

    @staticmethod
    def is_admin() -> bool:
        """
        Check if current process has administrator privileges.

        Returns:
            True if running as administrator
        """
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception as e:
            logger.error(f"Failed to check admin status: {e}")
            return False

    @staticmethod
    def request_admin_elevation() -> bool:
        """
        Request administrator elevation for the current process.

        This does NOT automatically elevate - it prompts the user with UAC dialog.

        Returns:
            True if elevation was successful (will restart the process)

        Raises:
            PrivilegeError: If elevation fails or is denied
        """
        if SystemOperations.is_admin():
            logger.info("Already running as administrator")
            return True

        logger.warning("Administrator privileges required - requesting elevation")
        audit_logger.warning("User requested admin elevation")

        try:
            # Re-run the program with admin rights (UAC prompt)
            params = " ".join([f'"{arg}"' for arg in sys.argv])
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, params, None, 1
            )

            if ret <= 32:
                raise PrivilegeError(f"Elevation request failed with code {ret}")

            # If successful, the new elevated process will start
            logger.info("Elevation successful, new process started")
            sys.exit(0)  # Exit current process

        except Exception as e:
            logger.error(f"Failed to elevate privileges: {e}")
            audit_logger.error(f"Admin elevation failed: {e}")
            raise PrivilegeError(f"Failed to obtain administrator privileges: {e}")

    def execute_command(
        self,
        command: str,
        timeout: Optional[int] = None,
        shell: bool = False,
        require_admin: bool = False,
        audit: bool = True,
    ) -> Tuple[bool, str, str]:
        """
        Execute a system command safely with validation and auditing.

        Args:
            command: Command to execute
            timeout: Command timeout in seconds (uses default if None)
            shell: Whether to use shell=True (NOT recommended)
            require_admin: Whether admin privileges are required
            audit: Whether to log to audit trail

        Returns:
            Tuple of (success, stdout, stderr)

        Raises:
            ValidationError: If command validation fails
            PrivilegeError: If admin privileges required but not available
            SystemOperationError: If command execution fails
        """
        # Validate command
        try:
            validators.validate_command(command, self.ALLOWED_COMMANDS, allow_shell=shell)
        except ValidationError as e:
            logger.error(f"Command validation failed: {e}")
            if audit:
                audit_logger.error(f"Rejected invalid command: {command[:100]}")
            raise

        # Check admin privileges if required
        if require_admin and not self.is_admin():
            logger.error("Admin privileges required but not available")
            if audit:
                audit_logger.error(f"Command requires admin: {command[:100]}")
            raise PrivilegeError("Administrator privileges required for this operation")

        # Use configured timeout if not specified
        if timeout is None:
            timeout = self.timeout

        # Validate timeout
        try:
            validators.validate_timeout(timeout, min_value=1, max_value=3600)
        except ValidationError as e:
            logger.warning(f"Invalid timeout, using default: {e}")
            timeout = 300

        # Log operation
        logger.info(f"Executing command: {command[:100]}")
        if audit:
            audit_logger.info(f"Command executed: {command} (admin={require_admin})")

        try:
            # Execute command
            if shell:
                logger.warning(f"Using shell=True for command (security risk): {command[:50]}")

            result = subprocess.run(
                command if shell else command.split(),
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=shell,
                check=False,
                creationflags=CREATE_NO_WINDOW,
            )

            success = result.returncode == 0
            stdout = result.stdout.strip() if result.stdout else ""
            stderr = result.stderr.strip() if result.stderr else ""

            if success:
                logger.info(f"Command completed successfully: {command[:50]}")
            else:
                logger.error(f"Command failed with code {result.returncode}: {command[:50]}")
                if stderr:
                    logger.error(f"Error output: {stderr[:200]}")

            if audit:
                status = "SUCCESS" if success else "FAILED"
                audit_logger.info(f"Command {status}: {command} (code={result.returncode})")

            return success, stdout, stderr

        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout}s: {command[:50]}")
            if audit:
                audit_logger.error(f"Command timeout: {command} (timeout={timeout}s)")
            raise SystemOperationError(f"Command timed out after {timeout} seconds")

        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            if audit:
                audit_logger.error(f"Command error: {command} - {str(e)}")
            raise SystemOperationError(f"Command execution failed: {e}")

    def flush_dns(self) -> bool:
        """
        Flush DNS cache.

        Returns:
            True if successful

        Raises:
            SystemOperationError: If operation fails
        """
        logger.info("Flushing DNS cache")
        success, stdout, stderr = self.execute_command(
            "ipconfig /flushdns", require_admin=False, audit=True
        )

        if not success:
            raise SystemOperationError(f"Failed to flush DNS: {stderr}")

        logger.info("DNS cache flushed successfully")
        return True

    def create_restore_point(self, name: str, description: Optional[str] = None) -> bool:
        """
        Create a system restore point.

        Args:
            name: Restore point name
            description: Optional description

        Returns:
            True if successful

        Raises:
            SystemOperationError: If operation fails
        """
        if not description:
            description = f"Created by Ghosty Toolz Evolved on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        # Sanitize name
        safe_name = validators.sanitize_filename(name)

        logger.info(f"Creating restore point: {safe_name}")

        # PowerShell command to create restore point
        ps_command = (
            f'powershell -Command "Checkpoint-Computer -Description \\"{safe_name}\\" '
            f'-RestorePointType MODIFY_SETTINGS"'
        )

        try:
            success, stdout, stderr = self.execute_command(
                ps_command, timeout=120, shell=True, require_admin=True, audit=True
            )

            if not success:
                raise SystemOperationError(f"Failed to create restore point: {stderr}")

            logger.info(f"Restore point created successfully: {safe_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create restore point: {e}")
            raise SystemOperationError(f"Failed to create restore point: {e}")

    def run_system_maintenance(self) -> Dict[str, Any]:
        """
        Run comprehensive system maintenance tasks.

        Returns:
            Dictionary with results of each task

        Raises:
            SystemOperationError: If critical operations fail
        """
        logger.info("Starting system maintenance")
        results = {}

        # DNS Flush
        try:
            self.flush_dns()
            results["dns_flush"] = {"success": True, "message": "DNS cache flushed"}
        except Exception as e:
            results["dns_flush"] = {"success": False, "error": str(e)}

        # System File Checker
        try:
            logger.info("Running System File Checker...")
            success, stdout, stderr = self.execute_command(
                "sfc /scannow", timeout=600, require_admin=True
            )
            results["sfc"] = {"success": success, "output": stdout or stderr}
        except Exception as e:
            results["sfc"] = {"success": False, "error": str(e)}

        # DISM Repair
        try:
            logger.info("Running DISM repair...")
            success, stdout, stderr = self.execute_command(
                "DISM /Online /Cleanup-Image /RestoreHealth",
                timeout=1800,
                require_admin=True,
            )
            results["dism"] = {"success": success, "output": stdout or stderr}
        except Exception as e:
            results["dism"] = {"success": False, "error": str(e)}

        logger.info("System maintenance completed")
        audit_logger.info(f"System maintenance completed with results: {results}")

        return results

    def edit_hosts_file(self) -> bool:
        """
        Open the Windows hosts file in notepad for editing.
        
        Requires administrator privileges.
        
        Returns:
            True if hosts file was opened successfully
            
        Raises:
            PrivilegeError: If not running as administrator
        """
        if not self.is_admin():
            raise PrivilegeError("Administrator privileges required to edit hosts file")
        
        logger.info("Opening hosts file for editing")
        audit_logger.info("User opened hosts file for editing")
        
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        
        try:
            # Open hosts file with notepad
            subprocess.Popen(["notepad.exe", hosts_path], creationflags=CREATE_NO_WINDOW)
            logger.info("Hosts file opened successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to open hosts file: {e}")
            raise SystemOperationError(f"Failed to open hosts file: {e}")
    
    def set_dns_servers(self, adapter: str, primary: str, secondary: Optional[str] = None) -> bool:
        """
        Set DNS servers for a network adapter.
        
        Args:
            adapter: Network adapter name (e.g., "Ethernet", "Wi-Fi")
            primary: Primary DNS server IP
            secondary: Optional secondary DNS server IP
            
        Returns:
            True if DNS servers were set successfully
            
        Raises:
            PrivilegeError: If not running as administrator
        """
        if not self.is_admin():
            raise PrivilegeError("Administrator privileges required to set DNS servers")
        
        logger.info(f"Setting DNS servers for adapter '{adapter}': {primary}, {secondary}")
        audit_logger.info(f"User set DNS servers for adapter '{adapter}'")
        
        try:
            # Set primary DNS
            cmd_primary = f'netsh interface ip set dns name="{adapter}" static {primary}'
            success, stdout, stderr = self.execute_command(cmd_primary, shell=True, require_admin=True)
            
            if not success:
                raise SystemOperationError(f"Failed to set primary DNS: {stderr}")
            
            # Set secondary DNS if provided
            if secondary:
                cmd_secondary = f'netsh interface ip add dns name="{adapter}" {secondary} index=2'
                success, stdout, stderr = self.execute_command(cmd_secondary, shell=True, require_admin=True)
                
                if not success:
                    logger.warning(f"Failed to set secondary DNS: {stderr}")
            
            logger.info("DNS servers set successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set DNS servers: {e}")
            raise SystemOperationError(f"Failed to set DNS servers: {e}")
    
    def reset_dns_to_auto(self, adapter: str) -> bool:
        """
        Reset DNS to automatic (DHCP) for a network adapter.
        
        Args:
            adapter: Network adapter name (e.g., "Ethernet", "Wi-Fi")
            
        Returns:
            True if DNS was reset successfully
            
        Raises:
            PrivilegeError: If not running as administrator
        """
        if not self.is_admin():
            raise PrivilegeError("Administrator privileges required to reset DNS")
        
        logger.info(f"Resetting DNS to auto for adapter '{adapter}'")
        audit_logger.info(f"User reset DNS to auto for adapter '{adapter}'")
        
        try:
            cmd = f'netsh interface ip set dns name="{adapter}" dhcp'
            success, stdout, stderr = self.execute_command(cmd, shell=True, require_admin=True)
            
            if not success:
                raise SystemOperationError(f"Failed to reset DNS: {stderr}")
            
            logger.info("DNS reset to auto successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset DNS: {e}")
            raise SystemOperationError(f"Failed to reset DNS: {e}")
    
    def view_dns_cache(self) -> str:
        """
        View the DNS cache.
        
        Returns:
            DNS cache contents as string
        """
        logger.info("Viewing DNS cache")
        
        try:
            success, stdout, stderr = self.execute_command("ipconfig /displaydns", timeout=30)
            
            if not success:
                raise SystemOperationError(f"Failed to view DNS cache: {stderr}")
            
            return stdout
            
        except Exception as e:
            logger.error(f"Failed to view DNS cache: {e}")
            raise SystemOperationError(f"Failed to view DNS cache: {e}")
    
    def get_network_adapters(self) -> List[str]:
        """
        Get list of network adapter names.
        
        Returns:
            List of network adapter names
        """
        logger.info("Getting network adapters")
        
        try:
            cmd = "netsh interface show interface"
            success, stdout, stderr = self.execute_command(cmd, timeout=30)
            
            if not success:
                raise SystemOperationError(f"Failed to get network adapters: {stderr}")
            
            # Parse adapter names from output
            # Expected format has header like: "Admin State  State       Type             Interface Name"
            adapters = []
            lines = stdout.split('\n')
            
            # Skip header lines (first 2-3 lines typically)
            for i, line in enumerate(lines):
                line = line.strip()
                if not line or '---' in line:
                    continue
                
                # Skip the header line (contains "Admin State", "State", "Type", "Interface Name")
                if ('Admin State' in line) or ('State' in line and 'Type' in line):
                    continue
                
                # Parse data lines - adapter name is the last field
                # Line format: "Enabled      Connected    Dedicated    Ethernet"
                parts = line.split()
                if len(parts) >= 4:
                    # Join all parts from index 3 onwards as the adapter name (handles names with spaces)
                    adapter_name = ' '.join(parts[3:])
                    # Validate adapter name (should not be empty or just whitespace)
                    if adapter_name and adapter_name.strip() and adapter_name not in adapters:
                        adapters.append(adapter_name)
            
            return adapters
            
        except Exception as e:
            logger.error(f"Failed to get network adapters: {e}")
            return []

    def get_system_health_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive system health report.

        Returns:
            Dictionary with system health information
        """
        logger.info("Generating system health report")
        report = {
            "timestamp": datetime.now().isoformat(),
            "admin_privileges": self.is_admin(),
        }

        # Disk health check
        try:
            success, stdout, stderr = self.execute_command(
                "wmic diskdrive get status", timeout=30, audit=False
            )
            report["disk_health"] = stdout if success else "Unknown"
        except Exception as e:
            report["disk_health"] = f"Error: {e}"

        # Windows version
        try:
            success, stdout, stderr = self.execute_command(
                "cmd /c ver", timeout=10, shell=True, audit=False
            )
            report["windows_version"] = stdout if success else "Unknown"
        except Exception as e:
            report["windows_version"] = f"Error: {e}"

        logger.info("System health report generated")
        return report


# Example usage
if __name__ == "__main__":
    ops = SystemOperations()

    # Check admin status
    print(f"Admin: {ops.is_admin()}")

    # Test DNS flush (doesn't require admin on most systems)
    try:
        if ops.flush_dns():
            print("✓ DNS flushed successfully")
    except Exception as e:
        print(f"✗ DNS flush failed: {e}")

    # Get system health report
    report = ops.get_system_health_report()
    print(f"System Health Report: {report}")
