"""Tests for automated remediation module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.core.automated_remediation import (
    AutomatedRemediation,
    RemediationAction,
    RemediationResult,
    RemediationStatus,
    RemediationError
)
from src.core.security_scanner import Vulnerability, VulnerabilitySeverity


class TestAutomatedRemediation:
    """Test suite for AutomatedRemediation class."""
    
    @pytest.fixture
    def remediation(self):
        """Create AutomatedRemediation instance for testing."""
        return AutomatedRemediation()
    
    def test_initialization(self, remediation):
        """Test remediation initialization."""
        assert remediation is not None
        assert remediation.system_ops is not None
        assert len(remediation.remediation_history) == 0
    
    def test_predefined_actions_exist(self, remediation):
        """Test that predefined remediation actions exist."""
        assert 'enable_defender' in remediation.REMEDIATION_ACTIONS
        assert 'enable_firewall' in remediation.REMEDIATION_ACTIONS
        assert 'enable_uac' in remediation.REMEDIATION_ACTIONS
        assert 'disable_smbv1' in remediation.REMEDIATION_ACTIONS
        assert 'flush_dns' in remediation.REMEDIATION_ACTIONS
    
    def test_get_available_actions_all(self, remediation):
        """Test getting all available actions."""
        actions = remediation.get_available_actions()
        assert isinstance(actions, list)
        assert len(actions) > 0
        for action in actions:
            assert isinstance(action, RemediationAction)
    
    def test_get_available_actions_for_vulnerabilities(self, remediation):
        """Test getting actions for specific vulnerabilities."""
        vulnerabilities = [
            Vulnerability(
                name='Windows Defender Disabled',
                description='Test',
                severity=VulnerabilitySeverity.HIGH,
                category='Antivirus',
                recommendation='Enable it'
            ),
            Vulnerability(
                name='Firewall Disabled',
                description='Test',
                severity=VulnerabilitySeverity.CRITICAL,
                category='Firewall',
                recommendation='Enable it'
            )
        ]
        
        actions = remediation.get_available_actions(vulnerabilities)
        assert len(actions) == 2
        action_ids = [a.id for a in actions]
        assert 'enable_defender' in action_ids
        assert 'enable_firewall' in action_ids
    
    def test_execute_remediation_dry_run(self, remediation):
        """Test remediation execution in dry run mode."""
        result = remediation.execute_remediation('flush_dns', dry_run=True)
        
        assert isinstance(result, RemediationResult)
        assert result.action_id == 'flush_dns'
        assert result.status == RemediationStatus.SUCCESS
        assert 'DRY RUN' in result.message
    
    @patch('src.core.automated_remediation.SystemOperations')
    def test_execute_remediation_success(self, mock_sys_ops, remediation):
        """Test successful remediation execution."""
        remediation.system_ops.execute_command = Mock(return_value=(True, "Success", ""))
        remediation.system_ops.is_admin = Mock(return_value=False)
        
        result = remediation.execute_remediation('flush_dns', dry_run=False)
        
        assert result.status == RemediationStatus.SUCCESS
        assert result.action_id == 'flush_dns'
        assert len(remediation.remediation_history) == 1
    
    @patch('src.core.automated_remediation.SystemOperations')
    def test_execute_remediation_failure(self, mock_sys_ops, remediation):
        """Test failed remediation execution."""
        remediation.system_ops.execute_command = Mock(return_value=(False, "", "Error occurred"))
        remediation.system_ops.is_admin = Mock(return_value=False)
        
        result = remediation.execute_remediation('flush_dns', dry_run=False)
        
        assert result.status == RemediationStatus.FAILED
        assert result.error == "Error occurred"
        assert len(remediation.remediation_history) == 1
    
    @patch('src.core.automated_remediation.SystemOperations')
    def test_execute_remediation_requires_admin(self, mock_sys_ops, remediation):
        """Test remediation that requires admin privileges."""
        remediation.system_ops.is_admin = Mock(return_value=False)
        
        with pytest.raises(RemediationError) as exc_info:
            remediation.execute_remediation('enable_firewall', dry_run=False)
        
        assert 'Administrator privileges required' in str(exc_info.value)
    
    def test_execute_remediation_unknown_action(self, remediation):
        """Test execution of unknown remediation action."""
        with pytest.raises(RemediationError) as exc_info:
            remediation.execute_remediation('nonexistent_action', dry_run=False)
        
        assert 'Unknown remediation action' in str(exc_info.value)
    
    @patch('src.core.automated_remediation.SystemOperations')
    def test_rollback_remediation_success(self, mock_sys_ops, remediation):
        """Test successful remediation rollback."""
        remediation.system_ops.execute_command = Mock(return_value=(True, "Rolled back", ""))
        remediation.system_ops.is_admin = Mock(return_value=True)
        
        result = remediation.rollback_remediation('enable_firewall')
        
        assert result.status == RemediationStatus.ROLLED_BACK
        assert result.action_id == 'enable_firewall'
        assert len(remediation.remediation_history) == 1
    
    @patch('src.core.automated_remediation.SystemOperations')
    def test_rollback_remediation_failure(self, mock_sys_ops, remediation):
        """Test failed remediation rollback."""
        remediation.system_ops.execute_command = Mock(return_value=(False, "", "Rollback failed"))
        remediation.system_ops.is_admin = Mock(return_value=True)
        
        result = remediation.rollback_remediation('enable_firewall')
        
        assert result.status == RemediationStatus.FAILED
        assert result.error == "Rollback failed"
    
    def test_rollback_non_reversible_action(self, remediation):
        """Test rollback of non-reversible action."""
        with pytest.raises(RemediationError) as exc_info:
            remediation.rollback_remediation('flush_dns')
        
        assert 'not reversible' in str(exc_info.value)
    
    @patch.object(AutomatedRemediation, 'execute_remediation')
    def test_execute_batch_remediation(self, mock_execute, remediation):
        """Test batch remediation execution."""
        mock_execute.side_effect = [
            RemediationResult(
                action_id='flush_dns',
                status=RemediationStatus.SUCCESS,
                message='Success',
                timestamp=datetime.now()
            ),
            RemediationResult(
                action_id='update_windows_defender',
                status=RemediationStatus.SUCCESS,
                message='Success',
                timestamp=datetime.now()
            )
        ]
        
        results = remediation.execute_batch_remediation(['flush_dns', 'update_windows_defender'])
        
        assert len(results) == 2
        assert all(r.status == RemediationStatus.SUCCESS for r in results.values())
    
    @patch.object(AutomatedRemediation, 'execute_remediation')
    def test_execute_batch_remediation_stop_on_failure(self, mock_execute, remediation):
        """Test batch remediation with stop on failure."""
        mock_execute.side_effect = [
            RemediationResult(
                action_id='flush_dns',
                status=RemediationStatus.FAILED,
                message='Failed',
                timestamp=datetime.now()
            )
        ]
        
        results = remediation.execute_batch_remediation(
            ['flush_dns', 'update_windows_defender'],
            stop_on_failure=True
        )
        
        # Should only have one result because it stopped on failure
        assert len(results) == 1
        assert results['flush_dns'].status == RemediationStatus.FAILED
    
    def test_get_remediation_history(self, remediation):
        """Test getting remediation history."""
        # Add some mock history
        remediation.remediation_history.append(
            RemediationResult(
                action_id='test',
                status=RemediationStatus.SUCCESS,
                message='Test',
                timestamp=datetime.now()
            )
        )
        
        history = remediation.get_remediation_history()
        assert len(history) == 1
        assert isinstance(history, list)
    
    def test_generate_remediation_report(self, remediation):
        """Test remediation report generation."""
        vulnerabilities = [
            Vulnerability(
                name='Windows Defender Disabled',
                description='Test',
                severity=VulnerabilitySeverity.HIGH,
                category='Antivirus',
                recommendation='Enable it'
            ),
            Vulnerability(
                name='SMBv1 Enabled',
                description='Test',
                severity=VulnerabilitySeverity.HIGH,
                category='Network',
                recommendation='Disable it'
            )
        ]
        
        report = remediation.generate_remediation_report(vulnerabilities)
        
        assert 'timestamp' in report
        assert 'total_vulnerabilities' in report
        assert report['total_vulnerabilities'] == 2
        assert 'remediable_count' in report
        assert report['remediable_count'] == 2
        assert 'recommendations' in report
        assert len(report['recommendations']) == 2
        
        # Check recommendation structure
        for rec in report['recommendations']:
            assert 'action_id' in rec
            assert 'name' in rec
            assert 'description' in rec
            assert 'risk_level' in rec
            assert 'requires_admin' in rec
            assert 'reversible' in rec
            assert 'estimated_time_seconds' in rec
    
    def test_remediation_action_attributes(self, remediation):
        """Test that remediation actions have required attributes."""
        for action_id, action in remediation.REMEDIATION_ACTIONS.items():
            assert action.id == action_id
            assert action.name
            assert action.description
            assert action.target_vulnerability
            assert action.command
            assert isinstance(action.requires_admin, bool)
            assert isinstance(action.reversible, bool)
            assert action.risk_level in ['low', 'medium', 'high']
            assert action.estimated_time > 0
            
            if action.reversible:
                assert action.rollback_command is not None
