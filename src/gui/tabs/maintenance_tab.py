"""
Maintenance tab for system maintenance operations.

Provides access to system cleanup, DNS flush, restore points, and other maintenance tasks.
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
import subprocess
from typing import Tuple

from src.utils.logger import get_logger
from src.utils.admin_state import AdminState
from src.core.system_operations import SystemOperations
from src.core.restore_point_manager import RestorePointManager

logger = get_logger("maintenance_tab")

# Get CREATE_NO_WINDOW flag for Windows to prevent console flickering
# On Windows, this prevents subprocess from creating a visible console window
CREATE_NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


class MaintenanceTab:
    """System maintenance operations tab."""

    def __init__(self, parent: ctk.CTkFrame, main_window=None) -> None:
        """
        Initialize maintenance tab.

        Args:
            parent: Parent frame
        """
        self.parent = parent
        self.main_window = main_window
        self.system_ops = SystemOperations()
        
        # Initialize restore point manager with PowerShell executor
        self.restore_manager = RestorePointManager(
            execute_powershell_func=self._execute_powershell
        )
        
        # Thread-safe cancellation flag
        self.maintenance_cancelled = threading.Event()

        # Configure parent grid
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        # Create UI
        self._create_operations()
        
        # Set initial status
        if self.main_window:
            self.main_window.update_status("Ready")

        logger.info("Maintenance tab initialized")
    
    def _execute_powershell(self, command: str, timeout: int = 300) -> Tuple[bool, str, str]:
        """
        Execute a PowerShell command properly without double-wrapping.
        
        Args:
            command: PowerShell command to execute
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            # Build PowerShell command properly as a list
            ps_command = [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy", "Bypass",
                "-Command", command
            ]
            
            logger.debug(f"Executing PowerShell: {command[:100]}...")
            
            result = subprocess.run(
                ps_command,
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=CREATE_NO_WINDOW
            )
            
            success = result.returncode == 0
            stdout = result.stdout.strip() if result.stdout else ""
            stderr = result.stderr.strip() if result.stderr else ""
            
            if success:
                logger.debug("PowerShell command succeeded")
            else:
                logger.warning(f"PowerShell command failed with code {result.returncode}")
                if stderr:
                    logger.debug(f"Error output: {stderr[:200]}")
            
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            logger.error(f"PowerShell command timed out after {timeout}s")
            return False, "", f"Command timed out after {timeout} seconds"
            
        except Exception as e:
            logger.error(f"PowerShell execution failed: {e}")
            return False, "", str(e)

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
            dns_frame, text="DNS Operations", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        info = ctk.CTkLabel(
            dns_frame, text="DNS cache and configuration", font=ctk.CTkFont(size=11)
        )
        info.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        # Check admin status
        is_admin = AdminState.is_admin()

        # Flush DNS button (admin required)
        self.flush_dns_btn = ctk.CTkButton(
            dns_frame, 
            text="Flush DNS Cache", 
            command=self._flush_dns,
            state="normal" if is_admin else "disabled"
        )
        self.flush_dns_btn.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Edit hosts file button (admin required)
        self.edit_hosts_btn = ctk.CTkButton(
            dns_frame, 
            text="Edit Hosts File", 
            command=self._edit_hosts_file,
            state="normal" if is_admin else "disabled"
        )
        self.edit_hosts_btn.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Reset DNS to Google button (admin required)
        self.dns_google_btn = ctk.CTkButton(
            dns_frame, 
            text="DNS → Google (8.8.8.8)", 
            command=self._reset_dns_google,
            state="normal" if is_admin else "disabled"
        )
        self.dns_google_btn.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        # Reset DNS to Cloudflare button (admin required)
        self.dns_cloudflare_btn = ctk.CTkButton(
            dns_frame, 
            text="DNS → Cloudflare (1.1.1.1)", 
            command=self._reset_dns_cloudflare,
            state="normal" if is_admin else "disabled"
        )
        self.dns_cloudflare_btn.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

        # Reset DNS to Auto button (admin required)
        self.dns_auto_btn = ctk.CTkButton(
            dns_frame, 
            text="DNS → Auto (DHCP)", 
            command=self._reset_dns_auto,
            state="normal" if is_admin else "disabled"
        )
        self.dns_auto_btn.grid(row=6, column=0, padx=10, pady=5, sticky="ew")

        # View DNS cache button (doesn't require admin)
        ctk.CTkButton(
            dns_frame, text="View DNS Cache", command=self._view_dns_cache
        ).grid(row=7, column=0, padx=10, pady=5, sticky="ew")
        
        # Add admin warning if not admin
        if not is_admin:
            warning_label = ctk.CTkLabel(
                dns_frame,
                text="WARNING: Most DNS operations require Administrator",
                font=ctk.CTkFont(size=9),
                text_color="orange"
            )
            warning_label.grid(row=8, column=0, padx=10, pady=5, sticky="w")

    def _create_restore_point_section(self, parent: ctk.CTkFrame, row: int, column: int = 0) -> None:
        """Create restore point section."""
        restore_frame = ctk.CTkFrame(parent)
        restore_frame.grid(row=row, column=column, columnspan=3, sticky="nsew", padx=5, pady=5)
        restore_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            restore_frame, text="System Restore", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        info = ctk.CTkLabel(
            restore_frame,
            text="Create restore point before making changes (Requires Admin)",
            font=ctk.CTkFont(size=11),
        )
        info.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Last restore point info label
        self.restore_point_info_label = ctk.CTkLabel(
            restore_frame,
            text="Last restore point: Checking...",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.restore_point_info_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        # Check admin status
        is_admin = AdminState.is_admin()

        # Button frame for side-by-side buttons
        button_frame = ctk.CTkFrame(restore_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        
        self.create_restore_btn = ctk.CTkButton(
            button_frame, 
            text="Create Restore Point", 
            command=self._create_restore_point, 
            width=180,
            state="normal" if is_admin else "disabled"
        )
        self.create_restore_btn.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        self.restore_changes_btn = ctk.CTkButton(
            button_frame, 
            text="Restore Changes", 
            command=self._show_restore_dialog, 
            width=180,
            state="normal" if is_admin else "disabled"
        )
        self.restore_changes_btn.grid(row=0, column=1, padx=(0, 10), sticky="w")
        
        if not is_admin:
            warning_label = ctk.CTkLabel(
                restore_frame,
                text="WARNING: Administrator privileges required for restore operations",
                font=ctk.CTkFont(size=9),
                text_color="orange"
            )
            warning_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        
        # Refresh restore point info after UI is ready
        self.parent.after(100, self._refresh_restore_point_info)

    def _create_system_maintenance_section(self, parent: ctk.CTkFrame, row: int, column: int = 0) -> None:
        """Create system maintenance section."""
        maint_frame = ctk.CTkFrame(parent)
        maint_frame.grid(row=row, column=column, sticky="nsew", padx=5, pady=5)
        maint_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            maint_frame, text="System Maintenance", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        info = ctk.CTkLabel(
            maint_frame,
            text="Run comprehensive system maintenance (SFC, DISM) - Requires Admin",
            font=ctk.CTkFont(size=11),
        )
        info.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        # Check admin status
        is_admin = AdminState.is_admin()

        self.maintenance_button = ctk.CTkButton(
            maint_frame,
            text="Run Full Maintenance",
            command=self._run_maintenance,
            width=200,
            fg_color="#d9534f",
            hover_color="#c9302c",
            state="normal" if is_admin else "disabled"
        )
        self.maintenance_button.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        # Progress display
        self.maintenance_progress_label = ctk.CTkLabel(
            maint_frame, text="", font=ctk.CTkFont(size=11), text_color="gray"
        )
        self.maintenance_progress_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        if not is_admin:
            warning_label = ctk.CTkLabel(
                maint_frame,
                text="WARNING: Administrator privileges required",
                font=ctk.CTkFont(size=9),
                text_color="orange"
            )
            warning_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")

    def _create_disk_section(self, parent: ctk.CTkFrame, row: int, column: int = 0) -> None:
        """Create disk operations section."""
        disk_frame = ctk.CTkFrame(parent)
        disk_frame.grid(row=row, column=column, sticky="nsew", padx=5, pady=5)
        disk_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            disk_frame, text="Disk Health", font=ctk.CTkFont(size=14, weight="bold")
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
                error_msg = str(e)
                self.parent.after(0, lambda ex=error_msg: messagebox.showerror(
                    "Error", f"Failed to flush DNS: {ex}"
                ))

        threading.Thread(target=task, daemon=True).start()

    def _refresh_restore_point_info(self) -> None:
        """Refresh restore point information display."""
        def update_label(text):
            """Helper to update restore point info label."""
            self.restore_point_info_label.configure(text=text)
        
        def task():
            try:
                info = self.restore_manager.get_latest_restore_point_info()
                message = f"Last restore point: {info}"
                
                try:
                    self.parent.after(0, lambda m=message: update_label(m))
                except Exception as e:
                    logger.debug(f"GUI update timing issue (safe to ignore): {e}")
            except Exception as e:
                logger.error(f"Failed to refresh restore points: {e}")
                try:
                    self.parent.after(0, lambda: update_label("Failed to load restore points"))
                except Exception as ex:
                    logger.debug(f"GUI update timing issue (safe to ignore): {ex}")
        
        threading.Thread(target=task, daemon=True).start()

    def _create_restore_point(self) -> None:
        """Create system restore point with auto-generated name."""
        logger.info("User initiated restore point creation")

        def task():
            try:
                if not self.system_ops.is_admin():
                    self.parent.after(0, lambda: messagebox.showerror(
                        "Admin Required",
                        "Administrator privileges are required to create restore points.\n\n"
                        "Please restart the application as administrator."
                    ))
                    return

                # Create restore point with auto-generated timestamp name
                success, message = self.restore_manager.create_restore_point()
                
                if success:
                    self.parent.after(0, lambda: messagebox.showinfo(
                        "Success", "Restore point created successfully!"
                    ))
                    # Refresh the restore point info
                    self.parent.after(100, self._refresh_restore_point_info)
                else:
                    self.parent.after(0, lambda m=message: messagebox.showerror(
                        "Error", f"Failed to create restore point:\n{m}"
                    ))
            except Exception as e:
                logger.error(f"Restore point creation failed: {e}")
                error_msg = str(e)
                self.parent.after(0, lambda ex=error_msg: messagebox.showerror(
                    "Error", f"Failed to create restore point: {ex}"
                ))

        threading.Thread(target=task, daemon=True).start()

    def _show_restore_dialog(self) -> None:
        """Show dialog to select and restore from a restore point."""
        if not AdminState.is_admin():
            messagebox.showerror("Error", "Administrator privileges required for system restore")
            return
        
        logger.info("User initiated restore point selection")
        
        def task():
            try:
                # Get available restore points
                restore_points = self.restore_manager.get_restore_points()
                
                if not restore_points:
                    self.parent.after(0, lambda: messagebox.showwarning(
                        "No Restore Points", "No restore points available"
                    ))
                    return
                
                # Show dialog on main thread
                self.parent.after(0, lambda: self._display_restore_selection_dialog(restore_points))
                    
            except Exception as e:
                logger.error(f"Failed to get restore points: {e}")
                error_msg = str(e)
                self.parent.after(0, lambda ex=error_msg: messagebox.showerror(
                    "Error", f"Failed to get restore points:\n{ex}"
                ))
        
        threading.Thread(target=task, daemon=True).start()
    
    def _display_restore_selection_dialog(self, restore_points: list) -> None:
        """Display restore point selection dialog."""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Select Restore Point")
        dialog.geometry("700x500")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Title
        title = ctk.CTkLabel(
            dialog,
            text="Select a Restore Point",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(padx=10, pady=10)
        
        # Warning
        warning = ctk.CTkLabel(
            dialog,
            text="This will restore your system to a previous state.\nAll programs installed after the restore point will be removed.",
            font=ctk.CTkFont(size=11),
            text_color="orange"
        )
        warning.pack(padx=10, pady=5)
        
        # Scrollable frame for restore points
        scroll_frame = ctk.CTkScrollableFrame(dialog, width=650, height=300)
        scroll_frame.pack(padx=10, pady=10, fill="both", expand=True)
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Use list for simpler mutable storage
        selected_sequence = [None]
        # Shared radio button variable for proper grouping
        radio_var = ctk.StringVar(value="")
        
        # Create a radio button for each restore point
        for i, rp in enumerate(restore_points):
            sequence = rp.get('SequenceNumber', 0)
            description = rp.get('Description', 'Unknown')
            creation_time = self.restore_manager.format_creation_time(rp.get('CreationTime', ''))
            
            # Frame for each restore point
            rp_frame = ctk.CTkFrame(scroll_frame)
            rp_frame.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            rp_frame.grid_columnconfigure(1, weight=1)
            
            # Radio button - all share the same variable
            def select_restore_point(seq=sequence):
                selected_sequence[0] = seq
            
            radio = ctk.CTkRadioButton(
                rp_frame,
                text="",
                variable=radio_var,
                value=str(sequence),
                command=select_restore_point
            )
            radio.grid(row=0, column=0, rowspan=2, padx=5, pady=5)
            
            # Date/Time label
            date_label = ctk.CTkLabel(
                rp_frame,
                text=creation_time,
                font=ctk.CTkFont(size=12, weight="bold")
            )
            date_label.grid(row=0, column=1, padx=5, pady=(5, 0), sticky="w")
            
            # Description label
            desc_label = ctk.CTkLabel(
                rp_frame,
                text=description,
                font=ctk.CTkFont(size=11),
                text_color="gray"
            )
            desc_label.grid(row=1, column=1, padx=5, pady=(0, 5), sticky="w")
            
            # Auto-select the first (most recent) one
            if i == 0:
                radio.select()
                selected_sequence[0] = sequence
        
        # Button frame
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(padx=10, pady=10)
        
        def perform_restore():
            if selected_sequence[0] is None:
                messagebox.showwarning("No Selection", "Please select a restore point")
                return
            
            # Confirm
            confirm = messagebox.askyesno(
                "Confirm Restore",
                "Are you sure you want to restore your system?\n\n"
                "Your computer will restart automatically.",
                parent=dialog
            )
            
            if not confirm:
                return
            
            dialog.destroy()
            
            # Perform restore
            def restore_task():
                success, message = self.restore_manager.restore_system(selected_sequence[0])
                
                if success:
                    self.parent.after(0, lambda: messagebox.showinfo(
                        "System Restore", 
                        "System restore initiated.\nThe system will restart shortly."
                    ))
                else:
                    self.parent.after(0, lambda m=message: messagebox.showerror(
                        "Error", f"System restore failed:\n{m}"
                    ))
            
            threading.Thread(target=restore_task, daemon=True).start()
        
        # Restore button
        restore_btn = ctk.CTkButton(
            button_frame,
            text="Restore System",
            command=perform_restore,
            width=150,
            fg_color="#d9534f",
            hover_color="#c9302c"
        )
        restore_btn.grid(row=0, column=0, padx=5)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            width=150
        )
        cancel_btn.grid(row=0, column=1, padx=5)

    def _run_maintenance(self) -> None:
        """Run full system maintenance with real-time output."""
        response = messagebox.askyesno(
            "Confirm Maintenance",
            "This will run SFC and DISM system repairs.\n\n"
            "This may take 10-30 minutes and requires administrator privileges.\n\n"
            "Continue?",
        )

        if not response:
            return

        logger.info("User initiated full system maintenance")

        # Create output dialog
        output_dialog = ctk.CTkToplevel(self.parent)
        output_dialog.title("System Maintenance - Real-Time Output")
        output_dialog.geometry("900x650")
        output_dialog.transient(self.parent)
        output_dialog.grab_set()

        # Title
        title = ctk.CTkLabel(
            output_dialog,
            text="System Maintenance Progress",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(padx=10, pady=10)

        # Status label
        status_label = ctk.CTkLabel(
            output_dialog,
            text="Initializing...",
            font=ctk.CTkFont(size=12)
        )
        status_label.pack(padx=10, pady=5)

        # Output text area
        output_text = ctk.CTkTextbox(output_dialog, wrap="word", font=ctk.CTkFont(size=10))
        output_text.pack(padx=10, pady=10, fill="both", expand=True)

        # Cancel/Close button
        cancel_button = ctk.CTkButton(
            output_dialog,
            text="Cancel",
            command=lambda: self._cancel_maintenance(output_dialog),
            fg_color="#dc3545",
            hover_color="#c82333",
            width=100
        )
        cancel_button.pack(padx=10, pady=10)

        # Clear cancellation flag
        self.maintenance_cancelled.clear()

        def append_output(text: str):
            """Append text to output dialog."""
            output_text.insert("end", text)
            output_text.see("end")

        def update_status(text: str):
            """Update status label."""
            status_label.configure(text=text)

        def task():
            try:
                if not self.system_ops.is_admin():
                    output_dialog.after(0, lambda: append_output(
                        "[ERROR] Administrator privileges required\n"
                    ))
                    output_dialog.after(0, lambda: update_status("Failed - Admin required"))
                    output_dialog.after(0, lambda: cancel_button.configure(text="Close"))
                    return

                from datetime import datetime
                import subprocess

                # DNS Flush
                if not self.maintenance_cancelled.is_set():
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    output_dialog.after(0, lambda: append_output(
                        f"\n[{timestamp}] Starting DNS Cache Flush...\n"
                    ))
                    output_dialog.after(0, lambda: update_status("Flushing DNS cache..."))
                    
                    try:
                        result = subprocess.run(
                            ["ipconfig", "/flushdns"],
                            capture_output=True,
                            text=True,
                            timeout=30,
                            creationflags=CREATE_NO_WINDOW
                        )
                        output_dialog.after(0, lambda: append_output(result.stdout + "\n"))
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        output_dialog.after(0, lambda: append_output(
                            f"[{timestamp}] DNS cache flushed successfully.\n\n"
                        ))
                    except Exception as e:
                        error_msg = str(e)
                        output_dialog.after(0, lambda ex=error_msg: append_output(f"[ERROR] {ex}\n\n"))

                # System File Checker
                if not self.maintenance_cancelled.is_set():
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    output_dialog.after(0, lambda: append_output(
                        f"[{timestamp}] Starting System File Checker (sfc /scannow)...\n"
                        "This may take 10-15 minutes...\n\n"
                    ))
                    output_dialog.after(0, lambda: update_status("Running System File Checker..."))
                    
                    try:
                        process = subprocess.Popen(
                            ["sfc", "/scannow"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            bufsize=1,
                            universal_newlines=True,
                            creationflags=CREATE_NO_WINDOW
                        )
                        
                        # Read output line by line
                        for line in process.stdout:
                            if self.maintenance_cancelled.is_set():
                                process.terminate()
                                break
                            output_dialog.after(0, lambda l=line: append_output(l))
                        
                        process.wait()
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        
                        if process.returncode == 0:
                            output_dialog.after(0, lambda: append_output(
                                f"\n[{timestamp}] System File Checker completed successfully.\n\n"
                            ))
                        else:
                            output_dialog.after(0, lambda: append_output(
                                f"\n[{timestamp}] System File Checker completed with errors (code {process.returncode}).\n\n"
                            ))
                    except Exception as e:
                        error_msg = str(e)
                        output_dialog.after(0, lambda ex=error_msg: append_output(f"[ERROR] {ex}\n\n"))

                # DISM Health Check
                if not self.maintenance_cancelled.is_set():
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    output_dialog.after(0, lambda: append_output(
                        f"[{timestamp}] Starting DISM Health Restore...\n"
                        "This may take 15-20 minutes...\n\n"
                    ))
                    output_dialog.after(0, lambda: update_status("Running DISM Health Restore..."))
                    
                    try:
                        process = subprocess.Popen(
                            ["DISM", "/Online", "/Cleanup-Image", "/RestoreHealth"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            bufsize=1,
                            universal_newlines=True,
                            creationflags=CREATE_NO_WINDOW
                        )
                        
                        # Read output line by line
                        for line in process.stdout:
                            if self.maintenance_cancelled.is_set():
                                process.terminate()
                                break
                            output_dialog.after(0, lambda l=line: append_output(l))
                        
                        process.wait()
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        
                        if process.returncode == 0:
                            output_dialog.after(0, lambda: append_output(
                                f"\n[{timestamp}] DISM Health Restore completed successfully.\n\n"
                            ))
                        else:
                            output_dialog.after(0, lambda: append_output(
                                f"\n[{timestamp}] DISM completed with errors (code {process.returncode}).\n\n"
                            ))
                    except Exception as e:
                        error_msg = str(e)
                        output_dialog.after(0, lambda ex=error_msg: append_output(f"[ERROR] {ex}\n\n"))

                # Complete
                if not self.maintenance_cancelled.is_set():
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    output_dialog.after(0, lambda: append_output(
                        f"[{timestamp}] ====================================\n"
                        f"[{timestamp}] System Maintenance Complete!\n"
                        f"[{timestamp}] ====================================\n"
                    ))
                    output_dialog.after(0, lambda: update_status("Maintenance complete!"))
                else:
                    output_dialog.after(0, lambda: update_status("Maintenance cancelled"))
                
                output_dialog.after(0, lambda: cancel_button.configure(text="Close"))

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Maintenance failed: {error_msg}")
                output_dialog.after(0, lambda: append_output(f"\n[ERROR] {error_msg}\n"))
                output_dialog.after(0, lambda: update_status("Maintenance failed"))
                output_dialog.after(0, lambda: cancel_button.configure(text="Close"))

        threading.Thread(target=task, daemon=True).start()

    def _cancel_maintenance(self, dialog) -> None:
        """Cancel maintenance operation or close dialog."""
        if dialog.winfo_exists():
            self.maintenance_cancelled.set()
            dialog.destroy()

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
                error_msg = str(e)
                self.parent.after(0, lambda ex=error_msg: messagebox.showerror(
                    "Error", f"Failed to check disk health: {ex}"
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
