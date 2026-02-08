"""
System Tools Installation tab for installing developer tools.

Provides comprehensive UI for installing common developer tools including
Git, Python, Node.js, WSL, Windows Terminal, VS Code, PowerShell 7, and more.
"""

import subprocess
import customtkinter as ctk
from tkinter import messagebox
import threading
from pathlib import Path
from typing import Optional, Dict, List, Set, Tuple
from datetime import datetime

from src.utils.logger import get_logger
from src.utils.admin_state import AdminState
from src.core.system_tools_installer import (
    SystemToolsInstaller, SystemTool, ToolCategory,
    SystemToolsInstallerError
)

logger = get_logger("system_tools_tab")

# UI Layout Constants
EXPAND_BUTTON_PADDING = 35  # Left padding for category label to appear next to arrow
STATUS_COLUMN = 99  # High column number for status label to ensure right-alignment


class SystemToolsTab:
    """System Tools Installation tab for installing developer tools."""
    
    def __init__(self, parent: ctk.CTkFrame) -> None:
        """Initialize system tools tab."""
        self.parent = parent
        self.installer = SystemToolsInstaller()
        
        # State tracking
        self.selected_tools: Set[str] = set()
        self.tool_checkboxes: Dict[str, ctk.CTkCheckBox] = {}
        self.tool_status_labels: Dict[str, ctk.CTkLabel] = {}
        self.tool_install_buttons: Dict[str, ctk.CTkButton] = {}
        self.category_frames: Dict[str, ctk.CTkFrame] = {}
        self.category_expanded: Dict[str, bool] = {}
        self.expand_buttons: Dict[str, ctk.CTkButton] = {}
        self.is_installing = False
        
        # UI element references
        self.terminal_text: Optional[ctk.CTkTextbox] = None
        self.progress_bar: Optional[ctk.CTkProgressBar] = None
        self.progress_label: Optional[ctk.CTkLabel] = None
        self.status_label: Optional[ctk.CTkLabel] = None
        
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        
        self._create_content()
        
        logger.info("System Tools tab initialized")
    
    def _create_content(self) -> None:
        """Create content area."""
        content_frame = ctk.CTkScrollableFrame(self.parent)
        content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        
        row = 0
        
        # Info section
        row = self._create_info_section(content_frame, row)
        
        # Prerequisites check
        row = self._create_prerequisites_section(content_frame, row)
        
        # Tools selection section
        row = self._create_tools_section(content_frame, row)
        
        # Terminal output section
        row = self._create_terminal_section(content_frame, row)
        
        # Action buttons section
        row = self._create_action_buttons(content_frame, row)
        
        # Status section
        row = self._create_status_section(content_frame, row)
        
        # Initial status check
        self.parent.after(100, self._check_all_tool_status)
    
    def _create_info_section(self, parent: ctk.CTkFrame, start_row: int) -> int:
        """Create info section."""
        info_frame = ctk.CTkFrame(parent, fg_color="#1a472a", corner_radius=10)
        info_frame.grid(row=start_row, column=0, sticky="ew", padx=5, pady=10)
        info_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            info_frame,
            text="SYSTEM TOOLS INSTALLATION",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        title_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")
        
        # Info message
        info_text = (
            "Install common developer tools with a single click. Each tool will be installed "
            "using the Windows Package Manager (winget) or PowerShell commands.\n\n"
            "ℹ️ Some tools may require administrator privileges.\n"
            "ℹ️ Some tools may require a system restart to complete installation.\n"
            "ℹ️ Network connection is required for downloading packages."
        )
        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            text_color="white",
            wraplength=800,
            justify="left"
        )
        info_label.grid(row=1, column=0, padx=20, pady=(5, 15), sticky="w")
        
        return start_row + 1
    
    def _create_prerequisites_section(self, parent: ctk.CTkFrame, start_row: int) -> int:
        """Create prerequisites check section."""
        prereq_frame = ctk.CTkFrame(parent, corner_radius=10)
        prereq_frame.grid(row=start_row, column=0, sticky="ew", padx=5, pady=10)
        prereq_frame.grid_columnconfigure(1, weight=1)
        
        # Section title
        title_label = ctk.CTkLabel(
            prereq_frame,
            text="Prerequisites Check",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")
        
        # Admin status
        admin_label = ctk.CTkLabel(
            prereq_frame,
            text="Administrator Privileges:",
            font=ctk.CTkFont(size=11)
        )
        admin_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        is_admin = AdminState.is_admin()
        admin_status = "✓ Running as Administrator" if is_admin else "⚠️ Not running as Administrator"
        admin_color = "green" if is_admin else "orange"
        
        self.admin_status_label = ctk.CTkLabel(
            prereq_frame,
            text=admin_status,
            font=ctk.CTkFont(size=11),
            text_color=admin_color
        )
        self.admin_status_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Winget availability
        winget_label = ctk.CTkLabel(
            prereq_frame,
            text="Windows Package Manager (winget):",
            font=ctk.CTkFont(size=11)
        )
        winget_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.winget_status_label = ctk.CTkLabel(
            prereq_frame,
            text="Checking...",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.winget_status_label.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # Check winget in background
        self.parent.after(200, self._check_prerequisites)
        
        return start_row + 1
    
    def _check_prerequisites(self) -> None:
        """Check prerequisites in background thread."""
        def task():
            try:
                winget_available = self.installer.check_winget_available()
                
                if winget_available:
                    status_text = "✓ Available"
                    status_color = "green"
                else:
                    status_text = "⚠️ Not available (Install from 'System Tools' below)"
                    status_color = "orange"
                
                self.parent.after(0, lambda: self.winget_status_label.configure(
                    text=status_text,
                    text_color=status_color
                ))
            except Exception as e:
                logger.error(f"Failed to check prerequisites: {e}")
                self.parent.after(0, lambda: self.winget_status_label.configure(
                    text="⚠️ Check failed",
                    text_color="red"
                ))
        
        thread = threading.Thread(target=task, daemon=True)
        thread.start()
    
    def _create_tools_section(self, parent: ctk.CTkFrame, start_row: int) -> int:
        """Create tools selection section."""
        tools_frame = ctk.CTkFrame(parent, corner_radius=10)
        tools_frame.grid(row=start_row, column=0, sticky="ew", padx=5, pady=10)
        tools_frame.grid_columnconfigure(0, weight=1)
        
        # Section title
        title_label = ctk.CTkLabel(
            tools_frame,
            text="Available Tools",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Create category sections
        categories = self.installer.get_all_categories()
        for i, category in enumerate(categories):
            self._create_category_section(tools_frame, i + 1, category)
        
        return start_row + 1
    
    def _create_category_section(self, parent: ctk.CTkFrame, row: int, category: ToolCategory) -> None:
        """Create a collapsible category section."""
        # Category header frame
        category_header = ctk.CTkFrame(parent, fg_color="transparent")
        category_header.grid(row=row, column=0, sticky="ew", padx=10, pady=(10, 0))
        category_header.grid_columnconfigure(1, weight=1)  # Make middle column expand
        
        # Expand/collapse button
        self.category_expanded[category.value] = False  # Start collapsed
        expand_button = ctk.CTkButton(
            category_header,
            text="▶",
            width=30,
            height=30,
            font=ctk.CTkFont(size=14),
            command=lambda c=category: self._toggle_category(c)
        )
        expand_button.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")
        
        # Store reference to expand button
        self.expand_buttons[category.value] = expand_button
        
        # Category label (positioned with padding to appear next to arrow)
        tools_count = len(self.installer.get_tools_by_category(category))
        category_label = ctk.CTkLabel(
            category_header,
            text=f"{category.value} ({tools_count} tools)",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        category_label.grid(row=0, column=0, padx=(EXPAND_BUTTON_PADDING, 5), pady=5, sticky="w")
        
        # Tools container
        tools_container = ctk.CTkFrame(parent, fg_color="transparent")
        tools_container.grid_columnconfigure(0, weight=1)
        
        # Grid the container but hide it since categories start collapsed
        tools_container.grid(row=row + 1, column=0, sticky="ew", padx=20, pady=(5, 5))
        tools_container.grid_remove()  # Hide by default (collapsed state)
        
        self.category_frames[category.value] = tools_container
        
        # Add tools to category
        tools = self.installer.get_tools_by_category(category)
        for i, tool in enumerate(tools):
            self._create_tool_row(tools_container, i, tool)
    
    def _create_tool_row(self, parent: ctk.CTkFrame, row: int, tool: SystemTool) -> None:
        """Create a single tool row."""
        # Tool frame
        tool_frame = ctk.CTkFrame(parent, corner_radius=5, fg_color="#2b2b2b")
        tool_frame.grid(row=row, column=0, sticky="ew", pady=2)
        tool_frame.grid_columnconfigure(0, weight=1)
        
        # Top row: Tool name with badges
        top_frame = ctk.CTkFrame(tool_frame, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 0))
        top_frame.grid_columnconfigure(0, weight=1)  # Tool name expands
        
        # Tool name
        name_label = ctk.CTkLabel(
            top_frame,
            text=tool.name,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        name_label.grid(row=0, column=0, padx=0, pady=0, sticky="w")
        
        # Badge column tracker
        badge_col = 1
        
        # Admin badge if required (inline with name)
        if tool.requires_admin:
            admin_badge = ctk.CTkLabel(
                top_frame,
                text="[Requires Admin]",
                font=ctk.CTkFont(size=11),
                text_color="orange"
            )
            admin_badge.grid(row=0, column=badge_col, padx=(10, 0), pady=0, sticky="w")
            badge_col += 1
        
        # Restart badge if required (inline with name)
        if tool.requires_restart:
            restart_badge = ctk.CTkLabel(
                top_frame,
                text="[May Require Restart]",
                font=ctk.CTkFont(size=11),
                text_color="orange"
            )
            restart_badge.grid(row=0, column=badge_col, padx=(10, 0), pady=0, sticky="w")
        
        # Status label (right side of top row - uses high column number for right-alignment)
        status_label = ctk.CTkLabel(
            top_frame,
            text="Checking...",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        status_label.grid(row=0, column=STATUS_COLUMN, padx=(10, 0), pady=0, sticky="e")
        self.tool_status_labels[tool.id] = status_label
        
        # Bottom row: Description
        desc_label = ctk.CTkLabel(
            tool_frame,
            text=tool.description,
            font=ctk.CTkFont(size=10),
            text_color="gray",
            wraplength=600,
            justify="left",
            anchor="w"
        )
        desc_label.grid(row=1, column=0, padx=10, pady=(2, 0), sticky="w")
        
        # Bottom row: Install button (below everything)
        install_button = ctk.CTkButton(
            tool_frame,
            text="Install",
            width=100,
            height=28,
            command=lambda t=tool: self._install_single_tool(t)
        )
        install_button.grid(row=2, column=0, padx=10, pady=(5, 8), sticky="e")
        self.tool_install_buttons[tool.id] = install_button
    
    def _toggle_category(self, category: ToolCategory) -> None:
        """Toggle category expansion."""
        category_name = category.value
        is_expanded = self.category_expanded.get(category_name, False)
        
        if is_expanded:
            # Collapse
            self.category_frames[category_name].grid_remove()
            self.expand_buttons[category_name].configure(text="▶")
            self.category_expanded[category_name] = False
        else:
            # Expand
            self.category_frames[category_name].grid()
            self.expand_buttons[category_name].configure(text="▼")
            self.category_expanded[category_name] = True
    
    def _create_terminal_section(self, parent: ctk.CTkFrame, start_row: int) -> int:
        """Create terminal output section."""
        terminal_frame = ctk.CTkFrame(parent, corner_radius=10)
        terminal_frame.grid(row=start_row, column=0, sticky="ew", padx=5, pady=10)
        terminal_frame.grid_columnconfigure(0, weight=1)
        terminal_frame.grid_rowconfigure(1, weight=1)
        
        # Section title
        title_label = ctk.CTkLabel(
            terminal_frame,
            text="Installation Output",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Terminal textbox
        self.terminal_text = ctk.CTkTextbox(
            terminal_frame,
            height=250,
            font=ctk.CTkFont(family="Consolas", size=10),
            wrap="word"
        )
        self.terminal_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Initial message
        self._append_to_terminal("System Tools Installer ready.\n")
        self._append_to_terminal("Select a tool and click 'Install' to begin.\n\n")
        
        return start_row + 1
    
    def _create_action_buttons(self, parent: ctk.CTkFrame, start_row: int) -> int:
        """Create action buttons section."""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=start_row, column=0, sticky="ew", padx=5, pady=10)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        
        # Refresh status button
        self.refresh_button = ctk.CTkButton(
            button_frame,
            text="Refresh Status",
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._check_all_tool_status
        )
        self.refresh_button.grid(row=0, column=0, padx=5, sticky="ew")
        
        # Clear log button
        clear_button = ctk.CTkButton(
            button_frame,
            text="Clear Log",
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._clear_terminal
        )
        clear_button.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Open Tools folder button
        open_folder_button = ctk.CTkButton(
            button_frame,
            text="Open Programs",
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._open_programs_folder
        )
        open_folder_button.grid(row=0, column=2, padx=5, sticky="ew")
        
        return start_row + 1
    
    def _create_status_section(self, parent: ctk.CTkFrame, start_row: int) -> int:
        """Create status section."""
        status_frame = ctk.CTkFrame(parent, fg_color="transparent")
        status_frame.grid(row=start_row, column=0, sticky="ew", padx=5, pady=10)
        status_frame.grid_columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(status_frame)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.progress_bar.set(0)
        
        # Progress label
        self.progress_label = ctk.CTkLabel(
            status_frame,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.progress_label.grid(row=1, column=0, padx=10, pady=5)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="green"
        )
        self.status_label.grid(row=2, column=0, padx=10, pady=5)
        
        return start_row + 1
    
    def _check_all_tool_status(self) -> None:
        """Check status of all tools."""
        if self.is_installing:
            return
        
        self._append_to_terminal("\n=== Checking tool status ===\n")
        self._update_status("Checking tool status...", "blue")
        
        def task():
            try:
                total_tools = len(self.installer.get_all_tools())
                checked = 0
                
                for tool in self.installer.get_all_tools():
                    checked += 1
                    progress = checked / total_tools
                    
                    self.parent.after(0, lambda p=progress: self.progress_bar.set(p))
                    
                    is_installed, status_msg = self.installer.check_tool_status(tool.id)
                    
                    if is_installed:
                        status_text = "✓ Installed"
                        status_color = "green"
                        button_text = "Reinstall"
                        button_state = "normal"
                    else:
                        status_text = "Not Installed"
                        status_color = "gray"
                        button_text = "Install"
                        button_state = "normal"
                    
                    # Update UI
                    self.parent.after(0, lambda: self._update_tool_ui_state(
                        tool.id, status_text, status_color, button_text, button_state
                    ))
                    
                    self._append_to_terminal(f"{tool.name}: {status_text}\n")
                
                self.parent.after(0, lambda: self.progress_bar.set(0))
                self._append_to_terminal("\n=== Status check complete ===\n\n")
                self._update_status("Ready", "green")
                
            except Exception as e:
                logger.error(f"Failed to check tool status: {e}")
                self._append_to_terminal(f"\nError checking status: {e}\n\n")
                self._update_status("Status check failed", "red")
        
        thread = threading.Thread(target=task, daemon=True)
        thread.start()
    
    def _install_single_tool(self, tool: SystemTool) -> None:
        """Install a single tool."""
        if self.is_installing:
            messagebox.showwarning("Installation In Progress", "Please wait for the current installation to complete.")
            return
        
        # Check admin requirements
        if tool.requires_admin and not AdminState.is_admin():
            result = messagebox.askyesno(
                "Administrator Required",
                f"{tool.name} requires administrator privileges.\n\n"
                "Please restart the application as administrator to install this tool.\n\n"
                "Continue anyway? (Installation may fail)"
            )
            if not result:
                return
        
        # Confirm installation
        confirm_msg = f"Install {tool.name}?\n\n{tool.description}"
        if tool.requires_restart:
            confirm_msg += "\n\n⚠️ System restart may be required after installation."
        
        if not messagebox.askyesno("Confirm Installation", confirm_msg):
            return
        
        self.is_installing = True
        self._append_to_terminal(f"\n=== Installing {tool.name} ===\n")
        self._update_status(f"Installing {tool.name}...", "blue")
        
        # Disable all install buttons
        for button in self.tool_install_buttons.values():
            button.configure(state="disabled")
        self.refresh_button.configure(state="disabled")
        
        def task():
            try:
                def progress_callback(message: str):
                    self._append_to_terminal(f"{message}\n")
                    self.parent.after(0, lambda m=message: self.progress_label.configure(text=m))
                
                success, message = self.installer.install_tool(tool.id, progress_callback)
                
                if success:
                    self._append_to_terminal(f"\n✓ {message}\n")
                    self._update_status(f"{tool.name} installed successfully", "green")
                    
                    # Show post-install message
                    self.parent.after(0, lambda: messagebox.showinfo(
                        "Installation Successful",
                        message
                    ))
                    
                    # Update tool status
                    self.parent.after(0, lambda: (
                        self.tool_status_labels[tool.id].configure(text="✓ Installed", text_color="green"),
                        self.tool_install_buttons[tool.id].configure(text="Reinstall")
                    ))
                else:
                    self._append_to_terminal(f"\n✗ Installation failed: {message}\n")
                    self._update_status(f"Installation failed", "red")
                    
                    self.parent.after(0, lambda: messagebox.showerror(
                        "Installation Failed",
                        f"Failed to install {tool.name}:\n\n{message}"
                    ))
            
            except Exception as e:
                logger.error(f"Installation error: {e}")
                self._append_to_terminal(f"\n✗ Error: {e}\n")
                self._update_status("Installation error", "red")
            
            finally:
                self.is_installing = False
                # Re-enable buttons
                for button in self.tool_install_buttons.values():
                    self.parent.after(0, lambda b=button: b.configure(state="normal"))
                self.parent.after(0, lambda: self.refresh_button.configure(state="normal"))
                self.parent.after(0, lambda: self.progress_bar.set(0))
                self.parent.after(0, lambda: self.progress_label.configure(text=""))
        
        thread = threading.Thread(target=task, daemon=True)
        thread.start()
    
    # Helper methods
    
    def _update_tool_ui_state(self, tool_id: str, status_text: str, status_color: str, 
                              button_text: str, button_state: str) -> None:
        """
        Update UI state for a tool.
        
        Args:
            tool_id: Tool identifier
            status_text: Status text to display
            status_color: Color for status text
            button_text: Text for install button
            button_state: State for install button
        """
        if tool_id in self.tool_status_labels:
            self.tool_status_labels[tool_id].configure(text=status_text, text_color=status_color)
        if tool_id in self.tool_install_buttons:
            self.tool_install_buttons[tool_id].configure(text=button_text, state=button_state)
    
    def _append_to_terminal(self, text: str) -> None:
        """Append text to terminal."""
        if self.terminal_text:
            self.terminal_text.insert("end", text)
            self.terminal_text.see("end")
    
    def _clear_terminal(self) -> None:
        """Clear terminal output."""
        if self.terminal_text:
            self.terminal_text.delete("1.0", "end")
            self._append_to_terminal("Terminal cleared.\n\n")
    
    def _update_status(self, message: str, color: str = "white") -> None:
        """Update status label."""
        if self.status_label:
            self.status_label.configure(text=message, text_color=color)
    
    def _open_programs_folder(self) -> None:
        """Open Windows Programs folder."""
        try:
            subprocess.run(['explorer', 'shell:AppsFolder'], check=False)
        except Exception as e:
            logger.error(f"Failed to open programs folder: {e}")
            messagebox.showerror("Error", f"Failed to open programs folder:\n{e}")
