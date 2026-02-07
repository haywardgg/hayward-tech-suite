"""
DANGER tab for advanced registry tweaks with backup/restore functionality.

WARNING: This tab contains potentially dangerous operations that can break Windows.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
from pathlib import Path
from typing import Optional, Dict

from src.utils.logger import get_logger
from src.utils.admin_state import AdminState
from src.core.registry_manager import RegistryManager, RegistryError, RegistryTweak

logger = get_logger("danger_tab")


class DangerTab:
    """DANGER zone tab for advanced registry tweaks."""

    def __init__(self, parent: ctk.CTkFrame) -> None:
        """Initialize danger tab."""
        self.parent = parent
        self.registry_manager = RegistryManager()
        
        # Dictionary to store tweak buttons for state updates
        self.tweak_buttons = {}

        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        self._create_content()

        logger.info("DANGER tab initialized")

    def _create_content(self) -> None:
        """Create content area."""
        content_frame = ctk.CTkScrollableFrame(self.parent)
        content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)

        # Warning disclaimer
        self._create_warning_disclaimer(content_frame)

        # Backup/Restore section
        self._create_backup_section(content_frame)

        # Registry tweaks section
        self._create_tweaks_section(content_frame)

        # Backup history section
        self._create_history_section(content_frame)

    def _format_registry_value_text(self, value: Optional[Dict[str, str]], default: str = "Not Set") -> str:
        """
        Format registry value dictionary into display text.
        
        Args:
            value: Registry value dict with 'type' and 'data' keys, or None
            default: Default text to return if value is None or invalid
        
        Returns:
            Formatted text like "REG_DWORD: 0x1" or default if value is invalid
        """
        if value and 'type' in value and 'data' in value:
            return f"{value['type']}: {value['data']}"
        return default
    
    def _format_registry_change_message(
        self,
        tweak: RegistryTweak,
        before_value: Optional[Dict[str, str]],
        after_value: Optional[Dict[str, str]],
        is_restore: bool = False
    ) -> str:
        """
        Format a message showing before/after registry changes.
        
        Args:
            tweak: The registry tweak being applied or restored
            before_value: Registry value before change (dict with 'type' and 'data' keys, or None if not set)
            after_value: Registry value after change (dict with 'type' and 'data' keys, or None)
            is_restore: True if this is a restore operation where the value is expected to be deleted (after_value=None means success),
                       False if this is an apply operation where the value should exist (after_value=None means error)
        
        Returns:
            Formatted message string showing the registry change details
        """
        # Format before text
        before_text = self._format_registry_value_text(before_value, "Not Set")
        
        # Format after text - different default based on operation type
        after_default = "Deleted (Default)" if is_restore else "Failed to read"
        after_text = self._format_registry_value_text(after_value, after_default)
        
        return (
            f"\n\n📋 Registry Changes:\n"
            f"Key: {tweak.registry_key}\n"
            f"Value: {tweak.value_name or '(Default)'}\n\n"
            f"Before: {before_text}\n"
            f"After:  {after_text}"
        )
    
    def _create_warning_disclaimer(self, parent: ctk.CTkFrame) -> None:
        """Create professional warning disclaimer."""
        warning_frame = ctk.CTkFrame(parent, fg_color="#8B0000")
        warning_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 15))
        warning_frame.grid_columnconfigure(0, weight=1)

        warning_label = ctk.CTkLabel(
            warning_frame,
            text="⚠️ WARNING: Proceed at Your Own Risk ⚠️\n\n"
                 "The registry modifications in this section can potentially cause system instability "
                 "or break Windows functionality. Only proceed if you understand the implications.\n\n"
                 "A registry backup is automatically created before each change, allowing you to "
                 "restore previous settings if needed.",
            font=ctk.CTkFont(size=12),
            text_color="white",
            wraplength=900,
            justify="center"
        )
        warning_label.grid(row=0, column=0, padx=20, pady=15)

    def _create_backup_section(self, parent: ctk.CTkFrame) -> None:
        """Create backup/restore section."""
        backup_frame = ctk.CTkFrame(parent)
        backup_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
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
        
        # Check admin status
        is_admin = AdminState.is_admin()

        self.backup_button = ctk.CTkButton(
            btn_frame,
            text="📦 Backup Registry Now",
            command=self._backup_registry,
            width=200,
            height=40,
            fg_color="green",
            hover_color="darkgreen",
            state="normal" if is_admin else "disabled"
        )
        self.backup_button.grid(row=0, column=0, padx=5, pady=5)

        self.restore_button = ctk.CTkButton(
            btn_frame,
            text="↩️ Restore Registry",
            command=self._restore_registry,
            width=200,
            height=40,
            fg_color="orange",
            hover_color="darkorange",
            state="normal" if is_admin else "disabled"
        )
        self.restore_button.grid(row=0, column=1, padx=5, pady=5)

        self.undo_button = ctk.CTkButton(
            btn_frame,
            text="⏪ Undo Last Change",
            command=self._undo_last_change,
            width=200,
            height=40,
            fg_color="#d9534f",
            hover_color="#c9302c",
            state="normal" if is_admin else "disabled"
        )
        self.undo_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Add admin warning if not admin
        if not is_admin:
            warning_label = ctk.CTkLabel(
                backup_frame,
                text="⚠️ Administrator privileges required for registry operations",
                font=ctk.CTkFont(size=11),
                text_color="orange"
            )
            warning_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

    def _create_tweaks_section(self, parent: ctk.CTkFrame) -> None:
        """Create registry tweaks section."""
        tweaks_frame = ctk.CTkFrame(parent)
        tweaks_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
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

        # Check if tweak is already applied
        is_applied = self.registry_manager.is_tweak_applied(tweak.id)
        button_text = "RESTORE" if is_applied else "APPLY"
        
        # Check admin status
        is_admin = AdminState.is_admin()
        button_state = "normal" if is_admin else "disabled"
        fg_color = "orange" if is_applied else "green"

        # Apply/Restore button
        action_btn = ctk.CTkButton(
            tweak_frame,
            text=button_text,
            command=lambda t=tweak: self._toggle_tweak(t),
            width=100,
            height=35,
            state=button_state,
            fg_color=fg_color,
        )
        action_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Store button reference for later updates
        self.tweak_buttons[tweak.id] = action_btn

    def _create_history_section(self, parent: ctk.CTkFrame) -> None:
        """Create backup history section."""
        history_frame = ctk.CTkFrame(parent)
        history_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
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

    def _toggle_tweak(self, tweak) -> None:
        """Toggle a registry tweak (apply if not applied, restore if applied)."""
        is_applied = self.registry_manager.is_tweak_applied(tweak.id)
        
        if is_applied:
            self._restore_tweak(tweak)
        else:
            self._apply_tweak(tweak)

    def _restore_tweak(self, tweak) -> None:
        """Restore a registry tweak to Windows default."""
        # Get current value before restore
        before_value = self.registry_manager.get_registry_value(
            tweak.registry_key, tweak.value_name
        )
        
        if not messagebox.askyesno(
            f"Restore: {tweak.name}",
            f"This will restore the registry setting to Windows default.\n\n"
            f"Tweak: {tweak.name}\n"
            f"Description: {tweak.description}\n\n"
            f"Do you want to continue?",
        ):
            return

        logger.info(f"Restoring registry tweak to default: {tweak.name}")

        def task():
            try:
                # Create backup before restoring
                backup_id = self.registry_manager.backup_registry(
                    registry_keys=[tweak.registry_key],
                    description=f"Before restoring {tweak.name}"
                )

                # Restore to default - delete the registry value/key
                success = self.registry_manager.restore_tweak_to_default(tweak.id)
                
                # Get value after restore
                after_value = self.registry_manager.get_registry_value(
                    tweak.registry_key, tweak.value_name
                )

                restart_msg = (
                    "\n\nℹ️ A system restart may be required for this change to take effect."
                    if tweak.requires_restart
                    else ""
                )
                
                # Build before/after message using helper
                change_msg = self._format_registry_change_message(tweak, before_value, after_value, is_restore=True)

                self.parent.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Success",
                        f"Tweak restored to default successfully!\n\n"
                        f"Backup ID: {backup_id}"
                        f"{change_msg}"
                        f"{restart_msg}",
                    ),
                )
                self.parent.after(0, self._refresh_history)
                # Update button state
                tweak_id_to_update = tweak.id
                self.parent.after(0, lambda tid=tweak_id_to_update: self._update_tweak_button_state(tid))

            except RegistryError as e:
                logger.error(f"Failed to restore tweak: {e}")
                error_msg = str(e)
                self.parent.after(
                    0,
                    lambda: messagebox.showerror(
                        "Error", f"Failed to restore tweak:\n{error_msg}"
                    ),
                )

        threading.Thread(target=task, daemon=True).start()

    def _apply_tweak(self, tweak) -> None:
        """Apply a registry tweak."""
        # Get current value before applying
        before_value = self.registry_manager.get_registry_value(
            tweak.registry_key, tweak.value_name
        )
        
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
                
                # Get value after applying
                after_value = self.registry_manager.get_registry_value(
                    tweak.registry_key, tweak.value_name
                )

                restart_msg = (
                    "\n\nℹ️ A system restart is required for this change to take effect."
                    if tweak.requires_restart
                    else ""
                )
                
                # Build before/after message using helper
                change_msg = self._format_registry_change_message(tweak, before_value, after_value, is_restore=False)

                self.parent.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Success",
                        f"Tweak applied successfully!\n\n"
                        f"Backup ID: {backup_id}\n"
                        f"You can undo this change using the 'Undo Last Change' button."
                        f"{change_msg}"
                        f"{restart_msg}",
                    ),
                )
                self.parent.after(0, self._refresh_history)
                # Update button state after applying tweak
                # Capture tweak_id in local variable to avoid closure issues
                tweak_id_to_update = tweak.id
                self.parent.after(0, lambda tid=tweak_id_to_update: self._update_tweak_button_state(tid))

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
    
    def _update_tweak_button_state(self, tweak_id: str) -> None:
        """Update the button state for a specific tweak."""
        if tweak_id in self.tweak_buttons:
            button = self.tweak_buttons[tweak_id]
            is_applied = self.registry_manager.is_tweak_applied(tweak_id)
            
            button_text = "RESTORE" if is_applied else "APPLY"
            button_state = "normal"  # Always enabled
            fg_color = "orange" if is_applied else "green"
            
            button.configure(
                text=button_text,
                state=button_state,
                fg_color=fg_color
            )

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
