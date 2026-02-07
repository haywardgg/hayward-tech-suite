# DANGER Tab and Backup Fix Documentation

## Overview

This document describes the implementation of the DANGER tab feature and the fix for the backup/restore functionality.

## New Features

### 1. DANGER Tab

The DANGER tab provides access to advanced Windows 11 registry tweaks with comprehensive safety features.

#### Key Components

**Location**: `src/gui/tabs/danger_tab.py`
**Backend**: `src/core/registry_manager.py`

#### Safety Features

1. **Automatic Backup**: Every registry change automatically creates a backup before modification
2. **Undo Functionality**: Users can undo the last registry change with one click
3. **Risk Level Indicators**: Each tweak is marked as LOW, MEDIUM, or HIGH risk
4. **Warning Messages**: Prominent warnings throughout the interface
5. **Backup History**: All registry backups are tracked and displayed

#### Available Registry Tweaks

The DANGER tab includes 12 common Windows 11 registry tweaks organized by category:

**Privacy (3 tweaks)**:
- Disable Telemetry (LOW risk, requires restart)
- Disable Cortana (LOW risk)
- Disable Start Menu Ads (LOW risk)

**Performance (3 tweaks)**:
- Disable Startup Program Delay (LOW risk, requires restart)
- Disable Transparency Effects (LOW risk)
- Disable Xbox Game Bar (LOW risk)

**UI (4 tweaks)**:
- Show File Extensions (LOW risk)
- Show Hidden Files (LOW risk)
- Disable Lock Screen (LOW risk, requires restart)
- Restore Classic Context Menu (LOW risk)

**Security (1 tweak)**:
- Disable UAC Prompts (HIGH risk, requires restart) ⚠️

**System (1 tweak)**:
- Disable Windows Update (HIGH risk) ⚠️

#### User Interface

**Main Sections**:

1. **Header with Warning**
   - Bright red background with warning icon
   - Clear disclaimer about risks
   - Automatic backup notification

2. **Registry Backup & Restore**
   - Backup Registry Now button
   - Restore Registry button (opens backup selection dialog)
   - Undo Last Change button

3. **Registry Tweaks**
   - Organized by category
   - Each tweak shows:
     - Risk level indicator (colored)
     - Name and description
     - Restart requirement notice
     - Apply button

4. **Backup History**
   - List of all registry backups
   - Timestamps and descriptions
   - Refresh button

#### Registry Backup Location

All registry backups are stored in: `/tmp/ghosty_registry_backups/`

**Backup File Format**: `.reg` files (Windows Registry Editor format)
**Metadata Storage**: `registry_metadata.json` in the backup directory

### 2. Backup/Restore Tab Fix

#### Problem

The original backup/restore tab had a critical bug where:
1. Backups were not going to the user-selected folder
2. The destination was hardcoded to the default backup directory
3. Users couldn't find their backups because the location wasn't clear

#### Root Cause

In `backup_tab.py`, line 153:
```python
destination=str(self.backup_manager.backup_dir),  # Hardcoded!
```

The UI didn't provide a way to select the destination folder.

#### Solution

**Changes Made**:

1. **Added Destination Folder Selector** (`backup_tab.py`):
   - New "Destination Folder" field with text entry
   - Browse button to select destination
   - Default value set to default backup directory
   - Validation to ensure destination is provided

2. **Updated Backup Creation** (`backup_tab.py`):
   - Now uses user-selected destination from UI
   - Success message shows actual backup location
   - Proper error handling for invalid destinations

3. **UI Layout Updated**:
   ```
   - Backup Name: [text field]
   - Destination Folder: [text field] [Browse button]
   - Source Folders: [text area]
   - [Add Folder] [Create Backup]
   ```

#### Benefits

- Users can now choose where backups are saved
- Backup location is clearly displayed after creation
- Fixes confusion about missing backup files
- Maintains backward compatibility with default location

## Technical Implementation

### Registry Manager Class

**Core Methods**:

```python
class RegistryManager:
    def backup_registry(description, registry_keys=None) -> str
    def restore_registry(backup_id) -> bool
    def apply_tweak(tweak_id) -> Tuple[bool, str]
    def undo_last_change() -> bool
    def list_backups() -> List[RegistryBackup]
    def delete_backup(backup_id) -> bool
```

**Key Features**:
- Uses Windows `reg` command for registry operations
- JSON metadata tracking for all backups
- Automatic backup before any modification
- Support for both specific key and full registry backups
- Checksum validation for backup integrity

### Registry Tweak Definition

```python
@dataclass
class RegistryTweak:
    id: str
    name: str
    description: str
    category: str
    registry_key: str
    value_name: str
    value_data: str
    value_type: str  # REG_DWORD, REG_SZ, etc.
    risk_level: str  # low, medium, high
    requires_restart: bool
```

### Safety Pattern

**Before Every Registry Change**:
1. Create backup of affected registry key(s)
2. Store backup metadata with timestamp
3. Apply the registry modification
4. Log operation to audit log
5. Return backup_id for potential undo

**Example**:
```python
# Automatic backup before applying tweak
backup_id = self.backup_registry(
    description=f"Before applying: {tweak.name}",
    registry_keys=[tweak.registry_key]
)

# Apply the tweak
result = subprocess.run([
    "reg", "add", tweak.registry_key,
    "/v", tweak.value_name,
    "/t", tweak.value_type,
    "/d", tweak.value_data,
    "/f"
])

# Return success and backup_id for undo
return True, backup_id
```

## Testing

### Unit Tests

Core functionality tested without GUI:
- ✅ Registry manager initialization
- ✅ 12 registry tweaks loaded correctly
- ✅ Backup destination respects user selection
- ✅ Metadata tracking works properly

### Manual Testing Required

Due to the Windows-specific nature of these features, manual testing on Windows is required for:
1. Registry backup/restore operations
2. Registry tweak application
3. Undo functionality
4. UI interaction and layout
5. File selection dialogs

## Security Considerations

### Risk Mitigation

1. **Automatic Backups**: Every change creates a backup
2. **Risk Level Warnings**: HIGH risk tweaks clearly marked
3. **Audit Logging**: All operations logged to audit.log
4. **Confirmation Dialogs**: User must confirm dangerous operations
5. **Undo Capability**: Easy recovery from mistakes

### High-Risk Tweaks

The following tweaks are marked as HIGH risk:
- **Disable UAC Prompts**: Removes security layer, increases malware risk
- **Disable Windows Update**: Prevents security patches, system vulnerabilities

Users receive additional warnings for these tweaks.

## Usage Guidelines

### For Users

**DANGER Tab**:
1. Read all warnings carefully before proceeding
2. Understand the risk level of each tweak
3. Note which tweaks require system restart
4. Always test changes on non-production systems first
5. Keep track of backups for critical registry modifications

**Backup/Restore**:
1. Select destination folder before creating backup
2. Note the backup location shown in success message
3. Keep backups in accessible, backed-up locations
4. Test restore functionality before relying on it

### For Developers

**Adding New Registry Tweaks**:
1. Add to `_define_tweaks()` in `registry_manager.py`
2. Set appropriate risk_level (low/medium/high)
3. Specify if requires_restart
4. Test thoroughly on development system
5. Document any side effects or dependencies

**Modifying Registry Operations**:
1. Always maintain the backup-before-modify pattern
2. Update audit logging for traceability
3. Handle Windows registry errors gracefully
4. Test on multiple Windows versions if possible

## File Changes

### New Files
- `src/core/registry_manager.py` - Registry operations backend
- `src/gui/tabs/danger_tab.py` - DANGER tab UI

### Modified Files
- `src/gui/main_window.py` - Added DANGER tab integration
- `src/gui/tabs/backup_tab.py` - Fixed destination bug, added UI controls
- `src/core/__init__.py` - Added registry_manager export
- `src/gui/tabs/__init__.py` - Added DangerTab export

## Future Enhancements

### Potential Improvements

1. **Registry Tweak Categories**:
   - Add more tweaks based on user feedback
   - Create customizable tweak profiles
   - Import/export tweak configurations

2. **Backup Management**:
   - Scheduled automatic registry backups
   - Cloud backup integration
   - Backup size optimization

3. **Safety Features**:
   - Registry change simulation/preview
   - Rollback checkpoints
   - System restore point integration

4. **UI Enhancements**:
   - Search/filter tweaks
   - Favorite tweaks
   - Tweak recommendation system

## Troubleshooting

### Common Issues

**Registry Backup Fails**:
- Ensure running with appropriate permissions
- Check disk space in temp folder
- Verify Windows registry service is running

**Tweak Doesn't Apply**:
- Some tweaks require administrator privileges
- Check if registry key path is accessible
- Review logs for specific error messages

**Backup Location Not Found**:
- Check the destination path is valid
- Ensure write permissions to destination folder
- Verify path doesn't contain special characters

## Conclusion

This implementation adds powerful registry modification capabilities with comprehensive safety features and fixes a critical bug in the backup system. The DANGER tab is clearly marked and includes multiple layers of protection to prevent accidental system damage.
