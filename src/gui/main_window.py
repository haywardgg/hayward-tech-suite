"""
Main window for Ghosty Toolz Evolved.

Provides the main application window with tabbed interface for different functionality.
"""

import customtkinter as ctk
from typing import Optional
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.config import get_config
from src.gui.tabs.monitoring_tab import MonitoringTab
from src.gui.tabs.diagnostics_tab import DiagnosticsTab
from src.gui.tabs.maintenance_tab import MaintenanceTab
from src.gui.tabs.security_tab import SecurityTab
from src.gui.tabs.danger_tab import DangerTab
from src.gui.tabs.settings_tab import SettingsTab

logger = get_logger("main_window")
config = get_config()


class MainWindow(ctk.CTk):
    """Main application window with tabbed interface."""

    def __init__(self) -> None:
        """Initialize main window."""
        super().__init__()

        # Window configuration
        self.title(config.get("app.name", "Ghosty Toolz Evolved"))
        
        # Get window dimensions from config
        width = config.get("ui.window.width", 1200)
        height = config.get("ui.window.height", 800)
        self.geometry(f"{width}x{height}")
        
        # Set minimum size
        min_width = config.get("ui.window.min_width", 1000)
        min_height = config.get("ui.window.min_height", 700)
        self.minsize(min_width, min_height)

        # Configure theme
        theme = config.get("ui.theme", "dark")
        ctk.set_appearance_mode(theme)
        
        color_theme = config.get("ui.color_scheme.primary", "#4158D0")
        ctk.set_default_color_theme("blue")  # Can be customized further

        # Set icon if available
        icon_path = Path("images/ghosty icon.ico")
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception as e:
                logger.warning(f"Could not set window icon: {e}")

        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Create header
        self._create_header()

        # Create tabview
        self._create_tabview()

        # Create status bar
        self._create_status_bar()

        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        logger.info("Main window initialized")

    def _create_header(self) -> None:
        """Create header section."""
        header_frame = ctk.CTkFrame(self.main_container)
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        header_frame.grid_columnconfigure(1, weight=1)

        # App title
        title_label = ctk.CTkLabel(
            header_frame,
            text=config.get("app.name", "Ghosty Toolz Evolved"),
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        title_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Version info
        version_label = ctk.CTkLabel(
            header_frame,
            text=f"v{config.get('app.version', '2.0.0')}",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        version_label.grid(row=0, column=1, padx=10, pady=10, sticky="e")

    def _create_tabview(self) -> None:
        """Create main tabview with all tabs."""
        self.tabview = ctk.CTkTabview(self.main_container)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Add tabs
        self.monitoring_tab = None
        self.diagnostics_tab = None
        self.maintenance_tab = None
        self.security_tab = None
        self.danger_tab = None
        self.settings_tab = None

        try:
            # Monitoring tab
            self.tabview.add("Monitoring")
            tab_frame = self.tabview.tab("Monitoring")
            self.monitoring_tab = MonitoringTab(tab_frame)
            logger.info("Monitoring tab created")

        except Exception as e:
            logger.error(f"Failed to create Monitoring tab: {e}")

        try:
            # Diagnostics tab (Network Diagnostics)
            self.tabview.add("Diagnostics")
            tab_frame = self.tabview.tab("Diagnostics")
            self.diagnostics_tab = DiagnosticsTab(tab_frame)
            logger.info("Diagnostics tab created")

        except Exception as e:
            logger.error(f"Failed to create Diagnostics tab: {e}")

        try:
            # Maintenance tab
            self.tabview.add("Maintenance")
            tab_frame = self.tabview.tab("Maintenance")
            self.maintenance_tab = MaintenanceTab(tab_frame)
            logger.info("Maintenance tab created")

        except Exception as e:
            logger.error(f"Failed to create Maintenance tab: {e}")

        try:
            # Security tab
            self.tabview.add("Security")
            tab_frame = self.tabview.tab("Security")
            self.security_tab = SecurityTab(tab_frame)
            logger.info("Security tab created")

        except Exception as e:
            logger.error(f"Failed to create Security tab: {e}")

        try:
            # DANGER ZONE tab
            self.tabview.add("DANGER ZONE")
            tab_frame = self.tabview.tab("DANGER ZONE")
            # Set the tab background to red
            tab_frame.configure(fg_color="#8B0000")  # Dark red background
            self.danger_tab = DangerTab(tab_frame)
            logger.info("DANGER ZONE tab created")

        except Exception as e:
            logger.error(f"Failed to create DANGER ZONE tab: {e}")

        try:
            # Settings tab
            self.tabview.add("Settings")
            tab_frame = self.tabview.tab("Settings")
            self.settings_tab = SettingsTab(tab_frame, main_window=self)
            logger.info("Settings tab created")

        except Exception as e:
            logger.error(f"Failed to create Settings tab: {e}")

        # Set default tab
        self.tabview.set("Monitoring")

    def _create_status_bar(self) -> None:
        """Create status bar at bottom."""
        self.status_bar = ctk.CTkFrame(self.main_container, height=30)
        self.status_bar.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.status_bar.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=ctk.CTkFont(size=11),
            anchor="w",
        )
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

    def update_status(self, message: str) -> None:
        """
        Update status bar message.

        Args:
            message: Status message to display
        """
        self.status_label.configure(text=message)
        self.update_idletasks()
        logger.debug(f"Status updated: {message}")

    def show_message(self, title: str, message: str, message_type: str = "info") -> None:
        """
        Show a message dialog.

        Args:
            title: Dialog title
            message: Message to display
            message_type: Type of message ('info', 'warning', 'error')
        """
        from tkinter import messagebox

        if message_type == "info":
            messagebox.showinfo(title, message)
        elif message_type == "warning":
            messagebox.showwarning(title, message)
        elif message_type == "error":
            messagebox.showerror(title, message)

    def on_closing(self) -> None:
        """Handle window close event."""
        logger.info("Application closing")

        # Stop monitoring if active
        if self.monitoring_tab:
            try:
                self.monitoring_tab.stop_monitoring()
            except Exception as e:
                logger.error(f"Error stopping monitoring: {e}")

        # Destroy window
        self.destroy()


# Example usage
if __name__ == "__main__":
    # Set up logging
    from src.utils.logger import get_logger

    logger = get_logger("main")
    logger.info("Starting Ghosty Toolz Evolved")

    # Create and run main window
    app = MainWindow()
    app.mainloop()

    logger.info("Application closed")
