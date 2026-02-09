# Windows 11 Registry Tweaks Documentation

This document provides a comprehensive guide to all registry tweaks available in the Hayward Tech Suite. These tweaks allow you to customize Windows 11 behavior, improve performance, and enhance privacy.

## Table of Contents
- [Overview](#overview)
- [Safety & Backup](#safety--backup)
- [Available Tweaks by Category](#available-tweaks-by-category)
  - [File Explorer & UI](#file-explorer--ui)
  - [System & Performance](#system--performance)
  - [Storage](#storage)
  - [Network](#network)
  - [Security & Privacy](#security--privacy)
  - [Legacy & Compatibility](#legacy--compatibility)
  - [Windows Update](#windows-update)
  - [Miscellaneous](#miscellaneous)
  - [Privacy (Legacy Categories)](#privacy-legacy-categories)
  - [UI (Legacy Categories)](#ui-legacy-categories)
  - [Performance (Legacy Categories)](#performance-legacy-categories)
  - [System (Legacy Categories)](#system-legacy-categories)
  - [Security (Legacy Categories)](#security-legacy-categories)
- [Risk Levels Explained](#risk-levels-explained)
- [Restart Requirements](#restart-requirements)

---

## Overview

The Registry Hacks tab in Hayward Tech Suite provides an easy-to-use interface for applying Windows registry modifications without manually editing the registry. Each tweak can be:

- **Applied**: Activates the registry modification
- **Restored**: Reverts to Windows default settings
- **Backed up**: Automatically backed up before changes (recommended)

⚠️ **Important**: Always create a system restore point before applying registry tweaks, especially those marked as "high" risk.

---

## Safety & Backup

### Before You Start
1. **Create a System Restore Point**: Settings → System → System Protection → Create
2. **Backup Registry**: The application can create automatic backups
3. **Read Risk Levels**: Pay attention to risk ratings before applying tweaks
4. **Check Restart Requirements**: Plan accordingly for tweaks that require a restart

### Restoring Changes
- Use the "Restore" button in the app to revert any tweak to its default state
- If Windows becomes unstable, boot into Safe Mode and restore changes
- Use System Restore if needed to roll back all changes

---

## Available Tweaks by Category

### File Explorer & UI

#### Show Seconds in Taskbar Clock
- **ID**: `show_seconds_clock`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Displays seconds in the system clock on the taskbar. Useful for precise time tracking.
- **Note**: May slightly increase CPU usage due to more frequent updates.

#### Restore Classic Context Menu
- **ID**: `old_context_menu`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Restores the Windows 10 style right-click context menu, removing the simplified Windows 11 menu.
- **Recommendation**: Enable if you prefer the detailed classic menu with all options visible.

#### Disable Search Highlights in Taskbar
- **ID**: `disable_search_highlights`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Disables Bing search highlights and suggested content in the taskbar search box.
- **Privacy Benefit**: Reduces online data collection from search queries.

#### Remove Recommended Section from Start Menu
- **ID**: `remove_recommended_start`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Removes the 'Recommended' section from Windows 11 Start Menu, giving you more space for pinned apps.
- **Tip**: Cleaner Start Menu experience focused on your pinned items.

#### Show All Tray Icons
- **ID**: `show_all_tray_icons`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Shows all system tray icons instead of hiding them in the overflow menu.
- **Use Case**: Helpful if you monitor multiple background applications.

#### Show Taskbar Clock on All Monitors
- **ID**: `taskbar_clock_all_monitors`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Displays the system clock on taskbars of all connected monitors.
- **Multi-Monitor Setup**: Essential for multi-display setups.

#### Show File Extensions
- **ID**: `show_file_extensions`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Always shows file extensions in File Explorer (e.g., .txt, .exe, .jpg).
- **Security**: Helps identify file types and potential malware disguised with double extensions.

#### Show Hidden Files
- **ID**: `show_hidden_files`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Shows hidden files and folders in File Explorer.
- **Caution**: Hidden files are often system files; be careful not to modify them.

#### Disable Lock Screen
- **ID**: `disable_lock_screen`
- **Risk Level**: Low
- **Requires Restart**: Yes
- **Description**: Skips the lock screen on startup, going directly to the login screen.
- **Speed**: Saves a few seconds during boot.

#### Disable Chat Icon
- **ID**: `disable_chat_icon`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Removes the chat/Teams icon from the taskbar.
- **Cleaner UI**: Simplifies taskbar for users who don't use Microsoft Teams.

#### Enable Compact Mode in Explorer
- **ID**: `enable_compact_mode`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Enables compact view mode in File Explorer for Windows 11, showing more items per page.
- **Efficiency**: Better for users who prefer information density over spacing.

---

### System & Performance

#### Enable Hardware-Accelerated GPU Scheduling
- **ID**: `enable_hardware_gpu_scheduling`
- **Risk Level**: Medium
- **Requires Restart**: Yes
- **Description**: Enables hardware GPU scheduling for improved graphics performance.
- **Requirements**: Compatible GPU (NVIDIA RTX 2000+, AMD RX 5000+, Intel Xe Graphics)
- **Benefit**: Can reduce latency and improve performance in games and graphics applications.
- **Note**: May cause issues with older or incompatible GPUs.

#### Disable Tip Notifications and Ads
- **ID**: `disable_tip_notifications`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Disables Windows tips, tricks, and suggestions notifications.
- **Cleaner Experience**: Reduces interruptions from Windows promotional content.

#### Turn Off Windows Spotlight Lock Screen
- **ID**: `disable_spotlight_lockscreen`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Disables Windows Spotlight rotating images on the lock screen.
- **Privacy**: Stops background image downloads and related data collection.

#### Disable Spotlight Lock Screen Overlay
- **ID**: `disable_spotlight_lockscreen_overlay`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Disables the overlay information on Windows Spotlight lock screen.
- **Pairs With**: Use together with `disable_spotlight_lockscreen` for complete disabling.

#### Enable Verbose Startup/Shutdown Status
- **ID**: `enable_verbose_status`
- **Risk Level**: Low
- **Requires Restart**: Yes
- **Description**: Shows detailed status messages during Windows startup and shutdown.
- **Troubleshooting**: Helpful for diagnosing slow boot/shutdown issues.
- **Display**: Shows messages like "Applying user settings", "Loading services", etc.

#### Disable MPO (Multi-Plane Overlay)
- **ID**: `disable_mpo`
- **Risk Level**: Medium
- **Requires Restart**: Yes
- **Description**: Disables Multi-Plane Overlay to fix potential screen flickering and visual issues.
- **When to Use**: If experiencing screen flickering, black screens, or visual artifacts.
- **Compatibility**: Some older applications may have issues with MPO enabled.

#### Disable Startup Program Delay
- **ID**: `disable_startup_delay`
- **Risk Level**: Low
- **Requires Restart**: Yes
- **Description**: Removes 10-second delay for startup programs, allowing them to launch immediately.
- **Faster Boot**: Programs launch as soon as possible after login.

#### Disable Transparency Effects
- **ID**: `disable_transparency`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Disables window transparency and blur effects for better performance.
- **Performance**: Can improve performance on lower-end systems or VMs.

---

### Storage

#### Disable Storage Sense
- **ID**: `disable_storage_sense`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Disables automatic Storage Sense cleanup feature.
- **Manual Control**: Prevents Windows from automatically deleting temporary files and Recycle Bin contents.
- **Recommendation**: Disable if you prefer manual disk cleanup control.

#### Disable Thumbs.db Creation
- **ID**: `disable_thumbs_cache`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Prevents Windows from creating thumbs.db thumbnail cache files.
- **Benefit**: Cleaner folders, especially useful on network drives or USB storage.
- **Trade-off**: Thumbnail generation may be slower without cache.

---

### Network

#### Disable Network Throttling
- **ID**: `disable_network_throttling`
- **Risk Level**: Low
- **Requires Restart**: Yes
- **Description**: Disables Windows network throttling for improved network performance.
- **Use Case**: Can improve network performance for streaming, gaming, or file transfers.
- **Technical**: Sets NetworkThrottlingIndex to maximum (0xFFFFFFFF).

#### Disable LLMNR
- **ID**: `disable_llmnr`
- **Risk Level**: Medium
- **Requires Restart**: Yes
- **Description**: Disables Link-Local Multicast Name Resolution (security enhancement).
- **Security**: LLMNR can be exploited for man-in-the-middle attacks.
- **Enterprise**: Recommended for security-conscious users or enterprise environments.
- **Impact**: May affect local network name resolution in small networks.

---

### Security & Privacy

#### Disable Telemetry
- **ID**: `disable_telemetry`
- **Risk Level**: Low
- **Requires Restart**: Yes
- **Description**: Disables Windows telemetry and data collection.
- **Privacy**: Reduces data sent to Microsoft about system usage and errors.
- **Note**: Some features requiring telemetry may be limited.

#### Disable Cortana
- **ID**: `disable_cortana`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Disables Cortana voice assistant.
- **Privacy**: Stops voice data collection and processing.
- **Resource**: Frees up system resources used by Cortana.

#### Disable SmartScreen for Files/Apps
- **ID**: `disable_smartscreen`
- **Risk Level**: High ⚠️
- **Requires Restart**: No
- **Description**: Disables Windows SmartScreen filter for apps and files.
- **Warning**: Reduces security protection against malware and phishing.
- **Only Use If**: You have alternative antivirus/security software and find SmartScreen intrusive.
- **Not Recommended**: For most users due to security implications.

#### Block Windows Update Automatic Driver Updates
- **ID**: `block_driver_updates`
- **Risk Level**: Medium
- **Requires Restart**: Yes
- **Description**: Prevents Windows Update from automatically installing driver updates.
- **Use Case**: Useful if Windows installs problematic drivers for your hardware.
- **Caution**: You'll need to manually update drivers from manufacturers.

#### Disable Tailored Experiences
- **ID**: `disable_tailored_experiences`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Disables personalized experiences with diagnostic data.
- **Privacy**: Stops Windows from using your diagnostic data for personalized tips and ads.

#### Disable Start Menu Ads
- **ID**: `disable_ads`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Disables suggested apps and ads in Start Menu.
- **Cleaner UI**: Removes app recommendations and promotional content.

#### Disable Windows Copilot
- **ID**: `disable_copilot`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Disables Windows Copilot AI assistant.
- **Privacy**: Prevents AI assistant data collection.
- **Resource**: Frees system resources if you don't use Copilot.

---

### Legacy & Compatibility

#### Restore Old Windows Photo Viewer
- **ID**: `restore_photo_viewer`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Enables the classic Windows Photo Viewer from Windows 7/8.
- **Why**: Many users prefer the simpler, faster classic Photo Viewer.
- **Setup**: After enabling, right-click an image → Open With → Choose Photo Viewer.

#### Disable Windows 11 Snap Layouts Popup
- **ID**: `disable_snap_assist`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Disables the Snap Assist flyout when hovering over the maximize button.
- **Preference**: Useful if you find the popup distracting or prefer manual window snapping.

---

### Windows Update

#### Disable Windows Update (Temporary)
- **ID**: `disable_windows_update`
- **Risk Level**: High ⚠️
- **Requires Restart**: No
- **Description**: Temporarily disables automatic Windows updates.
- **Warning**: Leaves system vulnerable to security exploits.
- **Only Use**: For temporary testing or when an update causes issues.
- **Remember**: Re-enable as soon as possible.

#### Disable Windows Update Automatic Restart
- **ID**: `disable_auto_restart`
- **Risk Level**: Medium
- **Requires Restart**: Yes
- **Description**: Prevents Windows from automatically restarting after updates when users are logged on.
- **Benefit**: Avoids unexpected restarts that interrupt work.
- **Caution**: Remember to manually restart to complete updates.

#### Disable P2P Update Sharing
- **ID**: `disable_p2p_updates`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Disables peer-to-peer Windows Update delivery optimization.
- **Privacy**: Stops your PC from uploading updates to other computers.
- **Bandwidth**: May reduce internet bandwidth usage for uploads.

---

### Miscellaneous

#### Disable Widgets
- **ID**: `disable_widgets`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Disables Windows 11 widgets feature.
- **Performance**: Reduces background processes and resource usage.
- **Taskbar**: Removes widgets button from taskbar.

#### Disable Xbox Game Bar
- **ID**: `disable_game_bar`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Disables Xbox Game Bar overlay.
- **Performance**: Slight performance improvement in games.
- **Note**: Disables Win+G shortcut overlay.

#### Disable Modern Standby
- **ID**: `disable_modern_standby`
- **Risk Level**: High ⚠️
- **Requires Restart**: Yes
- **Description**: Disables Modern Standby (Connected Standby) power mode.
- **When to Use**: If experiencing sleep/wake issues or excessive battery drain.
- **Warning**: Changes fundamental power management; may affect laptop battery life.
- **Not For Everyone**: Only change if experiencing specific issues.

#### Hide 3D Objects Folder
- **ID**: `hide_3d_objects`
- **Risk Level**: Low
- **Requires Restart**: No
- **Description**: Removes the 3D Objects folder from File Explorer navigation pane.
- **Cleaner UI**: Simplifies File Explorer for users who don't use 3D content.

---

### Privacy (Legacy Categories)

These tweaks use the legacy "Privacy" category label from earlier versions.

- **Disable Telemetry** (`disable_telemetry`)
- **Disable Cortana** (`disable_cortana`)
- **Disable Start Menu Ads** (`disable_ads`)
- **Disable Windows Copilot** (`disable_copilot`)

---

### UI (Legacy Categories)

These tweaks use the legacy "UI" category label from earlier versions.

- **Show File Extensions** (`show_file_extensions`)
- **Show Hidden Files** (`show_hidden_files`)
- **Disable Lock Screen** (`disable_lock_screen`)
- **Restore Classic Context Menu** (`old_context_menu`)
- **Disable Chat Icon** (`disable_chat_icon`)
- **Enable Compact Mode in Explorer** (`enable_compact_mode`)
- **Show All Tray Icons** (`show_all_tray_icons`)

---

### Performance (Legacy Categories)

These tweaks use the legacy "Performance" category label from earlier versions.

- **Disable Startup Program Delay** (`disable_startup_delay`)
- **Disable Transparency Effects** (`disable_transparency`)
- **Disable Xbox Game Bar** (`disable_game_bar`)
- **Disable Widgets** (`disable_widgets`)

---

### System (Legacy Categories)

These tweaks use the legacy "System" category label from earlier versions.

- **Disable Windows Update (Temporary)** (`disable_windows_update`)

---

### Security (Legacy Categories)

These tweaks use the legacy "Security" category label from earlier versions.

- **Disable UAC Prompts** (`disable_uac`)

---

## Risk Levels Explained

### Low Risk ✅
- Safe for most users
- Easy to reverse
- Minimal system impact
- Primarily cosmetic or minor behavior changes
- **Examples**: Show file extensions, disable transparency, hide folders

### Medium Risk ⚠️
- Generally safe but requires careful consideration
- May affect system functionality
- Should understand the implications before applying
- **Examples**: Disable LLMNR, block driver updates, disable auto-restart

### High Risk 🛑
- Can significantly affect system security or stability
- Only for advanced users who understand the consequences
- Strong recommendation to backup before applying
- **Examples**: Disable UAC, disable SmartScreen, disable Windows Update, disable Modern Standby

---

## Restart Requirements

### Tweaks Requiring Restart

The following tweaks require a system restart to take effect:

**System & Performance:**
- Enable Hardware-Accelerated GPU Scheduling
- Enable Verbose Startup/Shutdown Status
- Disable MPO (Multi-Plane Overlay)
- Disable Startup Program Delay

**Network:**
- Disable Network Throttling
- Disable LLMNR

**Security & Privacy:**
- Disable Telemetry
- Block Windows Update Automatic Driver Updates

**Windows Update:**
- Disable Windows Update Automatic Restart

**Miscellaneous:**
- Disable Modern Standby

**Legacy Category:**
- Disable Lock Screen
- Disable UAC Prompts

### No Restart Required

All other tweaks take effect immediately or after restarting File Explorer (which the application handles automatically).

---

## Tips & Best Practices

### 1. Start Small
Begin with low-risk UI tweaks to get comfortable with the system before applying system-level changes.

### 2. Test in Phases
Apply tweaks one at a time or in small groups so you can identify which changes work best for you.

### 3. Document Changes
Keep a list of which tweaks you've enabled in case you need to troubleshoot later.

### 4. Regular Backups
Even with restore functionality, maintain regular system backups using Windows Backup or third-party tools.

### 5. Research Before Applying
If unsure about a tweak, research its effects online or ask in Windows communities.

### 6. Monitor Performance
After applying performance tweaks, monitor your system to ensure improvements match expectations.

### 7. Windows Updates
Some tweaks may be reset after major Windows updates. Check your preferred tweaks after updates.

---

## Troubleshooting

### Tweak Doesn't Work
1. Check if restart is required
2. Verify you have administrator privileges
3. Ensure Windows version supports the tweak
4. Try applying it again

### System Instability After Applying Tweaks
1. Use the Restore button for recently applied tweaks
2. Boot into Safe Mode if Windows won't start normally
3. Use System Restore to roll back to before the changes
4. Check Windows Event Viewer for error messages

### Can't Restore a Tweak
1. Try running the application as Administrator
2. Manually edit the registry using regedit (advanced users only)
3. Use System Restore to a point before the tweak was applied

---

## Registry Backup & Restore

### Automatic Backup
The application can automatically back up registry keys before modification. Enable this in Settings for maximum safety.

### Manual Registry Backup
1. Press Win+R, type `regedit`, press Enter
2. Navigate to the key you want to back up
3. Right-click → Export
4. Save the .reg file to a safe location

### Manual Registry Restore
1. Double-click the saved .reg file
2. Confirm the import
3. Restart Windows if required

---

## Additional Resources

- [Microsoft Registry Documentation](https://learn.microsoft.com/en-us/windows/win32/sysinfo/registry)
- [Windows 11 Privacy Settings Guide](https://support.microsoft.com/en-us/windows/windows-11-privacy-settings-3e83bc66-47c8-4e30-a4b6-9c77a6e9bd26)
- [Windows Sysinternals Tools](https://learn.microsoft.com/en-us/sysinternals/)

---

## Disclaimer

⚠️ **Important Notice**: Modifying the Windows registry can cause system instability if done incorrectly. While this application aims to make the process safer, always:

- Create a system restore point before making changes
- Understand what each tweak does before applying it
- Keep backups of important data
- Use high-risk tweaks only if you understand the implications

The developers of Hayward Tech Suite are not responsible for any damage or data loss resulting from the use of these registry tweaks. Use at your own risk.

---

*Last Updated: 2024*
*Total Tweaks Available: 40*
