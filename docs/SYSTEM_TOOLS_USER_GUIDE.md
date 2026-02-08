# System Tools Feature - User Guide

## Overview

The **System Tools** tab provides a user-friendly interface for installing common developer tools on Windows with a single click. No more manual downloads, extracting installers, or running multiple setup wizards!

## Features

### 🎯 One-Click Installation
Install popular developer tools instantly using Windows Package Manager (winget) or PowerShell commands.

### 📊 Real-Time Progress
Watch the installation progress in real-time with detailed terminal output showing exactly what's happening.

### ✅ Status Detection
Automatically detects which tools are already installed on your system before you start.

### 🔐 Smart Privilege Handling
- Automatically checks if tools require administrator privileges
- Warns you before installation if admin rights are needed
- Shows which tools need a system restart

### 📁 Organized Categories
Tools are organized into logical categories:
- **Development Environment**: WSL, Docker Desktop
- **Development Tools**: Git, Python, Node.js, VS Code
- **Terminal & Shell**: Windows Terminal, PowerShell 7
- **Package Managers**: winget, Chocolatey

## Available Tools

| Tool | Description | Admin | Restart |
|------|-------------|-------|---------|
| **WSL** | Windows Subsystem for Linux - Run Linux distributions on Windows | ✓ | ✓ |
| **Git** | Version control system with Git Bash and shell integration | ✗ | ✗ |
| **Python** | Python 3 interpreter with pip package manager | ✗ | ✗ |
| **Node.js** | JavaScript runtime with npm package manager | ✗ | ✗ |
| **Windows Terminal** | Modern terminal with tabs and split panes | ✗ | ✗ |
| **VS Code** | Lightweight but powerful source code editor | ✗ | ✗ |
| **PowerShell 7** | Cross-platform PowerShell with new features | ✗ | ✗ |
| **Docker Desktop** | Containerized application development | ✓ | ✓ |
| **winget** | Official Windows package manager | ✗ | ✗ |
| **Chocolatey** | Popular Windows package manager | ✓ | ✗ |

## How to Use

### Step 1: Check Prerequisites
Before installing tools, the tab will automatically check:
- ✓ Are you running as Administrator?
- ✓ Is Windows Package Manager (winget) available?

### Step 2: Browse Available Tools
- Tools are organized by category
- Click the ▼ button to expand/collapse categories
- Each tool shows:
  - Name and description
  - Current status (Installed / Not Installed)
  - Admin badge (👤) if admin privileges required
  - Restart badge (🔄) if restart required

### Step 3: Install a Tool
1. Find the tool you want to install
2. Click the **Install** button
3. Confirm the installation in the dialog
4. Watch the real-time progress in the terminal output
5. Follow any post-installation instructions

### Step 4: Verify Installation
- Use the **🔄 Refresh Status** button to check installation status
- Installed tools show ✓ Installed in green
- Not installed tools show "Not Installed" in gray

## Terminal Output

The terminal section at the bottom shows:
- Installation progress
- Command execution details
- Success/error messages
- Post-installation instructions

### Terminal Actions
- **🗑️ Clear Log**: Clear the terminal output
- **📁 Open Programs**: Open Windows Apps & Features

## Tips & Recommendations

### 🔹 Administrator Privileges
Some tools require administrator privileges:
- WSL (Windows Subsystem for Linux)
- Docker Desktop
- Chocolatey

**Recommendation**: Run the application as Administrator to install these tools.

### 🔹 System Restart
Some tools may require a restart to complete installation:
- WSL (must restart to enable features)
- Docker Desktop (recommended)

### 🔹 Internet Connection
All tools are downloaded from the internet during installation. Ensure you have:
- Active internet connection
- Sufficient bandwidth
- No restrictive firewall rules

### 🔹 Installation Order
For best results, install in this order:
1. **Package Managers**: winget, Chocolatey (if needed)
2. **WSL**: Required before Docker Desktop
3. **Other Tools**: Git, Python, Node.js, etc.

### 🔹 Post-Installation
After installing tools:
1. **Restart your terminal** or IDE to update PATH
2. **Restart your computer** if prompted
3. **Verify installation** by running commands:
   ```
   git --version
   python --version
   node --version
   wsl --status
   ```

## Troubleshooting

### "Administrator Required" Message
**Problem**: Tool requires admin privileges but app isn't running as admin.

**Solution**: 
1. Close the application
2. Right-click the application
3. Select "Run as Administrator"
4. Try installing the tool again

### "Winget Not Available" Warning
**Problem**: Windows Package Manager (winget) is not installed.

**Solution**:
1. Install winget from the System Tools list
2. Or manually install from Microsoft Store: "App Installer"
3. Restart the application

### Installation Fails
**Problem**: Tool installation fails with error.

**Solutions**:
1. Check the terminal output for specific error messages
2. Ensure internet connection is active
3. Try running as Administrator
4. Check if the tool is already installed elsewhere
5. Manually install from the tool's official website

### Tool Shows as "Not Installed" But It Is
**Problem**: Status check doesn't detect installed tool.

**Causes**:
- Tool installed in non-standard location
- Tool not in system PATH
- Different version than expected

**Solution**: 
- Click "Install" anyway (it may upgrade or repair)
- Or manually verify by running the tool's command

## Adding New Tools

Developers can easily add new tools by editing `config/system_tools.json`:

```json
{
  "id": "tool_id",
  "name": "Tool Name",
  "description": "What the tool does",
  "category": "Development Tools",
  "requires_admin": false,
  "requires_restart": false,
  "check_command": "tool --version",
  "install_commands": [
    "winget install --id ToolId -e --source winget --accept-package-agreements --accept-source-agreements"
  ],
  "post_install_message": "Tool installed! Instructions here."
}
```

## Safety & Security

### ✓ Safe Installation Methods
- Uses official Windows Package Manager (winget)
- Executes verified PowerShell commands
- No third-party installers or scripts

### ✓ Transparent Operations
- All commands shown in terminal output
- No hidden operations
- Full visibility into what's being installed

### ✓ User Confirmation
- Installation requires explicit confirmation
- Clear warnings for admin requirements
- Clear warnings for restart requirements

### ✓ Secure Source
- All tools sourced from official repositories
- Winget packages verified by Microsoft
- No modifications to system files

## Known Limitations

1. **Windows Only**: Feature requires Windows 10/11
2. **Internet Required**: Cannot install offline
3. **Winget Dependency**: Most tools use winget (can be installed via tool list)
4. **Admin Rights**: Some tools absolutely require administrator privileges
5. **WSL Dependency**: Docker Desktop requires WSL 2 to be installed first

## Feedback & Support

If you encounter issues:
1. Check the terminal output for error details
2. Verify prerequisites (admin, winget, internet)
3. Check the tool's official documentation
4. Report issues with full error logs

## Version History

- **v1.0** (2026-02-08): Initial release
  - 10 common developer tools
  - 4 categories
  - One-click installation
  - Real-time progress tracking
  - Status detection

---

**Enjoy hassle-free tool installation! 🚀**
