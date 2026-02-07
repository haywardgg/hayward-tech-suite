"""
Backup and restore management module for Ghost Toolz Evolved.

Provides comprehensive backup and restore functionality with scheduling,
compression, and verification.
"""

import os
import shutil
import json
import zipfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import hashlib

from src.utils.logger import get_logger, get_audit_logger
from src.utils.config import get_config
from src.utils.validators import Validators, ValidationError

logger = get_logger("backup_manager")
audit_logger = get_audit_logger()
config = get_config()
validators = Validators()


@dataclass
class BackupConfig:
    """Backup configuration."""

    name: str
    source_paths: List[str]
    destination: str
    compression: bool = True
    include_system_state: bool = False
    exclude_patterns: Optional[List[str]] = None


@dataclass
class BackupMetadata:
    """Backup metadata."""

    backup_id: str
    name: str
    timestamp: str
    size_bytes: int
    file_count: int
    source_paths: List[str]
    checksum: str
    compression: bool
    status: str


class BackupError(Exception):
    """Custom exception for backup errors."""

    pass


class BackupManager:
    """Professional backup and restore management."""

    def __init__(self) -> None:
        """Initialize backup manager."""
        self.backup_dir = Path(config.get("backup.default_location", "backups"))
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.metadata_file = self.backup_dir / "backup_metadata.json"
        self.metadata = self._load_metadata()

        self.compression = config.get("backup.compression", True)
        self.max_backups = config.get("backup.max_backups", 10)

        logger.info(f"Backup manager initialized (location: {self.backup_dir})")

    def _load_metadata(self) -> Dict[str, BackupMetadata]:
        """
        Load backup metadata from file.

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
                metadata[backup_id] = BackupMetadata(**meta_dict)

            logger.debug(f"Loaded metadata for {len(metadata)} backups")
            return metadata

        except Exception as e:
            logger.error(f"Failed to load backup metadata: {e}")
            return {}

    def _save_metadata(self) -> None:
        """Save backup metadata to file."""
        try:
            data = {backup_id: asdict(meta) for backup_id, meta in self.metadata.items()}

            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            logger.debug("Backup metadata saved")

        except Exception as e:
            logger.error(f"Failed to save backup metadata: {e}")

    def _generate_backup_id(self) -> str:
        """
        Generate unique backup ID.

        Returns:
            Backup ID string
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"backup_{timestamp}"

    def _calculate_checksum(self, file_path: Path) -> str:
        """
        Calculate SHA256 checksum of file.

        Args:
            file_path: Path to file

        Returns:
            Hex digest of checksum
        """
        sha256 = hashlib.sha256()

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)

        return sha256.hexdigest()

    def create_backup(self, backup_config: BackupConfig) -> str:
        """
        Create a new backup.

        Args:
            backup_config: Backup configuration

        Returns:
            Backup ID

        Raises:
            BackupError: If backup creation fails
        """
        backup_id = self._generate_backup_id()
        safe_name = validators.sanitize_filename(backup_config.name)

        logger.info(f"Creating backup: {safe_name} (ID: {backup_id})")
        audit_logger.info(f"Backup started: {safe_name}")

        # Validate source paths
        for path in backup_config.source_paths:
            try:
                validators.validate_path(path, must_exist=True)
            except ValidationError as e:
                raise BackupError(f"Invalid source path: {e}")

        # Validate destination
        try:
            validators.validate_path(backup_config.destination, must_be_dir=True)
        except ValidationError:
            # Create destination if it doesn't exist
            Path(backup_config.destination).mkdir(parents=True, exist_ok=True)

        # Create backup filename
        backup_filename = f"{backup_id}_{safe_name}"
        if backup_config.compression:
            backup_filename += ".zip"
            backup_path = Path(backup_config.destination) / backup_filename
        else:
            backup_path = Path(backup_config.destination) / backup_filename
            backup_path.mkdir(parents=True, exist_ok=True)

        try:
            file_count = 0
            total_size = 0

            if backup_config.compression:
                # Create compressed backup
                with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for source_path in backup_config.source_paths:
                        source = Path(source_path)

                        if source.is_file():
                            zipf.write(source, source.name)
                            file_count += 1
                            total_size += source.stat().st_size
                        elif source.is_dir():
                            for file_path in source.rglob("*"):
                                if file_path.is_file():
                                    # Check exclusion patterns
                                    if backup_config.exclude_patterns:
                                        if any(
                                            pattern in str(file_path)
                                            for pattern in backup_config.exclude_patterns
                                        ):
                                            continue

                                    arcname = file_path.relative_to(source.parent)
                                    zipf.write(file_path, arcname)
                                    file_count += 1
                                    total_size += file_path.stat().st_size

                backup_size = backup_path.stat().st_size
                checksum = self._calculate_checksum(backup_path)

            else:
                # Create uncompressed backup (directory copy)
                for source_path in backup_config.source_paths:
                    source = Path(source_path)
                    dest = backup_path / source.name

                    if source.is_file():
                        shutil.copy2(source, dest)
                        file_count += 1
                        total_size += source.stat().st_size
                    elif source.is_dir():
                        shutil.copytree(source, dest, dirs_exist_ok=True)
                        for file_path in dest.rglob("*"):
                            if file_path.is_file():
                                file_count += 1
                                total_size += file_path.stat().st_size

                backup_size = sum(f.stat().st_size for f in backup_path.rglob("*") if f.is_file())
                checksum = ""  # Skip checksum for directory backups

            # Create metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                name=safe_name,
                timestamp=datetime.now().isoformat(),
                size_bytes=backup_size,
                file_count=file_count,
                source_paths=backup_config.source_paths,
                checksum=checksum,
                compression=backup_config.compression,
                status="completed",
            )

            self.metadata[backup_id] = metadata
            self._save_metadata()

            logger.info(
                f"Backup completed: {safe_name} ({file_count} files, {backup_size / (1024**2):.2f} MB)"
            )
            audit_logger.info(f"Backup completed: {safe_name} (ID: {backup_id})")

            # Cleanup old backups if limit exceeded
            self._cleanup_old_backups()

            return backup_id

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            audit_logger.error(f"Backup failed: {safe_name} - {str(e)}")

            # Cleanup failed backup
            if backup_path.exists():
                try:
                    if backup_path.is_dir():
                        shutil.rmtree(backup_path)
                    else:
                        backup_path.unlink()
                except Exception as cleanup_error:
                    logger.error(f"Failed to cleanup failed backup: {cleanup_error}")

            raise BackupError(f"Backup creation failed: {e}")

    def restore_backup(self, backup_id: str, target_path: str) -> bool:
        """
        Restore a backup.

        Args:
            backup_id: Backup ID to restore
            target_path: Target path for restoration

        Returns:
            True if successful

        Raises:
            BackupError: If restoration fails
        """
        if backup_id not in self.metadata:
            raise BackupError(f"Backup not found: {backup_id}")

        metadata = self.metadata[backup_id]
        logger.info(f"Restoring backup: {metadata.name} (ID: {backup_id})")
        audit_logger.info(f"Restore started: {metadata.name} (ID: {backup_id})")

        # Validate target path
        try:
            target = Path(target_path)
            target.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise BackupError(f"Invalid target path: {e}")

        # Find backup file
        backup_file = None
        for file in self.backup_dir.rglob(f"{backup_id}_*"):
            backup_file = file
            break

        if not backup_file or not backup_file.exists():
            raise BackupError(f"Backup file not found for ID: {backup_id}")

        try:
            # Verify checksum if available
            if metadata.checksum:
                logger.info("Verifying backup integrity...")
                current_checksum = self._calculate_checksum(backup_file)
                if current_checksum != metadata.checksum:
                    raise BackupError("Backup integrity check failed (checksum mismatch)")
                logger.info("Backup integrity verified")

            # Restore backup
            if metadata.compression:
                with zipfile.ZipFile(backup_file, "r") as zipf:
                    zipf.extractall(target)
            else:
                shutil.copytree(backup_file, target, dirs_exist_ok=True)

            logger.info(f"Backup restored successfully to: {target}")
            audit_logger.info(f"Restore completed: {metadata.name} (ID: {backup_id})")

            return True

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            audit_logger.error(f"Restore failed: {metadata.name} - {str(e)}")
            raise BackupError(f"Restore failed: {e}")

    def list_backups(self) -> List[BackupMetadata]:
        """
        List all available backups.

        Returns:
            List of backup metadata
        """
        return sorted(self.metadata.values(), key=lambda x: x.timestamp, reverse=True)

    def delete_backup(self, backup_id: str) -> bool:
        """
        Delete a backup.

        Args:
            backup_id: Backup ID to delete

        Returns:
            True if successful

        Raises:
            BackupError: If deletion fails
        """
        if backup_id not in self.metadata:
            raise BackupError(f"Backup not found: {backup_id}")

        metadata = self.metadata[backup_id]
        logger.info(f"Deleting backup: {metadata.name} (ID: {backup_id})")
        audit_logger.info(f"Backup deletion: {metadata.name} (ID: {backup_id})")

        # Find and delete backup file
        backup_file = None
        for file in self.backup_dir.rglob(f"{backup_id}_*"):
            backup_file = file
            break

        if backup_file and backup_file.exists():
            try:
                if backup_file.is_dir():
                    shutil.rmtree(backup_file)
                else:
                    backup_file.unlink()
            except Exception as e:
                raise BackupError(f"Failed to delete backup file: {e}")

        # Remove metadata
        del self.metadata[backup_id]
        self._save_metadata()

        logger.info(f"Backup deleted: {metadata.name}")
        return True

    def _cleanup_old_backups(self) -> None:
        """Remove old backups if limit exceeded."""
        if len(self.metadata) <= self.max_backups:
            return

        logger.info(f"Cleaning up old backups (limit: {self.max_backups})")

        # Sort by timestamp (oldest first)
        sorted_backups = sorted(self.metadata.items(), key=lambda x: x[1].timestamp)

        # Delete oldest backups
        backups_to_delete = len(self.metadata) - self.max_backups
        for backup_id, _ in sorted_backups[:backups_to_delete]:
            try:
                self.delete_backup(backup_id)
                logger.info(f"Removed old backup: {backup_id}")
            except Exception as e:
                logger.error(f"Failed to delete old backup {backup_id}: {e}")


# Example usage
if __name__ == "__main__":
    manager = BackupManager()

    # List existing backups
    backups = manager.list_backups()
    print(f"Found {len(backups)} backup(s)")

    for backup in backups:
        print(f"  - {backup.name} ({backup.timestamp}): {backup.size_bytes / (1024**2):.2f} MB")
