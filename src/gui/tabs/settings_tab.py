"""
Settings tab for application configuration.
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
import shutil
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.config import get_config
from src.utils.admin_state import AdminState

logger = get_logger("settings_tab")


class SettingsTab:
    """Application settings and configuration tab."""

    def __init__(self, parent: ctk.CTkFrame, main_window=None) -> None:
        """Initialize settings tab."""
        self.parent = parent
        self.main_window = main_window
        self.config = get_config()

        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        self._create_content()

        logger.info("Settings tab initialized")

    def _create_content(self) -> None:
        """Create content area."""
        content_frame = ctk.CTkScrollableFrame(self.parent)
        content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)

        # Appearance settings
        self._create_appearance_section(content_frame)

        # Monitoring settings
        self._create_monitoring_section(content_frame)

        # About section
        self._create_about_section(content_frame)

    def _create_appearance_section(self, parent: ctk.CTkFrame) -> None:
        """Create appearance settings section."""
        appearance_frame = ctk.CTkFrame(parent)
        appearance_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        title = ctk.CTkLabel(
            appearance_frame, text="Appearance", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Theme selector
        ctk.CTkLabel(appearance_frame, text="Theme:").grid(row=1, column=0, padx=10, pady=5, sticky="w")

        theme_options = ["dark", "light", "system"]
        current_theme = self.config.get("ui.theme", "dark")

        self.theme_var = ctk.StringVar(value=current_theme)
        theme_menu = ctk.CTkOptionMenu(
            appearance_frame,
            values=theme_options,
            variable=self.theme_var,
            command=self._change_theme,
        )
        theme_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    def _create_monitoring_section(self, parent: ctk.CTkFrame) -> None:
        """Create monitoring settings section."""
        monitoring_frame = ctk.CTkFrame(parent)
        monitoring_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        title = ctk.CTkLabel(
            monitoring_frame, text="Monitoring", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        info = ctk.CTkLabel(
            monitoring_frame,
            text="Configure monitoring intervals (seconds)",
            font=ctk.CTkFont(size=11),
        )
        info.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # CPU interval
        ctk.CTkLabel(monitoring_frame, text="CPU/RAM Interval:").grid(
            row=2, column=0, padx=10, pady=5, sticky="w"
        )
        cpu_interval = self.config.get("monitoring.cpu_interval", 2)
        self.cpu_interval_var = ctk.StringVar(value=str(cpu_interval))
        ctk.CTkEntry(monitoring_frame, textvariable=self.cpu_interval_var, width=100).grid(
            row=2, column=1, padx=5, pady=5, sticky="w"
        )

    def _create_about_section(self, parent: ctk.CTkFrame) -> None:
        """Create about section."""
        about_frame = ctk.CTkFrame(parent)
        about_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        about_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(about_frame, text="About", font=ctk.CTkFont(size=14, weight="bold"))
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Updated about information as per requirements
        info_text = (
            "Ghosty Toolz Evolved\n"
            "Version 2.0.0\n"
            "By HaywardGG\n\n"
            "Professional Windows System Maintenance Tool\n"
            "Forked from Ghostshadow's Ghosty Tools Pro\n\n"
            "License: GPL-3.0-or-later"
        )
        info_label = ctk.CTkLabel(
            about_frame, text=info_text, font=ctk.CTkFont(size=11), justify="left"
        )
        info_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Save settings button
        ctk.CTkButton(
            about_frame,
            text="Save Settings",
            command=self._save_settings,
            width=150,
            fg_color="green",
        ).grid(row=2, column=0, padx=10, pady=10, sticky="w")

        # RESET button - admin required
        self.reset_button = ctk.CTkButton(
            about_frame,
            text="↻  RESET TO DEFAULTS",  # Using larger unicode icon with spacing
            command=self._reset_to_defaults,
            width=200,
            height=40,  # Increased height for better visibility
            fg_color="#dc3545",
            hover_color="#c82333",
            font=ctk.CTkFont(size=14, weight="bold"),  # Larger font for icon
        )
        self.reset_button.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        
        # Disable reset button if not admin
        if not AdminState.is_admin():
            self.reset_button.configure(state="disabled")
            # Add tooltip-like label
            ctk.CTkLabel(
                about_frame,
                text="WARNING: Requires Administrator - Restart app as admin",
                font=ctk.CTkFont(size=9),
                text_color="gray"
            ).grid(row=4, column=0, padx=10, pady=(0, 10), sticky="w")

    def _change_theme(self, choice: str) -> None:
        """Change application theme."""
        logger.info(f"Changing theme to: {choice}")
        ctk.set_appearance_mode(choice)
        self.config.set("ui.theme", choice)
        messagebox.showinfo("Theme Changed", f"Theme changed to {choice}")

    def _save_settings(self) -> None:
        """Save current settings."""
        try:
            # Update config with current values
            self.config.set("ui.theme", self.theme_var.get())

            cpu_interval = int(self.cpu_interval_var.get())
            self.config.set("monitoring.cpu_interval", cpu_interval)
            self.config.set("monitoring.ram_interval", cpu_interval)

            # Save to file
            self.config.save()

            logger.info("Settings saved")
            messagebox.showinfo("Success", "Settings saved successfully!")

        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings: {e}")

    def _reset_to_defaults(self) -> None:
        """Reset all application settings and registry changes to defaults."""
        if not AdminState.is_admin():
            messagebox.showerror(
                "Admin Required",
                "Administrator privileges are required to reset the application.\n\n"
                "Please restart the application as administrator."
            )
            return

        # Show confirmation dialog
        result = messagebox.askyesno(
            "Reset to Defaults",
            "WARNING: This will:\n\n"
            "• Delete all registry backups from temp folder\n"
            "• Reset application settings to defaults\n"
            "• Clear all logs\n\n"
            "Note: Registry tweaks will NOT be automatically restored.\n"
            "Use the RESTORE button in DANGER ZONE to undo individual tweaks.\n\n"
            "This action cannot be undone!\n\n"
            "Are you sure you want to continue?",
            icon='warning'
        )

        if not result:
            return

        # Disable button during operation
        self.reset_button.configure(state="disabled", text="Resetting...")

        def reset_task():
            try:
                # Import here to avoid circular dependencies
                from src.core.registry_manager import RegistryManager
                import tempfile

                registry_manager = RegistryManager()

                # Restore all registry changes to defaults
                logger.info("Restoring all registry changes to defaults...")
                try:
                    success_count, total_applied, failed_tweaks = registry_manager.restore_all_to_defaults()
                    if failed_tweaks:
                        logger.warning(f"Some tweaks failed to restore: {', '.join(failed_tweaks)}")
                    else:
                        logger.info(f"Successfully restored {success_count} registry tweaks to defaults")
                    restore_results = (success_count, total_applied, failed_tweaks)
                except Exception as e:
                    restore_results = None
                    logger.warning(f"Failed to restore registry defaults: {e}")

                # Delete registry backup directory
                logger.info("Deleting registry backup directory...")
                backup_dir = Path(tempfile.gettempdir()) / "ghosty_toolz_registry_backups"
                if backup_dir.exists():
                    try:
                        shutil.rmtree(backup_dir)
                        logger.info("Registry backups deleted")
                    except Exception as e:
                        logger.warning(f"Failed to delete registry backups: {e}")

                # Reset config to defaults
                logger.info("Resetting configuration to defaults...")
                try:
                    self.config.reset_to_defaults()
                except Exception as e:
                    logger.warning(f"Failed to reset config: {e}")

                # Clear log files
                logger.info("Clearing log files...")
                try:
                    log_dir = Path("logs")
                    if log_dir.exists():
                        for log_file in log_dir.glob("*.log"):
                            try:
                                log_file.unlink()
                            except Exception:
                                pass
                except Exception as e:
                    logger.warning(f"Failed to clear logs: {e}")

                # Re-enable button and show success
                self.parent.after(0, lambda: self.reset_button.configure(
                    state="normal", text="↻  RESET TO DEFAULTS"
                ))
                
                # Build success message with restore results
                success_msg = "Application has been reset to defaults!\n\n"
                if restore_results:
                    success_count, total_applied, failed_tweaks = restore_results
                    if total_applied > 0:
                        success_msg += f"Registry Tweaks Restored: {success_count}/{total_applied}\n"
                        if failed_tweaks:
                            success_msg += f"Failed Tweaks: {', '.join(failed_tweaks)}\n"
                        success_msg += "\n"
                
                success_msg += "Please restart the application for changes to take full effect."
                
                self.parent.after(0, lambda msg=success_msg: messagebox.showinfo(
                    "Reset Complete", msg
                ))

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Failed to reset application: {error_msg}")
                self.parent.after(0, lambda: self.reset_button.configure(
                    state="normal", text="↻  RESET TO DEFAULTS"
                ))
                self.parent.after(0, lambda: messagebox.showerror(
                    "Reset Failed",
                    f"Failed to reset application:\n{error_msg}"
                ))

        threading.Thread(target=reset_task, daemon=True).start()
