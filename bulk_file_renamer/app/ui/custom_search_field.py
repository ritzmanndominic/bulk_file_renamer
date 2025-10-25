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

from PySide6.QtWidgets import QLineEdit, QPushButton
from PySide6.QtCore import Qt


class CustomSearchField(QLineEdit):
    """Custom search field with integrated clear button."""
    
    def __init__(self, placeholder_text="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder_text)
        self._setup_clear_button()
        self._connect_signals()
    
    def _setup_clear_button(self):
        """Set up the clear button overlay."""
        # Create the clear button as a child widget
        self.clear_button = QPushButton("×", self)
        self.clear_button.setObjectName("ClearSearchButton")
        self.clear_button.setFixedSize(20, 20)
        self.clear_button.setCursor(Qt.PointingHandCursor)
        try:
            from app.utils.translation_manager import get_translation_manager
            tr = get_translation_manager()
            self.clear_button.setToolTip(tr.tr("ui.tooltip_clear_search"))
        except Exception:
            self.clear_button.setToolTip("Clear search")
        self.clear_button.setVisible(False)  # Initially hidden
        
        # Position the button on the right side
        self._position_clear_button()
    
    def _position_clear_button(self):
        """Position the clear button on the right side of the line edit."""
        # Get the line edit's geometry
        rect = self.rect()
        
        # Calculate button position (right side with some padding)
        button_size = self.clear_button.size()
        x = rect.width() - button_size.width() - 8  # 8px padding from right edge
        y = (rect.height() - button_size.height()) // 2  # Center vertically
        
        # Set the button position
        self.clear_button.move(x, y)
    
    def resizeEvent(self, event):
        """Handle resize events to reposition the clear button."""
        super().resizeEvent(event)
        self._position_clear_button()
    
    def _connect_signals(self):
        """Connect internal signals."""
        # Show/hide clear button based on text content
        self.textChanged.connect(self._on_text_changed)
        
        # Clear button functionality
        self.clear_button.clicked.connect(self.clear)
    
    def _on_text_changed(self, text):
        """Handle text changes to show/hide clear button."""
        self.clear_button.setVisible(bool(text.strip()))
    
    def clear(self):
        """Clear the search field."""
        super().clear()
