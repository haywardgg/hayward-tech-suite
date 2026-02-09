"""
Test registry manager enhancements.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.registry_manager import RegistryManager


def test_max_backups_constant():
    """Test that MAX_REGISTRY_BACKUPS constant exists."""
    rm = RegistryManager()
    assert hasattr(rm, 'MAX_REGISTRY_BACKUPS')
    assert rm.MAX_REGISTRY_BACKUPS == 10
    print("✓ MAX_REGISTRY_BACKUPS constant exists and equals 10")


def test_cleanup_method_exists():
    """Test that _cleanup_old_backups method exists."""
    rm = RegistryManager()
    assert hasattr(rm, '_cleanup_old_backups')
    assert callable(rm._cleanup_old_backups)
    print("✓ _cleanup_old_backups method exists")


def test_get_tweak_by_id_exists():
    """Test that _get_tweak_by_id method exists."""
    rm = RegistryManager()
    assert hasattr(rm, '_get_tweak_by_id')
    assert callable(rm._get_tweak_by_id)
    print("✓ _get_tweak_by_id method exists")


def test_is_tweak_applied_exists():
    """Test that is_tweak_applied method exists."""
    rm = RegistryManager()
    assert hasattr(rm, 'is_tweak_applied')
    assert callable(rm.is_tweak_applied)
    print("✓ is_tweak_applied method exists")


def test_get_tweak_by_id():
    """Test _get_tweak_by_id returns correct tweak."""
    rm = RegistryManager()
    
    # Get a known tweak
    tweaks = rm.get_available_tweaks()
    if tweaks:
        first_tweak = tweaks[0]
        found_tweak = rm._get_tweak_by_id(first_tweak.id)
        
        assert found_tweak is not None
        assert found_tweak.id == first_tweak.id
        print(f"✓ _get_tweak_by_id correctly returns tweak: {found_tweak.name}")
    
    # Test non-existent tweak
    none_tweak = rm._get_tweak_by_id("non_existent_id")
    assert none_tweak is None
    print("✓ _get_tweak_by_id returns None for non-existent tweak")


def test_is_tweak_applied():
    """Test is_tweak_applied method (returns bool without errors)."""
    rm = RegistryManager()
    
    tweaks = rm.get_available_tweaks()
    if tweaks:
        first_tweak = tweaks[0]
        # Should return False if not applied or True if applied, but shouldn't error
        result = rm.is_tweak_applied(first_tweak.id)
        assert isinstance(result, bool)
        print(f"✓ is_tweak_applied returns bool for tweak: {first_tweak.name} (result: {result})")
    
    # Test non-existent tweak
    result = rm.is_tweak_applied("non_existent_id")
    assert result is False
    print("✓ is_tweak_applied returns False for non-existent tweak")


def test_backup_nonexistent_key():
    """Test backing up a non-existent registry key (should skip gracefully)."""
    import subprocess
    from unittest.mock import patch, Mock
    
    rm = RegistryManager()
    
    # Mock subprocess to simulate non-existent key
    with patch('subprocess.run') as mock_run:
        # First call: reg query fails (key doesn't exist)
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="Key not found")
        
        # Should not raise an error, but return a backup_id
        backup_id = rm.backup_registry(
            description="Test backup",
            registry_keys=["HKEY_CURRENT_USER\\Software\\NonExistent\\Key"]
        )
        
        assert backup_id is not None
        assert backup_id.startswith("reg_backup_")
        
        # Check metadata was saved
        assert backup_id in rm.metadata
        metadata = rm.metadata[backup_id]
        assert metadata.skipped is True
        
        print(f"✓ backup_registry handles non-existent key gracefully: {backup_id}")


def test_restore_skipped_backup():
    """Test restoring a skipped backup (should not error)."""
    from unittest.mock import patch, Mock
    
    rm = RegistryManager()
    
    # First, create a skipped backup
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="Key not found")
        
        backup_id = rm.backup_registry(
            description="Test backup",
            registry_keys=["HKEY_CURRENT_USER\\Software\\NonExistent\\Key"]
        )
    
    # Now try to restore it
    result = rm.restore_registry(backup_id)
    
    # Should return True (success) even though nothing was restored
    assert result is True
    print(f"✓ restore_registry handles skipped backup gracefully")


if __name__ == "__main__":
    print("Testing Registry Manager Enhancements...\n")
    
    try:
        test_max_backups_constant()
        test_cleanup_method_exists()
        test_get_tweak_by_id_exists()
        test_is_tweak_applied_exists()
        test_get_tweak_by_id()
        test_is_tweak_applied()
        test_backup_nonexistent_key()
        test_restore_skipped_backup()
        
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
