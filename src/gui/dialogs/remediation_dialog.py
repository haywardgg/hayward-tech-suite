"""
Interactive remediation dialog for Ghosty Toolz Evolved.

Displays all available remediation actions in a modern card-based layout
with individual Execute, Rollback, and Test Run buttons.
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
from typing import List, Optional, Dict

from src.utils.logger import get_logger
from src.core.automated_remediation import (
    AutomatedRemediation,
    RemediationAction,
    RemediationStatus,
)
from src.core.security_scanner import Vulnerability

logger = get_logger("remediation_dialog")


class RemediationDialog(ctk.CTkToplevel):
    """Interactive dialog for managing remediation actions."""

    # Risk level color mapping
    RISK_COLORS = {
        "low": "#2ecc71",      # Green
        "medium": "#f39c12",   # Orange
        "high": "#e74c3c",     # Red
    }

    # Icons
    ICON_ADMIN = "🔐"
    ICON_REVERSIBLE = "↩️"
    ICON_NOT_REVERSIBLE = "⚠️"
    ICON_TIME = "⏱️"

    def __init__(
        self,
        parent: ctk.CTk,
        remediation: AutomatedRemediation,
        vulnerabilities: Optional[List[Vulnerability]] = None,
    ):
        """
        Initialize remediation dialog.

        Args:
            parent: Parent window
            remediation: AutomatedRemediation instance
            vulnerabilities: List of detected vulnerabilities
        """
        super().__init__(parent)

        self.remediation = remediation
        self.vulnerabilities = vulnerabilities or []
        self.action_widgets: Dict[str, Dict] = {}

        # Configure window
        self.title("Remediation Actions")
        self.geometry("900x600")
        self.minsize(800, 500)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._create_header()
        self._create_content()
        self._create_footer()

        # Load actions
        self._load_actions()

        logger.info("Remediation dialog opened")

    def _create_header(self) -> None:
        """Create header section."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(
            header_frame,
            text="🔧 Available Remediation Actions",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title.grid(row=0, column=0, sticky="w")

        # Subtitle
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Execute, rollback, or test remediation actions to fix security issues",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(5, 0))

    def _create_content(self) -> None:
        """Create content area with scrollable action cards."""
        # Content frame with scrollbar
        self.content_frame = ctk.CTkScrollableFrame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.content_frame.grid_columnconfigure(0, weight=1)

    def _create_footer(self) -> None:
        """Create footer with action buttons."""
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 20))
        footer_frame.grid_columnconfigure(0, weight=1)

        # Button container (right-aligned)
        button_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        button_frame.grid(row=0, column=1, sticky="e")

        # Refresh button
        ctk.CTkButton(
            button_frame,
            text="🔄 Refresh",
            command=self._refresh_actions,
            width=120,
            fg_color="gray40",
            hover_color="gray30",
        ).grid(row=0, column=0, padx=5)

        # History button
        ctk.CTkButton(
            button_frame,
            text="📜 History",
            command=self._show_history,
            width=120,
            fg_color="gray40",
            hover_color="gray30",
        ).grid(row=0, column=1, padx=5)

        # Close button
        ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.destroy,
            width=100,
        ).grid(row=0, column=2, padx=5)

    def _load_actions(self) -> None:
        """Load and display all available remediation actions."""
        # Clear existing widgets
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.action_widgets.clear()

        # Get all available actions
        available_actions = self.remediation.get_available_actions(self.vulnerabilities)

        if not available_actions:
            # Show empty state
            empty_label = ctk.CTkLabel(
                self.content_frame,
                text="No remediation actions available.\nRun a vulnerability scan first.",
                font=ctk.CTkFont(size=14),
                text_color="gray",
            )
            empty_label.grid(row=0, column=0, pady=50)
            return

        # Create cards for each action
        for idx, action in enumerate(available_actions):
            card = self._create_action_card(action, idx)
            card.grid(row=idx, column=0, sticky="ew", pady=10)

        logger.info(f"Loaded {len(available_actions)} remediation actions")

    def _create_action_card(self, action: RemediationAction, index: int) -> ctk.CTkFrame:
        """
        Create a card for a single remediation action.

        Args:
            action: RemediationAction to display
            index: Index for grid positioning

        Returns:
            CTkFrame containing the action card
        """
        # Main card frame
        card = ctk.CTkFrame(self.content_frame)
        card.grid_columnconfigure(0, weight=1)

        # Header section
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        header_frame.grid_columnconfigure(1, weight=1)

        # Action name
        name_label = ctk.CTkLabel(
            header_frame,
            text=action.name,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        name_label.grid(row=0, column=0, sticky="w", padx=(0, 10))

        # Risk badge
        risk_color = self.RISK_COLORS.get(action.risk_level, "#f39c12")
        risk_badge = ctk.CTkLabel(
            header_frame,
            text=action.risk_level.upper(),
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="white",
            fg_color=risk_color,
            corner_radius=6,
            padx=10,
            pady=4,
        )
        risk_badge.grid(row=0, column=1, sticky="e")

        # Description
        desc_label = ctk.CTkLabel(
            card,
            text=action.description,
            font=ctk.CTkFont(size=12),
            anchor="w",
            justify="left",
        )
        desc_label.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 10))

        # Info section
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=2, column=0, sticky="w", padx=15, pady=(0, 10))

        info_items = []

        # Admin requirement
        if action.requires_admin:
            info_items.append(f"{self.ICON_ADMIN} Requires Admin")

        # Reversibility
        if action.reversible:
            info_items.append(f"{self.ICON_REVERSIBLE} Reversible")
        else:
            info_items.append(f"{self.ICON_NOT_REVERSIBLE} Not Reversible")

        # Time estimate
        info_items.append(f"{self.ICON_TIME} ~{action.estimated_time}s")

        info_text = "  •  ".join(info_items)
        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(size=11),
            text_color="gray",
        )
        info_label.grid(row=0, column=0, sticky="w")

        # Button section
        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 15))

        # Execute button
        execute_btn = ctk.CTkButton(
            button_frame,
            text="▶ Execute",
            command=lambda: self._execute_action(action.id),
            width=120,
            fg_color=risk_color,
            hover_color=self._darken_color(risk_color),
        )
        execute_btn.grid(row=0, column=0, padx=(0, 10))

        # Rollback button (only if reversible)
        rollback_btn = None
        if action.reversible:
            rollback_btn = ctk.CTkButton(
                button_frame,
                text="↩ Rollback",
                command=lambda: self._rollback_action(action.id),
                width=120,
                fg_color="gray40",
                hover_color="gray30",
            )
            rollback_btn.grid(row=0, column=1, padx=(0, 10))

        # Test Run button
        test_btn = ctk.CTkButton(
            button_frame,
            text="🧪 Test Run",
            command=lambda: self._test_action(action.id),
            width=120,
            fg_color="gray40",
            hover_color="gray30",
        )
        test_btn.grid(row=0, column=2)

        # Store widget references
        self.action_widgets[action.id] = {
            "card": card,
            "execute_btn": execute_btn,
            "rollback_btn": rollback_btn,
            "test_btn": test_btn,
            "original_color": risk_color,
        }

        return card

    def _darken_color(self, color: str, factor: float = 0.8) -> str:
        """
        Darken a hex color.

        Args:
            color: Hex color string
            factor: Darkening factor (0-1)

        Returns:
            Darkened hex color
        """
        # Remove # if present
        color = color.lstrip("#")

        # Convert to RGB
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)

        # Darken
        r, g, b = int(r * factor), int(g * factor), int(b * factor)

        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

    def _execute_action(self, action_id: str) -> None:
        """
        Execute a remediation action.

        Args:
            action_id: ID of action to execute
        """
        logger.info(f"User requested execution: {action_id}")

        # Get action details
        action = self.remediation.REMEDIATION_ACTIONS.get(action_id)
        if not action:
            messagebox.showerror("Error", f"Unknown action: {action_id}")
            return

        # Confirm with user
        confirm_msg = f"Execute: {action.name}\n\n"
        confirm_msg += f"{action.description}\n\n"
        confirm_msg += f"Risk Level: {action.risk_level.upper()}\n"
        confirm_msg += f"Requires Admin: {'Yes' if action.requires_admin else 'No'}\n"
        confirm_msg += f"Reversible: {'Yes' if action.reversible else 'No'}\n\n"
        confirm_msg += "Do you want to proceed?"

        if not messagebox.askyesno("Confirm Execution", confirm_msg):
            logger.info("User cancelled execution")
            return

        # Update button state
        widgets = self.action_widgets.get(action_id)
        if widgets:
            widgets["execute_btn"].configure(
                state="disabled",
                text="⏳ Executing...",
                fg_color="gray50",
            )
            if widgets["rollback_btn"]:
                widgets["rollback_btn"].configure(state="disabled")
            widgets["test_btn"].configure(state="disabled")

        # Execute in background thread
        def task():
            try:
                result = self.remediation.execute_remediation(action_id, dry_run=False)

                # Update UI based on result
                def update_ui():
                    if widgets:
                        if result.status == RemediationStatus.SUCCESS:
                            widgets["execute_btn"].configure(
                                text="✓ Executed",
                                state="disabled",
                                fg_color="#2ecc71",
                            )
                            if widgets["rollback_btn"]:
                                widgets["rollback_btn"].configure(state="normal")
                            messagebox.showinfo(
                                "Success",
                                f"{action.name} completed successfully!\n\n{result.message}",
                            )
                        else:
                            widgets["execute_btn"].configure(
                                text="▶ Execute",
                                state="normal",
                                fg_color=widgets["original_color"],
                            )
                            if widgets["rollback_btn"]:
                                widgets["rollback_btn"].configure(state="normal")
                            messagebox.showerror(
                                "Failed",
                                f"{action.name} failed!\n\n{result.message}\n\nError: {result.error or 'Unknown'}",
                            )

                        widgets["test_btn"].configure(state="normal")

                self.after(0, update_ui)

            except Exception as e:
                logger.error(f"Execution failed: {e}")
                error_msg = str(e)

                def show_error():
                    if widgets:
                        widgets["execute_btn"].configure(
                            text="▶ Execute",
                            state="normal",
                            fg_color=widgets["original_color"],
                        )
                        if widgets["rollback_btn"]:
                            widgets["rollback_btn"].configure(state="normal")
                        widgets["test_btn"].configure(state="normal")

                    messagebox.showerror("Error", f"Execution failed: {error_msg}")

                self.after(0, show_error)

        threading.Thread(target=task, daemon=True).start()

    def _rollback_action(self, action_id: str) -> None:
        """
        Rollback a remediation action.

        Args:
            action_id: ID of action to rollback
        """
        logger.info(f"User requested rollback: {action_id}")

        # Get action details
        action = self.remediation.REMEDIATION_ACTIONS.get(action_id)
        if not action:
            messagebox.showerror("Error", f"Unknown action: {action_id}")
            return

        if not action.reversible:
            messagebox.showerror("Error", f"{action.name} is not reversible!")
            return

        # Confirm with user
        confirm_msg = f"Rollback: {action.name}\n\n"
        confirm_msg += "This will revert the changes made by this action.\n\n"
        confirm_msg += "Do you want to proceed?"

        if not messagebox.askyesno("Confirm Rollback", confirm_msg):
            logger.info("User cancelled rollback")
            return

        # Update button state
        widgets = self.action_widgets.get(action_id)
        if widgets:
            if widgets["rollback_btn"]:
                widgets["rollback_btn"].configure(
                    state="disabled",
                    text="⏳ Rolling back...",
                )
            widgets["execute_btn"].configure(state="disabled")
            widgets["test_btn"].configure(state="disabled")

        # Execute rollback in background thread
        def task():
            try:
                result = self.remediation.rollback_remediation(action_id)

                # Update UI based on result
                def update_ui():
                    if widgets:
                        if result.status == RemediationStatus.ROLLED_BACK:
                            widgets["execute_btn"].configure(
                                text="▶ Execute",
                                state="normal",
                                fg_color=widgets["original_color"],
                            )
                            if widgets["rollback_btn"]:
                                widgets["rollback_btn"].configure(
                                    text="↩ Rollback",
                                    state="normal",
                                )
                            messagebox.showinfo(
                                "Success",
                                f"{action.name} rolled back successfully!\n\n{result.message}",
                            )
                        else:
                            widgets["execute_btn"].configure(state="normal")
                            if widgets["rollback_btn"]:
                                widgets["rollback_btn"].configure(
                                    text="↩ Rollback",
                                    state="normal",
                                )
                            messagebox.showerror(
                                "Failed",
                                f"Rollback of {action.name} failed!\n\n{result.message}",
                            )

                        widgets["test_btn"].configure(state="normal")

                self.after(0, update_ui)

            except Exception as e:
                logger.error(f"Rollback failed: {e}")
                error_msg = str(e)

                def show_error():
                    if widgets:
                        widgets["execute_btn"].configure(state="normal")
                        if widgets["rollback_btn"]:
                            widgets["rollback_btn"].configure(
                                text="↩ Rollback",
                                state="normal",
                            )
                        widgets["test_btn"].configure(state="normal")

                    messagebox.showerror("Error", f"Rollback failed: {error_msg}")

                self.after(0, show_error)

        threading.Thread(target=task, daemon=True).start()

    def _test_action(self, action_id: str) -> None:
        """
        Test run a remediation action (dry run).

        Args:
            action_id: ID of action to test
        """
        logger.info(f"User requested test run: {action_id}")

        # Get action details
        action = self.remediation.REMEDIATION_ACTIONS.get(action_id)
        if not action:
            messagebox.showerror("Error", f"Unknown action: {action_id}")
            return

        # Update button state
        widgets = self.action_widgets.get(action_id)
        if widgets:
            widgets["test_btn"].configure(
                state="disabled",
                text="⏳ Testing...",
            )
            widgets["execute_btn"].configure(state="disabled")
            if widgets["rollback_btn"]:
                widgets["rollback_btn"].configure(state="disabled")

        # Execute test in background thread
        def task():
            try:
                result = self.remediation.execute_remediation(action_id, dry_run=True)

                # Update UI
                def update_ui():
                    if widgets:
                        widgets["test_btn"].configure(
                            text="🧪 Test Run",
                            state="normal",
                        )
                        widgets["execute_btn"].configure(state="normal")
                        if widgets["rollback_btn"]:
                            widgets["rollback_btn"].configure(state="normal")

                    messagebox.showinfo(
                        "Test Run Complete",
                        f"Test run of {action.name}:\n\n{result.message}\n\nCommand: {result.output or 'N/A'}",
                    )

                self.after(0, update_ui)

            except Exception as e:
                logger.error(f"Test run failed: {e}")
                error_msg = str(e)

                def show_error():
                    if widgets:
                        widgets["test_btn"].configure(
                            text="🧪 Test Run",
                            state="normal",
                        )
                        widgets["execute_btn"].configure(state="normal")
                        if widgets["rollback_btn"]:
                            widgets["rollback_btn"].configure(state="normal")

                    messagebox.showerror("Error", f"Test run failed: {error_msg}")

                self.after(0, show_error)

        threading.Thread(target=task, daemon=True).start()

    def _refresh_actions(self) -> None:
        """Refresh the list of available actions."""
        logger.info("Refreshing remediation actions")
        self._load_actions()
        messagebox.showinfo("Refreshed", "Remediation actions have been refreshed.")

    def _show_history(self) -> None:
        """Show remediation history."""
        logger.info("User viewing remediation history")

        history = self.remediation.get_remediation_history()

        if not history:
            messagebox.showinfo("History", "No remediation history available.")
            return

        # Create history dialog
        history_dialog = ctk.CTkToplevel(self)
        history_dialog.title("Remediation History")
        history_dialog.geometry("700x500")
        history_dialog.transient(self)
        history_dialog.grab_set()

        # Header
        header = ctk.CTkLabel(
            history_dialog,
            text="📜 Remediation History",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        header.pack(padx=20, pady=(20, 10))

        # Scrollable frame for history
        history_frame = ctk.CTkScrollableFrame(history_dialog)
        history_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Display history items
        for idx, result in enumerate(reversed(history), 1):
            action = self.remediation.REMEDIATION_ACTIONS.get(result.action_id)
            action_name = action.name if action else result.action_id

            # History item frame
            item_frame = ctk.CTkFrame(history_frame)
            item_frame.pack(fill="x", pady=5)

            # Status icon
            status_icon = "✓" if result.status == RemediationStatus.SUCCESS else "❌"
            status_color = "#2ecc71" if result.status == RemediationStatus.SUCCESS else "#e74c3c"

            # Item header
            header_text = f"{status_icon} {action_name}"
            item_header = ctk.CTkLabel(
                item_frame,
                text=header_text,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=status_color,
            )
            item_header.pack(anchor="w", padx=10, pady=(10, 5))

            # Item details
            details_text = f"Status: {result.status.value.upper()}\n"
            details_text += f"Time: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            details_text += f"Message: {result.message}"

            item_details = ctk.CTkLabel(
                item_frame,
                text=details_text,
                font=ctk.CTkFont(size=11),
                text_color="gray",
                justify="left",
            )
            item_details.pack(anchor="w", padx=10, pady=(0, 10))

        # Close button
        close_btn = ctk.CTkButton(
            history_dialog,
            text="Close",
            command=history_dialog.destroy,
            width=100,
        )
        close_btn.pack(pady=(10, 20))
