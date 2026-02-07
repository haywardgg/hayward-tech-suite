"""
Monitoring tab for system resource monitoring.

Displays real-time CPU, RAM, disk, battery, and network statistics.
"""

import customtkinter as ctk
from typing import Optional, Dict, Any

from src.utils.logger import get_logger
from src.core.monitoring import MonitoringService
from src.core.performance_profiler import PerformanceProfiler

logger = get_logger("monitoring_tab")


class MonitoringTab:
    """System monitoring tab with real-time resource display."""

    def __init__(self, parent: ctk.CTkFrame) -> None:
        """
        Initialize monitoring tab.

        Args:
            parent: Parent frame
        """
        self.parent = parent
        self.monitoring_service = MonitoringService()
        self.performance_profiler = PerformanceProfiler()
        self.is_monitoring = False

        # Configure parent grid
        self.parent.grid_rowconfigure(1, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)

        # Create UI
        self._create_control_panel()
        self._create_monitoring_displays()

        # Start monitoring automatically
        self.start_monitoring()

        logger.info("Monitoring tab initialized")

    def _create_control_panel(self) -> None:
        """Create control panel with start/stop buttons."""
        control_frame = ctk.CTkFrame(self.parent)
        control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        # Title
        title = ctk.CTkLabel(
            control_frame,
            text="System Monitoring",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Start/Stop button
        self.toggle_button = ctk.CTkButton(
            control_frame,
            text="Stop Monitoring",
            command=self.toggle_monitoring,
            width=150,
        )
        self.toggle_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        
        # Performance Profile button
        self.perf_profile_btn = ctk.CTkButton(
            control_frame,
            text="Run Performance Profile",
            command=self._run_performance_profile,
            width=200,
        )
        self.perf_profile_btn.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        
        control_frame.grid_columnconfigure(0, weight=1)

    def _create_monitoring_displays(self) -> None:
        """Create monitoring display panels in 2x3 grid layout."""
        # Main content frame without scroll - use regular frame
        self.content_frame = ctk.CTkFrame(self.parent)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.content_frame.grid_columnconfigure((0, 1), weight=1)
        self.content_frame.grid_rowconfigure((0, 1, 2), weight=1)

        # Row 0: CPU (left) and RAM (right)
        self._create_cpu_display()
        self._create_ram_display()

        # Row 1: Disk (left) and Network (right, first part)
        self._create_disk_display()
        self._create_network_display()

        # Row 2: Battery (left) and Network stats (right, second part continues)
        self._create_battery_display()

    def _create_cpu_display(self) -> None:
        """Create CPU monitoring display."""
        cpu_frame = ctk.CTkFrame(self.content_frame)
        cpu_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        cpu_frame.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(cpu_frame, text="CPU", font=ctk.CTkFont(size=16, weight="bold"))
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # CPU usage
        self.cpu_usage_label = ctk.CTkLabel(
            cpu_frame, text="Usage: ---%", font=ctk.CTkFont(size=14)
        )
        self.cpu_usage_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # CPU cores
        self.cpu_cores_label = ctk.CTkLabel(
            cpu_frame, text="Cores: ---", font=ctk.CTkFont(size=12)
        )
        self.cpu_cores_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # CPU frequency
        self.cpu_freq_label = ctk.CTkLabel(
            cpu_frame, text="Frequency: --- MHz", font=ctk.CTkFont(size=12)
        )
        self.cpu_freq_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        # Progress bar
        self.cpu_progress = ctk.CTkProgressBar(cpu_frame)
        self.cpu_progress.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        self.cpu_progress.set(0)

    def _create_ram_display(self) -> None:
        """Create RAM monitoring display."""
        ram_frame = ctk.CTkFrame(self.content_frame)
        ram_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        ram_frame.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(ram_frame, text="RAM", font=ctk.CTkFont(size=16, weight="bold"))
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # RAM usage
        self.ram_usage_label = ctk.CTkLabel(
            ram_frame, text="Usage: ---%", font=ctk.CTkFont(size=14)
        )
        self.ram_usage_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # RAM used/total
        self.ram_details_label = ctk.CTkLabel(
            ram_frame, text="--- GB / --- GB", font=ctk.CTkFont(size=12)
        )
        self.ram_details_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # Available
        self.ram_available_label = ctk.CTkLabel(
            ram_frame, text="Available: --- GB", font=ctk.CTkFont(size=12)
        )
        self.ram_available_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        # Progress bar
        self.ram_progress = ctk.CTkProgressBar(ram_frame)
        self.ram_progress.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        self.ram_progress.set(0)

    def _create_disk_display(self) -> None:
        """Create disk monitoring display."""
        disk_frame = ctk.CTkFrame(self.content_frame)
        disk_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        disk_frame.grid_columnconfigure(0, weight=1)

        # Title with proper spacing
        title = ctk.CTkLabel(disk_frame, text="💿  Disk", font=ctk.CTkFont(size=16, weight="bold"))
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Disk info text
        self.disk_info_text = ctk.CTkTextbox(disk_frame, height=100, wrap="word")
        self.disk_info_text.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.disk_info_text.insert("1.0", "Loading disk information...")
        self.disk_info_text.configure(state="disabled")

    def _create_battery_display(self) -> None:
        """Create battery monitoring display."""
        battery_frame = ctk.CTkFrame(self.content_frame)
        battery_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        battery_frame.grid_columnconfigure(0, weight=1)

        # Title with proper spacing
        title = ctk.CTkLabel(
            battery_frame, text="🔋  Battery", font=ctk.CTkFont(size=16, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Battery status
        self.battery_status_label = ctk.CTkLabel(
            battery_frame, text="Status: ---", font=ctk.CTkFont(size=14)
        )
        self.battery_status_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Battery level
        self.battery_level_label = ctk.CTkLabel(
            battery_frame, text="Level: ---%", font=ctk.CTkFont(size=12)
        )
        self.battery_level_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # Time remaining
        self.battery_time_label = ctk.CTkLabel(
            battery_frame, text="Time: ---", font=ctk.CTkFont(size=12)
        )
        self.battery_time_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        # Progress bar
        self.battery_progress = ctk.CTkProgressBar(battery_frame)
        self.battery_progress.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        self.battery_progress.set(0)

    def _create_network_display(self) -> None:
        """Create network monitoring display spanning two rows on the right."""
        network_frame = ctk.CTkFrame(self.content_frame)
        # Span rows 1 and 2, column 1 (right side)
        network_frame.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=5, pady=5)
        network_frame.grid_columnconfigure(0, weight=1)
        network_frame.grid_rowconfigure(1, weight=1)

        # Title
        title = ctk.CTkLabel(
            network_frame, text="Network", font=ctk.CTkFont(size=16, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Network details text box - now takes up more space, with parent's row weight for sizing
        self.net_details_text = ctk.CTkTextbox(network_frame, wrap="word", state="disabled", height=300)
        self.net_details_text.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

    def start_monitoring(self) -> None:
        """Start monitoring service."""
        if self.is_monitoring:
            return

        logger.info("Starting monitoring")
        
        # Register callbacks
        self.monitoring_service.register_callback("cpu", self._update_cpu_display)
        self.monitoring_service.register_callback("ram", self._update_ram_display)
        self.monitoring_service.register_callback("disk", self._update_disk_display)
        self.monitoring_service.register_callback("battery", self._update_battery_display)
        self.monitoring_service.register_callback("network", self._update_network_display)

        # Start monitoring
        self.monitoring_service.start()
        self.is_monitoring = True
        self.toggle_button.configure(text="Stop Monitoring")

    def stop_monitoring(self) -> None:
        """Stop monitoring service."""
        if not self.is_monitoring:
            return

        logger.info("Stopping monitoring")
        self.monitoring_service.stop()
        self.is_monitoring = False
        self.toggle_button.configure(text="Start Monitoring")

    def toggle_monitoring(self) -> None:
        """Toggle monitoring on/off."""
        if self.is_monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def _update_cpu_display(self, data: Dict[str, Any]) -> None:
        """Update CPU display with new data."""
        if "error" in data:
            return

        percent = data.get("percent", 0)
        physical_cores = data.get("physical_cores", 0)
        logical_cores = data.get("logical_cores", 0)
        freq = data.get("frequency", {}).get("current", 0)

        self.cpu_usage_label.configure(text=f"Usage: {percent:.1f}%")
        self.cpu_cores_label.configure(text=f"Cores: {physical_cores} physical, {logical_cores} logical")
        self.cpu_freq_label.configure(text=f"Frequency: {freq:.0f} MHz")
        self.cpu_progress.set(percent / 100)

    def _update_ram_display(self, data: Dict[str, Any]) -> None:
        """Update RAM display with new data."""
        if "error" in data:
            return

        percent = data.get("percent", 0)
        used_gb = data.get("used_gb", 0)
        total_gb = data.get("total_gb", 0)
        available_gb = data.get("available_gb", 0)

        self.ram_usage_label.configure(text=f"Usage: {percent:.1f}%")
        self.ram_details_label.configure(text=f"{used_gb:.1f} GB / {total_gb:.1f} GB")
        self.ram_available_label.configure(text=f"Available: {available_gb:.1f} GB")
        self.ram_progress.set(percent / 100)

    def _update_disk_display(self, data: Dict[str, Any]) -> None:
        """Update disk display with new data."""
        if "error" in data:
            return

        disks = data.get("disks", [])
        
        self.disk_info_text.configure(state="normal")
        self.disk_info_text.delete("1.0", "end")

        for disk in disks:
            device = disk.get("device", "Unknown")
            total_gb = disk.get("total_gb", 0)
            used_gb = disk.get("used_gb", 0)
            free_gb = disk.get("free_gb", 0)
            percent = disk.get("percent", 0)

            info = f"{device}: {used_gb:.1f} GB / {total_gb:.1f} GB ({percent:.1f}% used, {free_gb:.1f} GB free)\n"
            self.disk_info_text.insert("end", info)

        self.disk_info_text.configure(state="disabled")

    def _update_battery_display(self, data: Dict[str, Any]) -> None:
        """Update battery display with new data."""
        if "error" in data:
            return

        if not data.get("present", False):
            self.battery_status_label.configure(text="Status: No battery detected")
            return

        percent = data.get("percent", 0)
        power_plugged = data.get("power_plugged", False)
        time_left = data.get("time_left", "Unknown")

        status = "Charging" if power_plugged else "Discharging"
        self.battery_status_label.configure(text=f"Status: {status}")
        self.battery_level_label.configure(text=f"Level: {percent}%")
        self.battery_time_label.configure(text=f"Time: {time_left}")
        self.battery_progress.set(percent / 100)

    def _update_network_display(self, data: Dict[str, Any]) -> None:
        """Update network display with enhanced information."""
        if "error" in data:
            return

        bytes_sent = data.get("bytes_sent", 0) / (1024**2)  # Convert to MB
        bytes_recv = data.get("bytes_recv", 0) / (1024**2)
        interfaces = data.get("interfaces", [])
        
        # Build detailed network info text
        info_text = "Network Statistics:\n"
        info_text += f"  Sent: {bytes_sent:.2f} MB\n"
        info_text += f"  Received: {bytes_recv:.2f} MB\n\n"
        
        # Find active interface with details
        active_interface = None
        mac_address = None
        local_ip = None
        subnet_mask = None
        
        for iface in interfaces:
            if iface.get("is_up", False):
                active_interface = iface.get("name", "Unknown")
                # Extract MAC address and IP info
                for addr in iface.get("addresses", []):
                    addr_str = str(addr.get("family", ""))
                    address = addr.get("address", "")
                    
                    # MAC address (AddressFamily.AF_LINK or packet)
                    if "packet" in addr_str.lower() or "link" in addr_str.lower():
                        mac_address = address
                    # IPv4 address
                    elif "AF_INET" in addr_str and ":" not in address:
                        if not local_ip:  # Use first IPv4 found
                            local_ip = address
                            subnet_mask = addr.get("netmask", "N/A")
                
                if active_interface:
                    break  # Use first active interface
        
        # Get additional network details from data
        public_ip = data.get("public_ip", "Fetching...")
        default_gateway = data.get("default_gateway", "N/A")
        dns_servers = data.get("dns_servers", [])
        dhcp_enabled = data.get("dhcp_enabled", False)
        behind_nat = data.get("behind_nat", False)
        
        # Use local_ip from data if not found in interfaces
        if not local_ip:
            local_ip = data.get("local_ip", "N/A")
        
        info_text += "Active Interface:\n"
        if active_interface:
            info_text += f"  Name: {active_interface}\n"
            if mac_address:
                info_text += f"  MAC: {mac_address}\n"
            
            # Find speed for this interface
            for iface in interfaces:
                if iface.get("name") == active_interface:
                    speed = iface.get("speed", 0)
                    if speed > 0:
                        info_text += f"  Speed: {speed} Mbps\n"
                    info_text += f"  Status: Connected\n"
                    break
        else:
            info_text += "  No active interface detected\n"
        
        info_text += "\nIP Addressing:\n"
        info_text += f"  Local IP: {local_ip or 'N/A'}\n"
        info_text += f"  Public IP: {public_ip}\n"
        if subnet_mask and subnet_mask != "N/A":
            info_text += f"  Subnet Mask: {subnet_mask}\n"
        if default_gateway:
            info_text += f"  Gateway: {default_gateway}\n"
        
        info_text += "\nNetwork Configuration:\n"
        info_text += f"  DHCP: {'Enabled' if dhcp_enabled else 'Disabled/Unknown'}\n"
        
        if dns_servers:
            info_text += f"  DNS Servers:\n"
            for dns in dns_servers[:3]:  # Show max 3 DNS servers
                info_text += f"    - {dns}\n"
        else:
            info_text += f"  DNS Servers: N/A\n"
        
        info_text += f"  Network Type: {'Behind NAT' if behind_nat else 'Direct/Unknown'}\n"
        
        # Update the text box
        self.net_details_text.configure(state="normal")
        self.net_details_text.delete("1.0", "end")
        self.net_details_text.insert("1.0", info_text)
        self.net_details_text.configure(state="disabled")


    def _run_performance_profile(self) -> None:
        """Run comprehensive performance profile."""
        logger.info("User initiated performance profiling")

        import threading
        from tkinter import messagebox
        
        # Disable button and update text
        self.perf_profile_btn.configure(
            state="disabled",
            text="⏳ Please wait..."
        )

        def task():
            try:
                # Show progress dialog
                self.parent.after(0, lambda: messagebox.showinfo(
                    "Performance Profile",
                    "Running performance analysis...\nThis will take about 5-10 seconds."
                ))

                # Profile CPU
                cpu_profile = self.performance_profiler.profile_cpu(duration=5)

                # Profile memory
                mem_profile = self.performance_profiler.profile_memory()

                # Get top processes
                top_cpu_procs = self.performance_profiler.get_top_processes(sort_by='cpu', limit=5)
                top_mem_procs = self.performance_profiler.get_top_processes(sort_by='memory', limit=5)

                # Assess performance
                perf_level = self.performance_profiler.assess_performance()

                # Get bottlenecks
                bottlenecks = self.performance_profiler.get_system_bottlenecks()

                # Build report
                report = "=" * 60 + "\n"
                report += "PERFORMANCE PROFILE REPORT\n"
                report += "=" * 60 + "\n\n"

                report += f"Overall Performance: {perf_level.value.upper()}\n\n"

                # CPU section
                report += "CPU Performance:\n"
                report += f"  Average Usage: {cpu_profile.average_usage:.1f}%\n"
                report += f"  Current Usage: {cpu_profile.current_usage:.1f}%\n"
                report += f"  Cores: {cpu_profile.core_count} physical, {cpu_profile.thread_count} logical\n"
                if cpu_profile.frequency_current:
                    report += f"  Frequency: {cpu_profile.frequency_current:.0f} MHz (Max: {cpu_profile.frequency_max:.0f} MHz)\n"
                report += "\n"

                # Memory section
                report += "Memory Usage:\n"
                report += f"  Used: {mem_profile.used / (1024**3):.2f} GB / {mem_profile.total / (1024**3):.2f} GB ({mem_profile.percent_used:.1f}%)\n"
                report += f"  Available: {mem_profile.available / (1024**3):.2f} GB\n"
                if mem_profile.swap_total > 0:
                    report += f"  Swap: {mem_profile.swap_used / (1024**3):.2f} GB / {mem_profile.swap_total / (1024**3):.2f} GB ({mem_profile.swap_percent:.1f}%)\n"
                report += "\n"

                # Top CPU processes
                report += "Top CPU Consumers:\n"
                for proc in top_cpu_procs:
                    report += f"  • {proc.name} (PID {proc.pid}): {proc.cpu_percent:.1f}% CPU\n"
                report += "\n"

                # Top memory processes
                report += "Top Memory Consumers:\n"
                for proc in top_mem_procs:
                    report += f"  • {proc.name} (PID {proc.pid}): {proc.memory_mb:.0f} MB ({proc.memory_percent:.1f}%)\n"
                report += "\n"

                # Bottlenecks
                if bottlenecks:
                    report += f"Detected Bottlenecks ({len(bottlenecks)}):\n"
                    for bottleneck in bottlenecks:
                        severity = bottleneck['severity'].upper()
                        component = bottleneck['component']
                        description = bottleneck['description']
                        recommendation = bottleneck['recommendation']
                        report += f"  [{severity}] {component}\n"
                        report += f"    Issue: {description}\n"
                        report += f"    Action: {recommendation}\n\n"
                else:
                    report += "✓ No performance bottlenecks detected\n"

                # Show report in a new window
                def show_report():
                    report_window = ctk.CTkToplevel(self.parent)
                    report_window.title("Performance Profile Report")
                    report_window.geometry("800x600")

                    # Report text
                    text_widget = ctk.CTkTextbox(report_window)
                    text_widget.pack(fill="both", expand=True, padx=10, pady=10)
                    text_widget.insert("1.0", report)
                    text_widget.configure(state="disabled")

                    # Close button
                    ctk.CTkButton(
                        report_window,
                        text="Close",
                        command=report_window.destroy,
                        width=100
                    ).pack(pady=10)

                self.parent.after(0, show_report)
                logger.info("Performance profile completed successfully")
                
                # Re-enable button
                self.parent.after(0, self._reset_performance_button)

            except Exception as e:
                logger.error(f"Performance profiling failed: {e}")
                self.parent.after(0, lambda: messagebox.showerror(
                    "Error",
                    f"Performance profiling failed:\n{str(e)}"
                ))
                
                # Re-enable button even on error
                self.parent.after(0, self._reset_performance_button)

        threading.Thread(target=task, daemon=True).start()
    
    def _reset_performance_button(self) -> None:
        """Reset performance profile button to normal state."""
        self.perf_profile_btn.configure(
            state="normal",
            text="Run Performance Profile"
        )
