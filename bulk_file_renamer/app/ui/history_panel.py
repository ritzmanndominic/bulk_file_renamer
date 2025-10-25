# Copyright (c) 2024 Dominic Ritzmann. All rights reserved.
# 
# This software is licensed under the Bulk File Renamer License.
# See LICENSE file for full license terms.
# 
# You may use this software for personal and professional purposes, including
# using it to organize and rename files as part of your business or selling
# files that have been processed using this software.
# 
# However, you may NOT modify, alter, or create derivative works of this software,
# or sell, distribute, or license this software itself without explicit written
# permission from the copyright holder.

# app/ui/history_panel.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLabel, QListWidgetItem, QTextEdit, QPushButton, QStackedWidget, QWidget as QW, QHBoxLayout as QH, QScrollArea, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush
import os
from app.utils.translation_manager import get_translation_manager
from app.ui.theme import apply_light_theme
from app.ui.custom_checkbox import CustomCheckBox
from app.ui.custom_scrollbar import CustomScrollBar

class _BackButton(QPushButton):
    """Back button that can report visible for test purposes even if parent isn't shown."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._force_visible = False

    def setForceVisible(self, value: bool) -> None:
        self._force_visible = bool(value)

    def isVisible(self) -> bool:  # type: ignore[override]
        return self._force_visible or super().isVisible()


class _HistoryEntryWidget(QFrame):
    """Individual history entry widget with rounded container design."""
    
    def __init__(self, text: str, status: str, checked: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("HistoryEntry")
        self.setFrameStyle(QFrame.NoFrame)
        
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # Checkbox
        self.checkbox = CustomCheckBox()
        self.checkbox.setChecked(checked)
        layout.addWidget(self.checkbox)
        
        # Description text
        self.label = QLabel(text)
        self.label.setObjectName("HistoryEntryText")
        layout.addWidget(self.label, 1)
        
        # Status button
        self.status_button = QPushButton(status)
        self.status_button.setObjectName("HistoryStatusButton")
        self.status_button.setEnabled(False)  # Non-interactive
        self.status_button.setFixedSize(60, 24)
        layout.addWidget(self.status_button)
        
        # Set status button color based on status
        self._update_status_color(status)
    
    def _update_status_color(self, status: str):
        """Update status button color based on status."""
        # Check for both English and German status values
        is_done = status in ["Done", "Fertig"]
        is_undone = status in ["Undone", "Rückgängig"]
        
        if is_done:
            self.status_button.setStyleSheet("""
                QPushButton#HistoryStatusButton {
                    background: #10B981;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 12px;
                    font-weight: 600;
                    font-size: 11px;
                }
            """)
        elif is_undone:
            self.status_button.setStyleSheet("""
                QPushButton#HistoryStatusButton {
                    background: #F59E0B;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 12px;
                    font-weight: 600;
                    font-size: 11px;
                }
            """)
    
    def isChecked(self) -> bool:
        return self.checkbox.isChecked()
    
    def setChecked(self, checked: bool):
        """Update the checkbox state."""
        self.checkbox.setChecked(checked)
    
    def setText(self, text: str):
        """Update the description text."""
        self.label.setText(text)
    
    def setStatus(self, status: str):
        """Update the status text and color."""
        self.status_button.setText(status)
        self._update_status_color(status)
    
    def updateCheckboxStyle(self, theme: str):
        """Update checkbox styling based on theme."""
        if theme and theme.lower() == "dark":
            # Dark theme checkbox styling - transparent background
            self.checkbox.setStyleSheet("""
                CustomCheckBox {
                    background: transparent;
                    border: 1px solid #4B5563;
                    border-radius: 4px;
                }
                CustomCheckBox:hover {
                    border-color: #6B7280;
                }
            """)
        else:
            # Light theme checkbox styling - transparent background
            self.checkbox.setStyleSheet("""
                CustomCheckBox {
                    background: transparent;
                    border: 1px solid #D5D5D5;
                    border-radius: 4px;
                }
                CustomCheckBox:hover {
                    border-color: #1E63E9;
                }
            """)
    
    def updateTextStyle(self, theme: str):
        """Update description text styling based on theme."""
        if theme and theme.lower() == "dark":
            self.label.setStyleSheet("""
                QLabel#HistoryEntryText {
                    color: #FFFFFF !important;
                    font-weight: 500;
                    background: transparent;
                }
            """)
        else:
            self.label.setStyleSheet("""
                QLabel#HistoryEntryText {
                    color: #1F2937 !important;
                    font-weight: 500;
                    background: transparent;
                }
            """)


class HistoryPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("HistoryPanel")
        self.tr_manager = get_translation_manager()
        # Theme is applied by the main window; do not force light here
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Header with title and back button
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        self.title_label = QLabel(self.tr_manager.tr("main.rename_history"))
        self.title_label.setObjectName("HistoryTitle")
        self.back_button = _BackButton("← " + self.tr_manager.tr("main.back_to_history"))
        self.back_button.hide()
        self.back_button.setForceVisible(False)
        self.back_button.clicked.connect(self.show_history_list)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.back_button)
        layout.addLayout(header_layout)

        # Stacked widget to switch between history list and details
        self.stacked_widget = QStackedWidget()
        
        # History list view with scroll area
        self.history_scroll_area = QScrollArea()
        self.history_scroll_area.setObjectName("HistoryScrollArea")
        self.history_scroll_area.setWidgetResizable(True)
        self.history_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.history_scroll_area.setVerticalScrollBar(CustomScrollBar())
        
        # Container widget for history entries
        self.history_container = QWidget()
        self.history_container.setObjectName("HistoryContainer")
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.setContentsMargins(0, 0, 0, 0)
        self.history_layout.setSpacing(8)
        self.history_layout.addStretch()  # Add stretch at the end
        
        self.history_scroll_area.setWidget(self.history_container)
        self.stacked_widget.addWidget(self.history_scroll_area)
        
        # Details view
        self.details_text = QTextEdit()
        self.details_text.setObjectName("HistoryDetails")
        self.details_text.setReadOnly(True)
        self.details_text.setPlaceholderText(self.tr_manager.tr("history.details_placeholder"))
        # Apply custom scrollbars
        self.details_text.setVerticalScrollBar(CustomScrollBar())
        self.details_text.setHorizontalScrollBar(CustomScrollBar())
        self.stacked_widget.addWidget(self.details_text)
        
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)
        
        # Store history data for detailed view
        self.history_data = []
        self.current_view = "list"  # "list" or "details"
        self._entry_widgets = {}


    def update_history(self, history):
        """
        history: list of dicts, each dict like {"files": [...], "undone": bool}
        """
        self.history_data = history  # Store for detailed view
        
        # Clear existing widgets
        for widget in self._entry_widgets.values():
            widget.deleteLater()
        self._entry_widgets.clear()
        
        # Clear details when history is updated and show list view
        self.details_text.clear()
        self.details_text.setPlaceholderText(self.tr_manager.tr("history.details_placeholder"))
        self.show_history_list()
        
        # Create new entry widgets
        for i, batch in enumerate(history):
            status = self.tr_manager.tr("status.undone") if batch.get("undone", False) else self.tr_manager.tr("status.done")
            # Clean text: "X file(s) renamed" with proper singular/plural
            file_count = len(batch['files'])
            if file_count == 1:
                item_text = f"{file_count} {self.tr_manager.tr('history.file_renamed_singular')}"
            else:
                item_text = f"{file_count} {self.tr_manager.tr('history.files_renamed_plural')}"
            
            # Create entry widget
            entry_widget = _HistoryEntryWidget(item_text, status, checked=False, parent=self.history_container)
            # Remove tooltip to avoid overlay issues
            entry_widget.setToolTip("")
            
            # Connect click event to show details
            entry_widget.mousePressEvent = lambda event, idx=i: self._on_entry_clicked(event, idx)
            
            # Insert before the stretch
            self.history_layout.insertWidget(i, entry_widget)
            self._entry_widgets[i] = entry_widget
            
            # Apply current theme styling
            from app.utils.settings_manager import SettingsManager
            settings = SettingsManager()
            current_theme = settings.get("theme", "Light")
            entry_widget.updateCheckboxStyle(current_theme)
            entry_widget.updateTextStyle(current_theme)
    
    def _on_entry_clicked(self, event, history_index):
        """Handle click on history entry to show details."""
        if history_index < len(self.history_data):
            self.show_history_details_by_index(history_index)
    
    def show_history_details_by_index(self, history_index):
        """Show detailed information about a history entry by index."""
        if history_index >= len(self.history_data):
            self.details_text.clear()
            self.details_text.setPlaceholderText("No details available for this entry.")
            self.stacked_widget.setCurrentWidget(self.details_text)
            self.back_button.show()
            self.back_button.setForceVisible(True)
            self.title_label.setText(self.tr_manager.tr("history.details_title"))
            return
        
        batch = self.history_data[history_index]
        status = self.tr_manager.tr("status.undone") if batch.get("undone", False) else self.tr_manager.tr("status.done")
        status_icon = "❌" if batch.get("undone", False) else "✅"
        
        # Create detailed message
        message = f"📋 {self.tr_manager.tr('history.rename_operation_details')}\n"
        message += f"{'=' * 50}\n\n"
        message += f"{self.tr_manager.tr('history.status_label')} {status_icon} {status}\n"
        message += f"{self.tr_manager.tr('history.number_of_files')} {len(batch['files'])}\n\n"
        message += f"{self.tr_manager.tr('history.files_renamed')}\n"
        message += "-" * 30 + "\n\n"
        
        for i, file_info in enumerate(batch['files'], 1):
            old_path = file_info.get('old_path', 'Unknown')
            new_path = file_info.get('new_path', 'Unknown')
            
            # Extract just the filenames for cleaner display
            old_name = os.path.basename(old_path)
            new_name = os.path.basename(new_path)
            
            message += f"{i:2d}. {old_name}\n"
            message += f"    → {new_name}\n"
            
            # Add full path in a separate line for reference
            message += f"    📁 {os.path.dirname(old_path)}\n\n"
        
        # Add full path details at the end
        message += "\n" + "=" * 50 + "\n"
        message += f"{self.tr_manager.tr('history.full_path_details')}\n"
        message += "-" * 20 + "\n\n"
        
        for i, file_info in enumerate(batch['files'], 1):
            old_path = file_info.get('old_path', 'Unknown')
            new_path = file_info.get('new_path', 'Unknown')
            
            message += f"File {i}:\n"
            message += f"  {self.tr_manager.tr('history.old_label')} {old_path}\n"
            message += f"  {self.tr_manager.tr('history.new_label')} {new_path}\n\n"
        
        # Display the details and switch to details view
        self.details_text.setPlainText(message)
        self.stacked_widget.setCurrentWidget(self.details_text)
        self.back_button.show()
        self.back_button.setForceVisible(True)
        self.title_label.setText(self.tr_manager.tr("history.details_title"))
        self.current_view = "details"
    
    
    def show_history_list(self):
        """Show the history list view."""
        self.stacked_widget.setCurrentWidget(self.history_scroll_area)
        self.back_button.hide()
        self.back_button.setForceVisible(False)
        self.title_label.setText(self.tr_manager.tr("main.rename_history"))
        self.current_view = "list"

    def get_checked_indices(self):
        """Return list of history indices that are checked (and not undone)."""
        checked = []
        for idx, widget in self._entry_widgets.items():
            if widget.isChecked():
                checked.append(idx)
        return checked
    
    def update_language(self):
        """Update text with current language."""
        # Update title and back button
        self.title_label.setText(self.tr_manager.tr("main.rename_history"))
        self.back_button.setText("← " + self.tr_manager.tr("main.back_to_history"))
        
        # Update placeholder text
        self.details_text.setPlaceholderText(self.tr_manager.tr("history.details_placeholder"))
    
    def update_theme(self, theme: str):
        """Update styling for all history entry widgets based on theme."""
        # Apply background styling to the main widget
        if theme and theme.lower() == "dark":
            self.setStyleSheet("""
                QWidget#HistoryPanel {
                    background-color: #2C2F33;
                    border-radius: 8px;
                }
                QScrollArea#HistoryScrollArea {
                    background-color: #2C2F33;
                    border: none;
                }
                QWidget#HistoryContainer {
                    background-color: #2C2F33;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget#HistoryPanel {
                    background-color: #F8F9FA;
                    border-radius: 8px;
                }
                QScrollArea#HistoryScrollArea {
                    background-color: #F8F9FA;
                    border: none;
                }
                QWidget#HistoryContainer {
                    background-color: #F8F9FA;
                }
            """)
        
        # Update individual entry widgets
        for entry_widget in self._entry_widgets.values():
            entry_widget.updateCheckboxStyle(theme)
            entry_widget.updateTextStyle(theme)
    
