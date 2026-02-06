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
        self.parent.grid_rowconfigure(1, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        # Create UI
        self._create_header()
        self._create_operations()

        logger.info("Maintenance tab initialized")

    def _create_header(self) -> None:
        """Create header section."""
        header_frame = ctk.CTkFrame(self.parent)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        title = ctk.CTkLabel(
            header_frame,
            text="System Maintenance",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Perform system maintenance and optimization tasks",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        subtitle.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="w")

    def _create_operations(self) -> None:
        """Create operation buttons and options."""
        # Scrollable content frame
        content_frame = ctk.CTkScrollableFrame(self.parent)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_columnconfigure((0, 1), weight=1)

        # DNS Operations
        self._create_dns_section(content_frame, row=0)

        # Restore Point Operations
        self._create_restore_point_section(content_frame, row=1)

        # System Maintenance
        self._create_system_maintenance_section(content_frame, row=2)

        # Disk Operations
        self._create_disk_section(content_frame, row=3)

    def _create_dns_section(self, parent: ctk.CTkFrame, row: int) -> None:
        """Create DNS operations section."""
        dns_frame = ctk.CTkFrame(parent)
        dns_frame.grid(row=row, column=0, sticky="nsew", padx=5, pady=5)
        dns_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            dns_frame, text="🌐 DNS Operations", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        info = ctk.CTkLabel(
            dns_frame, text="Clear DNS cache to resolve network issues", font=ctk.CTkFont(size=11)
        )
        info.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        btn = ctk.CTkButton(dns_frame, text="Flush DNS Cache", command=self._flush_dns, width=200)
        btn.grid(row=2, column=0, padx=10, pady=10, sticky="w")

    def _create_restore_point_section(self, parent: ctk.CTkFrame, row: int) -> None:
        """Create restore point section."""
        restore_frame = ctk.CTkFrame(parent)
        restore_frame.grid(row=row, column=1, sticky="nsew", padx=5, pady=5)
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

    def _create_system_maintenance_section(self, parent: ctk.CTkFrame, row: int) -> None:
        """Create system maintenance section."""
        maint_frame = ctk.CTkFrame(parent)
        maint_frame.grid(row=row, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
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

    def _create_disk_section(self, parent: ctk.CTkFrame, row: int) -> None:
        """Create disk operations section."""
        disk_frame = ctk.CTkFrame(parent)
        disk_frame.grid(row=row, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
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
