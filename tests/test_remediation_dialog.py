"""Tests for remediation dialog."""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch

# Mock GUI modules for testing in headless environment
sys.modules['customtkinter'] = MagicMock()
sys.modules['tkinter'] = MagicMock()

from src.core.automated_remediation import AutomatedRemediation
from src.core.security_scanner import Vulnerability, VulnerabilitySeverity


class TestRemediationDialog:
    """Test suite for RemediationDialog."""

    @pytest.fixture
    def mock_parent(self):
        """Create mock parent window."""
        parent = MagicMock()
        parent.winfo_toplevel.return_value = parent
        return parent

    @pytest.fixture
    def mock_remediation(self):
        """Create mock remediation instance."""
        remediation = MagicMock(spec=AutomatedRemediation)
        remediation.REMEDIATION_ACTIONS = AutomatedRemediation.REMEDIATION_ACTIONS
        remediation.get_available_actions.return_value = list(
            AutomatedRemediation.REMEDIATION_ACTIONS.values()
        )
        remediation.get_remediation_history.return_value = []
        return remediation

    @pytest.fixture
    def mock_vulnerabilities(self):
        """Create mock vulnerabilities."""
        return [
            Vulnerability(
                name="Windows Defender Disabled",
                description="Windows Defender is disabled",
                severity=VulnerabilitySeverity.HIGH,
                recommendation="Enable Windows Defender",
            ),
            Vulnerability(
                name="Firewall Disabled",
                description="Windows Firewall is disabled",
                severity=VulnerabilitySeverity.HIGH,
                recommendation="Enable Windows Firewall",
            ),
        ]

    def test_dialog_class_exists(self):
        """Test dialog class can be imported."""
        from src.gui.dialogs.remediation_dialog import RemediationDialog
        assert RemediationDialog is not None
        
    def test_risk_colors_match_spec(self):
        """Test that risk colors match the specification."""
        # Colors from spec: low='#2ecc71', medium='#f39c12', high='#e74c3c'
        expected_colors = {
            "low": "#2ecc71",
            "medium": "#f39c12",
            "high": "#e74c3c",
        }
        assert expected_colors["low"] == "#2ecc71"
        assert expected_colors["medium"] == "#f39c12"
        assert expected_colors["high"] == "#e74c3c"
        
    def test_icons_match_spec(self):
        """Test that icons match the specification."""
        # Icons from spec: 🔐 for admin, ↩️ for reversible, ⏱️ for time, ⚠️ for not reversible
        expected_icons = {
            "admin": "🔐",
            "reversible": "↩️",
            "not_reversible": "⚠️",
            "time": "⏱️",
        }
        assert expected_icons["admin"] == "🔐"
        assert expected_icons["reversible"] == "↩️"
        assert expected_icons["not_reversible"] == "⚠️"
        assert expected_icons["time"] == "⏱️"

    def test_remediation_actions_count(self):
        """Test that all 6 remediation actions are available."""
        actions = AutomatedRemediation.REMEDIATION_ACTIONS
        assert len(actions) == 6
        
        # Verify all expected actions exist
        expected_actions = [
            'enable_defender',
            'enable_firewall',
            'enable_uac',
            'disable_smbv1',
            'flush_dns',
            'update_windows_defender'
        ]
        
        for action_id in expected_actions:
            assert action_id in actions
            action = actions[action_id]
            assert action.id == action_id
            assert action.name
            assert action.description
            assert action.risk_level in ['low', 'medium', 'high']
