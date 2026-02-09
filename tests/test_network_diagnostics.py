"""Tests for network diagnostics module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.core.network_diagnostics import (
    NetworkDiagnostics,
    NetworkDiagnosticsError,
    LatencyTest,
    DNSResults,
    ConnectionQuality
)


class TestNetworkDiagnostics:
    """Test suite for NetworkDiagnostics class."""
    
    @pytest.fixture
    def diagnostics(self):
        """Create NetworkDiagnostics instance for testing."""
        return NetworkDiagnostics()
    
    def test_initialization(self, diagnostics):
        """Test network diagnostics initialization."""
        assert diagnostics is not None
        assert diagnostics.system_ops is not None
    
    @patch('src.core.network_diagnostics.SystemOperations')
    def test_ping_test_success(self, mock_sys_ops, diagnostics):
        """Test successful ping test."""
        # Mock ping output
        mock_ping_output = """
Pinging 8.8.8.8 with 32 bytes of data:
Reply from 8.8.8.8: bytes=32 time=15ms TTL=117
Reply from 8.8.8.8: bytes=32 time=14ms TTL=117
Reply from 8.8.8.8: bytes=32 time=16ms TTL=117
Reply from 8.8.8.8: bytes=32 time=15ms TTL=117

Ping statistics for 8.8.8.8:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
        """
        
        diagnostics.system_ops.execute_command = Mock(return_value=(True, mock_ping_output, ""))
        
        result = diagnostics.ping_test("8.8.8.8", count=4)
        
        assert isinstance(result, LatencyTest)
        assert result.host == "8.8.8.8"
        assert result.min_latency > 0
        assert result.max_latency > 0
        assert result.avg_latency > 0
        assert result.packet_loss >= 0
        assert isinstance(result.quality, ConnectionQuality)
    
    @patch('src.core.network_diagnostics.SystemOperations')
    def test_ping_test_with_packet_loss(self, mock_sys_ops, diagnostics):
        """Test ping test with packet loss."""
        mock_ping_output = """
Pinging 192.168.1.1 with 32 bytes of data:
Reply from 192.168.1.1: bytes=32 time=2ms TTL=64
Request timed out.
Reply from 192.168.1.1: bytes=32 time=3ms TTL=64

Ping statistics for 192.168.1.1:
    Packets: Sent = 3, Received = 2, Lost = 1 (33% loss),
        """
        
        diagnostics.system_ops.execute_command = Mock(return_value=(True, mock_ping_output, ""))
        
        result = diagnostics.ping_test("192.168.1.1", count=3)
        
        assert result.packet_loss > 0
        assert result.quality in [ConnectionQuality.POOR, ConnectionQuality.CRITICAL]
    
    def test_assess_connection_quality_excellent(self, diagnostics):
        """Test connection quality assessment - excellent."""
        quality = diagnostics._assess_connection_quality(
            avg_latency=10.0,
            packet_loss=0.0,
            jitter=2.0
        )
        assert quality == ConnectionQuality.EXCELLENT
    
    def test_assess_connection_quality_critical(self, diagnostics):
        """Test connection quality assessment - critical."""
        quality = diagnostics._assess_connection_quality(
            avg_latency=600.0,
            packet_loss=15.0,
            jitter=100.0
        )
        assert quality == ConnectionQuality.CRITICAL
    
    @patch('socket.gethostbyname_ex')
    def test_dns_lookup_success(self, mock_gethostbyname, diagnostics):
        """Test successful DNS lookup."""
        mock_gethostbyname.return_value = ('www.google.com', [], ['142.250.185.36'])
        
        result = diagnostics.dns_lookup('www.google.com')
        
        assert isinstance(result, DNSResults)
        assert result.hostname == 'www.google.com'
        assert len(result.resolved_ips) > 0
        assert result.resolution_time >= 0
    
    @patch('socket.gethostbyname_ex')
    def test_dns_lookup_failure(self, mock_gethostbyname, diagnostics):
        """Test DNS lookup failure."""
        import socket
        mock_gethostbyname.side_effect = socket.gaierror("DNS lookup failed")
        
        with pytest.raises(NetworkDiagnosticsError):
            diagnostics.dns_lookup('invalid.domain.xyz')
    
    def test_check_port_connectivity_open(self, diagnostics):
        """Test port connectivity check for open port."""
        # Test connection to a commonly open port (DNS on localhost won't work, so we mock)
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_sock.connect_ex.return_value = 0
            mock_socket.return_value = mock_sock
            
            is_open, connection_time = diagnostics.check_port_connectivity('127.0.0.1', 80)
            
            assert is_open is True
            assert connection_time >= 0
    
    def test_check_port_connectivity_closed(self, diagnostics):
        """Test port connectivity check for closed port."""
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_sock.connect_ex.return_value = 1  # Connection refused
            mock_socket.return_value = mock_sock
            
            is_open, connection_time = diagnostics.check_port_connectivity('127.0.0.1', 9999)
            
            assert is_open is False
    
    @patch('src.core.network_diagnostics.SystemOperations')
    def test_get_network_interfaces(self, mock_sys_ops, diagnostics):
        """Test getting network interfaces."""
        mock_json_output = '''[
            {"Name": "Ethernet", "Status": "Up", "LinkSpeed": "1 Gbps", "MacAddress": "00-11-22-33-44-55"},
            {"Name": "Wi-Fi", "Status": "Up", "LinkSpeed": "300 Mbps", "MacAddress": "AA-BB-CC-DD-EE-FF"}
        ]'''
        
        diagnostics.system_ops.execute_command = Mock(return_value=(True, mock_json_output, ""))
        
        interfaces = diagnostics.get_network_interfaces()
        
        assert isinstance(interfaces, list)
        assert len(interfaces) >= 0
    
    @patch.object(NetworkDiagnostics, 'ping_test')
    @patch.object(NetworkDiagnostics, 'dns_lookup')
    @patch.object(NetworkDiagnostics, 'get_network_interfaces')
    def test_generate_network_report(self, mock_interfaces, mock_dns, mock_ping, diagnostics):
        """Test network report generation."""
        # Mock the methods
        mock_interfaces.return_value = [{'Name': 'Ethernet', 'Status': 'Up'}]
        mock_dns.return_value = DNSResults(
            hostname='www.google.com',
            resolved_ips=['142.250.185.36'],
            resolution_time=50.0,
            dns_servers=['8.8.8.8'],
            reverse_dns=None
        )
        mock_ping.return_value = LatencyTest(
            host='8.8.8.8',
            min_latency=10.0,
            max_latency=20.0,
            avg_latency=15.0,
            median_latency=15.0,
            packet_loss=0.0,
            jitter=2.0,
            quality=ConnectionQuality.EXCELLENT
        )
        
        report = diagnostics.generate_network_report()
        
        assert 'timestamp' in report
        assert 'interfaces' in report
        assert 'dns_health' in report
        assert 'latency_tests' in report
