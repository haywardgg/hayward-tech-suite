"""
Automated remediation module for Ghosty Toolz Evolved.

Provides automated fixes for common security issues and system problems
with user approval and rollback capabilities.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from src.utils.logger import get_logger, get_audit_logger
from src.core.system_operations import SystemOperations
from src.core.security_scanner import Vulnerability, VulnerabilitySeverity

logger = get_logger("remediation")
audit_logger = get_audit_logger()


class RemediationStatus(Enum):
    """Remediation status."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    ROLLED_BACK = "rolled_back"


@dataclass
class RemediationAction:
    """Remediation action definition."""
    
    id: str
    name: str
    description: str
    target_vulnerability: str
    command: str
    requires_admin: bool
    reversible: bool
    rollback_command: Optional[str] = None
    risk_level: str = "medium"
    estimated_time: int = 30  # seconds


@dataclass
class RemediationResult:
    """Result of a remediation action."""
    
    action_id: str
    status: RemediationStatus
    message: str
    timestamp: datetime
    output: Optional[str] = None
    error: Optional[str] = None


class RemediationError(Exception):
    """Custom exception for remediation errors."""
    
    pass


class AutomatedRemediation:
    """Automated security and system issue remediation."""
    
    # Predefined remediation actions
    REMEDIATION_ACTIONS = {
        'enable_defender': RemediationAction(
            id='enable_defender',
            name='Enable Windows Defender',
            description='Enable Windows Defender real-time protection',
            target_vulnerability='Windows Defender Disabled',
            command='powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $false"',
            requires_admin=True,
            reversible=True,
            rollback_command='powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"',
            risk_level='low'
        ),
        'disable_defender': RemediationAction(
            id='disable_defender',
            name='Disable Windows Defender',
            description='Disable Windows Defender real-time protection (NOT RECOMMENDED)',
            target_vulnerability=None,
            command='powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"',
            requires_admin=True,
            reversible=True,
            rollback_command='powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $false"',
            risk_level='high'
        ),
        'enable_firewall': RemediationAction(
            id='enable_firewall',
            name='Enable Windows Firewall',
            description='Enable Windows Firewall on all profiles',
            target_vulnerability='Firewall Disabled',
            command='netsh advfirewall set allprofiles state on',
            requires_admin=True,
            reversible=True,
            rollback_command='netsh advfirewall set allprofiles state off',
            risk_level='medium'
        ),
        'disable_firewall': RemediationAction(
            id='disable_firewall',
            name='Disable Windows Firewall',
            description='Disable Windows Firewall on all profiles (NOT RECOMMENDED)',
            target_vulnerability=None,
            command='netsh advfirewall set allprofiles state off',
            requires_admin=True,
            reversible=True,
            rollback_command='netsh advfirewall set allprofiles state on',
            risk_level='high'
        ),
        'enable_uac': RemediationAction(
            id='enable_uac',
            name='Enable User Account Control',
            description='Enable UAC to improve security',
            target_vulnerability='UAC Disabled',
            command='powershell -Command "Set-ItemProperty -Path HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System -Name EnableLUA -Value 1"',
            requires_admin=True,
            reversible=True,
            rollback_command='powershell -Command "Set-ItemProperty -Path HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System -Name EnableLUA -Value 0"',
            risk_level='high'
        ),
        'disable_smbv1': RemediationAction(
            id='disable_smbv1',
            name='Disable SMBv1 Protocol',
            description='Disable vulnerable SMBv1 protocol',
            target_vulnerability='SMBv1 Enabled',
            command='powershell -Command "Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart"',
            requires_admin=True,
            reversible=True,
            rollback_command='powershell -Command "Enable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart"',
            risk_level='medium',
            estimated_time=60
        ),
        'flush_dns': RemediationAction(
            id='flush_dns',
            name='Flush DNS Cache',
            description='Clear DNS cache to resolve network issues',
            target_vulnerability='DNS Issues',
            command='ipconfig /flushdns',
            requires_admin=False,
            reversible=False,
            risk_level='low',
            estimated_time=5
        ),
        'update_windows_defender': RemediationAction(
            id='update_windows_defender',
            name='Update Windows Defender Signatures',
            description='Update Windows Defender virus definitions',
            target_vulnerability='Outdated Definitions',
            command='powershell -Command "Update-MpSignature"',
            requires_admin=True,
            reversible=False,
            risk_level='low',
            estimated_time=120
        ),
    }
    
    def __init__(self) -> None:
        """Initialize automated remediation."""
        self.system_ops = SystemOperations()
        self.remediation_history: List[RemediationResult] = []
        logger.info("Automated remediation initialized")
    
    def get_available_actions(
        self,
        vulnerabilities: Optional[List[Vulnerability]] = None
    ) -> List[RemediationAction]:
        """
        Get available remediation actions for detected vulnerabilities.
        
        Args:
            vulnerabilities: List of detected vulnerabilities
        
        Returns:
            List of applicable remediation actions
        """
        if not vulnerabilities:
            return list(self.REMEDIATION_ACTIONS.values())
        
        available_actions = []
        vuln_names = [v.name for v in vulnerabilities]
        
        for action in self.REMEDIATION_ACTIONS.values():
            if action.target_vulnerability in vuln_names:
                available_actions.append(action)
        
        logger.info(f"Found {len(available_actions)} applicable remediation actions")
        return available_actions
    
    def execute_remediation(
        self,
        action_id: str,
        dry_run: bool = False
    ) -> RemediationResult:
        """
        Execute a remediation action.
        
        Args:
            action_id: ID of the action to execute
            dry_run: If True, simulate execution without making changes
        
        Returns:
            RemediationResult with execution details
        
        Raises:
            RemediationError: If action execution fails
        """
        if action_id not in self.REMEDIATION_ACTIONS:
            raise RemediationError(f"Unknown remediation action: {action_id}")
        
        action = self.REMEDIATION_ACTIONS[action_id]
        
        logger.info(f"Executing remediation: {action.name} (dry_run={dry_run})")
        audit_logger.info(f"Remediation initiated: {action.name} (id={action_id})")
        
        if dry_run:
            result = RemediationResult(
                action_id=action_id,
                status=RemediationStatus.SUCCESS,
                message=f"DRY RUN: Would execute {action.name}",
                timestamp=datetime.now(),
                output=f"Command: {action.command}"
            )
            logger.info(f"Dry run completed: {action.name}")
            return result
        
        # Check admin privileges if required
        if action.requires_admin and not self.system_ops.is_admin():
            logger.error(f"Admin privileges required for: {action.name}")
            result = RemediationResult(
                action_id=action_id,
                status=RemediationStatus.FAILED,
                message="Administrator privileges required for this action",
                timestamp=datetime.now(),
                error="Not running as administrator"
            )
            self.remediation_history.append(result)
            return result
        
        try:
            # Execute the remediation command
            success, stdout, stderr = self.system_ops.execute_command(
                action.command,
                timeout=action.estimated_time * 2,
                shell=True,
                require_admin=action.requires_admin,
                audit=True
            )
            
            if success:
                result = RemediationResult(
                    action_id=action_id,
                    status=RemediationStatus.SUCCESS,
                    message=f"Successfully executed {action.name}",
                    timestamp=datetime.now(),
                    output=stdout
                )
                logger.info(f"Remediation successful: {action.name}")
                audit_logger.info(f"Remediation success: {action.name} (id={action_id})")
            else:
                result = RemediationResult(
                    action_id=action_id,
                    status=RemediationStatus.FAILED,
                    message=f"Failed to execute {action.name}",
                    timestamp=datetime.now(),
                    error=stderr
                )
                logger.error(f"Remediation failed: {action.name} - {stderr}")
                audit_logger.error(f"Remediation failed: {action.name} (id={action_id})")
            
            self.remediation_history.append(result)
            return result
            
        except Exception as e:
            logger.error(f"Remediation error: {action.name} - {e}")
            audit_logger.error(f"Remediation error: {action.name} (id={action_id}) - {str(e)}")
            
            result = RemediationResult(
                action_id=action_id,
                status=RemediationStatus.FAILED,
                message=f"Error executing {action.name}",
                timestamp=datetime.now(),
                error=str(e)
            )
            self.remediation_history.append(result)
            raise RemediationError(f"Remediation failed: {e}")
    
    def rollback_remediation(self, action_id: str) -> RemediationResult:
        """
        Rollback a previously executed remediation.
        
        Args:
            action_id: ID of the action to rollback
        
        Returns:
            RemediationResult with rollback details
        
        Raises:
            RemediationError: If rollback fails or action is not reversible
        """
        if action_id not in self.REMEDIATION_ACTIONS:
            raise RemediationError(f"Unknown remediation action: {action_id}")
        
        action = self.REMEDIATION_ACTIONS[action_id]
        
        if not action.reversible:
            raise RemediationError(f"Action {action.name} is not reversible")
        
        if not action.rollback_command:
            raise RemediationError(f"No rollback command defined for {action.name}")
        
        logger.info(f"Rolling back remediation: {action.name}")
        audit_logger.warning(f"Remediation rollback initiated: {action.name} (id={action_id})")
        
        try:
            success, stdout, stderr = self.system_ops.execute_command(
                action.rollback_command,
                timeout=action.estimated_time * 2,
                shell=True,
                require_admin=action.requires_admin,
                audit=True
            )
            
            if success:
                result = RemediationResult(
                    action_id=action_id,
                    status=RemediationStatus.ROLLED_BACK,
                    message=f"Successfully rolled back {action.name}",
                    timestamp=datetime.now(),
                    output=stdout
                )
                logger.info(f"Rollback successful: {action.name}")
                audit_logger.info(f"Remediation rolled back: {action.name} (id={action_id})")
            else:
                result = RemediationResult(
                    action_id=action_id,
                    status=RemediationStatus.FAILED,
                    message=f"Failed to rollback {action.name}",
                    timestamp=datetime.now(),
                    error=stderr
                )
                logger.error(f"Rollback failed: {action.name} - {stderr}")
                audit_logger.error(f"Rollback failed: {action.name} (id={action_id})")
            
            self.remediation_history.append(result)
            return result
            
        except Exception as e:
            logger.error(f"Rollback error: {action.name} - {e}")
            audit_logger.error(f"Rollback error: {action.name} (id={action_id}) - {str(e)}")
            raise RemediationError(f"Rollback failed: {e}")
    
    def execute_batch_remediation(
        self,
        action_ids: List[str],
        stop_on_failure: bool = False
    ) -> Dict[str, RemediationResult]:
        """
        Execute multiple remediation actions in batch.
        
        Args:
            action_ids: List of action IDs to execute
            stop_on_failure: If True, stop batch execution on first failure
        
        Returns:
            Dictionary mapping action IDs to their results
        """
        logger.info(f"Starting batch remediation: {len(action_ids)} actions")
        audit_logger.info(f"Batch remediation initiated: {action_ids}")
        
        results = {}
        
        for action_id in action_ids:
            try:
                result = self.execute_remediation(action_id, dry_run=False)
                results[action_id] = result
                
                if stop_on_failure and result.status == RemediationStatus.FAILED:
                    logger.warning("Stopping batch remediation due to failure")
                    break
                    
            except Exception as e:
                logger.error(f"Batch remediation error for {action_id}: {e}")
                results[action_id] = RemediationResult(
                    action_id=action_id,
                    status=RemediationStatus.FAILED,
                    message=str(e),
                    timestamp=datetime.now(),
                    error=str(e)
                )
                
                if stop_on_failure:
                    break
        
        success_count = sum(1 for r in results.values() if r.status == RemediationStatus.SUCCESS)
        logger.info(f"Batch remediation completed: {success_count}/{len(results)} successful")
        audit_logger.info(f"Batch remediation completed: {success_count}/{len(results)} successful")
        
        return results
    
    def get_remediation_history(self) -> List[RemediationResult]:
        """
        Get history of all remediation actions.
        
        Returns:
            List of remediation results
        """
        return self.remediation_history.copy()
    
    def generate_remediation_report(
        self,
        vulnerabilities: List[Vulnerability]
    ) -> Dict[str, Any]:
        """
        Generate remediation recommendations report.
        
        Args:
            vulnerabilities: List of detected vulnerabilities
        
        Returns:
            Dictionary with remediation recommendations
        """
        logger.info("Generating remediation report")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_vulnerabilities': len(vulnerabilities),
            'remediable_count': 0,
            'recommendations': []
        }
        
        available_actions = self.get_available_actions(vulnerabilities)
        report['remediable_count'] = len(available_actions)
        
        for action in available_actions:
            recommendation = {
                'action_id': action.id,
                'name': action.name,
                'description': action.description,
                'risk_level': action.risk_level,
                'requires_admin': action.requires_admin,
                'reversible': action.reversible,
                'estimated_time_seconds': action.estimated_time,
                'target_vulnerability': action.target_vulnerability
            }
            report['recommendations'].append(recommendation)
        
        # Sort by risk level and whether admin is required
        risk_priority = {'low': 0, 'medium': 1, 'high': 2}
        report['recommendations'].sort(
            key=lambda x: (risk_priority.get(x['risk_level'], 1), x['requires_admin'])
        )
        
        logger.info(f"Remediation report generated: {report['remediable_count']} actions available")
        return report


# Example usage
if __name__ == "__main__":
    remediation = AutomatedRemediation()
    
    print("=== Available Remediation Actions ===")
    actions = remediation.get_available_actions()
    for action in actions:
        print(f"\n{action.name}")
        print(f"  ID: {action.id}")
        print(f"  Description: {action.description}")
        print(f"  Risk Level: {action.risk_level}")
        print(f"  Requires Admin: {action.requires_admin}")
        print(f"  Reversible: {action.reversible}")
    
    # Simulate a remediation (dry run)
    print("\n=== Dry Run: Flush DNS ===")
    try:
        result = remediation.execute_remediation('flush_dns', dry_run=True)
        print(f"Status: {result.status.value}")
        print(f"Message: {result.message}")
    except Exception as e:
        print(f"Error: {e}")
