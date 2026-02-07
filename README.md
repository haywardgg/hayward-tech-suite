# 🛠️ Ghosty Toolz Evolved

**Professional Windows System Maintenance Tool v2.0.0**

A comprehensive, secure, and modern system maintenance suite for Windows, completely redesigned with a focus on security, modularity, and user experience.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-blue.svg)](https://www.microsoft.com/windows)

<img width="1920" height="1032" alt="Screenshot1" src="https://github.com/user-attachments/assets/892a0722-d532-4117-9e3b-7bfa0e7c912c" />
<img width="1920" height="1032" alt="Screenshot2" src="https://github.com/user-attachments/assets/e6b29d39-804e-40e7-9f6c-faa400f09d70" />
<img width="1920" height="1032" alt="Screenshot3" src="https://github.com/user-attachments/assets/d734bce9-8cd9-4fa6-8e82-5138ed7f0ecf" />


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

### 💾 **Backup & Restore**
- File and folder backup with compression
- Backup metadata tracking
- Checksum verification
- Automated old backup cleanup

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
│   ├── backup_manager.py
│   ├── security_scanner.py
│   └── monitoring.py
├── gui/                        # User interface
│   ├── main_window.py
│   └── tabs/
└── utils/                      # Utilities
    ├── logger.py
    ├── config.py
    └── validators.py
```

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
- Backup manager
- Real-time monitoring
- Configuration system
- Audit logging

#### Removed ❌
- Mini games
- Background music
- Automatic admin elevation
- Unsafe registry tweaks

See [CHANGELOG.md](CHANGELOG.md) for full details.

---

**Made with ❤️ for system administrators**
