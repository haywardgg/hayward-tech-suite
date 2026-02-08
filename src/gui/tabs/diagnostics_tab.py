"""
Diagnostics tab for network diagnostics and testing.

Provides network connectivity testing, latency analysis, DNS diagnostics,
and traceroute functionality.
"""

import customtkinter as ctk
from tkinter import messagebox
import threading

from src.utils.logger import get_logger
from src.core.network_diagnostics import NetworkDiagnostics, NetworkDiagnosticsError

logger = get_logger("diagnostics_tab")


class DiagnosticsTab:
    """Network diagnostics and testing tab."""

    def __init__(self, parent: ctk.CTkFrame, main_window=None) -> None:
        """Initialize diagnostics tab."""
        self.parent = parent
        self.main_window = main_window
        self.network_diag = NetworkDiagnostics()

        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        self._create_content()
        
        # Set initial status
        if self.main_window:
            self.main_window.update_status("Ready")

        logger.info("Diagnostics tab initialized")

    def _create_content(self) -> None:
        """Create content area."""
        content_frame = ctk.CTkScrollableFrame(self.parent)
        content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_columnconfigure((0, 1, 2), weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # Three diagnostic sections in columns on row 0
        self._create_ping_section(content_frame, row=0, column=0)
        self._create_dns_section(content_frame, row=0, column=1)
        self._create_traceroute_section(content_frame, row=0, column=2)

        # Results section spans full width on row 1
        self._create_results_section(content_frame)

    def _create_ping_section(self, parent: ctk.CTkFrame, row: int = 0, column: int = 0) -> None:
        """Create ping test section."""
        ping_frame = ctk.CTkFrame(parent)
        ping_frame.grid(row=row, column=column, sticky="nsew", padx=5, pady=5)
        ping_frame.grid_columnconfigure(0, weight=1)
        ping_frame.grid_columnconfigure(1, weight=0)

        title = ctk.CTkLabel(
            ping_frame, text="Ping Test", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Host and Count labels on row 1
        ctk.CTkLabel(ping_frame, text="Host:", font=ctk.CTkFont(size=11)).grid(
            row=1, column=0, padx=(10, 5), pady=5, sticky="w"
        )
        ctk.CTkLabel(ping_frame, text="Count:", font=ctk.CTkFont(size=11)).grid(
            row=1, column=1, padx=(5, 10), pady=5, sticky="w"
        )
        
        # Host and Count inputs on row 2 - same line
        self.ping_host_entry = ctk.CTkEntry(ping_frame, placeholder_text="8.8.8.8")
        self.ping_host_entry.grid(row=2, column=0, padx=(10, 5), pady=5, sticky="ew")
        self.ping_host_entry.insert(0, "8.8.8.8")

        self.ping_count_entry = ctk.CTkEntry(ping_frame, placeholder_text="10", width=80)
        self.ping_count_entry.grid(row=2, column=1, padx=(5, 10), pady=5, sticky="ew")
        self.ping_count_entry.insert(0, "10")

        # Ping button
        self.ping_button = ctk.CTkButton(
            ping_frame, text="Run Ping Test", command=self._run_ping_test
        )
        self.ping_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    def _create_dns_section(self, parent: ctk.CTkFrame, row: int = 0, column: int = 0) -> None:
        """Create DNS lookup section."""
        dns_frame = ctk.CTkFrame(parent)
        dns_frame.grid(row=row, column=column, sticky="nsew", padx=5, pady=5)
        dns_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            dns_frame, text="DNS Lookup", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Hostname input
        ctk.CTkLabel(dns_frame, text="Hostname:", font=ctk.CTkFont(size=11)).grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.dns_hostname_entry = ctk.CTkEntry(
            dns_frame, placeholder_text="www.google.com"
        )
        self.dns_hostname_entry.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.dns_hostname_entry.insert(0, "www.google.com")

        # DNS button
        self.dns_button = ctk.CTkButton(
            dns_frame, text="DNS Lookup", command=self._run_dns_lookup
        )
        self.dns_button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

    def _create_traceroute_section(self, parent: ctk.CTkFrame, row: int = 0, column: int = 0) -> None:
        """Create traceroute section."""
        trace_frame = ctk.CTkFrame(parent)
        trace_frame.grid(row=row, column=column, sticky="nsew", padx=5, pady=5)
        trace_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            trace_frame, text="Traceroute", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Host input
        ctk.CTkLabel(trace_frame, text="Host:", font=ctk.CTkFont(size=11)).grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.trace_host_entry = ctk.CTkEntry(
            trace_frame, placeholder_text="8.8.8.8"
        )
        self.trace_host_entry.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.trace_host_entry.insert(0, "8.8.8.8")

        # Traceroute button
        self.traceroute_button = ctk.CTkButton(
            trace_frame, text="Run Traceroute", command=self._run_traceroute
        )
        self.traceroute_button.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

    def _create_results_section(self, parent: ctk.CTkFrame) -> None:
        """Create results display section."""
        results_frame = ctk.CTkFrame(parent)
        results_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(
            results_frame, text="Test Results", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Results display
        self.results_text = ctk.CTkTextbox(results_frame, height=300)
        self.results_text.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.results_text.configure(state="normal")
        self.results_text.insert("1.0", "No test results yet. Run a diagnostic test to see results here.")
        self.results_text.configure(state="disabled")

    def _run_ping_test(self) -> None:
        """Run ping test."""
        host = self.ping_host_entry.get().strip()
        if not host:
            messagebox.showerror("Error", "Please enter a host to ping")
            return

        try:
            count = int(self.ping_count_entry.get().strip())
            if count < 1 or count > 100:
                messagebox.showerror("Error", "Count must be between 1 and 100")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid count value")
            return

        logger.info(f"User initiated ping test to {host}")

        # Disable button
        self.ping_button.configure(state="disabled", text="Running...")

        def task():
            try:
                self._update_results(f"Running ping test to {host}...\n\n")

                result = self.network_diag.ping_test(host, count=count)

                result_text = f"Ping Test Results for {host}\n"
                result_text += "=" * 50 + "\n\n"
                result_text += f"Packets Sent: {count}\n"
                result_text += f"Packet Loss: {result.packet_loss:.1f}%\n\n"
                result_text += f"Min Latency: {result.min_latency:.2f} ms\n"
                result_text += f"Max Latency: {result.max_latency:.2f} ms\n"
                result_text += f"Avg Latency: {result.avg_latency:.2f} ms\n"
                result_text += f"Median Latency: {result.median_latency:.2f} ms\n"
                result_text += f"Jitter: {result.jitter:.2f} ms\n\n"
                result_text += f"Connection Quality: {result.quality.value.upper()}\n"

                # Add quality indicator
                if result.quality.value == "excellent":
                    result_text += "\n✓ Excellent connection quality"
                elif result.quality.value == "good":
                    result_text += "\n✓ Good connection quality"
                elif result.quality.value == "fair":
                    result_text += "\n⚠️ Fair connection quality"
                elif result.quality.value == "poor":
                    result_text += "\n⚠️ Poor connection quality"
                else:
                    result_text += "\n❌ Critical connection issues"

                self._update_results(result_text)

            except NetworkDiagnosticsError as e:
                logger.error(f"Ping test failed: {e}")
                self._update_results(f"Ping test failed: {e}")
            except Exception as e:
                logger.error(f"Unexpected error during ping test: {e}")
                self._update_results(f"Unexpected error: {e}")
            finally:
                # Re-enable button
                self.parent.after(0, lambda: self.ping_button.configure(state="normal", text="Run Ping Test"))

        threading.Thread(target=task, daemon=True).start()

    def _run_dns_lookup(self) -> None:
        """Run DNS lookup."""
        hostname = self.dns_hostname_entry.get().strip()
        if not hostname:
            messagebox.showerror("Error", "Please enter a hostname")
            return

        logger.info(f"User initiated DNS lookup for {hostname}")

        # Disable button
        self.dns_button.configure(state="disabled", text="Looking up...")

        def task():
            try:
                self._update_results(f"Looking up DNS for {hostname}...\n\n")

                result = self.network_diag.dns_lookup(hostname)

                result_text = f"DNS Lookup Results for {hostname}\n"
                result_text += "=" * 50 + "\n\n"
                result_text += f"Resolution Time: {result.resolution_time:.2f} ms\n\n"
                result_text += "Resolved IP Addresses:\n"
                for ip in result.resolved_ips:
                    result_text += f"  • {ip}\n"
                
                if result.dns_servers:
                    result_text += "\nDNS Servers:\n"
                    for server in result.dns_servers:
                        result_text += f"  • {server}\n"

                if result.reverse_dns:
                    result_text += f"\nReverse DNS: {result.reverse_dns}\n"

                self._update_results(result_text)

            except NetworkDiagnosticsError as e:
                logger.error(f"DNS lookup failed: {e}")
                self._update_results(f"DNS lookup failed: {e}")
            except Exception as e:
                logger.error(f"Unexpected error during DNS lookup: {e}")
                self._update_results(f"Unexpected error: {e}")
            finally:
                # Re-enable button
                self.parent.after(0, lambda: self.dns_button.configure(state="normal", text="DNS Lookup"))

        threading.Thread(target=task, daemon=True).start()

    def _run_traceroute(self) -> None:
        """Run traceroute."""
        host = self.trace_host_entry.get().strip()
        if not host:
            messagebox.showerror("Error", "Please enter a host for traceroute")
            return

        logger.info(f"User initiated traceroute to {host}")

        # Disable button
        self.traceroute_button.configure(state="disabled", text="Tracing...")

        def task():
            try:
                self._update_results(f"Running traceroute to {host}...\n")
                self._update_results("This may take up to 30 seconds...\n\n")

                hops = self.network_diag.trace_route(host)

                result_text = f"Traceroute Results for {host}\n"
                result_text += "=" * 50 + "\n\n"

                if not hops:
                    result_text += "No hops recorded\n"
                else:
                    result_text += f"Total Hops: {len(hops)}\n\n"
                    for hop in hops:
                        hop_num = hop.get("hop", "?")
                        hostname = hop.get("hostname", "")
                        ip = hop.get("ip", "")
                        avg_latency = hop.get("avg_latency")

                        result_text += f"Hop {hop_num}: "
                        if hostname:
                            result_text += f"{hostname} "
                        if ip:
                            result_text += f"[{ip}] "
                        if avg_latency:
                            result_text += f"- {avg_latency:.1f} ms"
                        result_text += "\n"

                self._update_results(result_text)

            except NetworkDiagnosticsError as e:
                logger.error(f"Traceroute failed: {e}")
                self._update_results(f"Traceroute failed: {e}")
            except Exception as e:
                logger.error(f"Unexpected error during traceroute: {e}")
                self._update_results(f"Unexpected error: {e}")
            finally:
                # Re-enable button
                self.parent.after(0, lambda: self.traceroute_button.configure(state="normal", text="Run Traceroute"))

        threading.Thread(target=task, daemon=True).start()

    def _update_results(self, text: str) -> None:
        """Update results display."""

        def update():
            self.results_text.configure(state="normal")
            self.results_text.delete("1.0", "end")
            self.results_text.insert("1.0", text)
            self.results_text.configure(state="disabled")

        self.parent.after(0, update)
