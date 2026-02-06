"""
Backup and restore tab for managing system backups.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
from pathlib import Path

from src.utils.logger import get_logger
from src.core.backup_manager import BackupManager, BackupConfig

logger = get_logger("backup_tab")


class BackupTab:
    """Backup and restore management tab."""

    def __init__(self, parent: ctk.CTkFrame) -> None:
        """Initialize backup tab."""
        self.parent = parent
        self.backup_manager = BackupManager()

        self.parent.grid_rowconfigure(1, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        self._create_header()
        self._create_content()

        # Load existing backups
        self._refresh_backup_list()

        logger.info("Backup tab initialized")

    def _create_header(self) -> None:
        """Create header."""
        header_frame = ctk.CTkFrame(self.parent)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        title = ctk.CTkLabel(
            header_frame, text="Backup & Restore", font=ctk.CTkFont(size=18, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    def _create_content(self) -> None:
        """Create content area."""
        content_frame = ctk.CTkScrollableFrame(self.parent)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)

        # Create backup section
        self._create_backup_section(content_frame)

        # Backup list section
        self._create_backup_list_section(content_frame)

    def _create_backup_section(self, parent: ctk.CTkFrame) -> None:
        """Create backup creation section."""
        backup_frame = ctk.CTkFrame(parent)
        backup_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        backup_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            backup_frame, text="Create New Backup", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Backup name
        ctk.CTkLabel(backup_frame, text="Backup Name:").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.backup_name_entry = ctk.CTkEntry(backup_frame, placeholder_text="My Backup")
        self.backup_name_entry.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Source paths
        ctk.CTkLabel(backup_frame, text="Source Folders:").grid(
            row=3, column=0, padx=10, pady=5, sticky="w"
        )
        self.source_paths_text = ctk.CTkTextbox(backup_frame, height=80)
        self.source_paths_text.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        btn_frame = ctk.CTkFrame(backup_frame, fg_color="transparent")
        btn_frame.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

        ctk.CTkButton(btn_frame, text="Add Folder", command=self._add_source_folder, width=120).grid(
            row=0, column=0, padx=5
        )
        ctk.CTkButton(
            btn_frame, text="Create Backup", command=self._create_backup, width=120, fg_color="green"
        ).grid(row=0, column=1, padx=5)

    def _create_backup_list_section(self, parent: ctk.CTkFrame) -> None:
        """Create backup list section."""
        list_frame = ctk.CTkFrame(parent)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        list_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            list_frame, text="Existing Backups", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Backup list
        self.backup_list_text = ctk.CTkTextbox(list_frame, height=200)
        self.backup_list_text.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.backup_list_text.configure(state="disabled")

        # Buttons
        btn_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        ctk.CTkButton(btn_frame, text="Refresh", command=self._refresh_backup_list, width=120).grid(
            row=0, column=0, padx=5
        )
        ctk.CTkButton(btn_frame, text="Restore", command=self._restore_backup, width=120).grid(
            row=0, column=1, padx=5
        )
        ctk.CTkButton(
            btn_frame, text="Delete", command=self._delete_backup, width=120, fg_color="#d9534f"
        ).grid(row=0, column=2, padx=5)

    def _add_source_folder(self) -> None:
        """Add source folder to backup."""
        folder = filedialog.askdirectory(title="Select Folder to Backup")
        if folder:
            current_text = self.source_paths_text.get("1.0", "end").strip()
            if current_text:
                self.source_paths_text.insert("end", f"\n{folder}")
            else:
                self.source_paths_text.insert("1.0", folder)

    def _create_backup(self) -> None:
        """Create new backup."""
        name = self.backup_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a backup name")
            return

        source_paths_text = self.source_paths_text.get("1.0", "end").strip()
        if not source_paths_text:
            messagebox.showwarning("Warning", "Please add at least one source folder")
            return

        source_paths = [p.strip() for p in source_paths_text.split("\n") if p.strip()]

        logger.info(f"Creating backup: {name}")

        def task():
            try:
                backup_config = BackupConfig(
                    name=name,
                    source_paths=source_paths,
                    destination=str(self.backup_manager.backup_dir),
                    compression=True,
                )

                backup_id = self.backup_manager.create_backup(backup_config)

                self.parent.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Success", f"Backup created successfully!\n\nBackup ID: {backup_id}"
                    ),
                )
                self.parent.after(0, self._refresh_backup_list)

            except Exception as e:
                logger.error(f"Backup creation failed: {e}")
                self.parent.after(
                    0, lambda: messagebox.showerror("Error", f"Failed to create backup: {e}")
                )

        threading.Thread(target=task, daemon=True).start()

    def _refresh_backup_list(self) -> None:
        """Refresh backup list display."""
        backups = self.backup_manager.list_backups()

        self.backup_list_text.configure(state="normal")
        self.backup_list_text.delete("1.0", "end")

        if not backups:
            self.backup_list_text.insert("1.0", "No backups found.")
        else:
            for backup in backups:
                size_mb = backup.size_bytes / (1024**2)
                info = (
                    f"ID: {backup.backup_id}\n"
                    f"Name: {backup.name}\n"
                    f"Date: {backup.timestamp}\n"
                    f"Size: {size_mb:.2f} MB\n"
                    f"Files: {backup.file_count}\n"
                    f"Status: {backup.status}\n"
                    f"{'-' * 50}\n"
                )
                self.backup_list_text.insert("end", info)

        self.backup_list_text.configure(state="disabled")

    def _restore_backup(self) -> None:
        """Restore selected backup."""
        messagebox.showinfo("Restore", "Restore functionality - Select target folder")
        # Implementation would allow selecting backup ID and target path

    def _delete_backup(self) -> None:
        """Delete selected backup."""
        messagebox.showinfo("Delete", "Delete functionality - Select backup to delete")
        # Implementation would allow selecting backup ID to delete
