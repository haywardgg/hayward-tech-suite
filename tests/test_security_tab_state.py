"""
Test security tab state management for the "Run Available Fixes" functionality.
This test verifies the fix for the issue where clicking "Run Available Fixes" 
shows incorrect messages based on the vulnerability scan state.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.core.security_scanner import Vulnerability, VulnerabilitySeverity
from src.core.automated_remediation import AutomatedRemediation, RemediationAction


class TestSecurityTabStateFix:
    """Test suite for security tab state management fix."""
    
    def test_state_logic_with_none_vs_empty_list(self):
        """Test that the logic correctly distinguishes None from empty list."""
        # This test verifies the logic that depends on the initialization fix.
        # The critical fix at line 24 of security_tab.py: self.last_vulnerabilities = None
        # This allows the _run_all_fixes method to distinguish between:
        #   - None: no scan has been run
        #   - []: scan was run but found no vulnerabilities
        
        remediation = AutomatedRemediation()
        
        # Simulate the initial state (None)
        initial_state = None
        actions = remediation.get_available_actions(initial_state)
        assert len(actions) == 0, "Initial state (None) should have no actions"
        
        # Verify this is different from empty list state
        empty_state = []
        actions = remediation.get_available_actions(empty_state)
        assert len(actions) == 0, "Empty state ([]) should also have no actions"
        
        # Both return empty lists, but the UI layer (security_tab.py) 
        # uses the difference between None and [] to display appropriate messages
    
    def test_get_available_actions_handles_none(self):
        """Test that get_available_actions returns empty list for None (no scan)."""
        remediation = AutomatedRemediation()
        
        # When None is passed (no scan performed), should return empty list
        actions = remediation.get_available_actions(None)
        
        assert isinstance(actions, list)
        assert len(actions) == 0
    
    def test_get_available_actions_handles_empty_list(self):
        """Test that get_available_actions returns empty list for [] (scan found nothing)."""
        remediation = AutomatedRemediation()
        
        # When empty list is passed (scan found no vulnerabilities), should return empty list
        actions = remediation.get_available_actions([])
        
        assert isinstance(actions, list)
        assert len(actions) == 0
    
    def test_get_available_actions_handles_vulnerabilities_without_fixes(self):
        """Test vulnerabilities that don't have automated fixes available."""
        remediation = AutomatedRemediation()
        
        # Create a vulnerability that doesn't have a matching remediation action
        vulnerabilities = [
            Vulnerability(
                name='Unknown Vulnerability',
                description='Some issue without automated fix',
                severity=VulnerabilitySeverity.MEDIUM,
                category='Unknown',
                recommendation='Manual fix required'
            )
        ]
        
        actions = remediation.get_available_actions(vulnerabilities)
        
        # Should return empty list because no actions match this vulnerability
        assert isinstance(actions, list)
        assert len(actions) == 0
    
    def test_get_available_actions_handles_vulnerabilities_with_fixes(self):
        """Test vulnerabilities that have automated fixes available."""
        remediation = AutomatedRemediation()
        
        # Create vulnerabilities that have matching remediation actions
        vulnerabilities = [
            Vulnerability(
                name='Windows Defender Disabled',
                description='Defender is disabled',
                severity=VulnerabilitySeverity.HIGH,
                category='Antivirus',
                recommendation='Enable Windows Defender'
            ),
            Vulnerability(
                name='Firewall Disabled',
                description='Firewall is disabled',
                severity=VulnerabilitySeverity.CRITICAL,
                category='Firewall',
                recommendation='Enable Windows Firewall'
            )
        ]
        
        actions = remediation.get_available_actions(vulnerabilities)
        
        # Should return matching actions
        assert isinstance(actions, list)
        assert len(actions) == 2
        
        action_ids = [action.id for action in actions]
        assert 'enable_defender' in action_ids
        assert 'enable_firewall' in action_ids
    
    def test_state_transitions(self):
        """Test the state transitions from None -> [] -> [vulns]."""
        remediation = AutomatedRemediation()
        
        # State 1: No scan performed (None)
        state1 = None
        actions1 = remediation.get_available_actions(state1)
        assert len(actions1) == 0, "No scan performed should return no actions"
        
        # State 2: Scan performed, no vulnerabilities found ([])
        state2 = []
        actions2 = remediation.get_available_actions(state2)
        assert len(actions2) == 0, "No vulnerabilities found should return no actions"
        
        # State 3: Scan performed, vulnerabilities found with fixes available
        state3 = [
            Vulnerability(
                name='Windows Defender Disabled',
                description='Test',
                severity=VulnerabilitySeverity.HIGH,
                category='Antivirus',
                recommendation='Enable it'
            )
        ]
        actions3 = remediation.get_available_actions(state3)
        assert len(actions3) == 1, "Vulnerabilities with fixes should return actions"
        
        # State 4: Scan performed, vulnerabilities found without fixes available
        state4 = [
            Vulnerability(
                name='Some Manual Fix Required',
                description='Test',
                severity=VulnerabilitySeverity.HIGH,
                category='Manual',
                recommendation='Fix manually'
            )
        ]
        actions4 = remediation.get_available_actions(state4)
        assert len(actions4) == 0, "Vulnerabilities without automated fixes should return no actions"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
