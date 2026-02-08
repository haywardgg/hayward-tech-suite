"""
Settings tab for application configuration.
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
import shutil
from pathlib import Path
import platform
import psutil

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
        self.system_info = None  # Will be loaded in background

        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        self._create_content()

        logger.info("Settings tab initialized")

    def _create_content(self) -> None:
        """Create content area with two-column layout."""
        content_frame = ctk.CTkScrollableFrame(self.parent)
        content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Configure two-column layout
        content_frame.grid_columnconfigure(0, weight=1)  # Left column
        content_frame.grid_columnconfigure(1, weight=1)  # Right column

        # LEFT COLUMN - Existing sections
        left_column = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_column.grid_columnconfigure(0, weight=1)

        # Appearance settings
        self._create_appearance_section(left_column)

        # Monitoring settings
        self._create_monitoring_section(left_column)

        # About section
        self._create_about_section(left_column)

        # RIGHT COLUMN - PC Specs
        right_column = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_column.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_column.grid_columnconfigure(0, weight=1)

        # PC Specs section
        self._create_pc_specs_section(right_column)

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

    def _create_pc_specs_section(self, parent: ctk.CTkFrame) -> None:
        """Create PC specifications section."""
        specs_frame = ctk.CTkFrame(parent)
        specs_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        specs_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            specs_frame, text="PC Specs", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Loading label
        self.specs_loading_label = ctk.CTkLabel(
            specs_frame,
            text="Loading system information...",
            font=ctk.CTkFont(size=11),
        )
        self.specs_loading_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Specs text area (will be populated)
        self.specs_text = ctk.CTkTextbox(
            specs_frame,
            width=400,
            height=500,
            font=ctk.CTkFont(family="Courier New", size=11),
        )
        self.specs_text.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.specs_text.configure(state="disabled")

        # Copy button
        self.copy_button = ctk.CTkButton(
            specs_frame,
            text="📋 Copy to Clipboard",
            command=self._copy_specs_to_clipboard,
            width=200,
            fg_color="#0078d4",
            hover_color="#005a9e",
            state="disabled",
        )
        self.copy_button.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        # Start gathering system info in background
        threading.Thread(target=self._gather_system_info, daemon=True).start()

    def _gather_system_info(self) -> None:
        """Gather system information in background thread."""
        try:
            info_lines = []

            # Header
            info_lines.append("=" * 50)
            info_lines.append("SYSTEM INFORMATION")
            info_lines.append("=" * 50)
            info_lines.append("")

            # Operating System
            info_lines.append("━━━ OPERATING SYSTEM ━━━")
            try:
                os_name = platform.system()
                os_version = platform.version()
                os_release = platform.release()
                os_machine = platform.machine()
                
                info_lines.append(f"OS: {os_name} {os_release}")
                info_lines.append(f"Version: {os_version}")
                info_lines.append(f"Architecture: {os_machine}")
                
                # Try to get Windows edition
                try:
                    import winreg
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                        r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                    product_name = winreg.QueryValueEx(key, "ProductName")[0]
                    build_number = winreg.QueryValueEx(key, "CurrentBuild")[0]
                    info_lines.append(f"Edition: {product_name}")
                    info_lines.append(f"Build: {build_number}")
                    winreg.CloseKey(key)
                except Exception:
                    pass
            except Exception as e:
                info_lines.append(f"Error: {e}")
            info_lines.append("")

            # CPU Information
            info_lines.append("━━━ PROCESSOR (CPU) ━━━")
            try:
                processor = platform.processor()
                cpu_count_physical = psutil.cpu_count(logical=False)
                cpu_count_logical = psutil.cpu_count(logical=True)
                cpu_freq = psutil.cpu_freq()
                
                info_lines.append(f"Model: {processor}")
                info_lines.append(f"Physical Cores: {cpu_count_physical}")
                info_lines.append(f"Logical Cores (Threads): {cpu_count_logical}")
                if cpu_freq:
                    info_lines.append(f"Base Frequency: {cpu_freq.current:.2f} MHz")
                    if cpu_freq.max > 0:
                        info_lines.append(f"Max Frequency: {cpu_freq.max:.2f} MHz")
            except Exception as e:
                info_lines.append(f"Error: {e}")
            info_lines.append("")

            # Memory Information
            info_lines.append("━━━ MEMORY (RAM) ━━━")
            try:
                mem = psutil.virtual_memory()
                total_gb = mem.total / (1024 ** 3)
                available_gb = mem.available / (1024 ** 3)
                used_gb = mem.used / (1024 ** 3)
                
                info_lines.append(f"Total: {total_gb:.2f} GB")
                info_lines.append(f"Available: {available_gb:.2f} GB")
                info_lines.append(f"Used: {used_gb:.2f} GB")
                info_lines.append(f"Usage: {mem.percent}%")
            except Exception as e:
                info_lines.append(f"Error: {e}")
            info_lines.append("")

            # Storage Information
            info_lines.append("━━━ STORAGE (DISKS) ━━━")
            try:
                partitions = psutil.disk_partitions()
                for partition in partitions:
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        total_gb = usage.total / (1024 ** 3)
                        used_gb = usage.used / (1024 ** 3)
                        free_gb = usage.free / (1024 ** 3)
                        
                        # Determine drive type
                        drive_type = "Unknown"
                        if "cdrom" in partition.opts or partition.fstype == "":
                            drive_type = "CD/DVD"
                        elif "removable" in partition.opts:
                            drive_type = "Removable"
                        else:
                            drive_type = "HDD/SSD"
                        
                        info_lines.append(f"Drive {partition.device}")
                        info_lines.append(f"  Type: {drive_type}")
                        info_lines.append(f"  Filesystem: {partition.fstype}")
                        info_lines.append(f"  Total: {total_gb:.2f} GB")
                        info_lines.append(f"  Used: {used_gb:.2f} GB")
                        info_lines.append(f"  Free: {free_gb:.2f} GB")
                        info_lines.append(f"  Usage: {usage.percent}%")
                        info_lines.append("")
                    except PermissionError:
                        continue
            except Exception as e:
                info_lines.append(f"Error: {e}")
                info_lines.append("")

            # Graphics Card Information (Windows only)
            info_lines.append("━━━ GRAPHICS CARD (GPU) ━━━")
            try:
                if platform.system() == "Windows":
                    import winreg
                    gpu_list = []
                    
                    try:
                        # Try to read from registry
                        key_path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                        
                        i = 0
                        while True:
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                subkey = winreg.OpenKey(key, subkey_name)
                                
                                try:
                                    desc = winreg.QueryValueEx(subkey, "DriverDesc")[0]
                                    if desc and desc not in gpu_list:
                                        gpu_list.append(desc)
                                        
                                        # Try to get VRAM
                                        try:
                                            vram = winreg.QueryValueEx(subkey, "HardwareInformation.qwMemorySize")[0]
                                            vram_gb = vram / (1024 ** 3)
                                            info_lines.append(f"GPU: {desc}")
                                            info_lines.append(f"  VRAM: {vram_gb:.2f} GB")
                                        except Exception:
                                            info_lines.append(f"GPU: {desc}")
                                            info_lines.append(f"  VRAM: N/A")
                                except Exception:
                                    pass
                                
                                winreg.CloseKey(subkey)
                                i += 1
                            except OSError:
                                break
                        
                        winreg.CloseKey(key)
                    except Exception:
                        pass
                    
                    if not gpu_list:
                        info_lines.append("Unable to detect GPU information")
                else:
                    info_lines.append("GPU detection only available on Windows")
            except Exception as e:
                info_lines.append(f"Error: {e}")
            info_lines.append("")

            # Motherboard Information (Windows only)
            info_lines.append("━━━ MOTHERBOARD ━━━")
            try:
                if platform.system() == "Windows":
                    import subprocess
                    
                    try:
                        # Get manufacturer
                        manufacturer = subprocess.check_output(
                            ["wmic", "baseboard", "get", "manufacturer"],
                            text=True, creationflags=0x08000000
                        ).strip().split("\n")[-1].strip()
                        
                        # Get product name
                        product = subprocess.check_output(
                            ["wmic", "baseboard", "get", "product"],
                            text=True, creationflags=0x08000000
                        ).strip().split("\n")[-1].strip()
                        
                        info_lines.append(f"Manufacturer: {manufacturer}")
                        info_lines.append(f"Model: {product}")
                    except Exception:
                        info_lines.append("Unable to detect motherboard information")
                else:
                    info_lines.append("Motherboard detection only available on Windows")
            except Exception as e:
                info_lines.append(f"Error: {e}")
            info_lines.append("")

            # Network Information
            info_lines.append("━━━ NETWORK ━━━")
            try:
                hostname = platform.node()
                info_lines.append(f"Computer Name: {hostname}")
                
                # Network interfaces
                net_if_addrs = psutil.net_if_addrs()
                for interface_name, interface_addresses in net_if_addrs.items():
                    for address in interface_addresses:
                        if str(address.family) == 'AddressFamily.AF_INET':
                            info_lines.append(f"{interface_name}:")
                            info_lines.append(f"  IP Address: {address.address}")
                            info_lines.append(f"  Netmask: {address.netmask}")
            except Exception as e:
                info_lines.append(f"Error: {e}")
            info_lines.append("")

            # Additional System Info
            info_lines.append("━━━ ADDITIONAL INFO ━━━")
            try:
                boot_time = psutil.boot_time()
                import datetime
                boot_time_str = datetime.datetime.fromtimestamp(boot_time).strftime("%Y-%m-%d %H:%M:%S")
                info_lines.append(f"Boot Time: {boot_time_str}")
                info_lines.append(f"Python Version: {platform.python_version()}")
            except Exception as e:
                info_lines.append(f"Error: {e}")

            info_lines.append("")
            info_lines.append("=" * 50)
            info_lines.append("End of System Information")
            info_lines.append("=" * 50)

            # Store the info
            self.system_info = "\n".join(info_lines)

            # Update UI on main thread
            self.parent.after(0, self._update_specs_display)

        except Exception as e:
            logger.error(f"Failed to gather system info: {e}")
            self.parent.after(0, lambda: self._update_specs_display(error=str(e)))

    def _update_specs_display(self, error: str = None) -> None:
        """Update the specs display in UI thread."""
        try:
            # Hide loading label
            self.specs_loading_label.grid_remove()

            # Update text area
            self.specs_text.configure(state="normal")
            
            if error:
                self.specs_text.delete("1.0", "end")
                self.specs_text.insert("1.0", f"Error gathering system information:\n{error}")
            elif self.system_info:
                self.specs_text.delete("1.0", "end")
                self.specs_text.insert("1.0", self.system_info)
                # Enable copy button
                self.copy_button.configure(state="normal")
            
            self.specs_text.configure(state="disabled")

        except Exception as e:
            logger.error(f"Failed to update specs display: {e}")

    def _copy_specs_to_clipboard(self) -> None:
        """Copy system specs to clipboard."""
        try:
            if self.system_info:
                self.parent.clipboard_clear()
                self.parent.clipboard_append(self.system_info)
                messagebox.showinfo(
                    "Copied",
                    "System specifications copied to clipboard!\n\n"
                    "You can now paste this information in support forums or tickets."
                )
                logger.info("System specs copied to clipboard")
        except Exception as e:
            logger.error(f"Failed to copy to clipboard: {e}")
            messagebox.showerror("Error", f"Failed to copy to clipboard: {e}")

