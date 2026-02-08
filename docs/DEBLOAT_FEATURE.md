# Windows Bloatware Removal Tool

## Overview

The **Debloat Windows** feature provides a comprehensive, safe, and user-friendly interface for removing unwanted bloatware from Windows 10 and Windows 11 systems. This tool helps optimize system performance and privacy by removing unnecessary pre-installed applications, services, and features.

## Features

### Core Functionality

1. **Bloatware Detection & Removal**
   - Microsoft Store Apps (Xbox, Cortana, Bing apps, etc.)
   - Windows Features (Internet Explorer, Media Player, legacy protocols)
   - OneDrive uninstallation
   - Telemetry and privacy settings
   - OEM bloatware (Dell, HP, Lenovo, Asus, Acer, etc.)
   - Windows Services (diagnostic tracking, remote registry, etc.)
   - Optional Components (Quick Assist, PowerShell ISE, etc.)

2. **System Protection**
   - Automatic system restore point creation before changes
   - Manual restore point creation
   - Restore point history viewing
   - System restore functionality to undo changes

3. **Safety Features**
   - Three-tier safety classification (Safe, Moderate, Risky)
   - Risk acceptance agreement before operations
   - Administrator privilege checks
   - PowerShell command validation
   - Comprehensive logging of all operations

4. **User Interface**
   - Intuitive collapsible category sections
   - Color-coded safety indicators
   - Real-time operation output terminal
   - Progress tracking
   - Preset selection for safe items only
   - Category-level select/deselect all
   - Detailed item descriptions and tooltips

## Architecture

### Core Module (`src/core/bloat_remover.py`)

The `BloatRemover` class provides:
- PowerShell command execution with proper Windows integration
- System restore point management
- Bloatware detection and validation
- Asynchronous removal operations
- Thread-safe UI callbacks
- Comprehensive error handling

Key Classes:
- `BloatRemover`: Main bloatware removal engine
- `BloatwareItem`: Represents a single removable item
- `BloatwareCategory`: Enum for item categories
- `SafetyLevel`: Enum for safety classification

### Configuration (`config/bloatware_config.json`)

JSON-based configuration defining:
- 53 bloatware items across 7 categories
- PowerShell commands for detection and removal
- Safety levels and compatibility information
- Admin requirements and restart flags
- Windows version compatibility

### UI Tab (`src/gui/tabs/debloat_tab.py`)

The `DebloatTab` class provides:
- Warning disclaimer with risk acceptance
- Restore point management UI
- Categorized bloatware selection
- Real-time terminal output with color coding
- Progress tracking and status updates
- Action buttons for scan, remove, and undo operations

## Usage

### Prerequisites

1. **Administrator Privileges**: Required for most operations
2. **Windows 10/11**: Designed for modern Windows versions
3. **PowerShell**: Must be available (default on Windows)

### Getting Started

1. **Accept Risk Agreement**
   - Read and understand the warning message
   - Check "I understand and accept the risks" to enable features

2. **Create Restore Point** (Highly Recommended)
   - Enable "Create restore point before making changes" checkbox
   - Or manually click "Create Restore Point Now"

3. **Select Items to Remove**
   - Expand categories by clicking the arrow button
   - Use "Select Safe Items Only" for recommended preset
   - Or manually select individual items
   - Use "Select All" / "Deselect All" per category

4. **Scan System** (Optional but Recommended)
   - Click "Scan System" to detect what's installed
   - Progress bar shows scanning status
   - Terminal displays found items

5. **Start Removal**
   - Click "Start Debloat" to begin removal
   - Confirm the operation
   - Monitor progress in terminal output
   - Wait for completion message

6. **Restart if Needed**
   - Some changes require system restart
   - Terminal will indicate if restart is needed

### Undoing Changes

If you need to undo changes:

1. Click "Undo Changes" button
2. Confirm system restore operation
3. System will restore to selected restore point
4. Computer will restart automatically

## Safety Levels

### ✓ Safe (Green)
- Minimal risk to system stability
- Removes non-essential bloatware
- Safe for most users
- Examples: Xbox apps, Solitaire, Cortana, Bing apps

### ⚠ Moderate (Orange)
- May affect some functionality
- Review before removing
- Examples: OneDrive, SMB1 Protocol, Telemetry

### ⚠ Risky (Red)
- Can significantly affect system
- Only for advanced users
- Ensure restore point exists
- Examples: (Currently limited in config)

## Categories

### 📦 Microsoft Store Apps (24 items)
Pre-installed Microsoft Store applications like Xbox, Cortana, Bing apps, Solitaire, Office Hub, etc.

### 🔧 Windows Features (8 items)
Legacy Windows features like Internet Explorer, Media Player, PowerShell 2.0, SMB1 Protocol, etc.

### ☁️ OneDrive (1 item)
Complete OneDrive removal including sync folders

### 🔒 Telemetry & Privacy (3 items)
Privacy-focused registry changes to disable telemetry and data collection

### 🏢 OEM Bloatware (8 items)
Manufacturer-specific bloatware (Dell, HP, Lenovo, Asus, Acer, McAfee, Norton, etc.)

### ⚙️ Windows Services (5 items)
Background services like Remote Registry, Diagnostic Tracking, Xbox services, Fax, etc.

### 📋 Optional Components (4 items)
Windows capabilities like Quick Assist, Steps Recorder, Math Recognizer, PowerShell ISE

## Technical Details

### PowerShell Execution

All operations use PowerShell with:
- `-NoProfile` flag (faster startup)
- `-NonInteractive` mode (no prompts)
- `-ExecutionPolicy Bypass` (allows script execution)
- `CREATE_NO_WINDOW` flag (prevents console flashing)
- Error action `SilentlyContinue` (graceful failures)

### Commands Used

- `Get-AppxPackage` / `Remove-AppxPackage`: Store apps
- `Get-WindowsOptionalFeature` / `Disable-WindowsOptionalFeature`: Windows features
- `Get-WindowsCapability` / `Remove-WindowsCapability`: Optional components
- `Get-Service` / `Stop-Service` / `Set-Service`: Windows services
- `Get-ComputerRestorePoint` / `Checkpoint-Computer`: Restore points
- `Set-ItemProperty` / `New-Item`: Registry modifications

### Thread Safety

All long-running operations run on background threads:
- System scanning
- Bloatware removal
- Restore point operations
- UI callbacks use `parent.after()` for thread-safe updates

### Error Handling

Comprehensive error handling includes:
- PowerShell command validation
- Timeout protection (default 300s)
- Admin privilege checks
- JSON parsing validation
- Graceful degradation on failures
- Detailed error logging

## Logging

All operations are logged to:
- Application log file: `logs/bloat_remover.log`
- UI terminal output with timestamps
- Level indicators: ✓ Success, ✗ Error, ⚠️ Warning, ℹ️ Info

Export logs using "Export Log" button for troubleshooting.

## Known Limitations

1. **Windows Store Reinstallation**: Some apps may return after Windows updates
2. **System Apps**: Certain critical system apps cannot be removed
3. **PowerShell Dependency**: Requires PowerShell to be functional
4. **Restart Requirements**: Many changes need restart to take effect
5. **OEM Variations**: OEM bloatware varies by manufacturer and model

## Troubleshooting

### "Administrator privileges required"
- Run the application as Administrator
- Right-click → "Run as administrator"

### "Failed to create restore point"
- Enable System Restore on C: drive
- Run `rstrui.exe` to verify System Restore is enabled
- Check available disk space (minimum 300MB recommended)

### "PowerShell command failed"
- Verify PowerShell is functional
- Check Windows Update status
- Ensure no pending restarts

### Items not removed
- Check terminal output for specific errors
- Some items may not be installed
- Verify Windows version compatibility

## Best Practices

1. ✅ **Always create a restore point before removal**
2. ✅ **Start with "Select Safe Items Only" preset**
3. ✅ **Run "Scan System" before removal to see what's installed**
4. ✅ **Review terminal output during operations**
5. ✅ **Restart system after removal completes**
6. ✅ **Export logs for troubleshooting**
7. ❌ **Don't select "risky" items unless you know what you're doing**
8. ❌ **Don't interrupt operations in progress**

## Contributing

To add new bloatware items:

1. Edit `config/bloatware_config.json`
2. Add new item with required fields:
   - `id`: Unique identifier
   - `name`: Display name
   - `description`: User-friendly description
   - `category`: One of the 7 categories
   - `safety_level`: safe/moderate/risky
   - `commands`: PowerShell commands (array)
   - `check_command`: Detection command (optional)
   - `requires_admin`: true/false
   - `requires_restart`: true/false
   - `windows_versions`: ["10", "11"]

3. Test thoroughly with restore point

## Security Considerations

- All PowerShell commands use parameterization where possible
- No user input is directly injected into commands
- Admin operations are logged to audit trail
- Commands use error suppression to prevent hangs
- CREATE_NO_WINDOW prevents console injection

## License

This feature is part of Ghosty Toolz Evolved and follows the same license terms.

## Support

For issues or questions:
1. Check terminal output for error messages
2. Export and review log files
3. Verify system restore points are available
4. File an issue on the project repository

---

**⚠️ DISCLAIMER**: This tool modifies system components. While designed with safety in mind, use at your own risk. Always maintain system restore points and backups. The developers are not responsible for any system issues that may occur.
