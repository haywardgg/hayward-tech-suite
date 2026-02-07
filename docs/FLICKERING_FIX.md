# Fix for Console Window Flickering in Compiled .exe

## Problem
When the compiled .exe application runs, there's significant flickering caused by console windows flashing open and closed rapidly. This is particularly noticeable during:
- Application startup
- Monitoring operations (continuously running background processes)
- System operations (DNS flush, registry queries, etc.)

The flickering occurs because subprocess calls on Windows create visible console windows by default.

## Root Cause
On Windows, when Python's `subprocess` module runs external commands (like `ipconfig`, `reg.exe`, `route`, etc.), it creates a new console window for each command. Even though these windows only exist for milliseconds, they cause visible flickering.

## Solution
Use the `subprocess.CREATE_NO_WINDOW` flag when creating subprocess calls on Windows. This flag prevents the creation of a visible console window for child processes.

### Implementation Details

1. **Cross-platform compatibility**: The `CREATE_NO_WINDOW` constant is only available on Windows (Python 3.6+). We handle this gracefully:
   ```python
   CREATE_NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
   ```
   - On Windows: Returns the actual flag value (0x08000000)
   - On other platforms: Returns 0 (no effect)

2. **Apply to all subprocess calls**: Added `creationflags=CREATE_NO_WINDOW` parameter to all `subprocess.run()` and `subprocess.Popen()` calls throughout the codebase.

## Files Modified

### Core Modules
1. **src/core/monitoring.py**
   - Added CREATE_NO_WINDOW constant
   - Updated 3 subprocess.run() calls:
     - `route print 0.0.0.0` (for gateway detection)
     - `ipconfig /all` (for DNS servers)
     - `ipconfig /all` (for DHCP status)

2. **src/core/system_operations.py**
   - Added CREATE_NO_WINDOW constant
   - Updated subprocess.run() in execute_command() method
   - Updated subprocess.Popen() for notepad.exe (hosts file editing)

3. **src/core/registry_manager.py**
   - Added CREATE_NO_WINDOW constant
   - Updated 10 subprocess.run() calls for various reg.exe operations:
     - Registry queries
     - Registry exports (backups)
     - Registry imports (restore)
     - Registry modifications (add/delete)

### GUI Modules
4. **src/gui/tabs/maintenance_tab.py**
   - Added CREATE_NO_WINDOW constant
   - Updated 3 subprocess calls:
     - `ipconfig /flushdns` (subprocess.run)
     - `sfc /scannow` (subprocess.Popen)
     - `DISM /Online /Cleanup-Image /RestoreHealth` (subprocess.Popen)

## Testing
All existing tests pass with the new changes:
- test_monitoring.py: ✓ Passed
- test_system_operations.py: ✓ Passed
- test_registry_enhancements.py: ✓ Passed

The creationflags parameter:
- Works correctly on all platforms (0 on non-Windows has no effect)
- Does not break existing functionality
- Successfully prevents console window creation on Windows

## Benefits
1. **No more flickering**: Console windows no longer flash during subprocess calls
2. **Professional appearance**: The compiled .exe looks more polished
3. **Better user experience**: No visual distractions during monitoring operations
4. **Cross-platform safe**: Implementation works on all platforms without errors

## Related Issues
- Monitoring functionality was particularly affected due to continuous subprocess calls
- Startup flickering reduced by eliminating console windows during initialization
- Long-running operations (SFC, DISM) now run without visual artifacts

## Additional Notes
- The CREATE_NO_WINDOW flag only affects Windows; it has no effect on Linux/macOS
- All subprocess calls now use this flag consistently across the codebase
- The flag is applied at the individual subprocess call level for maximum control
- No changes to PyInstaller build configuration were required

## References
- [Python subprocess documentation](https://docs.python.org/3/library/subprocess.html#subprocess.CREATE_NO_WINDOW)
- [subprocess.CREATE_NO_WINDOW constant](https://docs.python.org/3/library/subprocess.html#windows-constants)
