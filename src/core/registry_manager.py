"""
Registry manager for Windows registry tweaks and backups.

Provides safe registry manipulation with automatic backup and undo functionality.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import json

from src.utils.logger import get_logger, get_audit_logger
from src.utils.config import get_config
from src.utils.validators import Validators, ValidationError

logger = get_logger("registry_manager")
audit_logger = get_audit_logger()
config = get_config()
validators = Validators()


@dataclass
class RegistryTweak:
    """Registry tweak definition."""
    
    id: str
    name: str
    description: str
    category: str
    registry_key: str
    value_name: str
    value_data: str
    value_type: str  # REG_DWORD, REG_SZ, REG_BINARY, etc.
    risk_level: str  # low, medium, high
    requires_restart: bool


@dataclass
class RegistryBackup:
    """Registry backup metadata."""
    
    backup_id: str
    timestamp: str
    backup_path: str
    description: str
    registry_keys: List[str]
    skipped: bool = False  # True if backup was skipped because key didn't exist


class RegistryError(Exception):
    """Custom exception for registry errors."""
    
    pass


class RegistryManager:
    """Professional Windows registry management with safety features."""
    
    # Maximum number of registry backups to keep
    MAX_REGISTRY_BACKUPS = 10
    
    def __init__(self) -> None:
        """Initialize registry manager."""
        self.tmp_dir = Path(tempfile.gettempdir()) / "ghosty_toolz_registry_backups"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata_file = self.tmp_dir / "registry_metadata.json"
        self.metadata = self._load_metadata()
        
        # Define common Windows 11 registry tweaks
        self.available_tweaks = self._define_tweaks()
        
        # Load additional tweaks from JSON config files
        self._load_tweaks_from_json()
        
        logger.info(f"Registry manager initialized (backup location: {self.tmp_dir})")
        logger.info(f"Loaded {len(self.available_tweaks)} registry tweaks")
    
    def _load_metadata(self) -> Dict[str, RegistryBackup]:
        """
        Load registry backup metadata from file.
        
        Returns:
            Dictionary of backup ID to metadata
        """
        if not self.metadata_file.exists():
            return {}
        
        try:
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            metadata = {}
            for backup_id, meta_dict in data.items():
                metadata[backup_id] = RegistryBackup(**meta_dict)
            
            logger.debug(f"Loaded metadata for {len(metadata)} registry backups")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to load registry backup metadata: {e}")
            return {}
    
    def _save_metadata(self) -> None:
        """Save registry backup metadata to file."""
        try:
            data = {backup_id: asdict(meta) for backup_id, meta in self.metadata.items()}
            
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            
            logger.debug("Registry backup metadata saved")
            
        except Exception as e:
            logger.error(f"Failed to save registry backup metadata: {e}")
    
    def _define_tweaks(self) -> List[RegistryTweak]:
        """
        Define common Windows 11 registry tweaks.
        
        Returns:
            List of available registry tweaks
        """
        tweaks = [
            RegistryTweak(
                id="disable_telemetry",
                name="Disable Telemetry",
                description="Disables Windows telemetry and data collection",
                category="Privacy",
                registry_key=r"HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\DataCollection",
                value_name="AllowTelemetry",
                value_data="0",
                value_type="REG_DWORD",
                risk_level="low",
                requires_restart=True
            ),
            RegistryTweak(
                id="disable_cortana",
                name="Disable Cortana",
                description="Disables Cortana voice assistant",
                category="Privacy",
                registry_key=r"HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Windows Search",
                value_name="AllowCortana",
                value_data="0",
                value_type="REG_DWORD",
                risk_level="low",
                requires_restart=False
            ),
            RegistryTweak(
                id="disable_windows_update",
                name="Disable Windows Update (Temporary)",
                description="Temporarily disables automatic Windows updates (use with caution)",
                category="System",
                registry_key=r"HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU",
                value_name="NoAutoUpdate",
                value_data="1",
                value_type="REG_DWORD",
                risk_level="high",
                requires_restart=False
            ),
            RegistryTweak(
                id="show_file_extensions",
                name="Show File Extensions",
                description="Always show file extensions in File Explorer",
                category="UI",
                registry_key=r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                value_name="HideFileExt",
                value_data="0",
                value_type="REG_DWORD",
                risk_level="low",
                requires_restart=False
            ),
            RegistryTweak(
                id="show_hidden_files",
                name="Show Hidden Files",
                description="Show hidden files and folders in File Explorer",
                category="UI",
                registry_key=r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                value_name="Hidden",
                value_data="1",
                value_type="REG_DWORD",
                risk_level="low",
                requires_restart=False
            ),
            RegistryTweak(
                id="disable_lock_screen",
                name="Disable Lock Screen",
                description="Skip lock screen on startup",
                category="UI",
                registry_key=r"HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\Personalization",
                value_name="NoLockScreen",
                value_data="1",
                value_type="REG_DWORD",
                risk_level="low",
                requires_restart=True
            ),
            RegistryTweak(
                id="disable_uac",
                name="Disable UAC Prompts",
                description="Disables User Account Control prompts (SECURITY RISK)",
                category="Security",
                registry_key=r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
                value_name="EnableLUA",
                value_data="0",
                value_type="REG_DWORD",
                risk_level="high",
                requires_restart=True
            ),
            RegistryTweak(
                id="disable_startup_delay",
                name="Disable Startup Program Delay",
                description="Removes 10-second delay for startup programs",
                category="Performance",
                registry_key=r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Serialize",
                value_name="StartupDelayInMSec",
                value_data="0",
                value_type="REG_DWORD",
                risk_level="low",
                requires_restart=True
            ),
            RegistryTweak(
                id="disable_transparency",
                name="Disable Transparency Effects",
                description="Disables window transparency for better performance",
                category="Performance",
                registry_key=r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                value_name="EnableTransparency",
                value_data="0",
                value_type="REG_DWORD",
                risk_level="low",
                requires_restart=False
            ),
            RegistryTweak(
                id="old_context_menu",
                name="Restore Classic Context Menu",
                description="Restores Windows 10 style right-click context menu",
                category="UI",
                registry_key=r"HKEY_CURRENT_USER\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32",
                value_name="",
                value_data="",
                value_type="REG_SZ",
                risk_level="low",
                requires_restart=False
            ),
            RegistryTweak(
                id="disable_ads",
                name="Disable Start Menu Ads",
                description="Disables suggested apps and ads in Start Menu",
                category="Privacy",
                registry_key=r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                value_name="SystemPaneSuggestionsEnabled",
                value_data="0",
                value_type="REG_DWORD",
                risk_level="low",
                requires_restart=False
            ),
            RegistryTweak(
                id="disable_game_bar",
                name="Disable Xbox Game Bar",
                description="Disables Xbox Game Bar overlay",
                category="Performance",
                registry_key=r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\GameDVR",
                value_name="AppCaptureEnabled",
                value_data="0",
                value_type="REG_DWORD",
                risk_level="low",
                requires_restart=False
            ),
            # Windows 11 specific tweaks
            RegistryTweak(
                id="disable_copilot",
                name="Disable Windows Copilot",
                description="Disables Windows Copilot AI assistant",
                category="Privacy",
                registry_key=r"HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\WindowsCopilot",
                value_name="TurnOffWindowsCopilot",
                value_data="1",
                value_type="REG_DWORD",
                risk_level="low",
                requires_restart=False
            ),
            RegistryTweak(
                id="disable_widgets",
                name="Disable Widgets",
                description="Disables Windows 11 widgets feature",
                category="Performance",
                registry_key=r"HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Dsh",
                value_name="AllowNewsAndInterests",
                value_data="0",
                value_type="REG_DWORD",
                risk_level="low",
                requires_restart=False
            ),
            RegistryTweak(
                id="disable_chat_icon",
                name="Disable Chat Icon",
                description="Removes the chat icon from the taskbar",
                category="UI",
                registry_key=r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                value_name="TaskbarMn",
                value_data="0",
                value_type="REG_DWORD",
                risk_level="low",
                requires_restart=False
            ),
            RegistryTweak(
                id="enable_compact_mode",
                name="Enable Compact Mode in Explorer",
                description="Enables compact view mode in File Explorer for Windows 11",
                category="UI",
                registry_key=r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                value_name="UseCompactMode",
                value_data="1",
                value_type="REG_DWORD",
                risk_level="low",
                requires_restart=False
            ),
            RegistryTweak(
                id="show_all_tray_icons",
                name="Show All Tray Icons",
                description="Shows all system tray icons instead of hiding them",
                category="UI",
                registry_key=r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer",
                value_name="EnableAutoTray",
                value_data="0",
                value_type="REG_DWORD",
                risk_level="low",
                requires_restart=False
            ),
        ]
        
        return tweaks
    
    def _load_tweaks_from_json(self) -> None:
        """
        Load additional registry tweaks from JSON config files.
        
        Loads from:
        - config/registry_tweaks.json
        - plugins/*.json (for extensibility)
        """
        json_files = []
        
        # Load from config directory
        config_file = Path("config") / "registry_tweaks.json"
        if config_file.exists():
            json_files.append(config_file)
        
        # Load from plugins directory
        plugins_dir = Path("plugins")
        if plugins_dir.exists():
            json_files.extend(plugins_dir.glob("*.json"))
        
        for json_file in json_files:
            try:
                logger.debug(f"Loading tweaks from {json_file}")
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Validate JSON structure
                if not self._validate_tweaks_json(data):
                    logger.warning(f"Invalid JSON structure in {json_file}, skipping")
                    continue
                
                # Parse tweaks from JSON
                for tweak_data in data.get("tweaks", []):
                    try:
                        # Convert JSON format to RegistryTweak format
                        apply_data = tweak_data.get("apply", {})
                        
                        # JSON uses escaped backslashes (\\) which Python reads as single backslash
                        # No need to replace - just use as-is
                        tweak = RegistryTweak(
                            id=tweak_data.get("id"),
                            name=tweak_data.get("name"),
                            description=tweak_data.get("description"),
                            category=tweak_data.get("category"),
                            registry_key=apply_data.get("key", ""),
                            value_name=apply_data.get("value_name"),
                            value_data=str(apply_data.get("value_data")),
                            value_type=apply_data.get("value_type"),
                            risk_level=tweak_data.get("risk_level", "medium"),
                            requires_restart=tweak_data.get("requires_restart", False)
                        )
                        
                        # Check if tweak ID already exists
                        if not any(t.id == tweak.id for t in self.available_tweaks):
                            self.available_tweaks.append(tweak)
                            logger.debug(f"Loaded tweak: {tweak.id}")
                        else:
                            logger.warning(f"Duplicate tweak ID '{tweak.id}' found in {json_file}, skipping. Tweak IDs must be unique.")
                            
                    except Exception as e:
                        logger.warning(f"Failed to parse tweak in {json_file}: {e}")
                        
            except Exception as e:
                logger.error(f"Failed to load tweaks from {json_file}: {e}")
    
    def _validate_tweaks_json(self, data: Dict[str, Any]) -> bool:
        """
        Validate JSON structure for registry tweaks.
        
        Args:
            data: Parsed JSON data
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(data, dict):
            return False
        
        if "tweaks" not in data:
            return False
        
        if not isinstance(data["tweaks"], list):
            return False
        
        # Validate each tweak has required fields
        required_fields = ["id", "name", "description", "category", "apply"]
        for tweak in data["tweaks"]:
            if not isinstance(tweak, dict):
                return False
            
            for field in required_fields:
                if field not in tweak:
                    logger.warning(f"Tweak missing required field: {field}")
                    return False
            
            # Validate apply section
            apply_data = tweak.get("apply", {})
            if not isinstance(apply_data, dict):
                return False
            
            required_apply_fields = ["key", "value_name", "value_data", "value_type"]
            for field in required_apply_fields:
                if field not in apply_data:
                    logger.warning(f"Apply section missing required field: {field}")
                    return False
        
        return True
    
    def get_available_tweaks(self) -> List[RegistryTweak]:
        """
        Get list of available registry tweaks.
        
        Returns:
            List of registry tweaks
        """
        return self.available_tweaks
    
    def _get_tweak_by_id(self, tweak_id: str) -> Optional[RegistryTweak]:
        """
        Get a registry tweak by its ID.
        
        Args:
            tweak_id: ID of the tweak to find
        
        Returns:
            RegistryTweak if found, None otherwise
        """
        for tweak in self.available_tweaks:
            if tweak.id == tweak_id:
                return tweak
        return None
    
    def is_tweak_applied(self, tweak_id: str) -> bool:
        """
        Check if a registry tweak is currently applied.
        
        Args:
            tweak_id: ID of the tweak to check
        
        Returns:
            True if the tweak is applied, False otherwise
        """
        tweak = self._get_tweak_by_id(tweak_id)
        if not tweak:
            return False
        
        try:
            result = subprocess.run(
                ["reg", "query", tweak.registry_key, "/v", tweak.value_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse output to check if value matches tweak.value_data
                # The output format is:
                # <key path>
                #     <value_name>    <value_type>    <value_data>
                output = result.stdout
                
                # Split by lines and find the line with the value
                for line in output.split('\n'):
                    line = line.strip()
                    if line and tweak.value_name in line:
                        # Check if the value data appears after the value type
                        parts = line.split()
                        if len(parts) >= 3 and tweak.value_data in parts[-1]:
                            return True
            return False
        except Exception as e:
            logger.debug(f"Error checking tweak {tweak_id}: {e}")
            return False
    
    def get_registry_value(self, registry_key: str, value_name: str) -> Optional[Dict[str, str]]:
        """
        Get current registry value.
        
        Args:
            registry_key: Registry key path (e.g. "HKEY_CURRENT_USER\\Software\\...")
            value_name: Value name (empty string "" for default value, named string for specific values)
        
        Returns:
            Dictionary with 'type' and 'data' keys if value exists, None if not found
            
        Note:
            For default values, pass empty string "" as value_name (not None).
            This method uses the /ve parameter for querying default registry values.
        """
        try:
            # Build command: use /ve for default value (empty string), /v <name> for named values
            cmd = ["reg", "query", registry_key] + (["/ve"] if value_name == "" else ["/v", value_name])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                return None
            
            # Parse output to extract type and data
            output = result.stdout.strip()
            for line in output.split('\n'):
                line = line.strip()
                if not line or line.startswith("HKEY"):
                    continue
                
                # Parse line like: "    ValueName    REG_DWORD    0x1"
                parts = line.split(None, 2)  # Split into max 3 parts
                if len(parts) >= 3:
                    name = parts[0]
                    reg_type = parts[1]
                    data = parts[2]
                    
                    # Match the value name (handle empty string for default values)
                    # Note: value_name should be empty string for defaults (not None)
                    is_default_value = (value_name == "") and name == "(Default)"
                    is_named_value = value_name and name == value_name
                    
                    if is_default_value or is_named_value:
                        return {"type": reg_type, "data": data}
            
            return None
            
        except Exception as e:
            logger.debug(f"Error getting registry value {registry_key}\\{value_name}: {e}")
            return None
    
    def _cleanup_old_backups(self) -> None:
        """Keep only the most recent registry backups based on MAX_REGISTRY_BACKUPS."""
        backups = sorted(
            self.metadata.items(),
            key=lambda x: x[1].timestamp,
            reverse=True
        )
        
        if len(backups) > self.MAX_REGISTRY_BACKUPS:
            for backup_id, backup in backups[self.MAX_REGISTRY_BACKUPS:]:
                try:
                    backup_path = Path(backup.backup_path)
                    if backup_path.exists():
                        backup_path.unlink()
                    del self.metadata[backup_id]
                    logger.info(f"Deleted old backup: {backup_id}")
                except Exception as e:
                    logger.error(f"Failed to delete backup {backup_id}: {e}")
            
            self._save_metadata()
    
    def backup_registry(self, description: str = "Manual backup", 
                       registry_keys: Optional[List[str]] = None) -> str:
        """
        Backup Windows registry.
        
        Args:
            description: Backup description
            registry_keys: Specific registry keys to backup (None = full backup)
        
        Returns:
            Backup ID
        
        Raises:
            RegistryError: If backup fails
        """
        backup_id = f"reg_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.tmp_dir / f"{backup_id}.reg"
        
        logger.info(f"Creating registry backup: {backup_id}")
        audit_logger.info(f"Registry backup started: {description}")
        
        try:
            if registry_keys:
                # Backup specific keys
                # Note: For simplicity and reliability, we only backup the first key
                # to avoid file concatenation issues that break the .reg format
                if isinstance(registry_keys, list):
                    if len(registry_keys) > 1:
                        logger.warning(f"Multiple keys provided ({len(registry_keys)}), only backing up first key: {registry_keys[0]}")
                    key_to_backup = registry_keys[0]
                else:
                    key_to_backup = registry_keys
                
                # Check if key exists before trying to export
                check_result = subprocess.run(
                    ["reg", "query", key_to_backup],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if check_result.returncode != 0:
                    # Key doesn't exist - this is OK, just skip backup
                    logger.warning(f"Registry key does not exist yet: {key_to_backup}")
                    logger.info("Skipping backup - key will be created when tweak is applied")
                    
                    # Save metadata noting that backup was skipped
                    metadata = RegistryBackup(
                        backup_id=backup_id,
                        timestamp=datetime.now().isoformat(),
                        backup_path=str(backup_path),
                        description=description,
                        registry_keys=registry_keys or ["Full backup"],
                        skipped=True
                    )
                    
                    self.metadata[backup_id] = metadata
                    self._save_metadata()
                    
                    return backup_id
                
                # Key exists, proceed with backup
                logger.info(f"Backing up registry key: {key_to_backup}")
                result = subprocess.run(
                    ["reg", "export", key_to_backup, str(backup_path), "/y"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    error_msg = f"Failed to export key {key_to_backup}: {result.stderr}"
                    logger.error(error_msg)
                    raise RegistryError(error_msg)
                    
                # Verify the backup file was created and is valid
                if not backup_path.exists() or backup_path.stat().st_size == 0:
                    raise RegistryError(f"Backup file not created or is empty: {backup_path}")
            else:
                # For full backup, just export HKEY_CURRENT_USER which is safer
                logger.info("Creating full registry backup (HKEY_CURRENT_USER)")
                result = subprocess.run(
                    ["reg", "export", "HKEY_CURRENT_USER", str(backup_path), "/y"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode != 0:
                    error_msg = f"Failed to export HKEY_CURRENT_USER: {result.stderr}"
                    logger.error(error_msg)
                    raise RegistryError(error_msg)
                    
                # Verify the backup file was created and is valid
                if not backup_path.exists() or backup_path.stat().st_size == 0:
                    raise RegistryError(f"Backup file not created or is empty: {backup_path}")
            
            # Save metadata
            metadata = RegistryBackup(
                backup_id=backup_id,
                timestamp=datetime.now().isoformat(),
                backup_path=str(backup_path),
                description=description,
                registry_keys=registry_keys or ["Full backup"]
            )
            
            self.metadata[backup_id] = metadata
            self._save_metadata()
            
            # Cleanup old backups
            self._cleanup_old_backups()
            
            logger.info(f"Registry backup completed: {backup_id}")
            audit_logger.info(f"Registry backup completed: {backup_id}")
            
            return backup_id
            
        except Exception as e:
            logger.error(f"Registry backup failed: {e}")
            audit_logger.error(f"Registry backup failed: {str(e)}")
            raise RegistryError(f"Failed to backup registry: {e}")
    
    def restore_registry(self, backup_id: str) -> bool:
        """
        Restore registry from backup.
        
        Args:
            backup_id: Backup ID to restore
        
        Returns:
            True if successful
        
        Raises:
            RegistryError: If restore fails
        """
        if backup_id not in self.metadata:
            raise RegistryError(f"Backup not found: {backup_id}")
        
        metadata = self.metadata[backup_id]
        backup_path = Path(metadata.backup_path)
        
        # Check if backup was skipped (no file created)
        if metadata.skipped:
            logger.info(f"Backup was skipped (key didn't exist): {backup_id}")
            logger.info("Nothing to restore - this is expected for new registry keys")
            return True
        
        if not backup_path.exists():
            raise RegistryError(f"Backup file not found: {backup_path}")
        
        logger.info(f"Restoring registry from backup: {backup_id}")
        audit_logger.info(f"Registry restore started: {backup_id}")
        
        try:
            # Import registry file
            result = subprocess.run(
                ["reg", "import", str(backup_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                raise RegistryError(f"Registry import failed: {result.stderr}")
            
            logger.info(f"Registry restored successfully: {backup_id}")
            audit_logger.info(f"Registry restore completed: {backup_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Registry restore failed: {e}")
            audit_logger.error(f"Registry restore failed: {str(e)}")
            raise RegistryError(f"Failed to restore registry: {e}")
    
    def apply_tweak(self, tweak_id: str) -> Tuple[bool, str]:
        """
        Apply a registry tweak with automatic backup.
        
        Args:
            tweak_id: ID of tweak to apply
        
        Returns:
            Tuple of (success, backup_id)
        
        Raises:
            RegistryError: If tweak application fails
        """
        # Find tweak
        tweak = None
        for t in self.available_tweaks:
            if t.id == tweak_id:
                tweak = t
                break
        
        if not tweak:
            raise RegistryError(f"Tweak not found: {tweak_id}")
        
        logger.info(f"Applying registry tweak: {tweak.name}")
        audit_logger.info(f"Registry tweak applied: {tweak.name} (ID: {tweak_id})")
        
        try:
            # Backup registry key before modification
            backup_id = self.backup_registry(
                description=f"Before applying: {tweak.name}",
                registry_keys=[tweak.registry_key]
            )
            
            # Apply the tweak
            # First ensure the key exists
            key_parts = tweak.registry_key.split("\\")
            if len(key_parts) > 1:
                parent_key = "\\".join(key_parts[:-1])
                # Create key if it doesn't exist
                subprocess.run(
                    ["reg", "add", tweak.registry_key, "/f"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            
            # Set the value
            result = subprocess.run(
                [
                    "reg", "add", tweak.registry_key,
                    "/v", tweak.value_name,
                    "/t", tweak.value_type,
                    "/d", tweak.value_data,
                    "/f"
                ],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                raise RegistryError(f"Failed to apply tweak: {result.stderr}")
            
            logger.info(f"Registry tweak applied successfully: {tweak.name}")
            
            return True, backup_id
            
        except Exception as e:
            logger.error(f"Failed to apply registry tweak: {e}")
            audit_logger.error(f"Registry tweak failed: {tweak.name} - {str(e)}")
            raise RegistryError(f"Failed to apply tweak: {e}")
    
    def restore_tweak_to_default(self, tweak_id: str) -> bool:
        """
        Restore a registry tweak to Windows default by deleting the registry value.
        
        Args:
            tweak_id: ID of tweak to restore
        
        Returns:
            True if successful
        
        Raises:
            RegistryError: If restore fails
        """
        # Find tweak
        tweak = None
        for t in self.available_tweaks:
            if t.id == tweak_id:
                tweak = t
                break
        
        if not tweak:
            raise RegistryError(f"Tweak not found: {tweak_id}")
        
        logger.info(f"Restoring registry tweak to default: {tweak.name}")
        audit_logger.info(f"Registry tweak restored to default: {tweak.name} (ID: {tweak_id})")
        
        try:
            # Delete the registry value to restore to default
            # If value name is empty, delete the entire key
            if tweak.value_name:
                result = subprocess.run(
                    ["reg", "delete", tweak.registry_key, "/v", tweak.value_name, "/f"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:
                result = subprocess.run(
                    ["reg", "delete", tweak.registry_key, "/f"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            
            # Return code 0 means success, 1 might mean the value/key didn't exist (which is fine)
            if result.returncode not in [0, 1]:
                logger.warning(f"Registry delete returned code {result.returncode}: {result.stderr}")
            
            logger.info(f"Registry tweak restored to default: {tweak.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore registry tweak: {e}")
            audit_logger.error(f"Registry tweak restore failed: {tweak.name} - {str(e)}")
            raise RegistryError(f"Failed to restore tweak: {e}")
    
    def restore_all_to_defaults(self) -> Tuple[int, int, List[str]]:
        """
        Restore all applied registry tweaks to Windows defaults.
        
        This iterates through all available tweaks, checks if they're applied,
        and restores them to default values.
        
        Returns:
            Tuple of (success_count, total_applied, failed_tweaks)
        
        Raises:
            RegistryError: If critical failure occurs
        """
        logger.info("Restoring all registry tweaks to defaults")
        audit_logger.info("Restore all registry tweaks to defaults initiated")
        
        success_count = 0
        failed_tweaks = []
        applied_tweaks = []
        
        # Find all applied tweaks
        for tweak in self.available_tweaks:
            if self.is_tweak_applied(tweak.id):
                applied_tweaks.append(tweak)
        
        total_applied = len(applied_tweaks)
        
        if total_applied == 0:
            logger.info("No applied tweaks found to restore")
            return 0, 0, []
        
        logger.info(f"Found {total_applied} applied tweaks to restore")
        
        # Restore each applied tweak
        for tweak in applied_tweaks:
            try:
                self.restore_tweak_to_default(tweak.id)
                success_count += 1
                logger.info(f"Restored tweak to default: {tweak.name}")
            except Exception as e:
                failed_tweaks.append(tweak.name)
                logger.error(f"Failed to restore tweak {tweak.name}: {e}")
        
        logger.info(f"Restore all completed: {success_count}/{total_applied} successful")
        audit_logger.info(f"Restore all completed: {success_count}/{total_applied} successful, {len(failed_tweaks)} failed")
        
        return success_count, total_applied, failed_tweaks
    
    def undo_last_change(self) -> bool:
        """
        Undo the last registry change by restoring the most recent backup.
        
        Returns:
            True if successful
        
        Raises:
            RegistryError: If undo fails
        """
        if not self.metadata:
            raise RegistryError("No backups available to undo")
        
        # Get most recent backup
        backups = sorted(self.metadata.items(), key=lambda x: x[1].timestamp, reverse=True)
        latest_backup_id = backups[0][0]
        
        logger.info(f"Undoing last change using backup: {latest_backup_id}")
        
        return self.restore_registry(latest_backup_id)
    
    def list_backups(self) -> List[RegistryBackup]:
        """
        List all registry backups.
        
        Returns:
            List of registry backups
        """
        return sorted(self.metadata.values(), key=lambda x: x.timestamp, reverse=True)
    
    def delete_backup(self, backup_id: str) -> bool:
        """
        Delete a registry backup.
        
        Args:
            backup_id: Backup ID to delete
        
        Returns:
            True if successful
        """
        if backup_id not in self.metadata:
            raise RegistryError(f"Backup not found: {backup_id}")
        
        metadata = self.metadata[backup_id]
        backup_path = Path(metadata.backup_path)
        
        if backup_path.exists():
            backup_path.unlink()
        
        del self.metadata[backup_id]
        self._save_metadata()
        
        logger.info(f"Registry backup deleted: {backup_id}")
        
        return True


# Example usage
if __name__ == "__main__":
    manager = RegistryManager()
    
    # List available tweaks
    tweaks = manager.get_available_tweaks()
    print(f"Found {len(tweaks)} registry tweaks")
    
    for tweak in tweaks:
        print(f"  - {tweak.name} ({tweak.category}): {tweak.description}")
