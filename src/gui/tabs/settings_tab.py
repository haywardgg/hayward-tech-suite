"""
Settings tab for application configuration.
"""

import customtkinter as ctk
from tkinter import messagebox

from src.utils.logger import get_logger
from src.utils.config import get_config

logger = get_logger("settings_tab")


class SettingsTab:
    """Application settings and configuration tab."""

    def __init__(self, parent: ctk.CTkFrame, main_window=None) -> None:
        """Initialize settings tab."""
        self.parent = parent
        self.main_window = main_window
        self.config = get_config()

        self.parent.grid_rowconfigure(1, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        self._create_header()
        self._create_content()

        logger.info("Settings tab initialized")

    def _create_header(self) -> None:
        """Create header."""
        header_frame = ctk.CTkFrame(self.parent)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        title = ctk.CTkLabel(
            header_frame, text="Settings", font=ctk.CTkFont(size=18, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    def _create_content(self) -> None:
        """Create content area."""
        content_frame = ctk.CTkScrollableFrame(self.parent)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
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
        appearance_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            appearance_frame, text="Appearance", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

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
        theme_menu.grid(row=1, column=0, padx=10, pady=5, sticky="e")

    def _create_monitoring_section(self, parent: ctk.CTkFrame) -> None:
        """Create monitoring settings section."""
        monitoring_frame = ctk.CTkFrame(parent)
        monitoring_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        monitoring_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            monitoring_frame, text="Monitoring", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        info = ctk.CTkLabel(
            monitoring_frame,
            text="Configure monitoring intervals (seconds)",
            font=ctk.CTkFont(size=11),
        )
        info.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # CPU interval
        ctk.CTkLabel(monitoring_frame, text="CPU/RAM Interval:").grid(
            row=2, column=0, padx=10, pady=5, sticky="w"
        )
        cpu_interval = self.config.get("monitoring.cpu_interval", 2)
        self.cpu_interval_var = ctk.StringVar(value=str(cpu_interval))
        ctk.CTkEntry(monitoring_frame, textvariable=self.cpu_interval_var, width=100).grid(
            row=2, column=0, padx=10, pady=5, sticky="e"
        )

    def _create_about_section(self, parent: ctk.CTkFrame) -> None:
        """Create about section."""
        about_frame = ctk.CTkFrame(parent)
        about_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        about_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(about_frame, text="About", font=ctk.CTkFont(size=14, weight="bold"))
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        app_name = self.config.get("app.name", "Ghosty Tools Pro")
        app_version = self.config.get("app.version", "2.0.0")
        description = self.config.get("app.description", "Professional Windows System Maintenance Tool")

        info_text = f"{app_name}\nVersion {app_version}\n\n{description}\n\nLicense: GPL-3.0-or-later"
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
