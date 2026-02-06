"""
Security tab for security scanning and monitoring.
"""

import customtkinter as ctk
from tkinter import messagebox
import threading

from src.utils.logger import get_logger
from src.core.security_scanner import SecurityScanner

logger = get_logger("security_tab")


class SecurityTab:
    """Security scanning and monitoring tab."""

    def __init__(self, parent: ctk.CTkFrame) -> None:
        """Initialize security tab."""
        self.parent = parent
        self.security_scanner = SecurityScanner()

        self.parent.grid_rowconfigure(1, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        self._create_header()
        self._create_content()

        logger.info("Security tab initialized")

    def _create_header(self) -> None:
        """Create header."""
        header_frame = ctk.CTkFrame(self.parent)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        title = ctk.CTkLabel(
            header_frame, text="Security Scanner", font=ctk.CTkFont(size=18, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    def _create_content(self) -> None:
        """Create content area."""
        content_frame = ctk.CTkScrollableFrame(self.parent)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)

        # Scan section
        self._create_scan_section(content_frame)

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

    def _create_results_section(self, parent: ctk.CTkFrame) -> None:
        """Create results display section."""
        results_frame = ctk.CTkFrame(parent)
        results_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        results_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            results_frame, text="Scan Results", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Results display
        self.results_text = ctk.CTkTextbox(results_frame, height=300)
        self.results_text.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.results_text.configure(state="disabled")
        self.results_text.insert("1.0", "No scan results yet. Click 'Run Vulnerability Scan' to start.")

    def _run_scan(self) -> None:
        """Run vulnerability scan."""
        logger.info("User initiated vulnerability scan")

        def task():
            try:
                self._update_results("Scanning for vulnerabilities...\n\n")

                vulnerabilities = self.security_scanner.scan_vulnerabilities()

                if not vulnerabilities:
                    result_text = "✓ No vulnerabilities detected!\n\nYour system appears to be secure."
                else:
                    result_text = f"Found {len(vulnerabilities)} potential issue(s):\n\n"

                    for i, vuln in enumerate(vulnerabilities, 1):
                        result_text += f"{i}. [{vuln.severity.value.upper()}] {vuln.name}\n"
                        result_text += f"   {vuln.description}\n"
                        result_text += f"   Recommendation: {vuln.recommendation}\n\n"

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

    def _update_results(self, text: str) -> None:
        """Update results display."""

        def update():
            self.results_text.configure(state="normal")
            self.results_text.delete("1.0", "end")
            self.results_text.insert("1.0", text)
            self.results_text.configure(state="disabled")

        self.parent.after(0, update)
