"""
DANGER tab for advanced registry tweaks with backup/restore functionality.

WARNING: This tab contains potentially dangerous operations that can break Windows.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
from pathlib import Path

from src.utils.logger import get_logger
from src.core.registry_manager import RegistryManager, RegistryError

logger = get_logger("danger_tab")


class DangerTab:
    """DANGER zone tab for advanced registry tweaks."""

    def __init__(self, parent: ctk.CTkFrame) -> None:
        """Initialize danger tab."""
        self.parent = parent
        self.registry_manager = RegistryManager()

        self.parent.grid_rowconfigure(1, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        self._create_header()
        self._create_content()

        logger.info("DANGER tab initialized")

    def _create_header(self) -> None:
        """Create header with prominent warning."""
        header_frame = ctk.CTkFrame(self.parent, fg_color="#8B0000")  # Dark red
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        title = ctk.CTkLabel(
            header_frame,
            text="⚠️ DANGER ZONE ⚠️",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FFD700",
        )
        title.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        warning = ctk.CTkLabel(
            header_frame,
            text="WARNING: The registry tweaks in this section can potentially break Windows functionality.\n"
            "Proceed at your own risk! A registry backup is automatically created before each change.",
            font=ctk.CTkFont(size=12),
            text_color="white",
            wraplength=900,
        )
        warning.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

    def _create_content(self) -> None:
        """Create content area."""
        content_frame = ctk.CTkScrollableFrame(self.parent)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)

        # Backup/Restore section
        self._create_backup_section(content_frame)

        # Registry tweaks section
        self._create_tweaks_section(content_frame)

        # Backup history section
        self._create_history_section(content_frame)

    def _create_backup_section(self, parent: ctk.CTkFrame) -> None:
        """Create backup/restore section."""
        backup_frame = ctk.CTkFrame(parent)
        backup_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        backup_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            backup_frame,
            text="Registry Backup & Restore",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        btn_frame = ctk.CTkFrame(backup_frame, fg_color="transparent")
        btn_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(
            btn_frame,
            text="📦 Backup Registry Now",
            command=self._backup_registry,
            width=200,
            height=40,
            fg_color="green",
            hover_color="darkgreen",
        ).grid(row=0, column=0, padx=5, pady=5)

        ctk.CTkButton(
            btn_frame,
            text="↩️ Restore Registry",
            command=self._restore_registry,
            width=200,
            height=40,
            fg_color="orange",
            hover_color="darkorange",
        ).grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkButton(
            btn_frame,
            text="⏪ Undo Last Change",
            command=self._undo_last_change,
            width=200,
            height=40,
            fg_color="#d9534f",
            hover_color="#c9302c",
        ).grid(row=0, column=2, padx=5, pady=5)

    def _create_tweaks_section(self, parent: ctk.CTkFrame) -> None:
        """Create registry tweaks section."""
        tweaks_frame = ctk.CTkFrame(parent)
        tweaks_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        tweaks_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            tweaks_frame,
            text="Windows 11 Registry Tweaks",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Get available tweaks and organize by category
        tweaks = self.registry_manager.get_available_tweaks()
        categories = {}
        for tweak in tweaks:
            if tweak.category not in categories:
                categories[tweak.category] = []
            categories[tweak.category].append(tweak)

        # Create sections for each category
        row = 1
        for category, category_tweaks in sorted(categories.items()):
            category_frame = ctk.CTkFrame(tweaks_frame)
            category_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
            category_frame.grid_columnconfigure(0, weight=1)

            category_label = ctk.CTkLabel(
                category_frame,
                text=f"📂 {category}",
                font=ctk.CTkFont(size=14, weight="bold"),
            )
            category_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

            for i, tweak in enumerate(category_tweaks):
                self._create_tweak_button(category_frame, tweak, i + 1)

            row += 1

    def _create_tweak_button(
        self, parent: ctk.CTkFrame, tweak, row: int
    ) -> None:
        """Create a button for a registry tweak."""
        tweak_frame = ctk.CTkFrame(parent, fg_color="transparent")
        tweak_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=3)
        tweak_frame.grid_columnconfigure(1, weight=1)

        # Risk level indicator
        risk_colors = {"low": "green", "medium": "orange", "high": "red"}
        risk_label = ctk.CTkLabel(
            tweak_frame,
            text=f"[{tweak.risk_level.upper()}]",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=risk_colors.get(tweak.risk_level, "gray"),
            width=70,
        )
        risk_label.grid(row=0, column=0, padx=5, pady=5)

        # Tweak info
        info_frame = ctk.CTkFrame(tweak_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        info_frame.grid_columnconfigure(0, weight=1)

        name_label = ctk.CTkLabel(
            info_frame,
            text=tweak.name,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        )
        name_label.grid(row=0, column=0, sticky="w")

        desc_label = ctk.CTkLabel(
            info_frame,
            text=tweak.description
            + (" (Requires restart)" if tweak.requires_restart else ""),
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w",
        )
        desc_label.grid(row=1, column=0, sticky="w")

        # Apply button
        apply_btn = ctk.CTkButton(
            tweak_frame,
            text="Apply",
            command=lambda t=tweak: self._apply_tweak(t),
            width=100,
            height=35,
        )
        apply_btn.grid(row=0, column=2, padx=5, pady=5)

    def _create_history_section(self, parent: ctk.CTkFrame) -> None:
        """Create backup history section."""
        history_frame = ctk.CTkFrame(parent)
        history_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        history_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            history_frame,
            text="Registry Backup History",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # History list
        self.history_text = ctk.CTkTextbox(history_frame, height=150)
        self.history_text.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.history_text.configure(state="disabled")

        # Refresh button
        ctk.CTkButton(
            history_frame,
            text="🔄 Refresh History",
            command=self._refresh_history,
            width=150,
        ).grid(row=2, column=0, padx=10, pady=10)

        # Load initial history
        self._refresh_history()

    def _backup_registry(self) -> None:
        """Backup registry manually."""
        logger.info("Manual registry backup requested")

        def task():
            try:
                backup_id = self.registry_manager.backup_registry(
                    description="Manual backup"
                )

                self.parent.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Success",
                        f"Registry backed up successfully!\n\n"
                        f"Backup ID: {backup_id}\n"
                        f"Location: {self.registry_manager.tmp_dir}",
                    ),
                )
                self.parent.after(0, self._refresh_history)

            except RegistryError as e:
                logger.error(f"Registry backup failed: {e}")
                error_msg = str(e)
                self.parent.after(
                    0,
                    lambda: messagebox.showerror(
                        "Error", f"Failed to backup registry:\n{error_msg}"
                    ),
                )

        threading.Thread(target=task, daemon=True).start()

    def _restore_registry(self) -> None:
        """Restore registry from backup."""
        backups = self.registry_manager.list_backups()

        if not backups:
            messagebox.showwarning(
                "No Backups", "No registry backups found to restore."
            )
            return

        # Create selection dialog
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Select Backup to Restore")
        dialog.geometry("600x400")
        dialog.transient(self.parent)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="Select a backup to restore:",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(padx=10, pady=10)

        # List backups
        list_frame = ctk.CTkScrollableFrame(dialog)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        selected_backup = {"id": None}

        for backup in backups:
            backup_frame = ctk.CTkFrame(list_frame)
            backup_frame.pack(fill="x", padx=5, pady=5)

            info_text = (
                f"ID: {backup.backup_id}\n"
                f"Date: {backup.timestamp}\n"
                f"Description: {backup.description}"
            )

            ctk.CTkLabel(backup_frame, text=info_text, anchor="w").pack(
                side="left", padx=10, pady=5
            )

            ctk.CTkButton(
                backup_frame,
                text="Restore This",
                command=lambda b=backup.backup_id: self._do_restore(b, dialog),
                width=100,
            ).pack(side="right", padx=10, pady=5)

    def _do_restore(self, backup_id: str, dialog: ctk.CTkToplevel) -> None:
        """Perform restore operation."""
        # Confirm
        if not messagebox.askyesno(
            "Confirm Restore",
            "Are you sure you want to restore this registry backup?\n\n"
            "This will modify your system registry.",
            parent=dialog,
        ):
            return

        dialog.destroy()
        logger.info(f"Restoring registry backup: {backup_id}")

        def task():
            try:
                self.registry_manager.restore_registry(backup_id)

                self.parent.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Success",
                        "Registry restored successfully!\n\n"
                        "Some changes may require a restart to take effect.",
                    ),
                )

            except RegistryError as e:
                logger.error(f"Registry restore failed: {e}")
                error_msg = str(e)
                self.parent.after(
                    0,
                    lambda: messagebox.showerror(
                        "Error", f"Failed to restore registry:\n{error_msg}"
                    ),
                )

        threading.Thread(target=task, daemon=True).start()

    def _undo_last_change(self) -> None:
        """Undo the last registry change."""
        if not messagebox.askyesno(
            "Confirm Undo",
            "This will restore the registry to the state before your last change.\n\n"
            "Are you sure you want to continue?",
        ):
            return

        logger.info("Undo last registry change requested")

        def task():
            try:
                self.registry_manager.undo_last_change()

                self.parent.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Success",
                        "Last change undone successfully!\n\n"
                        "Some changes may require a restart to take effect.",
                    ),
                )
                self.parent.after(0, self._refresh_history)

            except RegistryError as e:
                logger.error(f"Undo failed: {e}")
                error_msg = str(e)
                self.parent.after(
                    0,
                    lambda: messagebox.showerror(
                        "Error", f"Failed to undo last change:\n{error_msg}"
                    ),
                )

        threading.Thread(target=task, daemon=True).start()

    def _apply_tweak(self, tweak) -> None:
        """Apply a registry tweak."""
        # Show confirmation dialog with risk level
        risk_warnings = {
            "low": "This tweak is generally safe but will modify your registry.",
            "medium": "This tweak has moderate risk and may affect system behavior.",
            "high": "⚠️ WARNING: This tweak is HIGH RISK and could cause system instability!",
        }

        warning = risk_warnings.get(tweak.risk_level, "This will modify your registry.")

        if not messagebox.askyesno(
            f"Apply: {tweak.name}",
            f"{warning}\n\n"
            f"Tweak: {tweak.name}\n"
            f"Description: {tweak.description}\n"
            f"Risk Level: {tweak.risk_level.upper()}\n\n"
            f"A backup will be created automatically before applying.\n\n"
            f"Do you want to continue?",
        ):
            return

        logger.info(f"Applying registry tweak: {tweak.name}")

        def task():
            try:
                success, backup_id = self.registry_manager.apply_tweak(tweak.id)

                restart_msg = (
                    "\n\nℹ️ A system restart is required for this change to take effect."
                    if tweak.requires_restart
                    else ""
                )

                self.parent.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Success",
                        f"Tweak applied successfully!\n\n"
                        f"Backup ID: {backup_id}\n"
                        f"You can undo this change using the 'Undo Last Change' button."
                        f"{restart_msg}",
                    ),
                )
                self.parent.after(0, self._refresh_history)

            except RegistryError as e:
                logger.error(f"Failed to apply tweak: {e}")
                error_msg = str(e)
                self.parent.after(
                    0,
                    lambda: messagebox.showerror(
                        "Error", f"Failed to apply tweak:\n{error_msg}"
                    ),
                )

        threading.Thread(target=task, daemon=True).start()

    def _refresh_history(self) -> None:
        """Refresh backup history display."""
        backups = self.registry_manager.list_backups()

        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", "end")

        if not backups:
            self.history_text.insert("1.0", "No registry backups found.")
        else:
            for backup in backups:
                info = (
                    f"📦 {backup.backup_id}\n"
                    f"   Date: {backup.timestamp}\n"
                    f"   Description: {backup.description}\n"
                    f"   Keys: {', '.join(backup.registry_keys)}\n"
                    f"{'-' * 70}\n"
                )
                self.history_text.insert("end", info)

        self.history_text.configure(state="disabled")
