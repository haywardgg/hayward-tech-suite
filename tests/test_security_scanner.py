"""Tests for security scanner module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.core.security_scanner import (
    SecurityScanner,
    Vulnerability,
    VulnerabilitySeverity,
    FirewallStatus,
    SecurityError
)


class TestSecurityScanner:
    """Test suite for SecurityScanner class."""
    
    @pytest.fixture
    def scanner(self):
        """Create SecurityScanner instance for testing."""
        return SecurityScanner()
    
    def test_initialization(self, scanner):
        """Test security scanner initialization."""
        assert scanner is not None
        assert scanner.system_ops is not None
    
    @patch('src.core.security_scanner.SystemOperations')
    def test_check_windows_defender_disabled(self, mock_sys_ops, scanner):
        """Test Windows Defender check when disabled."""
        mock_output = """
AntivirusEnabled        : False
RealTimeProtectionEnabled : False
        """
        
        scanner.system_ops.execute_command = Mock(return_value=(True, mock_output, ""))
        
        vuln = scanner._check_windows_defender()
        
        assert vuln is not None
        assert isinstance(vuln, Vulnerability)
        assert vuln.severity == VulnerabilitySeverity.HIGH
        assert "Defender" in vuln.name
    
    @patch('src.core.security_scanner.SystemOperations')
    def test_check_windows_defender_enabled(self, mock_sys_ops, scanner):
        """Test Windows Defender check when enabled."""
        mock_output = """
AntivirusEnabled        : True
RealTimeProtectionEnabled : True
        """
        
        scanner.system_ops.execute_command = Mock(return_value=(True, mock_output, ""))
        
        vuln = scanner._check_windows_defender()
        
        assert vuln is None
    
    @patch('src.core.security_scanner.SystemOperations')
    def test_check_windows_updates_pending(self, mock_sys_ops, scanner):
        """Test Windows Update check with pending updates."""
        scanner.system_ops.execute_command = Mock(return_value=(True, "5", ""))
        
        vuln = scanner._check_windows_updates()
        
        assert vuln is not None
        assert isinstance(vuln, Vulnerability)
        assert vuln.severity == VulnerabilitySeverity.MEDIUM
        assert "Updates" in vuln.name
        assert vuln.details['pending_count'] == 5
    
    @patch('src.core.security_scanner.SystemOperations')
    def test_check_windows_updates_none_pending(self, mock_sys_ops, scanner):
        """Test Windows Update check with no pending updates."""
        scanner.system_ops.execute_command = Mock(return_value=(True, "0", ""))
        
        vuln = scanner._check_windows_updates()
        
        assert vuln is None
    
    @patch('src.core.security_scanner.SystemOperations')
    def test_check_firewall_disabled(self, mock_sys_ops, scanner):
        """Test firewall check when disabled."""
        mock_output = """
Domain Profile Settings:
State                                 OFF

Private Profile Settings:
State                                 OFF

Public Profile Settings:
State                                 OFF
        """
        
        scanner.system_ops.execute_command = Mock(return_value=(True, mock_output, ""))
        
        vuln = scanner._check_firewall_basic()
        
        assert vuln is not None
        assert isinstance(vuln, Vulnerability)
        assert vuln.severity == VulnerabilitySeverity.CRITICAL
        assert "Firewall" in vuln.name
    
    @patch('src.core.security_scanner.SystemOperations')
    def test_check_firewall_enabled(self, mock_sys_ops, scanner):
        """Test firewall check when enabled."""
        mock_output = """
Domain Profile Settings:
State                                 ON

Private Profile Settings:
State                                 ON

Public Profile Settings:
State                                 ON
        """
        
        scanner.system_ops.execute_command = Mock(return_value=(True, mock_output, ""))
        
        vuln = scanner._check_firewall_basic()
        
        assert vuln is None
    
    @patch('src.core.security_scanner.SystemOperations')
    def test_check_uac_disabled(self, mock_sys_ops, scanner):
        """Test UAC check when disabled."""
        scanner.system_ops.execute_command = Mock(return_value=(True, "0", ""))
        
        vuln = scanner._check_uac()
        
        assert vuln is not None
        assert isinstance(vuln, Vulnerability)
        assert vuln.severity == VulnerabilitySeverity.HIGH
        assert "UAC" in vuln.name
    
    @patch('src.core.security_scanner.SystemOperations')
    def test_check_uac_enabled(self, mock_sys_ops, scanner):
        """Test UAC check when enabled."""
        scanner.system_ops.execute_command = Mock(return_value=(True, "1", ""))
        
        vuln = scanner._check_uac()
        
        assert vuln is None
    
    @patch('src.core.security_scanner.SystemOperations')
    def test_check_network_shares(self, mock_sys_ops, scanner):
        """Test network share check."""
        mock_output = """
Share name   Resource                        Remark

C$           C:\\                             Default share
ADMIN$       C:\\Windows                      Remote Admin
IPC$                                         Remote IPC
MyShare      D:\\Shared                       My shared folder
        """
        
        scanner.system_ops.execute_command = Mock(return_value=(True, mock_output, ""))
        
        vuln = scanner._check_network_shares()
        
        assert vuln is not None
        assert isinstance(vuln, Vulnerability)
        assert vuln.severity == VulnerabilitySeverity.LOW
        assert "Share" in vuln.name
    
    @patch('src.core.security_scanner.SystemOperations')
    def test_check_smbv1_enabled(self, mock_sys_ops, scanner):
        """Test SMBv1 check when enabled."""
        scanner.system_ops.is_admin = Mock(return_value=True)
        scanner.system_ops.execute_command = Mock(return_value=(True, "Enabled", ""))
        
        vuln = scanner._check_smbv1()
        
        assert vuln is not None
        assert isinstance(vuln, Vulnerability)
        assert vuln.severity == VulnerabilitySeverity.HIGH
        assert "SMBv1" in vuln.name
    
    @patch('src.core.security_scanner.SystemOperations')
    def test_check_smbv1_disabled(self, mock_sys_ops, scanner):
        """Test SMBv1 check when disabled."""
        scanner.system_ops.is_admin = Mock(return_value=True)
        scanner.system_ops.execute_command = Mock(return_value=(True, "Disabled", ""))
        
        vuln = scanner._check_smbv1()
        
        assert vuln is None
    
    @patch('src.core.security_scanner.SystemOperations')
    def test_check_smbv1_no_admin(self, mock_sys_ops, scanner):
        """Test SMBv1 check when not admin - should skip."""
        scanner.system_ops.is_admin = Mock(return_value=False)
        
        vuln = scanner._check_smbv1()
        
        # Should return None because check is skipped without admin
        assert vuln is None
    
    @patch.object(SecurityScanner, '_check_windows_defender')
    @patch.object(SecurityScanner, '_check_windows_updates')
    @patch.object(SecurityScanner, '_check_firewall_basic')
    @patch.object(SecurityScanner, '_check_uac')
    @patch.object(SecurityScanner, '_check_network_shares')
    @patch.object(SecurityScanner, '_check_smbv1')
    def test_scan_vulnerabilities(
        self,
        mock_smb,
        mock_shares,
        mock_uac,
        mock_firewall,
        mock_updates,
        mock_defender,
        scanner
    ):
        """Test comprehensive vulnerability scan."""
        # Mock admin check to avoid elevation prompt
        scanner.system_ops.is_admin = Mock(return_value=True)
        
        # Mock some vulnerabilities
        mock_defender.return_value = Vulnerability(
            name="Test Defender Issue",
            description="Test description",
            severity=VulnerabilitySeverity.HIGH,
            category="Antivirus",
            recommendation="Fix it"
        )
        mock_updates.return_value = None
        mock_firewall.return_value = None
        mock_uac.return_value = None
        mock_shares.return_value = None
        mock_smb.return_value = None
        
        vulnerabilities = scanner.scan_vulnerabilities()
        
        assert isinstance(vulnerabilities, list)
        assert len(vulnerabilities) == 1
        assert vulnerabilities[0].name == "Test Defender Issue"
    
    @patch('src.core.security_scanner.SystemOperations')
    def test_check_firewall_status_success(self, mock_sys_ops, scanner):
        """Test getting firewall status."""
        mock_output = """
Domain Profile Settings:
State                                 ON

Private Profile Settings:
State                                 ON

Public Profile Settings:
State                                 ON
        """
        
        scanner.system_ops.execute_command = Mock(return_value=(True, mock_output, ""))
        
        status = scanner.check_firewall_status()
        
        assert isinstance(status, FirewallStatus)
        assert status.enabled is True
        assert status.profile == "All Profiles"
    
    @patch('src.core.security_scanner.SystemOperations')
    def test_check_firewall_status_failure(self, mock_sys_ops, scanner):
        """Test firewall status check failure."""
        scanner.system_ops.execute_command = Mock(return_value=(False, "", "Error"))
        
        with pytest.raises(SecurityError):
            scanner.check_firewall_status()
    
    def test_scan_ports(self, scanner):
        """Test port scanning."""
        # Test with mock socket
        with patch('socket.socket') as mock_socket:
            mock_sock = MagicMock()
            mock_sock.connect_ex.return_value = 0  # Port open
            mock_socket.return_value = mock_sock
            
            results = scanner.scan_ports('127.0.0.1', ports=[80, 443])
            
            assert isinstance(results, dict)
            assert len(results) == 2
            assert 80 in results
            assert 443 in results
    
    @patch.object(SecurityScanner, 'scan_vulnerabilities')
    @patch.object(SecurityScanner, 'check_firewall_status')
    def test_get_security_report(self, mock_firewall, mock_scan, scanner):
        """Test security report generation."""
        # Mock vulnerabilities
        mock_scan.return_value = [
            Vulnerability(
                name="Test Vuln",
                description="Test",
                severity=VulnerabilitySeverity.HIGH,
                category="Test",
                recommendation="Fix"
            )
        ]
        
        # Mock firewall status
        mock_firewall.return_value = FirewallStatus(
            enabled=True,
            profile="All",
            inbound_rules=100,
            outbound_rules=50,
            details={}
        )
        
        report = scanner.get_security_report()
        
        assert 'timestamp' in report
        assert 'vulnerabilities' in report
        assert 'firewall_status' in report
        assert 'summary' in report
        assert len(report['vulnerabilities']) == 1
