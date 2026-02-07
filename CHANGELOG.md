# Changelog

All notable changes to Ghosty Toolz Evolved will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.1] - 2024-02-06

### Security 🔒

#### Fixed
- **CRITICAL**: Updated `cryptography` from 42.0.2 to 42.0.4
  - Fixes CVE: NULL pointer dereference vulnerability in `pkcs12.serialize_key_and_certificates`
  - Impact: Potential crash when called with non-matching certificate and private key
  - Severity: Medium
  
- **HIGH**: Updated `Pillow` from 10.2.0 to 10.3.0
  - Fixes CVE: Buffer overflow vulnerability
  - Impact: Potential memory corruption and arbitrary code execution
  - Severity: High

## [2.0.0] - 2024-02-06

### 🎉 Complete Rewrite

This version represents a complete architectural redesign of Ghosty Tools, transforming it from a monolithic script into a professional, modular application.

### Added ✨

#### Core Functionality
- **System Operations Module** - Safe, audited command execution with timeout support
- **Backup Manager** - Professional backup/restore with compression and verification
- **Security Scanner** - Vulnerability detection and firewall monitoring
- **Monitoring Service** - Real-time system resource monitoring with callbacks
- **Configuration System** - YAML-based config with environment variable support
- **Logging System** - Color-coded console and file logging with rotation
- **Validation Framework** - Input sanitization and command validation

#### User Interface
- **Modern Tabbed Interface** - Clean, organized layout using CustomTkinter
- **Monitoring Tab** - Real-time CPU, RAM, disk, battery, network displays
- **Maintenance Tab** - DNS flush, restore points, system maintenance
- **Backup Tab** - Create and manage backups with compression
- **Security Tab** - Run vulnerability scans and check firewall
- **Settings Tab** - Configure theme, intervals, and preferences
- **Progress Indicators** - Visual feedback for long-running operations
- **Status Bar** - Real-time status messages

#### Security
- **No Auto-Elevation** - Explicit user consent for admin operations
- **Input Validation** - All commands and paths validated
- **Command Whitelisting** - Only approved commands can execute
- **Audit Logging** - Complete operation history
- **Safe Subprocess Execution** - Timeouts prevent hanging
- **Path Traversal Prevention** - Sanitized file system access
- **Checksum Verification** - Backup integrity checking

#### Developer Experience
- **Type Hints** - Full type annotation throughout codebase
- **Comprehensive Docstrings** - Detailed documentation for all modules
- **Modular Architecture** - Clear separation of concerns
- **Configuration Management** - Centralized settings with defaults
- **Error Handling** - Graceful degradation and user-friendly messages
- **Testing Framework** - pytest setup with coverage reporting

### Removed ❌

#### Features
- Mini games (Click the Target, Tic-Tac-Toe)
- Background music system
- Sound effects and click sounds
- Twitch/GitHub footer links
- Dubious registry tweaks (WiFi Sense, HomeGroup - deprecated)

#### Security Concerns
- Automatic administrator elevation
- Unchecked shell command execution
- Direct registry manipulation without validation
- Unsafe system operations

### Changed 🔄

#### Architecture
- **Before**: Single 1300-line monolithic file
- **After**: Modular structure with 20+ organized modules
- **Before**: Mixed UI and business logic
- **After**: Clear separation between GUI, core, and utilities

#### Security Model
- **Before**: Auto-elevates to admin on startup
- **After**: Requests elevation only when needed with user confirmation
- **Before**: Shell=True for many commands (injection risk)
- **After**: Safe subprocess execution with validation and timeouts

#### User Experience
- **Before**: Cluttered single-window layout
- **After**: Clean tabbed interface with logical grouping
- **Before**: No feedback for long operations
- **After**: Progress indicators and status updates
- **Before**: Hardcoded values
- **After**: Configurable settings with persistence

### Technical Details

#### Dependencies
```
customtkinter==5.2.1      # Modern UI framework
psutil==5.9.8             # System monitoring
PyYAML==6.0.1             # Configuration
python-dotenv==1.0.0      # Environment variables
colorlog==6.8.0           # Colored logging
cryptography==42.0.2      # Security features
reportlab==4.0.9          # Report generation
```

#### Python Version
- **Minimum**: Python 3.8+
- **Recommended**: Python 3.10+

#### Platform
- **Supported**: Windows 10/11 (64-bit recommended)
- **Required**: Some features require administrator privileges

### Migration Guide

#### For Users

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run New Version**:
   ```bash
   python src/main.py
   ```

3. **Configuration**: 
   - Copy `.env.example` to `.env` for custom settings
   - Edit `config/config.yaml` for advanced options

4. **Admin Rights**:
   - No longer auto-elevates
   - Run specific operations that require admin will prompt UAC

#### For Developers

1. **New Structure**:
   ```
   src/
   ├── core/        # Business logic
   ├── gui/         # User interface
   ├── utils/       # Utilities
   └── services/    # External services
   ```

2. **Import Changes**:
   ```python
   # Old (v1.x)
   from ghosty_tools import *
   
   # New (v2.0)
   from src.core.system_operations import SystemOperations
   from src.core.monitoring import MonitoringService
   ```

3. **Configuration**:
   ```python
   # Old: Hardcoded
   INTERVAL = 2
   
   # New: Configurable
   from src.utils.config import get_config
   config = get_config()
   interval = config.get("monitoring.cpu_interval", 2)
   ```

### Known Issues

- Port scanning feature basic (single-threaded)
- Report generation not yet implemented
- Scheduled backup feature planned but not complete
- Some error messages could be more descriptive

### Future Roadmap

#### v2.1.0 (Planned)
- Report generation (PDF/HTML)
- Scheduled maintenance tasks
- Email notifications
- Process manager

#### v2.2.0 (Planned)
- Startup program manager
- Service manager
- Network traffic monitoring
- Advanced restore point management

#### v3.0.0 (Future)
- Plugin system
- Multi-language support
- Cloud backup integration
- Remote monitoring capabilities

---

## [1.x] - Legacy

The original Ghosty Tools version is archived as `Ghosty Tools.py`.

### Features (Legacy)
- System tweaks and optimizations
- Mini games
- Background music
- Network speed test
- Disk operations
- Registry modifications

### Deprecation Notice
Version 1.x is no longer maintained. All users should upgrade to 2.0.0 for:
- Security improvements
- Better stability
- Modern interface
- Active development

---

## Links

- [GitHub Repository](https://github.com/haywardgg/ghosty-toolz-evolved)
- [Issue Tracker](https://github.com/haywardgg/ghosty-toolz-evolved/issues)
- [License](LICENSE)
