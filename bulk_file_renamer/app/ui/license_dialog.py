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

"""
License Activation Dialog for Bulk File Renamer
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap
from app.utils.license_manager import LicenseManager


class LicenseDialog(QDialog):
    """Dialog for license activation."""
    
    license_activated = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.license_manager = LicenseManager()
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("License Activation")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_frame = QFrame()
        header_frame.setObjectName("LicenseHeader")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Bulk File Renamer")
        title_label.setObjectName("LicenseTitle")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("License Activation Required")
        subtitle_label.setObjectName("LicenseSubtitle")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        layout.addWidget(header_frame)
        
        # Instructions
        instructions = QTextEdit()
        instructions.setObjectName("LicenseInstructions")
        instructions.setMaximumHeight(120)
        instructions.setReadOnly(True)
        instructions.setPlainText(
            "To activate your license:\n\n"
            "1. Run the License Generator tool on your computer\n"
            "2. Copy the Machine ID and send it to support\n"
            "3. Enter the license key provided by support\n"
            "4. Click 'Activate License'"
        )
        layout.addWidget(instructions)
        
        # Machine ID display
        machine_frame = QFrame()
        machine_layout = QVBoxLayout(machine_frame)
        machine_layout.setContentsMargins(0, 0, 0, 0)
        
        machine_label = QLabel("Your Machine ID:")
        machine_label.setObjectName("MachineLabel")
        
        self.machine_id_display = QLineEdit()
        self.machine_id_display.setObjectName("MachineIdDisplay")
        self.machine_id_display.setText(self.license_manager.get_machine_id())
        self.machine_id_display.setReadOnly(True)
        self.machine_id_display.setStyleSheet("""
            QLineEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                padding: 8px;
                font-family: monospace;
            }
        """)
        
        machine_layout.addWidget(machine_label)
        machine_layout.addWidget(self.machine_id_display)
        layout.addWidget(machine_frame)
        
        # License key input
        license_frame = QFrame()
        license_layout = QVBoxLayout(license_frame)
        license_layout.setContentsMargins(0, 0, 0, 0)
        
        license_label = QLabel("License Key:")
        license_label.setObjectName("LicenseLabel")
        
        self.license_input = QLineEdit()
        self.license_input.setObjectName("LicenseInput")
        self.license_input.setPlaceholderText("Enter your 16-character license key")
        self.license_input.setMaxLength(16)
        self.license_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 4px;
                font-family: monospace;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #007acc;
            }
        """)
        
        license_layout.addWidget(license_label)
        license_layout.addWidget(self.license_input)
        layout.addWidget(license_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.activate_button = QPushButton("Activate License")
        self.activate_button.setObjectName("ActivateButton")
        self.activate_button.setDefault(True)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("CancelButton")
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.activate_button)
        layout.addLayout(button_layout)
        
        # Apply styling
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QFrame#LicenseHeader {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 15px;
            }
            QLabel#LicenseTitle {
                color: #2c3e50;
                margin-bottom: 5px;
            }
            QLabel#LicenseSubtitle {
                color: #6c757d;
                font-size: 12px;
            }
            QTextEdit#LicenseInstructions {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                padding: 10px;
                font-size: 12px;
                color: #495057;
            }
            QLabel#MachineLabel, QLabel#LicenseLabel {
                color: #495057;
                font-weight: 600;
                margin-bottom: 5px;
            }
            QPushButton#ActivateButton {
                background-color: #007acc;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: 600;
                min-width: 120px;
            }
            QPushButton#ActivateButton:hover {
                background-color: #005a9e;
            }
            QPushButton#ActivateButton:pressed {
                background-color: #004578;
            }
            QPushButton#CancelButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: 600;
                min-width: 80px;
            }
            QPushButton#CancelButton:hover {
                background-color: #5a6268;
            }
        """)
    
    def setup_connections(self):
        """Setup signal connections."""
        self.activate_button.clicked.connect(self.activate_license)
        self.cancel_button.clicked.connect(self.reject)
        self.license_input.textChanged.connect(self.on_license_input_changed)
        self.license_input.returnPressed.connect(self.activate_license)
    
    def on_license_input_changed(self, text):
        """Handle license input changes."""
        # Auto-format license key (add dashes for readability)
        clean_text = text.replace("-", "").upper()
        if len(clean_text) > 16:
            clean_text = clean_text[:16]
        
        # Add dashes for readability (XXXX-XXXX-XXXX-XXXX)
        formatted = ""
        for i, char in enumerate(clean_text):
            if i > 0 and i % 4 == 0:
                formatted += "-"
            formatted += char
        
        if formatted != text:
            self.license_input.setText(formatted)
            self.license_input.setCursorPosition(len(formatted))
    
    def activate_license(self):
        """Activate the license."""
        license_key = self.license_input.text().replace("-", "").strip()
        
        if not license_key:
            QMessageBox.warning(self, "Invalid License", "Please enter a license key.")
            return
        
        if len(license_key) != 16:
            QMessageBox.warning(self, "Invalid License", "License key must be 16 characters long.")
            return
        
        # Attempt to activate license
        success, message = self.license_manager.activate_license(license_key)
        
        if success:
            QMessageBox.information(self, "License Activated", message)
            self.license_activated.emit()
            self.accept()
        else:
            QMessageBox.critical(self, "License Activation Failed", message)
    
    def get_machine_id(self) -> str:
        """Get the machine ID for display."""
        return self.license_manager.get_machine_id()




