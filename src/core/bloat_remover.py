"""
Windows Bloatware Removal Module.

Provides comprehensive bloatware detection and removal functionality with
PowerShell command execution, system restore point management, and safe
removal operations for Microsoft Store apps, Windows features, OneDrive,
telemetry, OEM bloatware, services, and capabilities.
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

logger = get_logger("bloat_remover")

# Get CREATE_NO_WINDOW flag for Windows to prevent console flickering
CREATE_NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


class BloatwareCategory(Enum):
    """Bloatware category enumeration."""
    MICROSOFT_STORE_APPS = "Microsoft Store Apps"
    WINDOWS_FEATURES = "Windows Features"
    ONEDRIVE = "OneDrive"
    TELEMETRY = "Telemetry & Privacy"
    OEM_BLOATWARE = "OEM Bloatware"
    WINDOWS_SERVICES = "Windows Services"
    OPTIONAL_COMPONENTS = "Optional Components"


class SafetyLevel(Enum):
    """Safety level enumeration."""
    SAFE = "safe"
    MODERATE = "moderate"
    RISKY = "risky"


class BloatwareItem:
    """Represents a single bloatware item."""
    
    def __init__(
        self,
        item_id: str,
        name: str,
        description: str,
        category: BloatwareCategory,
        safety_level: SafetyLevel,
        commands: List[str],
        check_command: Optional[str] = None,
        requires_admin: bool = True,
        requires_restart: bool = False,
        windows_versions: Optional[List[str]] = None
    ):
        """
        Initialize bloatware item.
        
        Args:
            item_id: Unique identifier
            name: Display name
            description: Description of what it does
            category: Bloatware category
            safety_level: Safety level (safe/moderate/risky)
            commands: PowerShell commands to remove
            check_command: Command to check if installed
            requires_admin: Whether admin privileges are required
            requires_restart: Whether restart is needed after removal
            windows_versions: Compatible Windows versions (None = all)
        """
        self.id = item_id
        self.name = name
        self.description = description
        self.category = category
        self.safety_level = safety_level
        self.commands = commands
        self.check_command = check_command
        self.requires_admin = requires_admin
        self.requires_restart = requires_restart
        self.windows_versions = windows_versions or ["10", "11"]
        self.is_installed = False


class BloatRemoverError(Exception):
    """Custom exception for bloat remover errors."""
    pass


class BloatRemover:
    """Windows bloatware removal manager."""
    
    def __init__(self):
        """Initialize bloat remover."""
        self.items: Dict[str, BloatwareItem] = {}
        self.restore_points: List[Dict[str, Any]] = []
        self._load_config()
        
    def _load_config(self) -> None:
        """Load bloatware configuration from JSON file."""
        try:
            config_path = Path(resource_path("config/bloatware_config.json"))
            
            if not config_path.exists():
                logger.error(f"Bloatware config not found: {config_path}")
                raise BloatRemoverError("Configuration file not found")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Category mapping for robust conversion
            category_mapping = {
                "Microsoft Store Apps": BloatwareCategory.MICROSOFT_STORE_APPS,
                "Windows Features": BloatwareCategory.WINDOWS_FEATURES,
                "OneDrive": BloatwareCategory.ONEDRIVE,
                "Telemetry And Privacy": BloatwareCategory.TELEMETRY,
                "OEM Bloatware": BloatwareCategory.OEM_BLOATWARE,
                "Windows Services": BloatwareCategory.WINDOWS_SERVICES,
                "Optional Components": BloatwareCategory.OPTIONAL_COMPONENTS,
            }
            
            # Parse and create BloatwareItem objects
            for item_data in config.get("items", []):
                try:
                    category = category_mapping.get(item_data["category"])
                    if not category:
                        logger.error(f"Unknown category '{item_data['category']}' for item {item_data.get('id', 'unknown')}")
                        continue
                    
                    safety_level = SafetyLevel[item_data["safety_level"].upper()]
                    
                    item = BloatwareItem(
                        item_id=item_data["id"],
                        name=item_data["name"],
                        description=item_data["description"],
                        category=category,
                        safety_level=safety_level,
                        commands=item_data["commands"],
                        check_command=item_data.get("check_command"),
                        requires_admin=item_data.get("requires_admin", True),
                        requires_restart=item_data.get("requires_restart", False),
                        windows_versions=item_data.get("windows_versions")
                    )
                    
                    self.items[item.id] = item
                    
                except Exception as e:
                    logger.error(f"Failed to parse item {item_data.get('id', 'unknown')}: {e}")
                    
            logger.info(f"Loaded {len(self.items)} bloatware items from config")
            
        except Exception as e:
            logger.error(f"Failed to load bloatware config: {e}")
            raise BloatRemoverError(f"Failed to load configuration: {e}")
    
    def get_items_by_category(self, category: BloatwareCategory) -> List[BloatwareItem]:
        """
        Get all bloatware items in a category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of bloatware items
        """
        return [item for item in self.items.values() if item.category == category]
    
    def get_items_by_safety(self, safety_level: SafetyLevel) -> List[BloatwareItem]:
        """
        Get all bloatware items with a specific safety level.
        
        Args:
            safety_level: Safety level to filter by
            
        Returns:
            List of bloatware items
        """
        return [item for item in self.items.values() if item.safety_level == safety_level]
    
    def get_safe_items(self) -> List[BloatwareItem]:
        """Get all safe bloatware items."""
        return self.get_items_by_safety(SafetyLevel.SAFE)
    
    def get_all_items(self) -> List[BloatwareItem]:
        """Get all bloatware items."""
        return list(self.items.values())
    
    def execute_powershell(
        self,
        command: str,
        timeout: int = 300,
        check: bool = False
    ) -> Tuple[bool, str, str]:
        """
        Execute a PowerShell command.
        
        Args:
            command: PowerShell command to execute
            timeout: Command timeout in seconds
            check: Whether to check if command exists before running
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        if not AdminState.is_admin():
            logger.warning("Attempting PowerShell command without admin privileges")
        
        try:
            # Build PowerShell command
            ps_command = [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy", "Bypass",
                "-Command", command
            ]
            
            logger.debug(f"Executing PowerShell: {command[:100]}...")
            
            result = subprocess.run(
                ps_command,
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=CREATE_NO_WINDOW
            )
            
            success = result.returncode == 0
            stdout = result.stdout.strip() if result.stdout else ""
            stderr = result.stderr.strip() if result.stderr else ""
            
            if success:
                logger.debug(f"PowerShell command succeeded")
            else:
                logger.warning(f"PowerShell command failed with code {result.returncode}")
                if stderr:
                    logger.debug(f"Error output: {stderr[:200]}")
            
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            logger.error(f"PowerShell command timed out after {timeout}s")
            return False, "", f"Command timed out after {timeout} seconds"
            
        except Exception as e:
            logger.error(f"PowerShell execution failed: {e}")
            return False, "", str(e)
    
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
                creationflags=CREATE_NO_WINDOW
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"PowerShell check failed: {e}")
            return False
    
    def create_restore_point(self, description: str = "Before Debloat") -> Tuple[bool, str]:
        """
        Create a system restore point.
        
        Args:
            description: Description for the restore point
            
        Returns:
            Tuple of (success, message)
        """
        if not AdminState.is_admin():
            return False, "Administrator privileges required"
        
        logger.info(f"Creating restore point: {description}")
        
        # First, check if System Restore is enabled
        check_cmd = "Get-ComputerRestorePoint -ErrorAction SilentlyContinue | Select-Object -First 1"
        
        # Enable System Restore if not enabled
        enable_cmd = """
        try {
            Enable-ComputerRestore -Drive "$env:SystemDrive"
            Write-Output "System Restore enabled"
        } catch {
            Write-Output "Failed to enable System Restore: $_"
        }
        """
        
        # Create restore point
        create_cmd = f"""
        try {{
            $result = Checkpoint-Computer -Description "{description}" -RestorePointType "MODIFY_SETTINGS" -ErrorAction Stop
            Write-Output "Restore point created successfully"
        }} catch {{
            Write-Output "Failed to create restore point: $_"
        }}
        """
        
        try:
            # Try to enable System Restore first
            success, stdout, stderr = self.execute_powershell(enable_cmd, timeout=60)
            
            # Create the restore point
            success, stdout, stderr = self.execute_powershell(create_cmd, timeout=120)
            
            if success and "successfully" in stdout.lower():
                logger.info("Restore point created successfully")
                
                # Store restore point info
                restore_info = {
                    "description": description,
                    "timestamp": datetime.now().isoformat(),
                    "success": True
                }
                self.restore_points.append(restore_info)
                
                return True, "Restore point created successfully"
            else:
                error_msg = stderr if stderr else stdout
                logger.error(f"Failed to create restore point: {error_msg}")
                return False, f"Failed to create restore point: {error_msg}"
                
        except Exception as e:
            logger.error(f"Restore point creation error: {e}")
            return False, f"Error creating restore point: {e}"
    
    def get_restore_points(self) -> List[Dict[str, Any]]:
        """
        Get list of available restore points.
        
        Returns:
            List of restore point dictionaries
        """
        if not AdminState.is_admin():
            logger.warning("Cannot list restore points without admin privileges")
            return []
        
        cmd = """
        Get-ComputerRestorePoint | Select-Object -Property SequenceNumber, Description, CreationTime, RestorePointType | ConvertTo-Json
        """
        
        try:
            success, stdout, stderr = self.execute_powershell(cmd, timeout=30)
            
            if success and stdout:
                try:
                    restore_points = json.loads(stdout)
                    
                    # Handle single restore point (not in array)
                    if isinstance(restore_points, dict):
                        restore_points = [restore_points]
                    
                    logger.info(f"Found {len(restore_points)} restore points")
                    return restore_points
                    
                except json.JSONDecodeError:
                    logger.warning("Failed to parse restore points JSON")
                    return []
            else:
                logger.debug("No restore points found or query failed")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get restore points: {e}")
            return []
    
    def check_item_installed(self, item: BloatwareItem) -> bool:
        """
        Check if a bloatware item is installed.
        
        Args:
            item: Bloatware item to check
            
        Returns:
            True if installed
        """
        if not item.check_command:
            # If no check command, assume installed
            return True
        
        try:
            success, stdout, stderr = self.execute_powershell(item.check_command, timeout=30)
            
            # If command succeeds and has output, consider installed
            if success and stdout.strip():
                return True
            else:
                return False
                
        except Exception as e:
            logger.debug(f"Check failed for {item.id}: {e}")
            return False
    
    def scan_system(
        self,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> Dict[str, bool]:
        """
        Scan system for installed bloatware.
        
        Args:
            progress_callback: Callback function(progress, message)
            
        Returns:
            Dictionary of item_id -> is_installed
        """
        logger.info("Starting system scan for bloatware")
        results = {}
        
        items = list(self.items.values())
        total = len(items)
        
        for i, item in enumerate(items):
            if progress_callback:
                progress = int((i / total) * 100)
                progress_callback(progress, f"Checking {item.name}...")
            
            is_installed = self.check_item_installed(item)
            results[item.id] = is_installed
            item.is_installed = is_installed
            
            logger.debug(f"{item.name}: {'Installed' if is_installed else 'Not installed'}")
        
        if progress_callback:
            progress_callback(100, "Scan complete")
        
        installed_count = sum(1 for v in results.values() if v)
        logger.info(f"Scan complete: {installed_count}/{total} items found")
        
        return results
    
    def remove_item(
        self,
        item: BloatwareItem,
        output_callback: Optional[Callable[[str, str], None]] = None
    ) -> Tuple[bool, str]:
        """
        Remove a single bloatware item.
        
        Args:
            item: Bloatware item to remove
            output_callback: Callback function(message, level) for output
            
        Returns:
            Tuple of (success, message)
        """
        if not AdminState.is_admin() and item.requires_admin:
            msg = f"Administrator privileges required to remove {item.name}"
            logger.warning(msg)
            if output_callback:
                output_callback(msg, "error")
            return False, msg
        
        logger.info(f"Removing {item.name}...")
        if output_callback:
            output_callback(f"Removing {item.name}...", "info")
        
        overall_success = True
        messages = []
        
        for cmd in item.commands:
            if output_callback:
                output_callback(f"  Executing: {cmd[:80]}...", "debug")
            
            success, stdout, stderr = self.execute_powershell(cmd, timeout=300)
            
            if success:
                if stdout:
                    messages.append(stdout)
                    if output_callback:
                        output_callback(f"  ✓ {stdout[:100]}", "success")
            else:
                overall_success = False
                error_msg = stderr if stderr else "Command failed"
                messages.append(error_msg)
                if output_callback:
                    output_callback(f"  ✗ {error_msg[:100]}", "error")
        
        if overall_success:
            msg = f"Successfully removed {item.name}"
            logger.info(msg)
            if output_callback:
                output_callback(msg, "success")
        else:
            msg = f"Failed to completely remove {item.name}"
            logger.warning(msg)
            if output_callback:
                output_callback(msg, "warning")
        
        return overall_success, "\n".join(messages)
    
    def remove_items(
        self,
        item_ids: List[str],
        progress_callback: Optional[Callable[[int, str], None]] = None,
        output_callback: Optional[Callable[[str, str], None]] = None
    ) -> Dict[str, Tuple[bool, str]]:
        """
        Remove multiple bloatware items.
        
        Args:
            item_ids: List of item IDs to remove
            progress_callback: Callback function(progress, message)
            output_callback: Callback function(message, level)
            
        Returns:
            Dictionary of item_id -> (success, message)
        """
        logger.info(f"Starting removal of {len(item_ids)} items")
        if output_callback:
            output_callback(f"\n{'='*60}", "info")
            output_callback(f"Starting removal of {len(item_ids)} items", "info")
            output_callback(f"{'='*60}\n", "info")
        
        results = {}
        total = len(item_ids)
        
        for i, item_id in enumerate(item_ids):
            item = self.items.get(item_id)
            
            if not item:
                msg = f"Item not found: {item_id}"
                logger.error(msg)
                results[item_id] = (False, msg)
                continue
            
            if progress_callback:
                progress = int((i / total) * 100)
                progress_callback(progress, f"Removing {item.name}...")
            
            success, message = self.remove_item(item, output_callback)
            results[item_id] = (success, message)
            
            if output_callback:
                output_callback("", "info")  # Blank line between items
        
        if progress_callback:
            progress_callback(100, "Removal complete")
        
        # Summary
        successful = sum(1 for success, _ in results.values() if success)
        failed = total - successful
        
        if output_callback:
            output_callback(f"\n{'='*60}", "info")
            output_callback(f"SUMMARY:", "info")
            output_callback(f"  Total items: {total}", "info")
            output_callback(f"  Successful: {successful}", "success")
            output_callback(f"  Failed: {failed}", "error" if failed > 0 else "info")
            output_callback(f"{'='*60}\n", "info")
        
        logger.info(f"Removal complete: {successful}/{total} successful")
        
        return results
    
    def remove_items_async(
        self,
        item_ids: List[str],
        progress_callback: Optional[Callable[[int, str], None]] = None,
        output_callback: Optional[Callable[[str, str], None]] = None,
        completion_callback: Optional[Callable[[Dict[str, Tuple[bool, str]]], None]] = None
    ) -> threading.Thread:
        """
        Remove multiple bloatware items asynchronously.
        
        Args:
            item_ids: List of item IDs to remove
            progress_callback: Callback function(progress, message)
            output_callback: Callback function(message, level)
            completion_callback: Callback function(results)
            
        Returns:
            Thread object
        """
        def task():
            try:
                results = self.remove_items(item_ids, progress_callback, output_callback)
                if completion_callback:
                    completion_callback(results)
            except Exception as e:
                logger.error(f"Async removal failed: {e}")
                if output_callback:
                    output_callback(f"Error: {e}", "error")
        
        thread = threading.Thread(target=task, daemon=True)
        thread.start()
        return thread
    
    def scan_system_async(
        self,
        progress_callback: Optional[Callable[[int, str], None]] = None,
        completion_callback: Optional[Callable[[Dict[str, bool]], None]] = None
    ) -> threading.Thread:
        """
        Scan system for installed bloatware asynchronously.
        
        Args:
            progress_callback: Callback function(progress, message)
            completion_callback: Callback function(results)
            
        Returns:
            Thread object
        """
        def task():
            try:
                results = self.scan_system(progress_callback)
                if completion_callback:
                    completion_callback(results)
            except Exception as e:
                logger.error(f"Async scan failed: {e}")
        
        thread = threading.Thread(target=task, daemon=True)
        thread.start()
        return thread
    
    def restore_system(self, sequence_number: int) -> Tuple[bool, str]:
        """
        Restore system to a restore point.
        
        Args:
            sequence_number: Restore point sequence number
            
        Returns:
            Tuple of (success, message)
        """
        if not AdminState.is_admin():
            return False, "Administrator privileges required"
        
        logger.warning(f"Restoring system to restore point {sequence_number}")
        
        cmd = f"""
        try {{
            Restore-Computer -RestorePoint {sequence_number} -Confirm:$false
            Write-Output "System restore initiated successfully"
        }} catch {{
            Write-Output "Failed to restore system: $_"
        }}
        """
        
        try:
            success, stdout, stderr = self.execute_powershell(cmd, timeout=60)
            
            if success and "successfully" in stdout.lower():
                msg = "System restore initiated. The system will restart."
                logger.info(msg)
                return True, msg
            else:
                error_msg = stderr if stderr else stdout
                logger.error(f"System restore failed: {error_msg}")
                return False, f"Failed to restore system: {error_msg}"
                
        except Exception as e:
            logger.error(f"System restore error: {e}")
            return False, f"Error restoring system: {e}"
