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
        
        # First, disable the 24-hour frequency limit by setting registry key to 0
        # This allows multiple restore points to be created in a day
        registry_cmd = """
        try {
            $regPath = "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\SystemRestore"
            Set-ItemProperty -Path $regPath -Name "SystemRestorePointCreationFrequency" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
            Write-Output "Frequency limit disabled"
        } catch {
            Write-Output "Could not modify registry (may not affect restore point creation): $_"
        }
        """
        
        # Enable System Restore on system drive
        enable_cmd = """
        try {
            Enable-ComputerRestore -Drive "$env:SystemDrive" -ErrorAction SilentlyContinue
            Write-Output "System Restore enabled"
        } catch {
            Write-Output "System Restore may already be enabled or failed: $_"
        }
        """
        
        # Create restore point with verification
        create_cmd = f"""
        try {{
            # Get count of restore points before creation
            $beforeCount = @(Get-ComputerRestorePoint).Count
            
            # Create the restore point
            Checkpoint-Computer -Description "{description}" -RestorePointType "MODIFY_SETTINGS" -ErrorAction Stop
            
            # Wait for Windows to register the restore point in the system
            # 2 seconds is sufficient for most systems; restore point creation is typically instant
            Start-Sleep -Seconds 2
            
            # Verify the restore point was created by checking the count increased
            $afterCount = @(Get-ComputerRestorePoint).Count
            
            if ($afterCount -gt $beforeCount) {{
                Write-Output "Restore point created successfully"
            }} else {{
                Write-Output "Failed to create restore point: Restore point was not found after creation"
            }}
        }} catch {{
            # Check if it's the 24-hour frequency error or related restore point errors
            $errorMsg = $_.Exception.Message
            if ($errorMsg -like "*24 hours*" -or $errorMsg -like "*restore point*cannot be created*") {{
                Write-Output "Failed to create restore point: A restore point was already created within the past 24 hours. The frequency limit setting may not have taken effect yet. Please restart the computer and try again."
            }} else {{
                Write-Output "Failed to create restore point: $errorMsg"
            }}
        }}
        """
        
        try:
            if not self.execute_powershell:
                return False, "PowerShell execution function not configured"
                
            # Step 1: Disable the 24-hour frequency limit
            success, stdout, stderr = self.execute_powershell(registry_cmd, timeout=30)
            logger.debug(f"Registry modification result: {stdout}")
            
            # Step 2: Try to enable System Restore (silent, may already be enabled)
            success, stdout, stderr = self.execute_powershell(enable_cmd, timeout=60)
            logger.debug(f"System Restore enable result: {stdout}")
            
            # Step 3: Create the restore point with verification
            success, stdout, stderr = self.execute_powershell(create_cmd, timeout=120)
            
            # Check the output for success or failure messages
            # The PowerShell script writes to stdout in both success and failure cases
            output = stdout.lower()
            
            if "restore point created successfully" in output:
                logger.info("Restore point created successfully")
                return True, "Restore point created successfully"
            elif "failed to create restore point" in output:
                # Extract the error message from the output
                # Format: "Failed to create restore point: <error details>"
                error_msg = stdout.strip() if stdout else "Unknown error"
                logger.error(f"Failed to create restore point: {error_msg}")
                return False, error_msg
            elif not success:
                # PowerShell command itself failed (not the inner script)
                error_msg = stderr if stderr else stdout if stdout else "PowerShell execution failed"
                logger.error(f"Failed to create restore point: {error_msg}")
                return False, f"Failed to create restore point: {error_msg}"
            else:
                # Unexpected output - neither success nor explicit failure message
                error_msg = stdout if stdout else "Unknown error - no output from restore point creation"
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
                            except (ValueError, IndexError):
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
            Formatted date string like "2024-02-09 12:00:00" or "Unknown date" if parsing fails
        """
        if not creation_time_str:
            return "Unknown date"
            
        try:
            if creation_time_str.startswith('/Date(') and creation_time_str.endswith(')/'):
                timestamp_ms = int(creation_time_str[6:-2])
                # Convert milliseconds to seconds
                dt = datetime.fromtimestamp(timestamp_ms / 1000)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            logger.warning(f"Failed to parse creation time: {e}")
        
        # Return user-friendly default for invalid formats
        return "Unknown date"
    
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
        
        return f"{description}"
