# DANGER ZONE Tab Update

## Overview
The "DANGER" tab has been renamed to "DANGER ZONE" and now features a prominent red background to emphasize the critical nature of the operations within.

## Changes Made

### 1. Tab Rename
- **Old Name:** "DANGER"
- **New Name:** "DANGER ZONE"

### 2. Visual Enhancement
- **Background Color:** Dark red (`#8B0000`)
- **Purpose:** Provides clear visual warning to users that they are entering a dangerous area

### 3. Bug Fixes
Fixed 4 instances of `NameError: cannot access free variable 'e' where it is not associated with a value in enclosing scope`:
- `_backup_registry()` method - line 263
- `_do_restore()` method - line 352
- `_undo_last_change()` method - line 389
- `_apply_tweak()` method - line 447

**Solution:** Captured exception message in local variable before defining lambda callback:
```python
except RegistryError as e:
    logger.error(f"Operation failed: {e}")
    error_msg = str(e)  # Capture before lambda
    self.parent.after(
        0,
        lambda: messagebox.showerror("Error", f"Failed: {error_msg}")  # Use captured value
    )
```

## Visual Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  🖥️ Hayward Tech Suite                                v1.0.0  │
├──────────────────────────────────────────────────────────────────┤
│  [Monitoring] [Diagnostics] [Maintenance] [Security]             │
│  [DANGER ZONE]  <-- Red background tab                           │
├──────────────────────────────────────────────────────────────────┤
│  ╔══════════════════════════════════════════════════════════╗   │
│  ║  ⚠️ DANGER ZONE ⚠️                                        ║   │
│  ║  WARNING: The registry tweaks in this section can        ║   │
│  ║  potentially break Windows functionality.                ║   │
│  ║  Proceed at your own risk! A registry backup is          ║   │
│  ║  automatically created before each change.               ║   │
│  ╚══════════════════════════════════════════════════════════╝   │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ Registry Backup & Restore                              │     │
│  │                                                         │     │
│  │ [📦 Backup Registry Now]  [↩️ Restore Registry]         │     │
│  │ [⏪ Undo Last Change]                                   │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ Windows 11 Registry Tweaks                             │     │
│  │                                                         │     │
│  │ 📂 Privacy                                              │     │
│  │   [HIGH]  Disable Telemetry                   [Apply]  │     │
│  │   [MEDIUM] Disable Cortana                    [Apply]  │     │
│  │                                                         │     │
│  │ 📂 Performance                                          │     │
│  │   [LOW]   Disable Startup Delay               [Apply]  │     │
│  │   [MEDIUM] Disable Transparency Effects       [Apply]  │     │
│  │                                                         │     │
│  │ ... (more tweaks) ...                                  │     │
│  └────────────────────────────────────────────────────────┘     │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ Registry Backup History                                │     │
│  │ ┌────────────────────────────────────────────────┐     │     │
│  │ │ 📦 reg_backup_20260207_101846                  │     │     │
│  │ │    Date: 2026-02-07 10:18:46                   │     │     │
│  │ │    Description: Manual backup                  │     │     │
│  │ │    Keys: HKCU\Software\...                     │     │     │
│  │ │ ──────────────────────────────────────────     │     │     │
│  │ └────────────────────────────────────────────────┘     │     │
│  │                [🔄 Refresh History]                     │     │
│  └────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────┘
│ Ready                                                             │
└───────────────────────────────────────────────────────────────────┘
```

## Color Scheme

The DANGER ZONE tab uses a dark red background (`#8B0000`) which is applied directly to the tab frame:

```python
# In main_window.py
self.tabview.add("DANGER ZONE")
tab_frame = self.tabview.tab("DANGER ZONE")
tab_frame.configure(fg_color="#8B0000")  # Dark red background
```

The header within the tab also has a matching dark red background for consistency:

```python
# In danger_tab.py
header_frame = ctk.CTkFrame(self.parent, fg_color="#8B0000")  # Dark red
```

## Safety Features

The DANGER ZONE tab maintains all safety features:

1. **Automatic Backups:** Registry backup created before every change
2. **Risk Level Indicators:** 
   - `[LOW]` - Green indicator
   - `[MEDIUM]` - Orange indicator
   - `[HIGH]` - Red indicator
3. **Confirmation Dialogs:** Required for all operations
4. **Undo Functionality:** One-click undo for last change
5. **Backup History:** Complete tracking of all backups
6. **Restart Notifications:** Warnings when restart required

## Related Files Modified

- `src/gui/main_window.py` - Added DANGER ZONE tab with red background
- `src/gui/tabs/danger_tab.py` - Fixed 4 NameError bugs
- `src/gui/tabs/__init__.py` - Removed BackupTab
- `src/core/__init__.py` - Removed backup_manager
- `README.md` - Updated feature list and structure

## Related Files Deleted

- `src/gui/tabs/backup_tab.py` - General backup/restore feature removed
- `src/core/backup_manager.py` - General backup manager removed

## Testing Notes

When testing the DANGER ZONE tab:

1. Verify the tab appears with "DANGER ZONE" name
2. Confirm the tab has a dark red background
3. Test that all registry operations work without NameError
4. Verify confirmation dialogs appear
5. Test automatic backup before tweaks
6. Test undo functionality
7. Verify backup history displays correctly

## User Impact

- **Positive:** More obvious warning that the tab contains dangerous operations
- **Positive:** No more runtime errors from NameError bugs
- **Neutral:** "DANGER" renamed to "DANGER ZONE" (cosmetic change)
- **Neutral:** General backup/restore feature removed as per requirements
