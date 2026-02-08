"""
Network diagnostics module for Ghosty Toolz Evolved.

Provides advanced network diagnostics including latency testing,
bandwidth analysis, connection quality assessment, and DNS diagnostics.
"""

import socket
import time
import statistics
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from src.utils.logger import get_logger, get_audit_logger
from src.core.system_operations import SystemOperations

logger = get_logger("network_diagnostics")
audit_logger = get_audit_logger()


class ConnectionQuality(Enum):
    """Network connection quality levels."""
    
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class LatencyTest:
    """Latency test results."""
    
    host: str
    min_latency: float
    max_latency: float
    avg_latency: float
    median_latency: float
    packet_loss: float
    jitter: float
    quality: ConnectionQuality


@dataclass
class DNSResults:
    """DNS diagnostic results."""
    
    hostname: str
    resolved_ips: List[str]
    resolution_time: float
    dns_servers: List[str]
    reverse_dns: Optional[str]


class NetworkDiagnosticsError(Exception):
    """Custom exception for network diagnostics errors."""
    
    pass


class NetworkDiagnostics:
    """Advanced network diagnostics and monitoring tools."""
    
    def __init__(self) -> None:
        """Initialize network diagnostics."""
        self.system_ops = SystemOperations()
        logger.info("Network diagnostics initialized")
    
    def ping_test(
        self,
        host: str,
        count: int = 10,
        timeout: int = 2
    ) -> LatencyTest:
        """
        Perform comprehensive ping test with latency analysis.
        
        Args:
            host: Host to ping
            count: Number of pings to send
            timeout: Timeout in seconds per ping
        
        Returns:
            LatencyTest results
        
        Raises:
            NetworkDiagnosticsError: If test fails
        """
        logger.info(f"Starting ping test to {host} with {count} packets")
        audit_logger.info(f"Ping test initiated: {host}")
        
        try:
            # Execute ping command
            success, stdout, stderr = self.system_ops.execute_command(
                f"ping -n {count} -w {timeout * 1000} {host}",
                timeout=count * timeout + 10,
                audit=False
            )
            
            if not success:
                raise NetworkDiagnosticsError(f"Ping test failed: {stderr}")
            
            # Parse ping results
            latencies = []
            packet_loss = 0.0
            
            for line in stdout.split('\n'):
                if 'time=' in line or 'time<' in line:
                    try:
                        # Extract latency value
                        time_str = line.split('time')[1].split('ms')[0]
                        time_str = time_str.replace('=', '').replace('<', '').strip()
                        latency = float(time_str)
                        latencies.append(latency)
                    except (ValueError, IndexError):
                        continue
                elif 'Lost' in line or 'loss' in line:
                    try:
                        # Extract packet loss percentage
                        loss_str = line.split('(')[1].split('%')[0].strip()
                        packet_loss = float(loss_str)
                    except (ValueError, IndexError):
                        pass
            
            if not latencies:
                raise NetworkDiagnosticsError("No latency data collected")
            
            # Calculate statistics
            min_latency = min(latencies)
            max_latency = max(latencies)
            avg_latency = statistics.mean(latencies)
            median_latency = statistics.median(latencies)
            
            # Calculate jitter (variation in latency)
            jitter = statistics.stdev(latencies) if len(latencies) > 1 else 0.0
            
            # Determine connection quality
            quality = self._assess_connection_quality(avg_latency, packet_loss, jitter)
            
            result = LatencyTest(
                host=host,
                min_latency=min_latency,
                max_latency=max_latency,
                avg_latency=avg_latency,
                median_latency=median_latency,
                packet_loss=packet_loss,
                jitter=jitter,
                quality=quality
            )
            
            logger.info(
                f"Ping test completed: {host} - "
                f"Avg: {avg_latency:.2f}ms, Loss: {packet_loss}%, Quality: {quality.value}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Ping test failed: {e}")
            raise NetworkDiagnosticsError(f"Ping test failed: {e}")
    
    def _assess_connection_quality(
        self,
        avg_latency: float,
        packet_loss: float,
        jitter: float
    ) -> ConnectionQuality:
        """
        Assess connection quality based on metrics.
        
        Args:
            avg_latency: Average latency in ms
            packet_loss: Packet loss percentage
            jitter: Jitter in ms
        
        Returns:
            ConnectionQuality assessment
        """
        # Critical issues
        if packet_loss > 10 or avg_latency > 500:
            return ConnectionQuality.CRITICAL
        
        # Poor quality
        if packet_loss > 5 or avg_latency > 200 or jitter > 50:
            return ConnectionQuality.POOR
        
        # Fair quality
        if packet_loss > 2 or avg_latency > 100 or jitter > 25:
            return ConnectionQuality.FAIR
        
        # Good quality
        if packet_loss > 0.5 or avg_latency > 50 or jitter > 10:
            return ConnectionQuality.GOOD
        
        # Excellent quality
        return ConnectionQuality.EXCELLENT
    
    def trace_route(self, host: str, max_hops: int = 30) -> List[Dict[str, Any]]:
        """
        Perform traceroute to analyze network path.
        
        Args:
            host: Destination host
            max_hops: Maximum number of hops
        
        Returns:
            List of hop information
        
        Raises:
            NetworkDiagnosticsError: If traceroute fails
        """
        logger.info(f"Starting traceroute to {host}")
        audit_logger.info(f"Traceroute initiated: {host}")
        
        try:
            success, stdout, stderr = self.system_ops.execute_command(
                f"tracert -h {max_hops} {host}",
                timeout=max_hops * 5 + 30,
                audit=False
            )
            
            if not success:
                raise NetworkDiagnosticsError(f"Traceroute failed: {stderr}")
            
            # Parse traceroute results
            hops = []
            hop_num = 0
            
            for line in stdout.split('\n'):
                line = line.strip()
                if not line or 'Tracing route' in line or 'over a maximum' in line:
                    continue
                
                # Check if this is a hop line (starts with hop number)
                if line[0].isdigit():
                    try:
                        parts = line.split()
                        hop_num = int(parts[0])
                        
                        # Extract latencies
                        latencies = []
                        for part in parts[1:4]:
                            if part.replace('<', '').replace('ms', '').isdigit():
                                latencies.append(int(part.replace('<', '').replace('ms', '')))
                        
                        # Extract hostname/IP
                        hostname = None
                        ip_addr = None
                        for i, part in enumerate(parts):
                            if '[' in part and ']' in part:
                                ip_addr = part.strip('[]')
                                if i > 0:
                                    hostname = parts[i - 1]
                                break
                        
                        hop_info = {
                            'hop': hop_num,
                            'latencies': latencies,
                            'avg_latency': statistics.mean(latencies) if latencies else None,
                            'hostname': hostname,
                            'ip': ip_addr
                        }
                        hops.append(hop_info)
                        
                    except (ValueError, IndexError) as e:
                        logger.debug(f"Could not parse hop line: {line} - {e}")
                        continue
            
            logger.info(f"Traceroute completed: {len(hops)} hops to {host}")
            return hops
            
        except Exception as e:
            logger.error(f"Traceroute failed: {e}")
            raise NetworkDiagnosticsError(f"Traceroute failed: {e}")
    
    def dns_lookup(self, hostname: str) -> DNSResults:
        """
        Perform comprehensive DNS lookup and diagnostics.
        
        Args:
            hostname: Hostname to lookup
        
        Returns:
            DNS lookup results
        
        Raises:
            NetworkDiagnosticsError: If lookup fails
        """
        logger.info(f"Starting DNS lookup for {hostname}")
        
        try:
            # Time the DNS resolution
            start_time = time.time()
            resolved_ips = socket.gethostbyname_ex(hostname)[2]
            resolution_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Get DNS servers
            dns_servers = self._get_dns_servers()
            
            # Try reverse DNS lookup for first IP
            reverse_dns = None
            if resolved_ips:
                try:
                    reverse_dns = socket.gethostbyaddr(resolved_ips[0])[0]
                except Exception:
                    pass
            
            result = DNSResults(
                hostname=hostname,
                resolved_ips=resolved_ips,
                resolution_time=resolution_time,
                dns_servers=dns_servers,
                reverse_dns=reverse_dns
            )
            
            logger.info(
                f"DNS lookup completed: {hostname} -> {resolved_ips} "
                f"({resolution_time:.2f}ms)"
            )
            
            return result
            
        except socket.gaierror as e:
            logger.error(f"DNS lookup failed: {e}")
            raise NetworkDiagnosticsError(f"DNS lookup failed: {e}")
    
    def _get_dns_servers(self) -> List[str]:
        """
        Get configured DNS servers.
        
        Returns:
            List of DNS server IPs
        """
        try:
            success, stdout, stderr = self.system_ops.execute_command(
                'powershell -Command "Get-DnsClientServerAddress -AddressFamily IPv4 | '
                'Where-Object {$_.ServerAddresses} | '
                'Select-Object -ExpandProperty ServerAddresses"',
                shell=True,
                audit=False
            )
            
            if success:
                dns_servers = [line.strip() for line in stdout.split('\n') if line.strip()]
                return dns_servers
        except Exception as e:
            logger.debug(f"Could not get DNS servers: {e}")
        
        return []
    
    def check_port_connectivity(
        self,
        host: str,
        port: int,
        timeout: int = 3
    ) -> Tuple[bool, float]:
        """
        Check if a specific port is reachable.
        
        Args:
            host: Host to check
            port: Port number
            timeout: Connection timeout in seconds
        
        Returns:
            Tuple of (is_open, connection_time)
        """
        logger.debug(f"Checking connectivity to {host}:{port}")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        try:
            start_time = time.time()
            result = sock.connect_ex((host, port))
            connection_time = (time.time() - start_time) * 1000
            
            is_open = result == 0
            
            logger.debug(
                f"Port {port} on {host}: "
                f"{'OPEN' if is_open else 'CLOSED'} ({connection_time:.2f}ms)"
            )
            
            return is_open, connection_time
            
        except Exception as e:
            logger.debug(f"Connection check failed: {e}")
            return False, 0.0
        finally:
            sock.close()
    
    def get_network_interfaces(self) -> List[Dict[str, Any]]:
        """
        Get information about network interfaces.
        
        Returns:
            List of network interface information
        """
        logger.info("Getting network interface information")
        
        try:
            success, stdout, stderr = self.system_ops.execute_command(
                'powershell -Command "Get-NetAdapter | Select-Object Name, Status, '
                'LinkSpeed, MacAddress | ConvertTo-Json"',
                shell=True,
                audit=False
            )
            
            if success and stdout.strip():
                import json
                try:
                    interfaces = json.loads(stdout)
                    # Ensure it's always a list
                    if isinstance(interfaces, dict):
                        interfaces = [interfaces]
                    return interfaces
                except json.JSONDecodeError:
                    logger.warning("Could not parse network interface JSON")
        except Exception as e:
            logger.error(f"Failed to get network interfaces: {e}")
        
        return []
    
    def generate_network_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive network diagnostics report.
        
        Returns:
            Dictionary with network assessment
        """
        logger.info("Generating network diagnostics report")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'interfaces': [],
            'internet_connectivity': {},
            'dns_health': {},
            'latency_tests': []
        }
        
        # Get network interfaces
        try:
            report['interfaces'] = self.get_network_interfaces()
        except Exception as e:
            logger.error(f"Interface check failed: {e}")
            report['interfaces'] = {'error': str(e)}
        
        # Test internet connectivity to common hosts
        test_hosts = ['8.8.8.8', '1.1.1.1']
        for host in test_hosts:
            try:
                result = self.ping_test(host, count=4)
                report['latency_tests'].append({
                    'host': host,
                    'avg_latency': result.avg_latency,
                    'packet_loss': result.packet_loss,
                    'quality': result.quality.value
                })
            except Exception as e:
                logger.debug(f"Ping test to {host} failed: {e}")
        
        # Test DNS resolution
        try:
            dns_result = self.dns_lookup('www.google.com')
            report['dns_health'] = {
                'resolution_time': dns_result.resolution_time,
                'dns_servers': dns_result.dns_servers,
                'status': 'healthy' if dns_result.resolution_time < 100 else 'slow'
            }
        except Exception as e:
            logger.error(f"DNS test failed: {e}")
            report['dns_health'] = {'error': str(e)}
        
        logger.info("Network diagnostics report generated")
        return report


# Example usage
if __name__ == "__main__":
    diagnostics = NetworkDiagnostics()
    
    # Test ping
    print("=== Ping Test ===")
    try:
        result = diagnostics.ping_test("8.8.8.8", count=5)
        print(f"Host: {result.host}")
        print(f"Avg Latency: {result.avg_latency:.2f}ms")
        print(f"Packet Loss: {result.packet_loss}%")
        print(f"Quality: {result.quality.value}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test DNS
    print("\n=== DNS Lookup ===")
    try:
        dns_result = diagnostics.dns_lookup("www.google.com")
        print(f"Hostname: {dns_result.hostname}")
        print(f"IPs: {dns_result.resolved_ips}")
        print(f"Resolution Time: {dns_result.resolution_time:.2f}ms")
    except Exception as e:
        print(f"Error: {e}")
    
    # Generate report
    print("\n=== Network Report ===")
    report = diagnostics.generate_network_report()
    print(f"Timestamp: {report['timestamp']}")
    print(f"Interfaces: {len(report['interfaces'])}")
    print(f"Latency Tests: {len(report['latency_tests'])}")
