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

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QGroupBox, QLabel, 
    QSpinBox, QLineEdit, QCheckBox, QComboBox, QPushButton, QFileDialog,
    QMessageBox, QFormLayout, QSlider, QTextEdit, QSizePolicy
)
from .custom_spinbox import CustomSpinBox
from .custom_combobox import CustomComboBox
from .custom_checkbox import CustomCheckBox
from .plus_minus_spinbox import PlusMinusSpinBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from app.utils.translation_manager import get_translation_manager
from app.ui.theme import apply_light_theme


class SettingsTab(QWidget):
    """Settings tab with various configuration options."""
    
    settings_changed = Signal()  # Emitted when settings change
    settings_error = Signal(str)  # Emitted when settings error occurs
    language_changed = Signal(str)  # Emitted when language changes
    
    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager
        self.tr_manager = get_translation_manager()
        # Theme is applied by main window; don't force light here
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the settings UI."""
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Create tab widget for different setting categories
        self.tab_widget = QTabWidget()
        
        # Preview Settings Tab
        preview_tab = self.create_preview_tab()
        self.tab_widget.addTab(preview_tab, self.tr_manager.tr("settings.tabs.preview"))
        
        
        # UI Settings Tab
        ui_tab = self.create_ui_tab()
        self.tab_widget.addTab(ui_tab, self.tr_manager.tr("settings.tabs.interface"))
        
        # File Operations Tab
        file_ops_tab = self.create_file_operations_tab()
        self.tab_widget.addTab(file_ops_tab, self.tr_manager.tr("settings.tabs.file_operations"))
        
        # Advanced Tab
        advanced_tab = self.create_advanced_tab()
        self.tab_widget.addTab(advanced_tab, self.tr_manager.tr("settings.tabs.advanced"))
        
        layout.addWidget(self.tab_widget)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.reset_button = QPushButton(self.tr_manager.tr("settings.buttons.reset"))
        self.reset_button.clicked.connect(self.reset_to_defaults)
        
        self.save_button = QPushButton(self.tr_manager.tr("settings.buttons.save"))
        self.save_button.clicked.connect(self.save_settings)
        
        self.cancel_button = QPushButton(self.tr_manager.tr("settings.buttons.cancel"))
        self.cancel_button.clicked.connect(self.cancel_changes)

        # Style buttons via theme object names
        self.save_button.setObjectName("PrimaryButton")
        self.reset_button.setObjectName("SecondaryButton")
        self.cancel_button.setObjectName("SecondaryButton")
        
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def create_preview_tab(self):
        """Create preview settings tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Preview Settings Group
        self.preview_group = QGroupBox(self.tr_manager.tr("settings.preview.title"))
        preview_layout = QFormLayout()
        # Make form layout more responsive
        preview_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        
        self.auto_refresh_check = CustomCheckBox(self.tr_manager.tr("settings.preview.auto_refresh"))
        preview_layout.addRow(self.auto_refresh_check)
        
        self.show_file_count_check = CustomCheckBox(self.tr_manager.tr("settings.preview.show_file_count"))
        preview_layout.addRow(self.show_file_count_check)

        # Auto-resolve conflicts toggle
        self.auto_resolve_check = CustomCheckBox(self.tr_manager.tr("settings.preview.auto_resolve_conflicts"))
        self.auto_resolve_check.setEnabled(False)
        self.auto_resolve_check.setStyleSheet("color: #9CA3AF;")
        preview_layout.addRow(self.auto_resolve_check)
        
        self.preview_group.setLayout(preview_layout)
        layout.addWidget(self.preview_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    
    def create_ui_tab(self):
        """Create UI settings tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Theme Settings Group
        self.theme_group = QGroupBox(self.tr_manager.tr("settings.interface.theme_settings"))
        theme_layout = QFormLayout()
        # Make form layout more responsive
        theme_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        self.theme_combo = CustomComboBox()
        # Add translated theme names
        self.theme_combo.addItem(self.tr_manager.tr("settings.interface.themes.light"), "Light")
        self.theme_combo.addItem(self.tr_manager.tr("settings.interface.themes.dark"), "Dark")
        # Make combo box responsive
        self.theme_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        theme_layout.addRow(self.tr_manager.tr("settings.interface.theme") + ":", self.theme_combo)
        
        self.theme_group.setLayout(theme_layout)
        layout.addWidget(self.theme_group)
        
        # UI Behavior Group
        self.behavior_group = QGroupBox(self.tr_manager.tr("settings.interface.ui_behavior"))
        behavior_layout = QFormLayout()
        # Make form layout more responsive
        behavior_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        self.show_tooltips_check = CustomCheckBox(self.tr_manager.tr("settings.interface.show_tooltips"))
        behavior_layout.addRow(self.show_tooltips_check)
        
        self.confirm_rename_check = CustomCheckBox(self.tr_manager.tr("settings.interface.confirm_rename"))
        behavior_layout.addRow(self.confirm_rename_check)
        
        self.behavior_group.setLayout(behavior_layout)
        layout.addWidget(self.behavior_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_file_operations_tab(self):
        """Create file operations settings tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Backup Settings Group
        self.backup_group = QGroupBox(self.tr_manager.tr("settings.file_operations.title"))
        backup_layout = QFormLayout()
        # Make form layout more responsive
        backup_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        self.backup_before_check = CustomCheckBox(self.tr_manager.tr("settings.file_operations.backup_before"))
        # Warning label shown when backups enabled
        self.backup_warning_label = QLabel(self.tr_manager.tr("settings.file_operations.backup_warning_label"))
        try:
            self.backup_warning_label.setStyleSheet("color: #DC2626;")  # red
        except Exception:
            pass
        self.backup_warning_label.setWordWrap(True)
        try:
            self.backup_warning_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
            self.backup_warning_label.setMinimumHeight(1)
        except Exception:
            pass
        # Always visible regardless of toggle state
        self.backup_warning_label.setVisible(True)
        # Toggle warning visibility and warn once when enabling
        def _on_backup_toggle(state):
            # Keep label always visible; only notify when enabling
            enabled = state == Qt.Checked
            if enabled:
                try:
                    # Show a persistent, non-blocking in-app notification as well
                    from app.ui.custom_notification_bar import CustomNotificationManager
                    try:
                        # Try to notify via main window manager if present
                        mw = self.window()
                        if hasattr(mw, "notification_manager") and isinstance(mw.notification_manager, CustomNotificationManager):
                            mw.notification_manager.show_notification(
                                self.tr_manager.tr("settings.file_operations.backup_warning_dialog"),
                                "warning"
                            )
                    except Exception:
                        pass
                    # Also show a modal warning once, to ensure visibility
                    QMessageBox.warning(self, self.tr_manager.tr("settings.file_operations.title"), self.tr_manager.tr("settings.file_operations.backup_warning_dialog"))
                except Exception:
                    pass
        self.backup_before_check.stateChanged.connect(_on_backup_toggle)
        backup_layout.addRow(self.backup_before_check)
        backup_layout.addRow(self.backup_warning_label)
        
        backup_location_layout = QHBoxLayout()
        self.backup_location_input = QLineEdit()
        self.backup_browse_button = QPushButton(self.tr_manager.tr("settings.buttons.browse"))
        self.backup_browse_button.clicked.connect(self.browse_backup_location)
        backup_location_layout.addWidget(self.backup_location_input)
        backup_location_layout.addWidget(self.backup_browse_button)
        self.backup_location_label = QLabel(self.tr_manager.tr("settings.file_operations.backup_location"))
        backup_layout.addRow(self.backup_location_label, backup_location_layout)
        
        self.create_backup_folder_check = CustomCheckBox(self.tr_manager.tr("settings.file_operations.create_backup_folder"))
        backup_layout.addRow(self.create_backup_folder_check)
        
        self.backup_group.setLayout(backup_layout)
        layout.addWidget(self.backup_group)
        
        # File Handling Group
        self.file_group = QGroupBox(self.tr_manager.tr("settings.file_operations.title"))
        file_layout = QFormLayout()
        # Make form layout more responsive
        file_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        self.overwrite_existing_check = CustomCheckBox(self.tr_manager.tr("settings.file_operations.overwrite_existing"))
        file_layout.addRow(self.overwrite_existing_check)
        
        self.preserve_attributes_check = CustomCheckBox(self.tr_manager.tr("settings.file_operations.preserve_attributes"))
        file_layout.addRow(self.preserve_attributes_check)
        
        self.file_group.setLayout(file_layout)
        layout.addWidget(self.file_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_advanced_tab(self):
        """Create advanced settings tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Sorting Settings Group
        self.sorting_group = QGroupBox(self.tr_manager.tr("settings.advanced.sorting_settings"))
        sorting_layout = QFormLayout()
        # Make form layout more responsive
        sorting_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        self.case_sensitive_check = CustomCheckBox(self.tr_manager.tr("settings.advanced.case_sensitive_sorting"))
        sorting_layout.addRow(self.case_sensitive_check)
        
        self.sorting_group.setLayout(sorting_layout)
        layout.addWidget(self.sorting_group)
        
        # Logging Settings Group
        self.logging_group = QGroupBox(self.tr_manager.tr("settings.advanced.logging_settings"))
        logging_layout = QFormLayout()
        # Make form layout more responsive
        logging_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        self.log_operations_check = CustomCheckBox(self.tr_manager.tr("settings.advanced.log_operations"))
        logging_layout.addRow(self.log_operations_check)
        
        log_file_layout = QHBoxLayout()
        self.log_file_input = QLineEdit()
        self.log_browse_button = QPushButton(self.tr_manager.tr("settings.buttons.browse"))
        self.log_browse_button.clicked.connect(self.browse_log_file)
        log_file_layout.addWidget(self.log_file_input)
        log_file_layout.addWidget(self.log_browse_button)
        self.log_file_label = QLabel(self.tr_manager.tr("settings.advanced.log_file") + ":")
        logging_layout.addRow(self.log_file_label, log_file_layout)
        
        self.logging_group.setLayout(logging_layout)
        layout.addWidget(self.logging_group)
        
        # Recent Items Group
        self.recent_group = QGroupBox(self.tr_manager.tr("settings.advanced.recent_items"))
        recent_layout = QFormLayout()
        # Make form layout more responsive
        recent_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        self.max_recent_label = QLabel(self.tr_manager.tr("settings.advanced.max_recent_items_label"))
        self.max_recent_spin = PlusMinusSpinBox()
        self.max_recent_spin.setRange(1, 50)
        self.max_recent_spin.setSuffix(" " + self.tr_manager.tr("settings.advanced.items_suffix"))
        # Make spinbox take only minimum needed space
        self.max_recent_spin.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        recent_layout.addRow(self.max_recent_label, self.max_recent_spin)
        
        self.language_label = QLabel(self.tr_manager.tr("settings.advanced.language") + ":")
        self.language_combo = CustomComboBox()
        # Make language combo responsive
        self.language_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        recent_layout.addRow(self.language_label, self.language_combo)
        
        self.recent_group.setLayout(recent_layout)
        layout.addWidget(self.recent_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def browse_backup_location(self):
        """Browse for backup location."""
        folder = QFileDialog.getExistingDirectory(self, self.tr_manager.tr("dialogs.backup_location"))
        if folder:
            self.backup_location_input.setText(folder)
    
    def browse_log_file(self):
        """Browse for log file location."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, self.tr_manager.tr("dialogs.log_file"), "bulk_renamer.log", "Log Files (*.log);;All Files (*)"
        )
        if file_path:
            self.log_file_input.setText(file_path)
    
    def load_settings(self):
        """Load settings into UI controls."""
        # Preview settings
        self.auto_refresh_check.setChecked(self.settings_manager.get("preview_auto_refresh", True))
        self.show_file_count_check.setChecked(self.settings_manager.get("show_file_count", True))
        # Keep disabled and unchecked while in progress
        self.auto_resolve_check.setChecked(False)
        
        
        # UI settings
        theme = self.settings_manager.get("theme", "Light")
        # Find by data (the actual theme value) instead of display text
        index = self.theme_combo.findData(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        self.show_tooltips_check.setChecked(self.settings_manager.get("show_tooltips", True))
        self.confirm_rename_check.setChecked(self.settings_manager.get("confirm_before_rename", True))
        
        # File operations
        self.backup_before_check.setChecked(self.settings_manager.get("backup_before_rename", False))
        self.backup_location_input.setText(self.settings_manager.get("backup_location", "backups/"))
        self.create_backup_folder_check.setChecked(self.settings_manager.get("create_backup_folder", False))
        self.overwrite_existing_check.setChecked(self.settings_manager.get("overwrite_existing", False))
        self.preserve_attributes_check.setChecked(self.settings_manager.get("preserve_file_attributes", True))
        
        # Advanced settings
        self.case_sensitive_check.setChecked(self.settings_manager.get("case_sensitive_sorting", False))
        self.log_operations_check.setChecked(self.settings_manager.get("log_operations", False))
        self.log_file_input.setText(self.settings_manager.get("log_file", "bulk_renamer.log"))
        self.max_recent_spin.setValue(self.settings_manager.get("max_recent_items", 10))
        
        # Load language setting
        from app.utils.translation_manager import get_translation_manager
        translation_manager = get_translation_manager()
        available_languages = translation_manager.get_available_languages()
        self.language_combo.clear()
        for lang_code, lang_name in available_languages.items():
            self.language_combo.addItem(lang_name, lang_code)
        
        current_lang = self.settings_manager.get("language", "en")
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
    
    def save_settings(self):
        """Save settings from UI controls."""
        # Preview settings
        self.settings_manager.set("preview_auto_refresh", self.auto_refresh_check.isChecked())
        self.settings_manager.set("show_file_count", self.show_file_count_check.isChecked())
        # Do not persist auto_resolve while feature is in progress
        
        
        # UI settings
        self.settings_manager.set("theme", self.theme_combo.currentData())
        self.settings_manager.set("show_tooltips", self.show_tooltips_check.isChecked())
        self.settings_manager.set("confirm_before_rename", self.confirm_rename_check.isChecked())
        
        # File operations
        self.settings_manager.set("backup_before_rename", self.backup_before_check.isChecked())
        self.settings_manager.set("backup_location", self.backup_location_input.text())
        self.settings_manager.set("create_backup_folder", self.create_backup_folder_check.isChecked())
        self.settings_manager.set("overwrite_existing", self.overwrite_existing_check.isChecked())
        self.settings_manager.set("preserve_file_attributes", self.preserve_attributes_check.isChecked())
        
        # Advanced settings
        self.settings_manager.set("case_sensitive_sorting", self.case_sensitive_check.isChecked())
        self.settings_manager.set("log_operations", self.log_operations_check.isChecked())
        self.settings_manager.set("log_file", self.log_file_input.text())
        self.settings_manager.set("max_recent_items", self.max_recent_spin.value())
        
        # Save language setting
        selected_lang = self.language_combo.currentData()
        if selected_lang:
            current_lang = self.settings_manager.get("language", "en")
            self.settings_manager.set("language", selected_lang)
            # Emit language changed signal if language actually changed
            if selected_lang != current_lang:
                self.language_changed.emit(selected_lang)

        # Notify app that settings changed (theme, toggles, etc.) so UI can update without restart
        self.settings_changed.emit()
    
    def update_language(self):
        """Update all text with current language."""
        # Update tab names
        self.tab_widget.setTabText(0, self.tr_manager.tr("settings.tabs.preview"))
        self.tab_widget.setTabText(1, self.tr_manager.tr("settings.tabs.interface"))
        self.tab_widget.setTabText(2, self.tr_manager.tr("settings.tabs.file_operations"))
        self.tab_widget.setTabText(3, self.tr_manager.tr("settings.tabs.advanced"))
        
        # Update buttons
        self.reset_button.setText(self.tr_manager.tr("settings.buttons.reset"))
        self.save_button.setText(self.tr_manager.tr("settings.buttons.save"))
        self.cancel_button.setText(self.tr_manager.tr("settings.buttons.cancel"))
        
        # Update group box titles
        self.preview_group.setTitle(self.tr_manager.tr("settings.preview.title"))
        self.theme_group.setTitle(self.tr_manager.tr("settings.interface.theme_settings"))
        self.behavior_group.setTitle(self.tr_manager.tr("settings.interface.ui_behavior"))
        # Update both File Operations groups
        self.backup_group.setTitle(self.tr_manager.tr("settings.file_operations.title"))
        self.file_group.setTitle(self.tr_manager.tr("settings.file_operations.title"))
        self.sorting_group.setTitle(self.tr_manager.tr("settings.advanced.sorting_settings"))
        self.logging_group.setTitle(self.tr_manager.tr("settings.advanced.logging_settings"))
        self.recent_group.setTitle(self.tr_manager.tr("settings.advanced.recent_items"))
        
        # Update checkboxes
        self.auto_refresh_check.setText(self.tr_manager.tr("settings.preview.auto_refresh"))
        self.show_file_count_check.setText(self.tr_manager.tr("settings.preview.show_file_count"))
        self.auto_resolve_check.setText(self.tr_manager.tr("settings.preview.auto_resolve_conflicts"))
        self.show_tooltips_check.setText(self.tr_manager.tr("settings.interface.show_tooltips"))
        self.confirm_rename_check.setText(self.tr_manager.tr("settings.interface.confirm_rename"))
        self.case_sensitive_check.setText(self.tr_manager.tr("settings.advanced.case_sensitive_sorting"))
        self.log_operations_check.setText(self.tr_manager.tr("settings.advanced.log_operations"))

        # Update labels in forms that aren't children of checkboxes
        self.backup_location_label.setText(self.tr_manager.tr("settings.file_operations.backup_location"))
        # Update file operation checkbox labels
        self.backup_before_check.setText(self.tr_manager.tr("settings.file_operations.backup_before"))
        try:
            self.backup_warning_label.setText(self.tr_manager.tr("settings.file_operations.backup_warning_label"))
        except Exception:
            pass
        self.create_backup_folder_check.setText(self.tr_manager.tr("settings.file_operations.create_backup_folder"))
        self.overwrite_existing_check.setText(self.tr_manager.tr("settings.file_operations.overwrite_existing"))
        self.preserve_attributes_check.setText(self.tr_manager.tr("settings.file_operations.preserve_attributes"))
        self.log_file_label.setText(self.tr_manager.tr("settings.advanced.log_file") + ":")
        self.max_recent_label.setText(self.tr_manager.tr("settings.advanced.max_recent_items_label"))
        # Update spinbox suffix text
        self.max_recent_spin.setSuffix(" " + self.tr_manager.tr("settings.advanced.items_suffix"))
        self.language_label.setText(self.tr_manager.tr("settings.advanced.language") + ":")
        
        # Update theme combo - preserve current selection
        current_theme = self.theme_combo.currentData() if self.theme_combo.currentData() else "Light"
        self.theme_combo.clear()
        self.theme_combo.addItem(self.tr_manager.tr("settings.interface.themes.light"), "Light")
        self.theme_combo.addItem(self.tr_manager.tr("settings.interface.themes.dark"), "Dark")
        
        # Restore the previous selection
        index = self.theme_combo.findData(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        # Update browse button
        self.log_browse_button.setText(self.tr_manager.tr("settings.buttons.browse"))
        self.backup_browse_button.setText(self.tr_manager.tr("settings.buttons.browse"))
        
        # Update language combo
        available_languages = self.tr_manager.get_available_languages()
        current_lang = self.settings_manager.get("language", "en")
        self.language_combo.clear()
        for lang_code, lang_name in available_languages.items():
            self.language_combo.addItem(lang_name, lang_code)
        
        index = self.language_combo.findData(current_lang)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self,
            self.tr_manager.tr("dialogs.reset_settings_title"),
            self.tr_manager.tr("dialogs.reset_settings_message"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.settings_manager.reset_to_defaults()
            self.load_settings()
            self.settings_changed.emit()
    
    def cancel_changes(self):
        """Cancel changes and reload settings."""
        self.load_settings()
