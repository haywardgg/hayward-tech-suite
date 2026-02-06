"""
Monitoring tab for system resource monitoring.

Displays real-time CPU, RAM, disk, battery, and network statistics.
"""

import customtkinter as ctk
from typing import Optional, Dict, Any

from src.utils.logger import get_logger
from src.core.monitoring import MonitoringService

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
        control_frame.grid_columnconfigure(0, weight=1)

    def _create_monitoring_displays(self) -> None:
        """Create monitoring display panels."""
        # Main content frame with scroll
        self.content_frame = ctk.CTkScrollableFrame(self.parent)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.content_frame.grid_columnconfigure((0, 1), weight=1)

        # CPU Display
        self._create_cpu_display()

        # RAM Display
        self._create_ram_display()

        # Disk Display
        self._create_disk_display()

        # Battery Display
        self._create_battery_display()

        # Network Display
        self._create_network_display()

    def _create_cpu_display(self) -> None:
        """Create CPU monitoring display."""
        cpu_frame = ctk.CTkFrame(self.content_frame)
        cpu_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        cpu_frame.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(cpu_frame, text="🖥️ CPU", font=ctk.CTkFont(size=16, weight="bold"))
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
        title = ctk.CTkLabel(ram_frame, text="💾 RAM", font=ctk.CTkFont(size=16, weight="bold"))
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
        disk_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        disk_frame.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(disk_frame, text="💿 Disk", font=ctk.CTkFont(size=16, weight="bold"))
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

        # Title
        title = ctk.CTkLabel(
            battery_frame, text="🔋 Battery", font=ctk.CTkFont(size=16, weight="bold")
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
        """Create network monitoring display."""
        network_frame = ctk.CTkFrame(self.content_frame)
        network_frame.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)
        network_frame.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(
            network_frame, text="🌐 Network", font=ctk.CTkFont(size=16, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Bytes sent
        self.net_sent_label = ctk.CTkLabel(
            network_frame, text="Sent: --- MB", font=ctk.CTkFont(size=12)
        )
        self.net_sent_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Bytes received
        self.net_recv_label = ctk.CTkLabel(
            network_frame, text="Received: --- MB", font=ctk.CTkFont(size=12)
        )
        self.net_recv_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        # Active interfaces
        self.net_interfaces_label = ctk.CTkLabel(
            network_frame, text="Active: ---", font=ctk.CTkFont(size=12)
        )
        self.net_interfaces_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

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
        """Update network display with new data."""
        if "error" in data:
            return

        bytes_sent = data.get("bytes_sent", 0) / (1024**2)  # Convert to MB
        bytes_recv = data.get("bytes_recv", 0) / (1024**2)
        interfaces = data.get("interfaces", [])
        active_count = sum(1 for iface in interfaces if iface.get("is_up", False))

        self.net_sent_label.configure(text=f"Sent: {bytes_sent:.2f} MB")
        self.net_recv_label.configure(text=f"Received: {bytes_recv:.2f} MB")
        self.net_interfaces_label.configure(text=f"Active: {active_count} interface(s)")
