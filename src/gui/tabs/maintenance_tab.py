"""
Maintenance tab for system maintenance operations.

Provides access to system cleanup, DNS flush, restore points, and other maintenance tasks.
"""

import customtkinter as ctk
from tkinter import messagebox
import threading

from src.utils.logger import get_logger
from src.core.system_operations import SystemOperations, SystemOperationError, PrivilegeError

logger = get_logger("maintenance_tab")


class MaintenanceTab:
    """System maintenance operations tab."""

    def __init__(self, parent: ctk.CTkFrame) -> None:
        """
        Initialize maintenance tab.

        Args:
            parent: Parent frame
        """
        self.parent = parent
        self.system_ops = SystemOperations()

        # Configure parent grid
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        # Create UI
        self._create_operations()

        logger.info("Maintenance tab initialized")

    def _create_operations(self) -> None:
        """Create operation buttons and options."""
        # Scrollable content frame
        content_frame = ctk.CTkScrollableFrame(self.parent)
        content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Row 0: System Restore (full width)
        self._create_restore_point_section(content_frame, row=0, column=0)

        # Row 1: Disk Health, DNS Operations, System Maintenance
        self._create_disk_section(content_frame, row=1, column=0)
        self._create_dns_section(content_frame, row=1, column=1)
        self._create_system_maintenance_section(content_frame, row=1, column=2)

    def _create_dns_section(self, parent: ctk.CTkFrame, row: int, column: int = 0) -> None:
        """Create DNS operations section."""
        dns_frame = ctk.CTkFrame(parent)
        dns_frame.grid(row=row, column=column, sticky="nsew", padx=5, pady=5)
        dns_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            dns_frame, text="🌐 DNS Operations", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        info = ctk.CTkLabel(
            dns_frame, text="DNS cache and configuration", font=ctk.CTkFont(size=11)
        )
        info.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Flush DNS button
        ctk.CTkButton(
            dns_frame, text="Flush DNS Cache", command=self._flush_dns
        ).grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Edit hosts file button
        ctk.CTkButton(
            dns_frame, text="Edit Hosts File", command=self._edit_hosts_file
        ).grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Reset DNS to Google button
        ctk.CTkButton(
            dns_frame, text="DNS → Google (8.8.8.8)", command=self._reset_dns_google
        ).grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        # Reset DNS to Cloudflare button
        ctk.CTkButton(
            dns_frame, text="DNS → Cloudflare (1.1.1.1)", command=self._reset_dns_cloudflare
        ).grid(row=5, column=0, padx=10, pady=5, sticky="ew")

        # Reset DNS to Auto button
        ctk.CTkButton(
            dns_frame, text="DNS → Auto (DHCP)", command=self._reset_dns_auto
        ).grid(row=6, column=0, padx=10, pady=5, sticky="ew")

        # View DNS cache button
        ctk.CTkButton(
            dns_frame, text="View DNS Cache", command=self._view_dns_cache
        ).grid(row=7, column=0, padx=10, pady=5, sticky="ew")

    def _create_restore_point_section(self, parent: ctk.CTkFrame, row: int, column: int = 0) -> None:
        """Create restore point section."""
        restore_frame = ctk.CTkFrame(parent)
        restore_frame.grid(row=row, column=column, columnspan=3, sticky="nsew", padx=5, pady=5)
        restore_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            restore_frame, text="🔄 System Restore", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        info = ctk.CTkLabel(
            restore_frame,
            text="Create restore point before making changes",
            font=ctk.CTkFont(size=11),
        )
        info.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.restore_name_entry = ctk.CTkEntry(restore_frame, placeholder_text="Restore Point Name")
        self.restore_name_entry.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        btn = ctk.CTkButton(
            restore_frame, text="Create Restore Point", command=self._create_restore_point, width=200
        )
        btn.grid(row=3, column=0, padx=10, pady=10, sticky="w")

    def _create_system_maintenance_section(self, parent: ctk.CTkFrame, row: int, column: int = 0) -> None:
        """Create system maintenance section."""
        maint_frame = ctk.CTkFrame(parent)
        maint_frame.grid(row=row, column=column, sticky="nsew", padx=5, pady=5)
        maint_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            maint_frame, text="🛠️ System Maintenance", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        info = ctk.CTkLabel(
            maint_frame,
            text="Run comprehensive system maintenance (SFC, DISM) - Requires Admin",
            font=ctk.CTkFont(size=11),
        )
        info.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        btn = ctk.CTkButton(
            maint_frame,
            text="Run Full Maintenance",
            command=self._run_maintenance,
            width=200,
            fg_color="#d9534f",
            hover_color="#c9302c",
        )
        btn.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        # Progress display
        self.maintenance_progress_label = ctk.CTkLabel(
            maint_frame, text="", font=ctk.CTkFont(size=11), text_color="gray"
        )
        self.maintenance_progress_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

    def _create_disk_section(self, parent: ctk.CTkFrame, row: int, column: int = 0) -> None:
        """Create disk operations section."""
        disk_frame = ctk.CTkFrame(parent)
        disk_frame.grid(row=row, column=column, sticky="nsew", padx=5, pady=5)
        disk_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            disk_frame, text="💾 Disk Health", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        info = ctk.CTkLabel(
            disk_frame, text="Check disk health status", font=ctk.CTkFont(size=11)
        )
        info.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        btn = ctk.CTkButton(disk_frame, text="Check Disk Health", command=self._check_disk_health, width=200)
        btn.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        # Result display
        self.disk_health_text = ctk.CTkTextbox(disk_frame, height=100, wrap="word")
        self.disk_health_text.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.disk_health_text.configure(state="disabled")

    def _flush_dns(self) -> None:
        """Flush DNS cache."""
        logger.info("User initiated DNS flush")

        def task():
            try:
                success = self.system_ops.flush_dns()
                if success:
                    self.parent.after(0, lambda: messagebox.showinfo(
                        "Success", "DNS cache flushed successfully!"
                    ))
            except Exception as e:
                logger.error(f"DNS flush failed: {e}")
                self.parent.after(0, lambda: messagebox.showerror(
                    "Error", f"Failed to flush DNS: {e}"
                ))

        threading.Thread(target=task, daemon=True).start()

    def _create_restore_point(self) -> None:
        """Create system restore point."""
        name = self.restore_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a restore point name")
            return

        logger.info(f"User initiated restore point creation: {name}")

        def task():
            try:
                if not self.system_ops.is_admin():
                    self.parent.after(0, lambda: messagebox.showerror(
                        "Admin Required",
                        "Administrator privileges are required to create restore points.\n\n"
                        "Please restart the application as administrator."
                    ))
                    return

                success = self.system_ops.create_restore_point(name)
                if success:
                    self.parent.after(0, lambda: messagebox.showinfo(
                        "Success", f"Restore point '{name}' created successfully!"
                    ))
                    self.parent.after(0, lambda: self.restore_name_entry.delete(0, "end"))
            except PrivilegeError as e:
                logger.error(f"Privilege error: {e}")
                self.parent.after(0, lambda: messagebox.showerror(
                    "Admin Required", str(e)
                ))
            except Exception as e:
                logger.error(f"Restore point creation failed: {e}")
                self.parent.after(0, lambda: messagebox.showerror(
                    "Error", f"Failed to create restore point: {e}"
                ))

        threading.Thread(target=task, daemon=True).start()

    def _run_maintenance(self) -> None:
        """Run full system maintenance."""
        response = messagebox.askyesno(
            "Confirm Maintenance",
            "This will run SFC and DISM system repairs.\n\n"
            "This may take 10-30 minutes and requires administrator privileges.\n\n"
            "Continue?",
        )

        if not response:
            return

        logger.info("User initiated full system maintenance")

        def task():
            try:
                if not self.system_ops.is_admin():
                    self.parent.after(0, lambda: messagebox.showerror(
                        "Admin Required",
                        "Administrator privileges are required for system maintenance."
                    ))
                    return

                self.parent.after(0, lambda: self.maintenance_progress_label.configure(
                    text="Running maintenance... This may take several minutes."
                ))

                results = self.system_ops.run_system_maintenance()

                # Show results
                success_count = sum(1 for r in results.values() if r.get("success", False))
                total_count = len(results)

                msg = f"Maintenance completed: {success_count}/{total_count} tasks successful\n\n"
                for task_name, result in results.items():
                    status = "✓" if result.get("success", False) else "✗"
                    msg += f"{status} {task_name}\n"

                self.parent.after(0, lambda: messagebox.showinfo("Maintenance Complete", msg))
                self.parent.after(0, lambda: self.maintenance_progress_label.configure(text=""))

            except Exception as e:
                logger.error(f"Maintenance failed: {e}")
                self.parent.after(0, lambda: messagebox.showerror(
                    "Error", f"Maintenance failed: {e}"
                ))
                self.parent.after(0, lambda: self.maintenance_progress_label.configure(text=""))

        threading.Thread(target=task, daemon=True).start()

    def _check_disk_health(self) -> None:
        """Check disk health."""
        logger.info("User initiated disk health check")

        def task():
            try:
                success, stdout, stderr = self.system_ops.execute_command(
                    "wmic diskdrive get status", timeout=30, audit=False
                )

                result_text = stdout if success else f"Error: {stderr}"

                self.parent.after(0, lambda: self.disk_health_text.configure(state="normal"))
                self.parent.after(0, lambda: self.disk_health_text.delete("1.0", "end"))
                self.parent.after(0, lambda: self.disk_health_text.insert("1.0", result_text))
                self.parent.after(0, lambda: self.disk_health_text.configure(state="disabled"))

            except Exception as e:
                logger.error(f"Disk health check failed: {e}")
                self.parent.after(0, lambda: messagebox.showerror(
                    "Error", f"Failed to check disk health: {e}"
                ))

        threading.Thread(target=task, daemon=True).start()

    def _edit_hosts_file(self) -> None:
        """Open hosts file for editing."""
        logger.info("User initiated hosts file edit")

        def task():
            try:
                if not self.system_ops.is_admin():
                    self.parent.after(0, lambda: messagebox.showerror(
                        "Admin Required",
                        "Administrator privileges are required to edit the hosts file.\n\n"
                        "Please restart the application as administrator."
                    ))
                    return

                self.system_ops.edit_hosts_file()
                self.parent.after(0, lambda: messagebox.showinfo(
                    "Success", "Hosts file opened in Notepad."
                ))
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Failed to edit hosts file: {error_msg}")
                self.parent.after(0, lambda: messagebox.showerror(
                    "Error", f"Failed to open hosts file:\n{error_msg}"
                ))

        threading.Thread(target=task, daemon=True).start()

    def _reset_dns_google(self) -> None:
        """Reset DNS to Google DNS."""
        logger.info("User initiated DNS reset to Google")

        def task():
            try:
                if not self.system_ops.is_admin():
                    self.parent.after(0, lambda: messagebox.showerror(
                        "Admin Required",
                        "Administrator privileges are required to change DNS settings.\n\n"
                        "Please restart the application as administrator."
                    ))
                    return

                # Get network adapters
                adapters = self.system_ops.get_network_adapters()
                if not adapters:
                    self.parent.after(0, lambda: messagebox.showerror(
                        "Error", "No network adapters found."
                    ))
                    return

                # Use first active adapter
                adapter = adapters[0]
                self.system_ops.set_dns_servers(adapter, "8.8.8.8", "8.8.4.4")
                
                self.parent.after(0, lambda: messagebox.showinfo(
                    "Success", f"DNS set to Google DNS (8.8.8.8, 8.8.4.4) for adapter '{adapter}'"
                ))
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Failed to set Google DNS: {error_msg}")
                self.parent.after(0, lambda: messagebox.showerror(
                    "Error", f"Failed to set Google DNS:\n{error_msg}"
                ))

        threading.Thread(target=task, daemon=True).start()

    def _reset_dns_cloudflare(self) -> None:
        """Reset DNS to Cloudflare DNS."""
        logger.info("User initiated DNS reset to Cloudflare")

        def task():
            try:
                if not self.system_ops.is_admin():
                    self.parent.after(0, lambda: messagebox.showerror(
                        "Admin Required",
                        "Administrator privileges are required to change DNS settings.\n\n"
                        "Please restart the application as administrator."
                    ))
                    return

                # Get network adapters
                adapters = self.system_ops.get_network_adapters()
                if not adapters:
                    self.parent.after(0, lambda: messagebox.showerror(
                        "Error", "No network adapters found."
                    ))
                    return

                # Use first active adapter
                adapter = adapters[0]
                self.system_ops.set_dns_servers(adapter, "1.1.1.1", "1.0.0.1")
                
                self.parent.after(0, lambda: messagebox.showinfo(
                    "Success", f"DNS set to Cloudflare DNS (1.1.1.1, 1.0.0.1) for adapter '{adapter}'"
                ))
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Failed to set Cloudflare DNS: {error_msg}")
                self.parent.after(0, lambda: messagebox.showerror(
                    "Error", f"Failed to set Cloudflare DNS:\n{error_msg}"
                ))

        threading.Thread(target=task, daemon=True).start()

    def _reset_dns_auto(self) -> None:
        """Reset DNS to automatic (DHCP)."""
        logger.info("User initiated DNS reset to auto")

        def task():
            try:
                if not self.system_ops.is_admin():
                    self.parent.after(0, lambda: messagebox.showerror(
                        "Admin Required",
                        "Administrator privileges are required to change DNS settings.\n\n"
                        "Please restart the application as administrator."
                    ))
                    return

                # Get network adapters
                adapters = self.system_ops.get_network_adapters()
                if not adapters:
                    self.parent.after(0, lambda: messagebox.showerror(
                        "Error", "No network adapters found."
                    ))
                    return

                # Use first active adapter
                adapter = adapters[0]
                self.system_ops.reset_dns_to_auto(adapter)
                
                self.parent.after(0, lambda: messagebox.showinfo(
                    "Success", f"DNS reset to automatic (DHCP) for adapter '{adapter}'"
                ))
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Failed to reset DNS to auto: {error_msg}")
                self.parent.after(0, lambda: messagebox.showerror(
                    "Error", f"Failed to reset DNS to auto:\n{error_msg}"
                ))

        threading.Thread(target=task, daemon=True).start()

    def _view_dns_cache(self) -> None:
        """View DNS cache."""
        logger.info("User initiated DNS cache view")

        def task():
            try:
                cache_output = self.system_ops.view_dns_cache()
                
                # Create a dialog to show DNS cache
                self.parent.after(0, lambda: self._show_dns_cache_dialog(cache_output))
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Failed to view DNS cache: {error_msg}")
                self.parent.after(0, lambda: messagebox.showerror(
                    "Error", f"Failed to view DNS cache:\n{error_msg}"
                ))

        threading.Thread(target=task, daemon=True).start()

    def _show_dns_cache_dialog(self, cache_output: str) -> None:
        """Show DNS cache in a dialog."""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("DNS Cache")
        dialog.geometry("800x600")
        
        # Make dialog modal
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Title
        title = ctk.CTkLabel(
            dialog, 
            text="DNS Cache Contents", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(padx=10, pady=10)
        
        # Textbox for cache output
        text_box = ctk.CTkTextbox(dialog, wrap="word")
        text_box.pack(padx=10, pady=10, fill="both", expand=True)
        text_box.insert("1.0", cache_output)
        text_box.configure(state="disabled")
        
        # Close button
        ctk.CTkButton(
            dialog, 
            text="Close", 
            command=dialog.destroy,
            width=100
        ).pack(padx=10, pady=10)
