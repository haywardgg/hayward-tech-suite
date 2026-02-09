"""
Shared restore point management module.

Provides centralized functionality for creating, listing, and restoring system restore points.
Used by both the Maintenance tab and Debloat tab to avoid code duplication.
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from src.utils.logger import get_logger
from src.utils.admin_state import AdminState

logger = get_logger("restore_point_manager")


class RestorePointManager:
    """Manages system restore points with shared functionality."""
    
    def __init__(self, execute_powershell_func=None):
        """
        Initialize restore point manager.
        
        Args:
            execute_powershell_func: Function to execute PowerShell commands
                                   Should have signature: func(cmd, timeout) -> Tuple[bool, str, str]
        """
        self.execute_powershell = execute_powershell_func
        
    def create_restore_point(self, description: Optional[str] = None) -> Tuple[bool, str]:
        """
        Create a system restore point with auto-generated or custom description.
        
        Args:
            description: Optional custom description. If None, generates timestamp-based name
            
        Returns:
            Tuple of (success, message)
        """
        if not AdminState.is_admin():
            return False, "Administrator privileges required"
        
        # Auto-generate description with timestamp if not provided
        if not description:
            description = f"Hayward Tech Suite - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        logger.info(f"Creating restore point: {description}")
        
        # First, check if System Restore is enabled
        enable_cmd = """
        try {
            Enable-ComputerRestore -Drive "$env:SystemDrive" -ErrorAction SilentlyContinue
            Write-Output "System Restore enabled"
        } catch {
            Write-Output "System Restore may already be enabled or failed: $_"
        }
        """
        
        # Create restore point
        create_cmd = f"""
        try {{
            Checkpoint-Computer -Description "{description}" -RestorePointType "MODIFY_SETTINGS" -ErrorAction Stop
            Write-Output "Restore point created successfully"
        }} catch {{
            Write-Output "Failed to create restore point: $_"
        }}
        """
        
        try:
            if not self.execute_powershell:
                return False, "PowerShell execution function not configured"
                
            # Try to enable System Restore first (silent, may already be enabled)
            success, stdout, stderr = self.execute_powershell(enable_cmd, timeout=60)
            
            # Create the restore point
            success, stdout, stderr = self.execute_powershell(create_cmd, timeout=120)
            
            if success and "successfully" in stdout.lower():
                logger.info("Restore point created successfully")
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
        Get list of available restore points, sorted by most recent first.
        
        Returns:
            List of restore point dictionaries with keys:
            - SequenceNumber: Unique ID for the restore point
            - Description: Description text
            - CreationTime: DateTime object (converted to string)
            - RestorePointType: Type of restore point
        """
        if not AdminState.is_admin():
            logger.warning("Cannot list restore points without admin privileges")
            return []
        
        cmd = """
        Get-ComputerRestorePoint | Select-Object -Property SequenceNumber, Description, CreationTime, RestorePointType | ConvertTo-Json
        """
        
        try:
            if not self.execute_powershell:
                return []
                
            success, stdout, stderr = self.execute_powershell(cmd, timeout=30)
            
            if success and stdout:
                try:
                    restore_points = json.loads(stdout)
                    
                    # Handle single restore point (not in array)
                    if isinstance(restore_points, dict):
                        restore_points = [restore_points]
                    
                    # Sort by CreationTime (most recent first)
                    # CreationTime format: "/Date(1707436800000)/"
                    def get_creation_time(rp):
                        ct = rp.get('CreationTime', '')
                        if ct.startswith('/Date(') and ct.endswith(')/'):
                            try:
                                timestamp_ms = int(ct[6:-2])
                                return timestamp_ms
                            except:
                                return 0
                        return 0
                    
                    restore_points.sort(key=get_creation_time, reverse=True)
                    
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
    
    def restore_system(self, sequence_number: int) -> Tuple[bool, str]:
        """
        Restore system to a specific restore point.
        
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
            if not self.execute_powershell:
                return False, "PowerShell execution function not configured"
                
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
    
    def format_creation_time(self, creation_time_str: str) -> str:
        """
        Format CreationTime string from PowerShell JSON to readable format.
        
        Args:
            creation_time_str: Creation time in format "/Date(1707436800000)/"
            
        Returns:
            Formatted date string like "2024-02-09 12:00:00"
        """
        try:
            if creation_time_str.startswith('/Date(') and creation_time_str.endswith(')/'):
                timestamp_ms = int(creation_time_str[6:-2])
                # Convert milliseconds to seconds
                dt = datetime.fromtimestamp(timestamp_ms / 1000)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            logger.warning(f"Failed to parse creation time: {e}")
        
        return creation_time_str
    
    def get_latest_restore_point_info(self) -> str:
        """
        Get formatted information about the most recent restore point.
        
        Returns:
            String describing the latest restore point, or "No restore points found"
        """
        restore_points = self.get_restore_points()
        
        if not restore_points:
            return "No restore points found"
        
        latest = restore_points[0]
        creation_time = self.format_creation_time(latest.get('CreationTime', ''))
        description = latest.get('Description', 'Unknown')
        
        return f"{creation_time} - {description}"
