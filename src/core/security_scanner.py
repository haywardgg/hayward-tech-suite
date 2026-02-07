"""
Security scanner module for Ghosty Toolz Evolved.

Provides security assessment tools including vulnerability scanning,
firewall monitoring, and port checking.
"""

import subprocess
import socket
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from src.utils.logger import get_logger, get_audit_logger
from src.utils.config import get_config
from src.core.system_operations import SystemOperations

logger = get_logger("security_scanner")
audit_logger = get_audit_logger()
config = get_config()


class VulnerabilitySeverity(Enum):
    """Vulnerability severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Vulnerability:
    """Vulnerability information."""

    name: str
    description: str
    severity: VulnerabilitySeverity
    category: str
    recommendation: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class FirewallStatus:
    """Firewall status information."""

    enabled: bool
    profile: str
    inbound_rules: int
    outbound_rules: int
    details: Dict[str, Any]


class SecurityError(Exception):
    """Custom exception for security scanner errors."""

    pass


class SecurityScanner:
    """Security assessment and monitoring tools."""

    def __init__(self) -> None:
        """Initialize security scanner."""
        self.system_ops = SystemOperations()
        logger.info("Security scanner initialized")

    def scan_vulnerabilities(self) -> List[Vulnerability]:
        """
        Scan for common security issues and vulnerabilities.

        Returns:
            List of detected vulnerabilities

        Raises:
            SecurityError: If scan fails
        """
        logger.info("Starting vulnerability scan")
        audit_logger.info("Vulnerability scan initiated")

        vulnerabilities = []

        # Check Windows Defender status
        defender_vuln = self._check_windows_defender()
        if defender_vuln:
            vulnerabilities.append(defender_vuln)

        # Check Windows Update status
        update_vuln = self._check_windows_updates()
        if update_vuln:
            vulnerabilities.append(update_vuln)

        # Check firewall status
        firewall_vuln = self._check_firewall_basic()
        if firewall_vuln:
            vulnerabilities.append(firewall_vuln)

        # Check UAC status
        uac_vuln = self._check_uac()
        if uac_vuln:
            vulnerabilities.append(uac_vuln)

        # Check for shared folders
        shares_vuln = self._check_network_shares()
        if shares_vuln:
            vulnerabilities.append(shares_vuln)

        # Check SMBv1 status
        smb_vuln = self._check_smbv1()
        if smb_vuln:
            vulnerabilities.append(smb_vuln)

        logger.info(f"Vulnerability scan completed: {len(vulnerabilities)} issues found")
        audit_logger.info(f"Vulnerability scan completed with {len(vulnerabilities)} findings")

        return vulnerabilities

    def _check_windows_defender(self) -> Optional[Vulnerability]:
        """Check Windows Defender status."""
        try:
            success, stdout, stderr = self.system_ops.execute_command(
                'powershell -Command "Get-MpComputerStatus | Select-Object AntivirusEnabled, RealTimeProtectionEnabled"',
                shell=True,
                audit=False,
            )

            if success:
                # Parse output for defender status
                if "False" in stdout:
                    return Vulnerability(
                        name="Windows Defender Disabled",
                        description="Windows Defender antivirus or real-time protection is disabled",
                        severity=VulnerabilitySeverity.HIGH,
                        category="Antivirus",
                        recommendation="Enable Windows Defender and real-time protection",
                        details={"output": stdout},
                    )
        except Exception as e:
            logger.error(f"Failed to check Windows Defender: {e}")

        return None

    def _check_windows_updates(self) -> Optional[Vulnerability]:
        """Check for pending Windows updates."""
        try:
            # Try using Windows Update COM object (works without PSWindowsUpdate module)
            success, stdout, stderr = self.system_ops.execute_command(
                'powershell -Command "$UpdateSession = New-Object -ComObject Microsoft.Update.Session; '
                '$UpdateSearcher = $UpdateSession.CreateUpdateSearcher(); '
                '$SearchResult = $UpdateSearcher.Search(\'IsInstalled=0 and IsHidden=0\'); '
                '$SearchResult.Updates.Count"',
                timeout=60,
                shell=True,
                audit=False,
            )

            if success and stdout.strip().isdigit():
                update_count = int(stdout.strip())
                if update_count > 0:
                    return Vulnerability(
                        name="Pending Windows Updates",
                        description=f"{update_count} Windows update(s) are pending installation",
                        severity=VulnerabilitySeverity.MEDIUM,
                        category="Updates",
                        recommendation="Install pending Windows updates",
                        details={"pending_count": update_count},
                    )
        except Exception as e:
            logger.debug(f"Could not check Windows updates: {e}")

        return None

    def _check_firewall_basic(self) -> Optional[Vulnerability]:
        """Basic firewall status check."""
        try:
            success, stdout, stderr = self.system_ops.execute_command(
                "netsh advfirewall show allprofiles state", audit=False
            )

            if success:
                # Check if any profile shows firewall off
                if "OFF" in stdout.upper():
                    return Vulnerability(
                        name="Firewall Disabled",
                        description="Windows Firewall is disabled on one or more profiles",
                        severity=VulnerabilitySeverity.CRITICAL,
                        category="Firewall",
                        recommendation="Enable Windows Firewall on all profiles",
                        details={"output": stdout},
                    )
        except Exception as e:
            logger.error(f"Failed to check firewall: {e}")

        return None

    def _check_uac(self) -> Optional[Vulnerability]:
        """Check UAC (User Account Control) status."""
        try:
            success, stdout, stderr = self.system_ops.execute_command(
                'powershell -Command "(Get-ItemProperty HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System).EnableLUA"',
                shell=True,
                audit=False,
            )

            if success and "0" in stdout:
                return Vulnerability(
                    name="UAC Disabled",
                    description="User Account Control is disabled",
                    severity=VulnerabilitySeverity.HIGH,
                    category="Access Control",
                    recommendation="Enable User Account Control (UAC)",
                    details={},
                )
        except Exception as e:
            logger.debug(f"Could not check UAC: {e}")

        return None

    def _check_network_shares(self) -> Optional[Vulnerability]:
        """Check for network shares."""
        try:
            success, stdout, stderr = self.system_ops.execute_command(
                "net share", audit=False
            )

            if success:
                # Count non-default shares (excluding C$, ADMIN$, IPC$)
                lines = stdout.split("\n")
                share_count = 0
                for line in lines:
                    if "$" not in line and "Share name" not in line and line.strip():
                        share_count += 1

                if share_count > 0:
                    return Vulnerability(
                        name="Network Shares Active",
                        description=f"{share_count} network share(s) are active",
                        severity=VulnerabilitySeverity.LOW,
                        category="Network",
                        recommendation="Review and disable unnecessary network shares",
                        details={"share_count": share_count, "output": stdout},
                    )
        except Exception as e:
            logger.debug(f"Could not check network shares: {e}")

        return None

    def _check_smbv1(self) -> Optional[Vulnerability]:
        """Check if SMBv1 is enabled (security risk)."""
        try:
            success, stdout, stderr = self.system_ops.execute_command(
                'powershell -Command "(Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol).State"',
                shell=True,
                audit=False,
            )

            if success and "Enabled" in stdout:
                return Vulnerability(
                    name="SMBv1 Enabled",
                    description="SMBv1 protocol is enabled (known security vulnerability)",
                    severity=VulnerabilitySeverity.HIGH,
                    category="Network Protocol",
                    recommendation="Disable SMBv1 protocol",
                    details={},
                )
        except Exception as e:
            logger.debug(f"Could not check SMBv1: {e}")

        return None

    def check_firewall_status(self) -> FirewallStatus:
        """
        Get detailed firewall status.

        Returns:
            Firewall status information

        Raises:
            SecurityError: If status check fails
        """
        logger.info("Checking firewall status")

        try:
            success, stdout, stderr = self.system_ops.execute_command(
                "netsh advfirewall show allprofiles", audit=False
            )

            if not success:
                raise SecurityError(f"Failed to get firewall status: {stderr}")

            # Parse output
            enabled = "OFF" not in stdout.upper()
            profile = "All Profiles"

            # Get rule counts
            try:
                success_in, stdout_in, _ = self.system_ops.execute_command(
                    "netsh advfirewall firewall show rule name=all dir=in | find /c \"Rule Name\"",
                    shell=True,
                    audit=False,
                )
                inbound_count = int(stdout_in.strip()) if success_in else 0
            except Exception:
                inbound_count = 0

            try:
                success_out, stdout_out, _ = self.system_ops.execute_command(
                    "netsh advfirewall firewall show rule name=all dir=out | find /c \"Rule Name\"",
                    shell=True,
                    audit=False,
                )
                outbound_count = int(stdout_out.strip()) if success_out else 0
            except Exception:
                outbound_count = 0

            firewall_status = FirewallStatus(
                enabled=enabled,
                profile=profile,
                inbound_rules=inbound_count,
                outbound_rules=outbound_count,
                details={"output": stdout},
            )

            logger.info(
                f"Firewall status: {'Enabled' if enabled else 'Disabled'} "
                f"(In: {inbound_count}, Out: {outbound_count})"
            )

            return firewall_status

        except Exception as e:
            logger.error(f"Failed to check firewall status: {e}")
            raise SecurityError(f"Firewall status check failed: {e}")

    def scan_ports(self, host: str = "127.0.0.1", ports: Optional[List[int]] = None) -> Dict[int, bool]:
        """
        Scan network ports on specified host.

        Args:
            host: Host to scan (default: localhost)
            ports: List of ports to scan (default: common ports)

        Returns:
            Dictionary mapping port numbers to open status
        """
        if ports is None:
            # Common ports
            ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 3389, 8080, 8443]

        logger.info(f"Scanning {len(ports)} ports on {host}")
        audit_logger.info(f"Port scan initiated on {host}")

        results = {}

        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)

            try:
                result = sock.connect_ex((host, port))
                results[port] = result == 0
            except Exception:
                results[port] = False
            finally:
                sock.close()

        open_ports = [port for port, is_open in results.items() if is_open]
        logger.info(f"Port scan completed: {len(open_ports)} open port(s) found")
        audit_logger.info(f"Port scan completed: {len(open_ports)} open ports on {host}")

        return results

    def get_security_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive security report.

        Returns:
            Dictionary with security assessment
        """
        logger.info("Generating security report")

        report = {
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities": [],
            "firewall_status": None,
            "summary": {},
        }

        # Scan vulnerabilities
        try:
            vulnerabilities = self.scan_vulnerabilities()
            report["vulnerabilities"] = [
                {
                    "name": v.name,
                    "description": v.description,
                    "severity": v.severity.value,
                    "category": v.category,
                    "recommendation": v.recommendation,
                }
                for v in vulnerabilities
            ]

            # Calculate severity summary
            severity_counts = {
                "critical": sum(1 for v in vulnerabilities if v.severity == VulnerabilitySeverity.CRITICAL),
                "high": sum(1 for v in vulnerabilities if v.severity == VulnerabilitySeverity.HIGH),
                "medium": sum(1 for v in vulnerabilities if v.severity == VulnerabilitySeverity.MEDIUM),
                "low": sum(1 for v in vulnerabilities if v.severity == VulnerabilitySeverity.LOW),
            }
            report["summary"]["vulnerabilities"] = severity_counts

        except Exception as e:
            logger.error(f"Vulnerability scan failed: {e}")
            report["vulnerabilities"] = {"error": str(e)}

        # Get firewall status
        try:
            firewall = self.check_firewall_status()
            report["firewall_status"] = {
                "enabled": firewall.enabled,
                "profile": firewall.profile,
                "inbound_rules": firewall.inbound_rules,
                "outbound_rules": firewall.outbound_rules,
            }
        except Exception as e:
            logger.error(f"Firewall check failed: {e}")
            report["firewall_status"] = {"error": str(e)}

        logger.info("Security report generated")
        return report


# Example usage
if __name__ == "__main__":
    scanner = SecurityScanner()

    # Run vulnerability scan
    print("=== Vulnerability Scan ===")
    vulnerabilities = scanner.scan_vulnerabilities()
    for vuln in vulnerabilities:
        print(f"\n[{vuln.severity.value.upper()}] {vuln.name}")
        print(f"  {vuln.description}")
        print(f"  Recommendation: {vuln.recommendation}")

    # Check firewall
    print("\n=== Firewall Status ===")
    try:
        firewall = scanner.check_firewall_status()
        print(f"Enabled: {firewall.enabled}")
        print(f"Inbound Rules: {firewall.inbound_rules}")
        print(f"Outbound Rules: {firewall.outbound_rules}")
    except Exception as e:
        print(f"Error: {e}")

    # Generate full report
    print("\n=== Security Report ===")
    report = scanner.get_security_report()
    print(f"Timestamp: {report['timestamp']}")
    print(f"Total Vulnerabilities: {len(report.get('vulnerabilities', []))}")
