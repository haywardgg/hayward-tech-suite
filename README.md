# 🛠️ Ghosty Toolz Evolved

**Professional Windows System Maintenance Tool v2.0.0**

A comprehensive, secure, and modern system maintenance suite for Windows, completely redesigned with a focus on security, modularity, and user experience.

<img width="1920" height="1032" alt="Monitoring_" src="https://github.com/user-attachments/assets/49645e6a-f3f7-4cc7-94be-52fdb4d6f9ba" />
<img width="1920" height="1032" alt="Security_" src="https://github.com/user-attachments/assets/7dbe2a98-c602-4499-9025-3e061ee47aa9" />
<img width="1920" height="1032" alt="PerformanceProfileReport" src="https://github.com/user-attachments/assets/cd639514-3d34-48dd-a2d9-9de156b25fb8" />
<img width="1920" height="1032" alt="Diagnostics" src="https://github.com/user-attachments/assets/e6ecc390-2ec4-403d-b306-47d61d85d2d7" />
<img width="1920" height="1032" alt="Maintenance" src="https://github.com/user-attachments/assets/27cd2d48-7aed-431f-bca2-cf6f29f45282" />
<img width="1920" height="1032" alt="DangerZoneREGISTRY" src="https://github.com/user-attachments/assets/3201f7a2-e9d9-429b-ba42-d9ba0f815d57" />
<img width="1920" height="1032" alt="Screenshot 2026-02-07 171013" src="https://github.com/user-attachments/assets/6682e4e3-f272-4e6d-b992-fcacbdd29720" />

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

### ⚠️ **DANGER ZONE - Registry Tweaks**
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
│       ├── danger_tab.py      # DANGER ZONE
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

---

## ⚠️ DANGER ZONE Warning

**The DANGER ZONE tab contains advanced registry tweaks that can modify Windows system behavior.**

**Important Safety Information:**
- 🔴 **HIGH risk tweaks** can cause system instability
- 📦 **Automatic backups** are created before every change
- ↩️ **Undo functionality** available for recent changes
- 💾 **Registry backups** stored in temp folder: `/tmp/ghosty_toolz_registry_backups/`
- ⚠️ **Some tweaks require system restart** to take effect
- 🛡️ **Always test on non-production systems first**

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

### Version 2.0.0

**Complete Rewrite**

#### Added ✨
- Modern tabbed interface
- Security scanner
- Real-time monitoring
- Configuration system
- Audit logging
- Registry tweaks with safety features

#### Removed ❌
- Mini games
- Background music
- Automatic admin elevation
- Unsafe registry tweaks

See [CHANGELOG.md](CHANGELOG.md) for full details.

---

**Made with ❤️ for system administrators**
