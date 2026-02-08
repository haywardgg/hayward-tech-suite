# 🛠️ Hayward Tech Suite

**Professional Windows System Maintenance Tool v1.0.0**

A comprehensive, secure, and modern system maintenance suite for Windows, completely redesigned with a focus on security, modularity, and user experience.

<img width="1920" height="1032" alt="Monitoring_" src="https://github.com/user-attachments/assets/49645e6a-f3f7-4cc7-94be-52fdb4d6f9ba" />
<img width="1920" height="1032" alt="Security_" src="https://github.com/user-attachments/assets/7dbe2a98-c602-4499-9025-3e061ee47aa9" />
<img width="1920" height="1032" alt="PerformanceProfileReport" src="https://github.com/user-attachments/assets/cd639514-3d34-48dd-a2d9-9de156b25fb8" />
<img width="1920" height="1032" alt="Diagnostics" src="https://github.com/user-attachments/assets/e6ecc390-2ec4-403d-b306-47d61d85d2d7" />
<img width="1920" height="1032" alt="Maintenance" src="https://github.com/user-attachments/assets/27cd2d48-7aed-431f-bca2-cf6f29f45282" />
<img width="1920" height="1032" alt="DangerZoneREGISTRY" src="https://github.com/user-attachments/assets/3201f7a2-e9d9-429b-ba42-d9ba0f815d57" />
<img width="1920" height="1032" alt="Settings__" src="https://github.com/user-attachments/assets/5e3d55b0-83fe-4ef7-a107-6b5a41df1f95" />

---

## ✨ Features

### 🖥️ **System Monitoring**
- Real-time CPU, RAM, and disk usage tracking
- Battery status monitoring
- Network statistics and interface monitoring
- Configurable monitoring intervals

### 🔧 **System Maintenance**
- DNS cache flushing
- System restore point creation
- Comprehensive system maintenance (SFC, DISM)
- Disk health checking
- Safe command execution with validation
- Audit logging for all operations

### 🗑️ **Windows Debloat Tool**
- **Comprehensive bloatware removal** (53 items across 7 categories)
- **Safe, Moderate, and Risky classifications** with color coding
- **Automatic restore point creation** before changes
- **Categories:**
  - Microsoft Store Apps (Xbox, Cortana, Bing apps, etc.)
  - Windows Features (IE11, Media Player, legacy protocols)
  - OneDrive complete removal
  - Telemetry & Privacy settings
  - OEM Bloatware (Dell, HP, Lenovo, Asus, etc.)
  - Windows Services (diagnostic tracking, remote registry)
  - Optional Components (Quick Assist, PowerShell ISE)
- **System scanning** to detect installed bloatware
- **Real-time terminal output** with color-coded logging
- **Preset selection** for safe items only
- **Undo functionality** via system restore
- **Detailed documentation** for each item

### ⚠️ **Registry Hacks**
- **12 common Windows 11 registry tweaks**
- **Automatic backup before every change**
- **One-click undo functionality**
- Risk level indicators (LOW/MEDIUM/HIGH)
- Tweaks organized by category:
  - Privacy (Telemetry, Cortana, Ads)
  - Performance (Startup delay, Transparency, Game Bar)
  - UI (File extensions, Hidden files, Lock screen, Context menu)
  - Security (UAC controls)
  - System (Windows Update)
- Manual registry backup/restore
- Complete backup history tracking
- **All backups saved to temp folder**

### 🔒 **Security Features**
- Vulnerability scanning
- Firewall status monitoring
- Security configuration checks
- UAC and Windows Defender monitoring

### ⚙️ **Settings & Configuration**
- Theme customization (dark/light/system)
- Configurable monitoring intervals
- Persistent settings storage
- **PC Specifications Display** - View detailed system information:
  - Operating System (edition, build, version)
  - CPU (model, cores, threads, frequency)
  - RAM (total, available, usage)
  - Storage (all drives with capacity and type)
  - GPU (model and VRAM)
  - Motherboard (manufacturer and model)
  - Network (hostname and IP addresses)
  - One-click copy to clipboard for support sharing

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Windows 10/11**
- **Administrator privileges** (for some operations)

### Installation

1. Clone and install:
   ```bash
   git clone https://github.com/haywardgg/ghosty-toolz-evolved.git
   cd ghosty-toolz-evolved
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python src/main.py
   ```

---

## 📁 Project Structure

```
src/
├── main.py                     # Entry point
├── core/                       # Core modules
│   ├── system_operations.py
│   ├── security_scanner.py
│   ├── monitoring.py
│   └── registry_manager.py    # Registry operations
├── gui/                        # User interface
│   ├── main_window.py
│   └── tabs/
│       ├── monitoring_tab.py
│       ├── diagnostics_tab.py
│       ├── maintenance_tab.py
│       ├── security_tab.py
│       ├── registry_hacks_tab.py  # Registry Hacks
│       └── settings_tab.py
└── utils/                      # Utilities
    ├── logger.py
    ├── config.py
    └── validators.py
```

---

## 📚 Documentation

- [Registry Backup Management](docs/REGISTRY_BACKUP_MANAGEMENT.md) - Details on registry backup storage, cleanup, and restoration
- [Security Advisory](docs/SECURITY_ADVISORY.md)
- [UI Integration Summary](docs/UI_INTEGRATION_SUMMARY.md)

### 📝 Registry Tweaks Configuration

The application uses `config/registry_tweaks.json` to manage Windows registry modifications. This allows you to customize, add, or remove registry tweaks.

#### JSON Structure

Each registry tweak in the JSON file has the following structure:

```json
{
  "id": "unique_identifier",
  "name": "Display Name",
  "description": "What this tweak does",
  "category": "Privacy|Performance|UI|Security|System",
  "risk_level": "low|medium|high",
  "requires_restart": true|false,
  "apply": {
    "key": "HKEY_LOCAL_MACHINE\\Path\\To\\Key",
    "value_name": "ValueName",
    "value_data": "0",
    "value_type": "REG_DWORD"
  },
  "restore": {
    "key": "HKEY_LOCAL_MACHINE\\Path\\To\\Key",
    "value_name": "ValueName",
    "value_data": "1",
    "value_type": "REG_DWORD"
  }
}
```

#### Field Descriptions

- **id**: Unique identifier for the tweak (lowercase with underscores)
- **name**: Display name shown in the UI
- **description**: Brief explanation of what the tweak does
- **category**: Organizational category (Privacy, Performance, UI, Security, System)
- **risk_level**: Safety indicator
  - `low`: Safe changes (e.g., show file extensions)
  - `medium`: Moderate impact (e.g., disable startup delay)
  - `high`: Significant system changes (e.g., disable Windows Update)
- **requires_restart**: Whether a system restart is needed for changes to take effect
- **apply**: Registry settings to enable the tweak
  - `key`: Full registry path (use double backslashes)
  - `value_name`: Name of the registry value
  - `value_data`: Data to set (string or number)
  - `value_type`: Registry data type (REG_DWORD, REG_SZ, REG_BINARY, etc.)
- **restore**: Registry settings to undo the tweak (same structure as apply)

#### Adding New Tweaks

1. Open `config/registry_tweaks.json`
2. Add your new tweak object to the `tweaks` array:

```json
{
  "id": "my_custom_tweak",
  "name": "My Custom Tweak",
  "description": "Description of what this does",
  "category": "Performance",
  "risk_level": "low",
  "requires_restart": false,
  "apply": {
    "key": "HKEY_CURRENT_USER\\Software\\MyApp",
    "value_name": "EnableFeature",
    "value_data": "1",
    "value_type": "REG_DWORD"
  },
  "restore": {
    "key": "HKEY_CURRENT_USER\\Software\\MyApp",
    "value_name": "EnableFeature",
    "value_data": "0",
    "value_type": "REG_DWORD"
  }
}
```

3. Save the file and restart the application
4. The new tweak will appear in the Registry Hacks tab

#### Removing Tweaks

To remove a tweak:
1. Open `config/registry_tweaks.json`
2. Locate the tweak object by its `id`
3. Delete the entire object (including its opening and closing braces)
4. Ensure proper JSON formatting (no trailing commas)
5. Save and restart the application

#### Important Safety Notes

⚠️ **WARNING: Editing the Windows Registry can be dangerous!**

- **Always backup your registry** before making manual changes
- The application automatically creates backups before applying tweaks
- Test tweaks on non-production systems first
- Some tweaks may cause Windows features to stop working
- Incorrect registry values can make Windows unstable or unbootable
- Use the RESTORE button to undo applied tweaks
- Registry backups are stored in: `%TEMP%\ghosty_toolz_registry_backups\`

#### How Tweaks Are Applied

1. User clicks APPLY button in Registry Hacks tab
2. Application creates automatic backup of current registry value
3. Registry value is changed according to `apply` settings
4. Backup is saved with timestamp for later restoration
5. If `requires_restart` is true, user is notified to restart

#### Effect of Applying Tweaks

- Tweaks modify Windows registry keys to change system behavior
- Changes can affect privacy settings, UI appearance, performance, or system features
- Some tweaks take effect immediately, others require restart
- All changes are reversible using the RESTORE button
- Original values are preserved in automatic backups

---

### 🏗️ Building the Application

You can create a standalone executable (.exe) file that doesn't require Python to be installed.

#### Prerequisites

Install PyInstaller (included in `requirements.txt`):

```bash
pip install -r requirements.txt
```

Or install it separately:

```bash
pip install pyinstaller
```

#### Build Command

Run the build script from the project root:

```bash
python build.py
```

This will:
- Create a standalone executable
- Bundle all dependencies (customtkinter, psutil, etc.)
- Include the `images/` and `config/` folders
- Request UAC admin elevation when launched
- Use windowed mode (no console window)

#### Build Output

After building (takes 1-3 minutes), you'll find:

```
dist/
└── GhostyToolzEvolved/
    ├── GhostyToolzEvolved.exe  ← Main executable
    ├── images/                  ← Bundled images
    ├── config/                  ← Configuration files
    └── [various DLL files]      ← Required libraries
```

#### Build Options

The `build.py` script uses these PyInstaller options:

- `--onedir`: Creates a folder with the exe and dependencies (recommended)
- `--windowed`: No console window (GUI only)
- `--uac-admin`: Prompts for admin elevation on launch
- `--hidden-import`: Ensures critical modules are included
- `--clean`: Cleans cache before building

To customize the build:
1. Edit `build.py`
2. Modify the `args` list
3. Re-run `python build.py`

#### Alternative: One-File Build

For a single executable (slower startup, but portable):

Edit `build.py` and change `--onedir` to `--onefile`:

```python
args = [
    'src/main.py',
    '--onefile',  # ← Changed from --onedir
    '--windowed',
    # ... rest of options
]
```

---

### 📦 Using the Pre-built Application

If you downloaded a pre-built release from the `dist/` folder:

#### Quick Start

1. **Download** the `GhostyToolzEvolved` folder from the `dist/` directory
2. **Extract** to a location of your choice (e.g., `C:\Program Files\GhostyToolz\`)
3. **Run** `GhostyToolzEvolved.exe`
4. **Allow** UAC prompt (admin required for most features)

#### Is It Portable?

✅ **Yes, it's portable!**

- No installation required
- No registry entries (except when using Registry Hacks features)
- Can run from USB drive or any folder
- Settings stored in application directory
- Logs saved to `logs/` subfolder

#### Moving the Application

Simply move the entire `GhostyToolzEvolved` folder to a new location. All settings and configurations will remain intact.

#### Antivirus False Positives

⚠️ **Common Issue**: Antivirus software may flag the executable as suspicious.

**Why this happens:**
- PyInstaller executables are sometimes flagged due to their packing method
- UAC elevation request can trigger heuristic detection
- Registry modification features may be seen as risky

**Solutions:**
1. **Add to exclusions**: Add the folder to your antivirus exclusion list
2. **Build from source**: Compile yourself using `build.py` (see above)
3. **Submit false positive**: Report to your antivirus vendor
4. **Verify integrity**: Check the SHA256 hash against the release notes

**Building from source is always the safest option if you're concerned about security.**

#### Requirements

- **Windows 10/11** (64-bit)
- **No Python installation needed** (everything is bundled)
- **Administrator privileges** for most features

#### Updating

To update to a new version:
1. Download the new release
2. Close the old application
3. Replace the `GhostyToolzEvolved` folder
4. Your settings in `config/config.yaml` will be preserved

---

## ⚠️ Registry Hacks Warning

**The Registry Hacks tab contains advanced registry tweaks that can modify Windows system behavior.**

**Important Safety Information:**
- HIGH risk tweaks can cause system instability
- Automatic backups are created before every change
- Undo functionality available for recent changes
- Registry backups stored in temp folder: `/tmp/ghosty_toolz_registry_backups/`
- Some tweaks require system restart to take effect
- Always test on non-production systems first

**Use at your own risk!** The application provides safety features, but registry modifications can potentially break Windows functionality if misused.

---

## 🔒 Security

- No automatic privilege escalation
- Input validation for all commands
- Safe command execution with timeouts
- Comprehensive audit logging
- Confirmation dialogs for destructive operations

---

## 📝 License

GNU General Public License v3.0 - See [LICENSE](LICENSE)

---

## 📊 Changelog

### Version 1.0.0

**Complete Rewrite**

This has been a complete rewrite of the original code hosted on Ghostshadows Github. 

#### Added ✨
- Modern tabbed interface
- Security scanner
- Real-time monitoring
- Configuration system
- Audit logging
- Registry tweaks with safety 
- System Specs on settings page
- and more...

#### Removed ❌
- Mini games
- Background music
- Automatic admin elevation
- Unsafe registry tweaks

See [CHANGELOG.md](CHANGELOG.md) for full details.

---

**Made with ❤️ for system administrators**

Original concept by Ghostshadow

<img width="896" height="950" alt="ghostytools" src="https://github.com/user-attachments/assets/9c106c09-132e-4e24-aa13-e33b5c11bf63" />
