#!/usr/bin/env python3
"""
Verification script to demonstrate that command validation errors are fixed.

This script tests the exact commands from the user's error logs to show they
now validate successfully without errors.
"""

from src.utils.validators import Validators, ValidationError

def test_validation():
    """Test commands from the error logs."""
    print("=" * 80)
    print("COMMAND VALIDATION FIX VERIFICATION")
    print("=" * 80)
    print()
    
    validators = Validators()
    
    # Commands from the user's error logs that were failing
    test_cases = [
        {
            "name": "PowerShell with pipes (Windows Defender check)",
            "command": 'powershell -Command "Get-MpComputerStatus | Select-Object AntivirusEnabled, RealTimeProtectionEnabled"',
            "shell": True,
            "should_pass": True,
            "error_was": "Command contains unsafe characters: {';'}"
        },
        {
            "name": "PowerShell with registry path (UAC check)",
            "command": 'powershell -Command "(Get-ItemProperty HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System).EnableLUA"',
            "shell": True,
            "should_pass": True,
            "error_was": "Command contains unsafe characters: {';'}"
        },
        {
            "name": "PowerShell with Windows feature check (SMBv1)",
            "command": 'powershell -Command "(Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol).State"',
            "shell": True,
            "should_pass": True,
            "error_was": "Command contains unsafe characters: {';'}"
        },
        {
            "name": "netsh with pipe to find (Firewall rules count)",
            "command": 'netsh advfirewall firewall show rule name=all dir=in | find /c "Rule Name"',
            "shell": True,
            "should_pass": True,
            "error_was": "Command contains dangerous pattern: [;&|`]"
        },
        {
            "name": "netsh firewall check (basic)",
            "command": "netsh advfirewall show allprofiles",
            "shell": False,
            "should_pass": True,
            "error_was": "Command contains dangerous pattern: [;&|`]"
        },
        {
            "name": "Command injection attempt (should still be blocked)",
            "command": "ipconfig; del /f /s /q C:\\Windows",
            "shell": True,
            "should_pass": False,
            "error_was": "N/A - This should always fail"
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['name']}")
        print(f"  Command: {test['command'][:70]}...")
        print(f"  Previous error: {test['error_was']}")
        
        try:
            validators.validate_command(
                test['command'],
                ['powershell', 'netsh', 'find', 'ipconfig'],
                allow_shell=test['shell']
            )
            result = "PASS"
            success = test['should_pass']
        except ValidationError as e:
            result = f"BLOCKED: {str(e)}"
            success = not test['should_pass']
        
        if success:
            print(f"  ✅ Result: {result} (as expected)")
            passed += 1
        else:
            print(f"  ❌ Result: {result} (unexpected!)")
            failed += 1
        print()
    
    print("=" * 80)
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print("=" * 80)
    print()
    
    if failed == 0:
        print("✅ ALL TESTS PASSED!")
        print("The command validation errors have been successfully fixed.")
        print()
        print("What was fixed:")
        print("  • Pipes (|) are now allowed for shell commands")
        print("  • Semicolons (;) are allowed for PowerShell commands only")
        print("  • PowerShell special characters ({, }, [, ], $, @, `) are allowed")
        print("  • Command injection is still blocked for security")
        print()
        print("See docs/VALIDATION_FIX_SUMMARY.md for more details.")
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please review the failures above.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(test_validation())
