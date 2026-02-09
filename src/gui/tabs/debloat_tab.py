"""
Debloat Windows tab for bloatware removal.

Provides comprehensive UI for detecting and removing Windows bloatware including
Microsoft Store apps, Windows features, OneDrive, telemetry, OEM bloatware,
services, and optional components.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
from pathlib import Path
from typing import Optional, Dict, List, Set, Tuple
from datetime import datetime

from src.utils.logger import get_logger
from src.utils.admin_state import AdminState
from src.core.bloat_remover import (
    BloatRemover, BloatwareItem, BloatwareCategory,
    SafetyLevel, BloatRemoverError
)
from src.core.restore_point_manager import RestorePointManager

logger = get_logger("debloat_tab")


class DebloatTab:
    """Debloat Windows tab for bloatware removal."""
    
    def __init__(self, parent: ctk.CTkFrame, main_window=None) -> None:
        """Initialize debloat tab."""
        self.parent = parent
        self.main_window = main_window
        self.bloat_remover = BloatRemover()
        
        # Initialize restore point manager with PowerShell executor from bloat_remover
        self.restore_manager = RestorePointManager(
            execute_powershell_func=self.bloat_remover.execute_powershell
        )
        
        # State tracking
        self.selected_items: Set[str] = set()
        self.category_checkboxes: Dict[str, Dict[str, ctk.CTkCheckBox]] = {}
        self.category_frames: Dict[str, ctk.CTkFrame] = {}
        self.category_expanded: Dict[str, bool] = {}
        self.agreement_accepted = False
        self.is_scanning = False
        self.is_removing = False
        
        # UI element references
        self.agreement_checkbox: Optional[ctk.CTkCheckBox] = None
        self.restore_point_info_label: Optional[ctk.CTkLabel] = None
        self.create_restore_btn: Optional[ctk.CTkButton] = None
        self.restore_changes_btn: Optional[ctk.CTkButton] = None
        self.terminal_text: Optional[ctk.CTkTextbox] = None
        self.progress_bar: Optional[ctk.CTkProgressBar] = None
        self.progress_label: Optional[ctk.CTkLabel] = None
        self.status_label: Optional[ctk.CTkLabel] = None
        self.scan_button: Optional[ctk.CTkButton] = None
        self.debloat_button: Optional[ctk.CTkButton] = None
        
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        
        self._create_content()
        
        # Set initial status
        if self.main_window:
            self.main_window.update_status("Ready")
        
        logger.info("Debloat tab initialized")
    
    def _create_content(self) -> None:
        """Create content area."""
        content_frame = ctk.CTkScrollableFrame(self.parent)
        content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        
        row = 0
        
        # Warning disclaimer
        row = self._create_warning_disclaimer(content_frame, row)
        
        # Restore point section
        row = self._create_restore_point_section(content_frame, row)
        
        # Bloatware selection section
        row = self._create_selection_section(content_frame, row)
        
        # Terminal output section
        row = self._create_terminal_section(content_frame, row)
        
        # Action buttons section
        row = self._create_action_buttons(content_frame, row)
        
        # Status section
        # row = self._create_status_section(content_frame, row)
        
        # Update UI state
        self._update_ui_state()
    
    def _create_warning_disclaimer(self, parent: ctk.CTkFrame, start_row: int) -> int:
        """Create warning disclaimer section."""
        warning_frame = ctk.CTkFrame(parent, fg_color="#8B0000", corner_radius=10)
        warning_frame.grid(row=start_row, column=0, sticky="ew", padx=5, pady=10)
        warning_frame.grid_columnconfigure(0, weight=1)
        
        # Warning icon and title
        title_label = ctk.CTkLabel(
            warning_frame,
            text="⚠️  WARNING: SYSTEM MODIFICATION AHEAD  ⚠️",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        title_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")
        
        # Warning message
        warning_text = (
            "Modifying system components can potentially cause instability, break functionality, "
            "or prevent Windows updates. Only proceed if you understand the risks. "
            "The developer is not responsible for any system issues that may occur.\n\n"
            "⚠️ A system restore point is HIGHLY RECOMMENDED before proceeding.\n"
            "⚠️ Some changes may require a system restart to take effect.\n"
            "⚠️ Administrator privileges are required for most operations."
        )
        warning_label = ctk.CTkLabel(
            warning_frame,
            text=warning_text,
            font=ctk.CTkFont(size=12),
            text_color="white",
            wraplength=800,
            justify="left"
        )
        warning_label.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        # Agreement checkbox
        self.agreement_checkbox = ctk.CTkCheckBox(
            warning_frame,
            text="I understand and accept the risks",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white",
            command=self._on_agreement_changed,
         #   fg_color="white",
         #   hover_color="#CCCCCC"
        )
        self.agreement_checkbox.grid(row=2, column=0, padx=20, pady=(5, 15), sticky="w")
        
        return start_row + 1
    
    def _create_restore_point_section(self, parent: ctk.CTkFrame, start_row: int) -> int:
        """Create restore point section."""
        restore_frame = ctk.CTkFrame(parent)
        restore_frame.grid(row=start_row, column=0, sticky="ew", padx=5, pady=5)
        restore_frame.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(
            restore_frame, text="System Restore", font=ctk.CTkFont(size=14, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        info = ctk.CTkLabel(
            restore_frame,
            text="Create restore point before making changes (Requires Admin)",
            font=ctk.CTkFont(size=11),
        )
        info.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Last restore point info label
        self.restore_point_info_label = ctk.CTkLabel(
            restore_frame,
            text="Last restore point: Checking...",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.restore_point_info_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        # Check admin status
        is_admin = AdminState.is_admin()

        # Button frame for side-by-side buttons
        button_frame = ctk.CTkFrame(restore_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        
        self.create_restore_btn = ctk.CTkButton(
            button_frame, 
            text="Create Restore Point", 
            command=self._create_restore_point, 
            width=180,
            state="normal" if is_admin else "disabled"
        )
        self.create_restore_btn.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        self.restore_changes_btn = ctk.CTkButton(
            button_frame, 
            text="Restore Changes", 
            command=self._show_restore_dialog, 
            width=180,
            state="normal" if is_admin else "disabled"
        )
        self.restore_changes_btn.grid(row=0, column=1, padx=(0, 10), sticky="w")
        
        if not is_admin:
            warning_label = ctk.CTkLabel(
                restore_frame,
                text="WARNING: Administrator privileges required for restore operations",
                font=ctk.CTkFont(size=9),
                text_color="orange"
            )
            warning_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        
        # Refresh restore point info after UI is ready
        self.parent.after(100, self._refresh_restore_point_info)
        
        return start_row + 1
    
    def _create_selection_section(self, parent: ctk.CTkFrame, start_row: int) -> int:
        """Create bloatware selection section."""
        selection_frame = ctk.CTkFrame(parent)
        selection_frame.grid(row=start_row, column=0, sticky="ew", padx=5, pady=5)
        selection_frame.grid_columnconfigure(0, weight=1)
        
        # Title and preset button
        header_frame = ctk.CTkFrame(selection_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        header_frame.grid_columnconfigure(1, weight=1)
        
        title = ctk.CTkLabel(
            header_frame,
            text="Select Bloatware to Remove",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        preset_button = ctk.CTkButton(
            header_frame,
            text="Select Safe Items Only",
            command=self._select_safe_preset,
            width=180,
            fg_color="green"
        )
        preset_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Create category sections
        row = 1
        for category in BloatwareCategory:
            category_frame = self._create_category_section(selection_frame, category)
            category_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=3)
            self.category_frames[category.name] = category_frame
            self.category_expanded[category.name] = False
            row += 1
        
        return start_row + 1
    
    def _create_category_section(self, parent: ctk.CTkFrame, category: BloatwareCategory) -> ctk.CTkFrame:
        """Create a collapsible category section."""
        # Main category frame
        category_frame = ctk.CTkFrame(parent)
        category_frame.grid_columnconfigure(0, weight=1)
        
        # Header frame (always visible)
        header_frame = ctk.CTkFrame(category_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)  # Make middle column expand
        
        # Category title with expand/collapse button
        expand_button = ctk.CTkButton(
            header_frame,
            text="▶",
            command=lambda: self._toggle_category(category.name),
            width=30,
            height=30,
            font=ctk.CTkFont(size=14)
        )
        expand_button.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")
        
        # Store reference to expand button
        if not hasattr(self, '_expand_buttons'):
            self._expand_buttons = {}
        self._expand_buttons[category.name] = expand_button
        
        category_label = ctk.CTkLabel(
            header_frame,
            text=category.value,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        category_label.grid(row=0, column=0, padx=(35, 5), pady=5, sticky="w")
        
        # Select all / Deselect all buttons (aligned right)
        select_all_btn = ctk.CTkButton(
            header_frame,
            text="Select All",
            command=lambda: self._select_all_in_category(category),
            width=100,
            height=25,
            font=ctk.CTkFont(size=11)
        )
        select_all_btn.grid(row=0, column=2, padx=2, pady=5, sticky="e")
        
        deselect_all_btn = ctk.CTkButton(
            header_frame,
            text="Deselect All",
            command=lambda: self._deselect_all_in_category(category),
            width=100,
            height=25,
            font=ctk.CTkFont(size=11),
            fg_color="gray"
        )
        deselect_all_btn.grid(row=0, column=3, padx=2, pady=5, sticky="e")
        
        # Items frame (collapsible)
        items_frame = ctk.CTkFrame(category_frame)
        items_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        items_frame.grid_columnconfigure(0, weight=1)
        items_frame.grid_remove()  # Hide by default
        
        # Store reference to items frame
        if not hasattr(self, '_items_frames'):
            self._items_frames = {}
        self._items_frames[category.name] = items_frame
        
        # Add bloatware items
        items = self.bloat_remover.get_items_by_category(category)
        self.category_checkboxes[category.name] = {}
        
        for i, item in enumerate(items):
            self._create_item_checkbox(items_frame, item, i)
        
        return category_frame
    
    def _create_item_checkbox(self, parent: ctk.CTkFrame, item: BloatwareItem, row: int) -> None:
        """Create a checkbox for a bloatware item."""
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        item_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Safety indicator
        safety_colors = {
            SafetyLevel.SAFE: "green",
            SafetyLevel.MODERATE: "orange",
            SafetyLevel.RISKY: "red"
        }
        safety_symbols = {
            SafetyLevel.SAFE: "✓",
            SafetyLevel.MODERATE: "⚠",
            SafetyLevel.RISKY: "⚠"
        }
        
        safety_label = ctk.CTkLabel(
            item_frame,
            text=safety_symbols[item.safety_level],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=safety_colors[item.safety_level],
            width=25
        )
        safety_label.grid(row=0, column=0, padx=2, pady=2)
        
        # Checkbox with item name
        checkbox = ctk.CTkCheckBox(
            item_frame,
            text=item.name,
            font=ctk.CTkFont(size=12),
            command=lambda: self._on_item_toggled(item.id)
        )
        checkbox.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        # Store checkbox reference
        self.category_checkboxes[item.category.name][item.id] = checkbox
        
        # Description label
        desc_text = item.description
        if item.requires_restart:
            desc_text += " (Requires restart)"
        
        desc_label = ctk.CTkLabel(
            item_frame,
            text=desc_text,
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w",
            wraplength=600
        )
        desc_label.grid(row=1, column=1, padx=5, pady=(0, 2), sticky="w")
        
        # Note: Tooltip functionality could be added here in the future
        # Current implementation relies on visible descriptions below each checkbox
    
    def _create_terminal_section(self, parent: ctk.CTkFrame, start_row: int) -> int:
        """Create terminal output section."""
        terminal_frame = ctk.CTkFrame(parent)
        terminal_frame.grid(row=start_row, column=0, sticky="ew", padx=5, pady=5)
        terminal_frame.grid_columnconfigure(0, weight=1)
        
        # Title and buttons
        header_frame = ctk.CTkFrame(terminal_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        header_frame.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(
            header_frame,
            text="Output Log",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        clear_button = ctk.CTkButton(
            header_frame,
            text="Clear Output",
            command=self._clear_terminal,
            width=120,
            height=25
        )
        clear_button.grid(row=0, column=1, padx=5, pady=5)
        
        copy_button = ctk.CTkButton(
            header_frame,
            text="Copy to Clipboard",
            command=self._copy_terminal,
            width=140,
            height=25
        )
        copy_button.grid(row=0, column=2, padx=5, pady=5)
        
        export_button = ctk.CTkButton(
            header_frame,
            text="Export Log",
            command=self._export_log,
            width=120,
            height=25
        )
        export_button.grid(row=0, column=3, padx=5, pady=5)
        
        # Terminal text widget
        self.terminal_text = ctk.CTkTextbox(
            terminal_frame,
            height=250,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="word"
        )
        self.terminal_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Configure text tags for color coding
        # Note: CTkTextbox doesn't support tags like Tkinter Text widget
        # We'll use prefixes instead: [SUCCESS], [ERROR], [WARNING], [INFO]
        
        self._write_terminal("Ready. Select bloatware items and click 'Scan System' to begin.", "info")
        
        return start_row + 1
    
    def _create_action_buttons(self, parent: ctk.CTkFrame, start_row: int) -> int:
        """Create action buttons section."""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=start_row, column=0, sticky="ew", padx=5, pady=5)
        button_frame.grid_columnconfigure(0, weight=1)  # Make column 0 expand to push buttons right
        
        # Progress bar - full width on its own row
        self.progress_bar = ctk.CTkProgressBar(button_frame)
        self.progress_bar.grid(row=0, column=0, columnspan=4, padx=10, pady=5, sticky="ew")
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(
            button_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.progress_label.grid(row=1, column=0, columnspan=4, padx=10, pady=(0, 5), sticky="w")
        
        # Buttons row - Scan System on left, Start Debloat on right
        self.scan_button = ctk.CTkButton(
            button_frame,
            text="Scan System",
            command=self._scan_system,
            width=150,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
         #   fg_color="blue"
        )
        self.scan_button.grid(row=2, column=0, padx=(10, 5), pady=5, sticky="w")
        
        self.debloat_button = ctk.CTkButton(
            button_frame,
            text="Start Debloat",
            command=self._start_debloat,
            width=150,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
        #    fg_color="red"
        )
        self.debloat_button.grid(row=2, column=2, padx=5, pady=5, sticky="e")
        
        return start_row + 1
    
    def _create_status_section(self, parent: ctk.CTkFrame, start_row: int) -> int:
        """Create status section."""
        status_frame = ctk.CTkFrame(parent)
        status_frame.grid(row=start_row, column=0, sticky="ew", padx=5, pady=5)
        status_frame.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(
            status_frame,
            text="Status",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready to scan or remove bloatware.",
            font=ctk.CTkFont(size=12),
            anchor="w",
            justify="left"
        )
        self.status_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        return start_row + 1
    
    def _on_agreement_changed(self) -> None:
        """Handle agreement checkbox change."""
        self.agreement_accepted = self.agreement_checkbox.get() == 1
        self._update_ui_state()
    
    def _on_item_toggled(self, item_id: str) -> None:
        """Handle item checkbox toggle."""
        # Update selected items set
        checkbox = None
        for category_checkboxes in self.category_checkboxes.values():
            if item_id in category_checkboxes:
                checkbox = category_checkboxes[item_id]
                break
        
        if checkbox:
            if checkbox.get() == 1:
                self.selected_items.add(item_id)
            else:
                self.selected_items.discard(item_id)
        
        self._update_status()
    
    def _toggle_category(self, category_name: str) -> None:
        """Toggle category expansion."""
        is_expanded = self.category_expanded[category_name]
        
        if is_expanded:
            # Collapse
            self._items_frames[category_name].grid_remove()
            self._expand_buttons[category_name].configure(text="▶")
            self.category_expanded[category_name] = False
        else:
            # Expand
            self._items_frames[category_name].grid()
            self._expand_buttons[category_name].configure(text="▼")
            self.category_expanded[category_name] = True
    
    def _select_all_in_category(self, category: BloatwareCategory) -> None:
        """Select all items in a category."""
        checkboxes = self.category_checkboxes.get(category.name, {})
        for item_id, checkbox in checkboxes.items():
            checkbox.select()
            self.selected_items.add(item_id)
        self._update_status()
    
    def _deselect_all_in_category(self, category: BloatwareCategory) -> None:
        """Deselect all items in a category."""
        checkboxes = self.category_checkboxes.get(category.name, {})
        for item_id, checkbox in checkboxes.items():
            checkbox.deselect()
            self.selected_items.discard(item_id)
        self._update_status()
    
    def _select_safe_preset(self) -> None:
        """Select only safe bloatware items."""
        # First, deselect all
        for category_checkboxes in self.category_checkboxes.values():
            for item_id, checkbox in category_checkboxes.items():
                checkbox.deselect()
                self.selected_items.discard(item_id)
        
        # Then select safe items
        safe_items = self.bloat_remover.get_safe_items()
        for item in safe_items:
            for category_checkboxes in self.category_checkboxes.values():
                if item.id in category_checkboxes:
                    category_checkboxes[item.id].select()
                    self.selected_items.add(item.id)
        
        self._update_status()
        self._write_terminal(f"Selected {len(safe_items)} safe items.", "info")
    
    def _update_ui_state(self) -> None:
        """Update UI elements based on current state."""
        # Enable/disable elements based on agreement
        is_admin = AdminState.is_admin()
        
        if not self.agreement_accepted:
            # Disable everything except agreement checkbox
            if self.scan_button:
                self.scan_button.configure(state="disabled")
            if self.debloat_button:
                self.debloat_button.configure(state="disabled")
            
            # Disable all category checkboxes
            for category_checkboxes in self.category_checkboxes.values():
                for checkbox in category_checkboxes.values():
                    checkbox.configure(state="disabled")
        else:
            # Enable based on operation state (agreement accepted)
            
            if not self.is_scanning and not self.is_removing:
                # Enable scan button when agreement accepted (admin check happens at runtime)
                if self.scan_button:
                    self.scan_button.configure(state="normal")
                # Enable debloat button when agreement accepted and items selected
                if self.debloat_button:
                    self.debloat_button.configure(state="normal")
                
                # Enable checkboxes
                for category_checkboxes in self.category_checkboxes.values():
                    for checkbox in category_checkboxes.values():
                        checkbox.configure(state="normal")
            else:
                # Disable during operations
                if self.scan_button:
                    self.scan_button.configure(state="disabled")
                if self.debloat_button:
                    self.debloat_button.configure(state="disabled")
                
                for category_checkboxes in self.category_checkboxes.values():
                    for checkbox in category_checkboxes.values():
                        checkbox.configure(state="disabled")
    
    def _update_status(self) -> None:
        """Update status label."""
        count = len(self.selected_items)
        if self.main_window:
            if count == 0:
                self.main_window.update_status("No items selected. Select bloatware to remove.")
            else:
                self.main_window.update_status(f"{count} items selected for removal.")
    
    def _write_terminal(self, message: str, level: str = "info") -> None:
        """
        Write message to terminal with color coding.
        
        Args:
            message: Message to write
            level: Level (info/success/warning/error/debug)
        """
        if not self.terminal_text:
            return
        
        # Level prefixes and colors (simulated with text)
        prefixes = {
            "info": "ℹ️",
            "success": "✓",
            "warning": "⚠️",
            "error": "✗",
            "debug": "🔧"
        }
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = prefixes.get(level, "")
        formatted_message = f"[{timestamp}] {prefix} {message}\n"
        
        # Append to text widget
        self.terminal_text.configure(state="normal")
        self.terminal_text.insert("end", formatted_message)
        self.terminal_text.configure(state="disabled")
        
        # Auto-scroll to bottom
        self.terminal_text.see("end")
    
    def _clear_terminal(self) -> None:
        """Clear terminal output."""
        if self.terminal_text:
            self.terminal_text.configure(state="normal")
            self.terminal_text.delete("1.0", "end")
            self.terminal_text.configure(state="disabled")
    
    def _copy_terminal(self) -> None:
        """Copy terminal output to clipboard."""
        if self.terminal_text:
            content = self.terminal_text.get("1.0", "end")
            self.parent.clipboard_clear()
            self.parent.clipboard_append(content)
            messagebox.showinfo("Success", "Output copied to clipboard")
    
    def _export_log(self) -> None:
        """Export terminal log to file."""
        if not self.terminal_text:
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"debloat_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if file_path:
            try:
                content = self.terminal_text.get("1.0", "end")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Log exported to:\n{file_path}")
            except Exception as e:
                logger.error(f"Failed to export log: {e}")
                messagebox.showerror("Error", f"Failed to export log:\n{e}")
    
    def _refresh_restore_point_info(self) -> None:
        """Refresh restore point information."""
        def task():
            try:
                info = self.restore_manager.get_latest_restore_point_info()
                message = f"Last restore point: {info}"

                self.parent.after(0, lambda m=message: self.restore_point_info_label.configure(
                    text=m
                ))

            except Exception as e:
                logger.error(f"Failed to refresh restore points: {e}")
                # Safely update UI with error message
                try:
                    self.parent.after(0, lambda: self.restore_point_info_label.configure(
                        text="Failed to load restore points"
                    ))
                except Exception as ui_error:
                    logger.error(f"Failed to update UI: {ui_error}")

        thread = threading.Thread(target=task, daemon=True)
        thread.start()

    def _scan_system(self) -> None:
        """Scan system for installed bloatware."""
        if not AdminState.is_admin():
            messagebox.showwarning("Warning", "Administrator privileges recommended for accurate scanning")
        
        self.is_scanning = True
        self._update_ui_state()
        self._write_terminal("Starting system scan...", "info")
        
        # Update main window status
        if self.main_window:
            self.main_window.update_status("Scanning system for bloatware...")
        
        def progress_callback(progress: int, message: str):
            self.parent.after(0, lambda: self.progress_bar.set(progress / 100))
            self.parent.after(0, lambda: self.progress_label.configure(text=message))
        
        def completion_callback(results: Dict[str, bool]):
            installed_count = sum(1 for v in results.values() if v)
            total_count = len(results)
            
            # Display detailed scan results
            self.parent.after(0, lambda: self._write_terminal(f"\n{'='*70}", "info"))
            self.parent.after(0, lambda: self._write_terminal(f"Scan Complete: Found {installed_count} out of {total_count} items installed", "success"))
            self.parent.after(0, lambda: self._write_terminal(f"{'='*70}\n", "info"))
            
            # Group results by category and show installed items
            installed_by_category = {}
            for item_id, is_installed in results.items():
                if is_installed and item_id in self.bloat_remover.items:
                    item = self.bloat_remover.items[item_id]
                    category = item.category.value
                    if category not in installed_by_category:
                        installed_by_category[category] = []
                    installed_by_category[category].append(item.name)
            
            # Display installed items by category
            if installed_by_category:
                self.parent.after(0, lambda: self._write_terminal("Installed Items Found:", "info"))
                for category in sorted(installed_by_category.keys()):
                    items = installed_by_category[category]
                    self.parent.after(0, lambda c=category: self._write_terminal(f"\n{c}:", "info"))
                    for item_name in sorted(items):
                        self.parent.after(0, lambda n=item_name: self._write_terminal(f"  • {n}", "info"))
            else:
                self.parent.after(0, lambda: self._write_terminal("No bloatware items found installed on this system.", "success"))
            
            self.parent.after(0, lambda: self._write_terminal(f"\n{'='*70}\n", "info"))
            
            self.parent.after(0, lambda: self.progress_bar.set(0))
            self.parent.after(0, lambda: self.progress_label.configure(text=""))
            
            # Update checkbox states: gray out and disable non-installed items
            def update_checkboxes():
                for item_id, is_installed in results.items():
                    if item_id in self.bloat_remover.items:
                        item = self.bloat_remover.items[item_id]
                        category_name = item.category.name
                        
                        if category_name in self.category_checkboxes:
                            if item_id in self.category_checkboxes[category_name]:
                                checkbox = self.category_checkboxes[category_name][item_id]
                                
                                if not is_installed:
                                    # Item is not installed - gray it out and disable
                                    checkbox.configure(state="disabled", text_color="gray")
                                    # Uncheck if it was checked
                                    checkbox.deselect()
                                    # Remove from selected items
                                    self.selected_items.discard(item_id)
                                else:
                                    # Item is installed - ensure it's enabled
                                    checkbox.configure(state="normal", text_color=("gray10", "gray90"))
            
            self.parent.after(0, update_checkboxes)
            
            self.is_scanning = False
            self.parent.after(0, self._update_ui_state)
            
            # Update main window status
            if self.main_window:
                self.parent.after(0, lambda: self.main_window.update_status(f"Last task completed: Scan found {installed_count} bloatware items"))
        
        self.bloat_remover.scan_system_async(progress_callback, completion_callback)
    
    def _start_debloat(self) -> None:
        """Start bloatware removal process."""
        if not self.selected_items:
            messagebox.showwarning("Warning", "No items selected")
            return
        
        if not AdminState.is_admin():
            messagebox.showerror("Error", "Administrator privileges required for bloatware removal")
            return
        
        # Confirm
        confirm = messagebox.askyesno(
            "Confirm Removal",
            f"Are you sure you want to remove {len(self.selected_items)} selected items?"     
        )
        
        if not confirm:
            return
        
        self.is_removing = True
        self._update_ui_state()
        self._write_terminal(f"Starting removal of {len(self.selected_items)} items...", "info")
        
        # Update main window status
        if self.main_window:
            self.main_window.update_status(f"Removing {len(self.selected_items)} bloatware items...")
        
        def progress_callback(progress: int, message: str):
            self.parent.after(0, lambda: self.progress_bar.set(progress / 100))
            self.parent.after(0, lambda: self.progress_label.configure(text=message))
        
        def output_callback(message: str, level: str):
            self.parent.after(0, lambda: self._write_terminal(message, level))
        
        def completion_callback(results: Dict[str, Tuple[bool, str]]):
            successful = sum(1 for success, _ in results.values() if success)
            failed = len(results) - successful
            
            self.parent.after(0, lambda: self.progress_bar.set(0))
            self.parent.after(0, lambda: self.progress_label.configure(text=""))
            
            # Check if restart needed
            restart_needed = any(
                self.bloat_remover.items[item_id].requires_restart
                for item_id in self.selected_items
                if item_id in self.bloat_remover.items
            )
            
            if restart_needed:
                self.parent.after(0, lambda: self._write_terminal("⚠️ System restart recommended for changes to take effect", "warning"))
            
            # Show completion message
            msg = f"Removal complete:\n{successful} successful, {failed} failed"
            if restart_needed:
                msg += "\n\nSystem restart is recommended."
            
            self.parent.after(0, lambda: messagebox.showinfo("Complete", msg))
            
            self.is_removing = False
            self.parent.after(0, self._update_ui_state)
            
            # Update main window status
            if self.main_window:
                self.parent.after(0, lambda: self.main_window.update_status(f"Last task completed: Removed {successful} bloatware items"))
        
        item_ids = list(self.selected_items)
        self.bloat_remover.remove_items_async(
            item_ids,
            progress_callback,
            output_callback,
            completion_callback
        )
    
    def _create_restore_point(self) -> None:
        """Create system restore point with auto-generated name."""
        logger.info("User initiated restore point creation")
        
        # Disable button and show "Please wait..."
        if self.create_restore_btn:
            self.create_restore_btn.configure(state="disabled", text="Please wait...")

        def task():
            try:
                if not AdminState.is_admin():
                    self.parent.after(0, lambda: messagebox.showerror(
                        "Admin Required",
                        "Administrator privileges are required to create restore points.\n\n"
                        "Please restart the application as administrator."
                    ))
                    # Re-enable button
                    self.parent.after(0, lambda: self.create_restore_btn.configure(
                        state="normal", text="Create Restore Point"
                    ))
                    return

                # Create restore point with auto-generated timestamp name
                success, message = self.restore_manager.create_restore_point()
                
                if success:
                    self.parent.after(0, lambda: messagebox.showinfo(
                        "Success", "Restore point created successfully!"
                    ))
                    # Refresh the restore point info
                    self.parent.after(100, self._refresh_restore_point_info)
                else:
                    self.parent.after(0, lambda m=message: messagebox.showerror(
                        "Error", f"Failed to create restore point:\n{m}"
                    ))
                
                # Re-enable button
                self.parent.after(0, lambda: self.create_restore_btn.configure(
                    state="normal", text="Create Restore Point"
                ))
            except Exception as e:
                logger.error(f"Restore point creation failed: {e}")
                error_msg = str(e)
                self.parent.after(0, lambda ex=error_msg: messagebox.showerror(
                    "Error", f"Failed to create restore point: {ex}"
                ))
                # Re-enable button
                self.parent.after(0, lambda: self.create_restore_btn.configure(
                    state="normal", text="Create Restore Point"
                ))

        threading.Thread(target=task, daemon=True).start()

    def _show_restore_dialog(self) -> None:
        """Show dialog to select and restore from a restore point."""
        if not AdminState.is_admin():
            messagebox.showerror("Error", "Administrator privileges required for system restore")
            return
        
        logger.info("User initiated restore point selection")
        
        def task():
            try:
                # Get available restore points
                restore_points = self.restore_manager.get_restore_points()
                
                if not restore_points:
                    self.parent.after(0, lambda: messagebox.showwarning(
                        "No Restore Points", "No restore points available"
                    ))
                    return
                
                # Show dialog on main thread
                self.parent.after(0, lambda: self._display_restore_selection_dialog(restore_points))
                    
            except Exception as e:
                logger.error(f"Failed to get restore points: {e}")
                error_msg = str(e)
                self.parent.after(0, lambda ex=error_msg: messagebox.showerror(
                    "Error", f"Failed to get restore points:\n{ex}"
                ))
        
        threading.Thread(target=task, daemon=True).start()
    
    def _display_restore_selection_dialog(self, restore_points: list) -> None:
        """Display restore point selection dialog."""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Select Restore Point")
        dialog.geometry("600x500")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Title
        title = ctk.CTkLabel(
            dialog,
            text="Select a Restore Point",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(padx=10, pady=10)
        
        # Warning
        warning = ctk.CTkLabel(
            dialog,
            text="This will restore your system to a previous state.\nAll programs installed after the restore point will be removed.",
            font=ctk.CTkFont(size=11),
            text_color="orange"
        )
        warning.pack(padx=10, pady=5)
        
        # Scrollable frame for restore points
        scroll_frame = ctk.CTkScrollableFrame(dialog, width=550, height=300)
        scroll_frame.pack(padx=10, pady=10, fill="both", expand=True)
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Use list for simpler mutable storage
        selected_sequence = [None]
        # Shared radio button variable for proper grouping
        radio_var = ctk.StringVar(value="")
        
        # Helper function to update selected sequence
        def update_selection(seq):
            selected_sequence[0] = seq
        
        # Create a radio button for each restore point
        for i, rp in enumerate(restore_points):
            sequence = rp.get('SequenceNumber', 0)
            description = rp.get('Description', 'Unknown')
            
            # Frame for each restore point
            rp_frame = ctk.CTkFrame(scroll_frame)
            rp_frame.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            rp_frame.grid_columnconfigure(1, weight=1)
            
            # Radio button - all share the same variable
            # Use lambda with default argument to properly capture the sequence value
            radio = ctk.CTkRadioButton(
                rp_frame,
                text="",
                variable=radio_var,
                value=str(sequence),
                command=lambda seq=sequence: update_selection(seq)
            )
            radio.grid(row=0, column=0, padx=5, pady=5)
            
            # Description label only (no separate date/time)
            desc_label = ctk.CTkLabel(
                rp_frame,
                text=description,
                font=ctk.CTkFont(size=11)
            )
            desc_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
            
            # Auto-select the first (most recent) one
            if i == 0:
                radio.select()
                selected_sequence[0] = sequence
        
        # Button frame
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(padx=10, pady=10)
        
        def perform_restore():
            if selected_sequence[0] is None:
                messagebox.showwarning("No Selection", "Please select a restore point")
                return
            
            # Confirm
            confirm = messagebox.askyesno(
                "Confirm Restore",
                "Are you sure you want to restore your system?\n\n"
                "Your computer will restart automatically.",
                parent=dialog
            )
            
            if not confirm:
                return
            
            dialog.destroy()
            
            # Perform restore
            def restore_task():
                success, message = self.restore_manager.restore_system(selected_sequence[0])
                
                if success:
                    self.parent.after(0, lambda: messagebox.showinfo(
                        "System Restore", 
                        "System restore initiated.\nThe system will restart shortly."
                    ))
                else:
                    self.parent.after(0, lambda m=message: messagebox.showerror(
                        "Error", f"System restore failed:\n{m}"
                    ))
            
            threading.Thread(target=restore_task, daemon=True).start()
        
        # Restore button
        restore_btn = ctk.CTkButton(
            button_frame,
            text="Restore System",
            command=perform_restore,
            width=150,
            fg_color="#d9534f",
            hover_color="#c9302c"
        )
        restore_btn.grid(row=0, column=0, padx=5)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            width=150
        )
        cancel_btn.grid(row=0, column=1, padx=5)
