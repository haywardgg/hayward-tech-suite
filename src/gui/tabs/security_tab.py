"""
Security tab for security scanning and monitoring.
"""

import customtkinter as ctk
from tkinter import messagebox
import threading

from src.utils.logger import get_logger
from src.core.security_scanner import SecurityScanner
from src.core.automated_remediation import AutomatedRemediation, RemediationStatus

logger = get_logger("security_tab")


class SecurityTab:
    """Security scanning and monitoring tab."""

    def __init__(self, parent: ctk.CTkFrame) -> None:
        """Initialize security tab."""
        self.parent = parent
        self.security_scanner = SecurityScanner()
        self.remediation = AutomatedRemediation()
        self.last_vulnerabilities = []
        
        # Button references for dynamic state updates
        self.defender_button = None
        self.firewall_button = None

        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        self._create_content()

        logger.info("Security tab initialized")

    def _create_content(self) -> None:
        """Create content area."""
        content_frame = ctk.CTkScrollableFrame(self.parent)
        content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)

        # Scan section
        self._create_scan_section(content_frame)

        # Remediation section
        self._create_remediation_section(content_frame)

        # Results section
        self._create_results_section(content_frame)

    def _create_scan_section(self, parent: ctk.CTkFrame) -> None:
        """Create scan control section."""
        scan_frame = ctk.CTkFrame(parent)
        scan_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        scan_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            scan_frame, text="Vulnerability Scan", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        info = ctk.CTkLabel(
            scan_frame,
            text="Scan for common security vulnerabilities and misconfigurations",
            font=ctk.CTkFont(size=11),
        )
        info.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        btn_frame = ctk.CTkFrame(scan_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        ctk.CTkButton(btn_frame, text="Run Vulnerability Scan", command=self._run_scan, width=200).grid(
            row=0, column=0, padx=5
        )
        ctk.CTkButton(btn_frame, text="Check Firewall", command=self._check_firewall, width=200).grid(
            row=0, column=1, padx=5
        )

    def _create_remediation_section(self, parent: ctk.CTkFrame) -> None:
        """Create automated remediation section."""
        remediation_frame = ctk.CTkFrame(parent)
        remediation_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        remediation_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            remediation_frame, text="Automated Remediation", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        info = ctk.CTkLabel(
            remediation_frame,
            text="Automatically fix detected security issues with one click",
            font=ctk.CTkFont(size=11),
        )
        info.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        btn_frame = ctk.CTkFrame(remediation_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        ctk.CTkButton(
            btn_frame, text="Run Available Fixes", command=self._run_all_fixes, width=180
        ).grid(row=0, column=0, padx=5)

        # Check defender status and create dynamic button
        # Wrap in try/except to prevent startup failures
        # Default to False (disabled state) to show enable option when status is uncertain
        try:
            defender_enabled = self._check_defender_status()
        except Exception as e:
            logger.warning(f"Failed to check initial defender status: {e}")
            defender_enabled = False
        
        defender_text = "Disable Defender" if defender_enabled else "Enable Defender"
        self.defender_button = ctk.CTkButton(
            btn_frame, text=defender_text, command=self._toggle_defender, width=150
        )
        self.defender_button.grid(row=0, column=1, padx=5)

        # Check firewall status and create dynamic button
        # Wrap in try/except to prevent startup failures
        # Default to False (disabled state) to show enable option when status is uncertain
        try:
            firewall_enabled = self._check_firewall_enabled()
        except Exception as e:
            logger.warning(f"Failed to check initial firewall status: {e}")
            firewall_enabled = False
        
        firewall_text = "Disable Firewall" if firewall_enabled else "Enable Firewall"
        self.firewall_button = ctk.CTkButton(
            btn_frame, text=firewall_text, command=self._toggle_firewall, width=150
        )
        self.firewall_button.grid(row=0, column=2, padx=5)

        ctk.CTkButton(
            btn_frame, text="Flush DNS", command=lambda: self._execute_remediation("flush_dns"), width=120
        ).grid(row=0, column=3, padx=5)

    def _create_results_section(self, parent: ctk.CTkFrame) -> None:
        """Create results display section."""
        results_frame = ctk.CTkFrame(parent)
        results_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        results_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            results_frame, text="Real-Time Output", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Results display
        self.results_text = ctk.CTkTextbox(results_frame, height=300)
        self.results_text.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.results_text.configure(state="disabled")
        self.results_text.insert("1.0", "No scan results yet. Click 'Run Vulnerability Scan' to start.")

    def _run_scan(self) -> None:
        """Run vulnerability scan with real-time output."""
        logger.info("User initiated vulnerability scan")

        def task():
            try:
                result_text = "Scanning for vulnerabilities...\n"
                result_text += "=" * 50 + "\n\n"
                self._update_results(result_text)

                # Check Windows Defender
                result_text += f"{self._format_timestamp()} Checking Windows Defender status...\n"
                self._update_results(result_text)
                
                defender_vuln = self.security_scanner._check_windows_defender()
                if defender_vuln:
                    result_text += f"{self._format_timestamp()} ⚠️ Windows Defender: ISSUE DETECTED\n\n"
                else:
                    result_text += f"{self._format_timestamp()} ✓ Windows Defender: ENABLED\n\n"
                self._update_results(result_text)

                # Check Windows Firewall
                result_text += f"{self._format_timestamp()} Checking Windows Firewall...\n"
                self._update_results(result_text)
                
                firewall_vuln = self.security_scanner._check_firewall_basic()
                if firewall_vuln:
                    result_text += f"{self._format_timestamp()} ⚠️ Firewall: DISABLED\n\n"
                else:
                    result_text += f"{self._format_timestamp()} ✓ Firewall: ENABLED\n\n"
                self._update_results(result_text)

                # Check for pending Windows updates
                result_text += f"{self._format_timestamp()} Checking for pending Windows updates...\n"
                self._update_results(result_text)
                
                update_vuln = self.security_scanner._check_windows_updates()
                if update_vuln:
                    update_count = update_vuln.details.get('pending_count', 0)
                    result_text += f"{self._format_timestamp()} ⚠️ Found {update_count} pending update(s)\n\n"
                else:
                    result_text += f"{self._format_timestamp()} ✓ Windows Updates: UP TO DATE\n\n"
                self._update_results(result_text)

                # Check UAC status
                result_text += f"{self._format_timestamp()} Checking UAC status...\n"
                self._update_results(result_text)
                
                uac_vuln = self.security_scanner._check_uac()
                if uac_vuln:
                    result_text += f"{self._format_timestamp()} ⚠️ UAC: DISABLED\n\n"
                else:
                    result_text += f"{self._format_timestamp()} ✓ UAC: ENABLED\n\n"
                self._update_results(result_text)

                # Check SMBv1 status
                result_text += f"{self._format_timestamp()} Checking SMBv1 status...\n"
                self._update_results(result_text)
                
                smb_vuln = self.security_scanner._check_smbv1()
                if smb_vuln:
                    result_text += f"{self._format_timestamp()} ⚠️ SMBv1: ENABLED (Security Risk)\n\n"
                else:
                    result_text += f"{self._format_timestamp()} ✓ SMBv1: DISABLED\n\n"
                self._update_results(result_text)

                # Check network shares
                result_text += f"{self._format_timestamp()} Checking network shares...\n"
                self._update_results(result_text)
                
                shares_vuln = self.security_scanner._check_network_shares()
                if shares_vuln:
                    result_text += f"{self._format_timestamp()} ⚠️ Network Shares: DETECTED\n\n"
                else:
                    result_text += f"{self._format_timestamp()} ✓ Network Shares: NONE\n\n"
                self._update_results(result_text)

                # Collect all vulnerabilities
                vulnerabilities = []
                if defender_vuln:
                    vulnerabilities.append(defender_vuln)
                if firewall_vuln:
                    vulnerabilities.append(firewall_vuln)
                if update_vuln:
                    vulnerabilities.append(update_vuln)
                if uac_vuln:
                    vulnerabilities.append(uac_vuln)
                if smb_vuln:
                    vulnerabilities.append(smb_vuln)
                if shares_vuln:
                    vulnerabilities.append(shares_vuln)
                    
                self.last_vulnerabilities = vulnerabilities

                # Summary
                result_text += "=" * 50 + "\n"
                result_text += f"SCAN COMPLETE: Found {len(vulnerabilities)} potential issue(s)\n"
                
                if not vulnerabilities:
                    result_text += "\n✓ No vulnerabilities detected!\nYour system appears to be secure.\n"
                else:
                    result_text += "\n"
                    for i, vuln in enumerate(vulnerabilities, 1):
                        result_text += f"{i}. [{vuln.severity.value.upper()}] {vuln.name}\n"
                        result_text += f"   {vuln.description}\n"
                        result_text += f"   Recommendation: {vuln.recommendation}\n\n"

                    # Show remediation suggestions
                    available_actions = self.remediation.get_available_actions(vulnerabilities)
                    if available_actions:
                        result_text += f"✓ {len(available_actions)} automated fix(es) available\n"
                        result_text += "Click 'Run Available Fixes' to automatically apply all fixes.\n"

                self._update_results(result_text)

            except Exception as e:
                logger.error(f"Vulnerability scan failed: {e}")
                self._update_results(f"Scan failed: {e}")

        threading.Thread(target=task, daemon=True).start()

    def _check_firewall(self) -> None:
        """Check firewall status."""
        logger.info("User initiated firewall check")

        def task():
            try:
                self._update_results("Checking firewall status...\n\n")

                firewall = self.security_scanner.check_firewall_status()

                result_text = "Firewall Status:\n\n"
                result_text += f"Enabled: {'Yes' if firewall.enabled else 'No'}\n"
                result_text += f"Profile: {firewall.profile}\n"
                result_text += f"Inbound Rules: {firewall.inbound_rules}\n"
                result_text += f"Outbound Rules: {firewall.outbound_rules}\n"

                if not firewall.enabled:
                    result_text += "\n⚠️ WARNING: Firewall is disabled! Your system is vulnerable.\n"

                self._update_results(result_text)

            except Exception as e:
                logger.error(f"Firewall check failed: {e}")
                self._update_results(f"Firewall check failed: {e}")

        threading.Thread(target=task, daemon=True).start()

    def _view_remediation_actions(self) -> None:
        """View available remediation actions in interactive dialog."""
        logger.info("User viewing remediation actions")
        
        # Import here to avoid circular imports
        from src.gui.dialogs import RemediationDialog
        
        # Open interactive dialog
        dialog = RemediationDialog(
            parent=self.parent.winfo_toplevel(),
            remediation=self.remediation,
            vulnerabilities=self.last_vulnerabilities
        )
        dialog.focus()

    def _execute_remediation(self, action_id: str) -> None:
        """Execute a remediation action."""
        logger.info(f"User requested remediation: {action_id}")

        # Get action details
        actions = self.remediation.REMEDIATION_ACTIONS
        if action_id not in actions:
            messagebox.showerror("Error", f"Unknown remediation action: {action_id}")
            return

        action = actions[action_id]

        # Confirm with user
        confirm_msg = f"Execute: {action.name}\n\n"
        confirm_msg += f"{action.description}\n\n"
        confirm_msg += f"Risk Level: {action.risk_level.upper()}\n"
        confirm_msg += f"Requires Admin: {'Yes' if action.requires_admin else 'No'}\n\n"
        confirm_msg += "Do you want to proceed?"

        if not messagebox.askyesno("Confirm Remediation", confirm_msg):
            logger.info("User cancelled remediation")
            return

        def task():
            try:
                self._update_results(f"Executing: {action.name}...\n\n")

                result = self.remediation.execute_remediation(action_id, dry_run=False)

                result_text = f"Remediation: {action.name}\n"
                result_text += "=" * 50 + "\n\n"
                result_text += f"Status: {result.status.value.upper()}\n"
                result_text += f"Message: {result.message}\n"

                if result.output:
                    result_text += f"\nOutput:\n{result.output}\n"

                if result.error:
                    result_text += f"\nError:\n{result.error}\n"

                if result.status == RemediationStatus.SUCCESS:
                    result_text += "\n✓ Remediation completed successfully!"
                    messagebox.showinfo("Success", f"{action.name} completed successfully!")
                else:
                    result_text += "\n❌ Remediation failed!"
                    messagebox.showerror("Failed", f"{action.name} failed. Check the output for details.")

                self._update_results(result_text)

            except Exception as e:
                logger.error(f"Remediation execution failed: {e}")
                error_text = f"Failed to execute {action.name}\n\n"
                error_text += f"Error: {str(e)}\n"
                self._update_results(error_text)
                messagebox.showerror("Error", f"Remediation failed: {e}")

        threading.Thread(target=task, daemon=True).start()

    def _check_defender_status(self) -> bool:
        """
        Check if Windows Defender is currently enabled.
        
        Returns:
            True if Defender is enabled, False otherwise
        """
        try:
            from src.core.system_operations import SystemOperations
            sys_ops = SystemOperations()
            success, stdout, stderr = sys_ops.execute_command(
                'powershell -Command "Get-MpComputerStatus | Select-Object -ExpandProperty AntivirusEnabled"',
                shell=True,
                audit=False,
            )
            if success and "True" in stdout:
                return True
        except Exception as e:
            logger.warning(f"Failed to check Defender status: {e}")
        return False

    def _check_firewall_enabled(self) -> bool:
        """
        Check if Windows Firewall is currently enabled.
        
        Returns:
            True if Firewall is enabled, False otherwise
        """
        try:
            firewall_status = self.security_scanner.check_firewall_status()
            return firewall_status.enabled
        except Exception as e:
            logger.warning(f"Failed to check Firewall status: {e}")
        return False

    def _toggle_defender(self) -> None:
        """Toggle Windows Defender on/off."""
        defender_enabled = self._check_defender_status()
        if defender_enabled:
            # Defender is on, so disable it
            self._execute_remediation("disable_defender")
        else:
            # Defender is off, so enable it
            self._execute_remediation("enable_defender")
        
        # Update button text after toggle
        self.parent.after(1000, self._update_button_states)

    def _toggle_firewall(self) -> None:
        """Toggle Windows Firewall on/off."""
        firewall_enabled = self._check_firewall_enabled()
        if firewall_enabled:
            # Firewall is on, so disable it
            self._execute_remediation("disable_firewall")
        else:
            # Firewall is off, so enable it
            self._execute_remediation("enable_firewall")
        
        # Update button text after toggle
        self.parent.after(1000, self._update_button_states)

    def _update_button_states(self) -> None:
        """Update button text to reflect current system state."""
        if self.defender_button:
            defender_enabled = self._check_defender_status()
            defender_text = "Disable Defender" if defender_enabled else "Enable Defender"
            self.defender_button.configure(text=defender_text)
        
        if self.firewall_button:
            firewall_enabled = self._check_firewall_enabled()
            firewall_text = "Disable Firewall" if firewall_enabled else "Enable Firewall"
            self.firewall_button.configure(text=firewall_text)

    def _run_all_fixes(self) -> None:
        """Run all available automated fixes with enhanced real-time output."""
        logger.info("User requested to run all available fixes")
        
        def task():
            try:
                result_text = "Running all available fixes...\n"
                result_text += "=" * 50 + "\n\n"
                self._update_results(result_text)
                
                # Get available actions based on last scan
                available_actions = self.remediation.get_available_actions(self.last_vulnerabilities)
                
                if not available_actions:
                    result_text += "No fixes available. Run a vulnerability scan first.\n"
                    self._update_results(result_text)
                    return
                
                result_text += f"Found {len(available_actions)} fix(es) to apply\n\n"
                self._update_results(result_text)
                
                success_count = 0
                fail_count = 0
                
                for action in available_actions:
                    # Extract the action ID from the RemediationAction object
                    action_id = action.id
                    
                    result_text += f"{self._format_timestamp()} Running: {action.name}\n"
                    result_text += f"{self._format_timestamp()} Executing: {action.command}\n"
                    self._update_results(result_text)
                    
                    try:
                        result = self.remediation.execute_remediation(action_id, dry_run=False)
                        
                        # Show command output if available
                        if result.output and result.output.strip():
                            result_text += f"{self._format_timestamp()} Output:\n"
                            # Indent output for readability
                            for line in result.output.strip().split('\n'):
                                result_text += f"  {line}\n"
                        
                        if result.status == RemediationStatus.SUCCESS:
                            result_text += f"{self._format_timestamp()} ✓ SUCCESS: {action.name}\n"
                            result_text += f"  {result.message}\n"
                            success_count += 1
                        else:
                            result_text += f"{self._format_timestamp()} ❌ FAILED: {action.name}\n"
                            result_text += f"  {result.message}\n"
                            if result.error:
                                result_text += f"  Error: {result.error}\n"
                            fail_count += 1
                        
                        result_text += "\n"
                        self._update_results(result_text)
                        
                    except Exception as e:
                        result_text += f"{self._format_timestamp()} ❌ ERROR: {action.name}\n"
                        result_text += f"  {str(e)}\n\n"
                        fail_count += 1
                        self._update_results(result_text)
                
                # Summary
                result_text += "=" * 50 + "\n"
                result_text += f"SUMMARY: {success_count} succeeded, {fail_count} failed\n"
                self._update_results(result_text)
                
                if fail_count == 0:
                    messagebox.showinfo("Success", f"All {success_count} fix(es) applied successfully!")
                else:
                    messagebox.showwarning("Partial Success", f"{success_count} fix(es) succeeded, {fail_count} failed. Check output for details.")
                
            except Exception as e:
                logger.error(f"Failed to run all fixes: {e}")
                error_text = f"Failed to run fixes\n\nError: {str(e)}\n"
                self._update_results(error_text)
                messagebox.showerror("Error", f"Failed to run fixes: {e}")
        
        threading.Thread(target=task, daemon=True).start()

    def _update_results(self, text: str) -> None:
        """Update results display."""

        def update():
            self.results_text.configure(state="normal")
            self.results_text.delete("1.0", "end")
            self.results_text.insert("1.0", text)
            self.results_text.configure(state="disabled")

        self.parent.after(0, update)

    def _format_timestamp(self) -> str:
        """Format current time as [HH:MM:SS]."""
        from datetime import datetime
        return datetime.now().strftime("[%H:%M:%S]")
