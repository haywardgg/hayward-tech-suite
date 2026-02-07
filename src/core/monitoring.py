"""
System monitoring module for Ghosty Toolz Evolved.

Provides real-time monitoring of system resources including CPU, RAM, disk, battery, and network.
"""

import psutil
import threading
import time
from typing import Optional, Dict, Any, Callable
from datetime import datetime

from src.utils.logger import get_logger
from src.utils.config import get_config

logger = get_logger("monitoring")
config = get_config()


class MonitoringService:
    """Real-time system monitoring service with configurable intervals."""

    def __init__(self) -> None:
        """Initialize monitoring service."""
        self.cpu_interval = config.get("monitoring.cpu_interval", 2)
        self.ram_interval = config.get("monitoring.ram_interval", 2)
        self.disk_interval = config.get("monitoring.disk_check_interval", 60)
        self.network_interval = config.get("monitoring.network_interval", 5)
        self.battery_interval = config.get("monitoring.battery_interval", 10)

        self._monitoring_active = False
        self._threads: Dict[str, threading.Thread] = {}
        self._callbacks: Dict[str, Callable] = {}
        self._stop_event = threading.Event()

        logger.info("Monitoring service initialized")

    def start(self) -> None:
        """Start all monitoring threads."""
        if self._monitoring_active:
            logger.warning("Monitoring already active")
            return

        self._monitoring_active = True
        self._stop_event.clear()

        logger.info("Starting monitoring service")

        # Start monitoring threads
        self._start_cpu_monitor()
        self._start_ram_monitor()
        self._start_disk_monitor()
        self._start_network_monitor()
        self._start_battery_monitor()

        logger.info("All monitoring threads started")

    def stop(self) -> None:
        """Stop all monitoring threads."""
        if not self._monitoring_active:
            logger.warning("Monitoring not active")
            return

        logger.info("Stopping monitoring service")

        self._monitoring_active = False
        self._stop_event.set()

        # Wait for all threads to finish
        for name, thread in self._threads.items():
            if thread.is_alive():
                logger.debug(f"Waiting for {name} thread to stop...")
                thread.join(timeout=5)

        self._threads.clear()
        logger.info("Monitoring service stopped")

    def register_callback(self, monitor_type: str, callback: Callable) -> None:
        """
        Register a callback function for specific monitor type.

        Args:
            monitor_type: Type of monitor ('cpu', 'ram', 'disk', 'network', 'battery')
            callback: Function to call with monitoring data
        """
        self._callbacks[monitor_type] = callback
        logger.debug(f"Registered callback for {monitor_type} monitor")

    def _start_cpu_monitor(self) -> None:
        """Start CPU monitoring thread."""

        def monitor():
            logger.debug("CPU monitor thread started")
            while self._monitoring_active and not self._stop_event.is_set():
                try:
                    data = self.get_cpu_info()
                    if "cpu" in self._callbacks:
                        self._callbacks["cpu"](data)
                except Exception as e:
                    logger.error(f"CPU monitor error: {e}")

                self._stop_event.wait(self.cpu_interval)

            logger.debug("CPU monitor thread stopped")

        thread = threading.Thread(target=monitor, daemon=True, name="CPUMonitor")
        thread.start()
        self._threads["cpu"] = thread

    def _start_ram_monitor(self) -> None:
        """Start RAM monitoring thread."""

        def monitor():
            logger.debug("RAM monitor thread started")
            while self._monitoring_active and not self._stop_event.is_set():
                try:
                    data = self.get_ram_info()
                    if "ram" in self._callbacks:
                        self._callbacks["ram"](data)
                except Exception as e:
                    logger.error(f"RAM monitor error: {e}")

                self._stop_event.wait(self.ram_interval)

            logger.debug("RAM monitor thread stopped")

        thread = threading.Thread(target=monitor, daemon=True, name="RAMMonitor")
        thread.start()
        self._threads["ram"] = thread

    def _start_disk_monitor(self) -> None:
        """Start disk monitoring thread."""

        def monitor():
            logger.debug("Disk monitor thread started")
            while self._monitoring_active and not self._stop_event.is_set():
                try:
                    data = self.get_disk_info()
                    if "disk" in self._callbacks:
                        self._callbacks["disk"](data)
                except Exception as e:
                    logger.error(f"Disk monitor error: {e}")

                self._stop_event.wait(self.disk_interval)

            logger.debug("Disk monitor thread stopped")

        thread = threading.Thread(target=monitor, daemon=True, name="DiskMonitor")
        thread.start()
        self._threads["disk"] = thread

    def _start_network_monitor(self) -> None:
        """Start network monitoring thread."""

        def monitor():
            logger.debug("Network monitor thread started")
            while self._monitoring_active and not self._stop_event.is_set():
                try:
                    data = self.get_network_info()
                    if "network" in self._callbacks:
                        self._callbacks["network"](data)
                except Exception as e:
                    logger.error(f"Network monitor error: {e}")

                self._stop_event.wait(self.network_interval)

            logger.debug("Network monitor thread stopped")

        thread = threading.Thread(target=monitor, daemon=True, name="NetworkMonitor")
        thread.start()
        self._threads["network"] = thread

    def _start_battery_monitor(self) -> None:
        """Start battery monitoring thread."""

        def monitor():
            logger.debug("Battery monitor thread started")
            while self._monitoring_active and not self._stop_event.is_set():
                try:
                    data = self.get_battery_info()
                    if "battery" in self._callbacks:
                        self._callbacks["battery"](data)
                except Exception as e:
                    logger.error(f"Battery monitor error: {e}")

                self._stop_event.wait(self.battery_interval)

            logger.debug("Battery monitor thread stopped")

        thread = threading.Thread(target=monitor, daemon=True, name="BatteryMonitor")
        thread.start()
        self._threads["battery"] = thread

    @staticmethod
    def get_cpu_info() -> Dict[str, Any]:
        """
        Get current CPU information.

        Returns:
            Dictionary with CPU metrics
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)
            cpu_freq = psutil.cpu_freq()

            return {
                "percent": cpu_percent,
                "physical_cores": cpu_count,
                "logical_cores": cpu_count_logical,
                "frequency": {
                    "current": cpu_freq.current if cpu_freq else 0,
                    "min": cpu_freq.min if cpu_freq else 0,
                    "max": cpu_freq.max if cpu_freq else 0,
                },
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get CPU info: {e}")
            return {"error": str(e)}

    @staticmethod
    def get_ram_info() -> Dict[str, Any]:
        """
        Get current RAM information.

        Returns:
            Dictionary with RAM metrics
        """
        try:
            ram = psutil.virtual_memory()

            return {
                "total": ram.total,
                "available": ram.available,
                "used": ram.used,
                "percent": ram.percent,
                "total_gb": round(ram.total / (1024**3), 2),
                "available_gb": round(ram.available / (1024**3), 2),
                "used_gb": round(ram.used / (1024**3), 2),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get RAM info: {e}")
            return {"error": str(e)}

    @staticmethod
    def get_disk_info() -> Dict[str, Any]:
        """
        Get disk information for all partitions.

        Returns:
            Dictionary with disk metrics
        """
        try:
            disks = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append(
                        {
                            "device": partition.device,
                            "mountpoint": partition.mountpoint,
                            "fstype": partition.fstype,
                            "total": usage.total,
                            "used": usage.used,
                            "free": usage.free,
                            "percent": usage.percent,
                            "total_gb": round(usage.total / (1024**3), 2),
                            "used_gb": round(usage.used / (1024**3), 2),
                            "free_gb": round(usage.free / (1024**3), 2),
                        }
                    )
                except PermissionError:
                    # Skip inaccessible partitions
                    continue

            return {"disks": disks, "timestamp": datetime.now().isoformat()}
        except Exception as e:
            logger.error(f"Failed to get disk info: {e}")
            return {"error": str(e)}

    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        """
        Get network interface information and statistics.

        Returns:
            Dictionary with network metrics including public IP, gateway, DNS, etc.
        """
        try:
            import socket
            import urllib.request
            import urllib.error
            
            # DNS test server for local IP detection
            DNS_TEST_SERVER = "8.8.8.8"
            
            net_io = psutil.net_io_counters()
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()

            interfaces = []
            for interface_name, addresses in net_if_addrs.items():
                if_stats = net_if_stats.get(interface_name)

                interface_info = {
                    "name": interface_name,
                    "is_up": if_stats.isup if if_stats else False,
                    "speed": if_stats.speed if if_stats else 0,
                    "addresses": [],
                }

                for addr in addresses:
                    interface_info["addresses"].append(
                        {
                            "family": str(addr.family),
                            "address": addr.address,
                            "netmask": addr.netmask,
                            "broadcast": addr.broadcast,
                        }
                    )

                interfaces.append(interface_info)
            
            # Get public IP (with timeout and error handling)
            # Note: Uses HTTPS with default SSL verification
            public_ip = None
            try:
                with urllib.request.urlopen('https://api.ipify.org', timeout=3) as response:
                    public_ip = response.read().decode('utf-8')
            except (urllib.error.URLError, Exception) as e:
                logger.debug(f"Could not fetch public IP: {e}")
                public_ip = "Unavailable"
            
            # Get default gateway
            default_gateway = None
            try:
                # Try to get gateway via netifaces if available
                import netifaces
                gws = netifaces.gateways()
                if 'default' in gws and netifaces.AF_INET in gws['default']:
                    default_gateway = gws['default'][netifaces.AF_INET][0]
            except (ImportError, Exception):
                # Fallback: try to parse route output on Windows
                try:
                    import subprocess
                    result = subprocess.run(['route', 'print', '0.0.0.0'], 
                                          capture_output=True, text=True, timeout=2)
                    for line in result.stdout.split('\n'):
                        if '0.0.0.0' in line and 'On-link' not in line:
                            parts = line.split()
                            if len(parts) >= 3:
                                default_gateway = parts[2]
                                break
                except Exception as e:
                    logger.debug(f"Could not determine default gateway: {e}")
            
            # Get DNS servers (Windows-specific)
            dns_servers = []
            try:
                import subprocess
                result = subprocess.run(['ipconfig', '/all'], 
                                      capture_output=True, text=True, timeout=5)
                for line in result.stdout.split('\n'):
                    if 'DNS Servers' in line or 'DNS-Server' in line:
                        # Extract DNS server IP
                        parts = line.split(':')
                        if len(parts) > 1:
                            dns_ip = parts[1].strip()
                            if dns_ip and dns_ip[0].isdigit():
                                dns_servers.append(dns_ip)
            except Exception as e:
                logger.debug(f"Could not get DNS servers: {e}")
            
            # Detect DHCP status and NAT
            dhcp_enabled = False
            behind_nat = False
            local_ip = None
            
            # Find primary local IP
            try:
                # Get local IP by creating a socket
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect((DNS_TEST_SERVER, 80))
                local_ip = s.getsockname()[0]
                s.close()
                
                # Check if behind NAT (private IP ranges)
                if local_ip:
                    octets = local_ip.split('.')
                    if len(octets) == 4:
                        first_octet = int(octets[0])
                        second_octet = int(octets[1])
                        # Check private IP ranges
                        if (first_octet == 10 or 
                            (first_octet == 172 and 16 <= second_octet <= 31) or
                            (first_octet == 192 and second_octet == 168)):
                            behind_nat = True
            except Exception as e:
                logger.debug(f"Could not determine local IP: {e}")
            
            # Try to detect DHCP (Windows-specific)
            try:
                import subprocess
                result = subprocess.run(['ipconfig', '/all'], 
                                      capture_output=True, text=True, timeout=5)
                if 'DHCP Enabled' in result.stdout:
                    for line in result.stdout.split('\n'):
                        if 'DHCP Enabled' in line:
                            dhcp_enabled = 'Yes' in line or 'True' in line
                            break
            except Exception as e:
                logger.debug(f"Could not determine DHCP status: {e}")

            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errin": net_io.errin,
                "errout": net_io.errout,
                "dropin": net_io.dropin,
                "dropout": net_io.dropout,
                "interfaces": interfaces,
                "public_ip": public_ip,
                "local_ip": local_ip,
                "default_gateway": default_gateway,
                "dns_servers": dns_servers,
                "dhcp_enabled": dhcp_enabled,
                "behind_nat": behind_nat,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get network info: {e}")
            return {"error": str(e)}

    @staticmethod
    def get_battery_info() -> Dict[str, Any]:
        """
        Get battery information.

        Returns:
            Dictionary with battery metrics
        """
        try:
            battery = psutil.sensors_battery()

            if battery is None:
                return {
                    "present": False,
                    "message": "No battery detected (desktop or no sensor support)",
                }

            return {
                "present": True,
                "percent": battery.percent,
                "power_plugged": battery.power_plugged,
                "secsleft": battery.secsleft,
                "time_left": (
                    f"{battery.secsleft // 3600}h {(battery.secsleft % 3600) // 60}m"
                    if battery.secsleft > 0
                    else "Charging" if battery.power_plugged else "Unknown"
                ),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get battery info: {e}")
            return {"error": str(e)}

    @staticmethod
    def get_system_temperature() -> Dict[str, Any]:
        """
        Get system temperature (if available).

        Returns:
            Dictionary with temperature metrics
        """
        try:
            temps = psutil.sensors_temperatures()

            if not temps:
                return {"available": False, "message": "Temperature sensors not available"}

            temp_data = {}
            for name, entries in temps.items():
                temp_data[name] = [
                    {
                        "label": entry.label or name,
                        "current": entry.current,
                        "high": entry.high,
                        "critical": entry.critical,
                    }
                    for entry in entries
                ]

            return {"available": True, "sensors": temp_data, "timestamp": datetime.now().isoformat()}
        except Exception as e:
            logger.error(f"Failed to get temperature info: {e}")
            return {"error": str(e)}


# Example usage
if __name__ == "__main__":
    monitor = MonitoringService()

    # Print current system info
    print("=== CPU Info ===")
    print(monitor.get_cpu_info())

    print("\n=== RAM Info ===")
    print(monitor.get_ram_info())

    print("\n=== Disk Info ===")
    print(monitor.get_disk_info())

    print("\n=== Network Info ===")
    net_info = monitor.get_network_info()
    print(f"Bytes Sent: {net_info.get('bytes_sent', 0) / (1024**2):.2f} MB")
    print(f"Bytes Received: {net_info.get('bytes_recv', 0) / (1024**2):.2f} MB")

    print("\n=== Battery Info ===")
    print(monitor.get_battery_info())

    # Test monitoring with callbacks
    def cpu_callback(data):
        print(f"CPU: {data.get('percent', 0):.1f}%")

    monitor.register_callback("cpu", cpu_callback)
    monitor.start()

    # Run for 10 seconds
    time.sleep(10)
    monitor.stop()
