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

from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Qt, Signal
import re


class DateInput(QLineEdit):
    """A QLineEdit that automatically formats dates as YYYY-MM-DD while typing."""
    
    # Signal to notify parent about date validation status
    date_validation_changed = Signal(bool, str)  # (is_valid, message)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("YYYY-MM-DD")
        self.setMaxLength(10)  # YYYY-MM-DD format
        self._formatting = False  # Flag to prevent infinite loops
        self._last_validation_state = None  # Track previous validation state
        self.textChanged.connect(self._on_text_changed)
        
    def _on_text_changed(self, text):
        """Handle text changes and auto-format the date."""
        # Prevent infinite loops
        if self._formatting:
            return
            
        # Remove any non-digit characters
        digits_only = re.sub(r'[^\d]', '', text)
        
        # Limit to 8 digits (YYYYMMDD)
        if len(digits_only) > 8:
            digits_only = digits_only[:8]
        
        # Format the date
        formatted = self._format_date(digits_only)
        
        # Only update if the formatted text is different
        if formatted != text:
            self._formatting = True
            self.setText(formatted)
            # Move cursor to end
            self.setCursorPosition(len(formatted))
            self._formatting = False
        
        # Validate the date and emit signal if validation state changed
        self._validate_and_notify()
    
    def _format_date(self, digits):
        """Format digits into YYYY-MM-DD format."""
        if not digits:
            return ""
        
        # Add separators at appropriate positions
        if len(digits) <= 4:
            return digits
        elif len(digits) <= 6:
            return f"{digits[:4]}-{digits[4:]}"
        else:
            return f"{digits[:4]}-{digits[4:6]}-{digits[6:]}"
    
    def _validate_and_notify(self):
        """Validate the current date and emit notification if validation state changed.
        Only validates when user has typed a complete date (YYYY-MM-DD format).
        """
        text = self.text().strip()
        is_valid = False
        message = ""
        
        # Only validate if we have a complete date format (YYYY-MM-DD)
        if text and len(text) == 10 and text.count('-') == 2:
            # Updated regex to accept single-digit months and days: YYYY-M-D, YYYY-MM-D, YYYY-M-DD, YYYY-MM-DD
            if re.match(r'^\d{4}-(0?[1-9]|1[0-2])-(0?[1-9]|[12][0-9]|3[01])$', text):
                try:
                    from datetime import datetime
                    # This will raise for invalid dates (e.g., 2025-02-30)
                    datetime.strptime(text, '%Y-%m-%d')
                    is_valid = True
                except Exception:
                    message = "Invalid date (e.g., 2025-02-30)"
            else:
                message = "Invalid date format (use YYYY-MM-DD)"
        
        # Only emit signal if validation state changed
        if self._last_validation_state != (is_valid, message):
            self._last_validation_state = (is_valid, message)
            self.date_validation_changed.emit(is_valid, message)
    
    def get_date_value(self):
        """Get the current date value as a string in YYYY-MM-DD format.
        Validates with flexible regex accepting single-digit months/days, then datetime parsing.
        """
        text = self.text().strip()
        # Flexible regex validation: accepts YYYY-M-D, YYYY-MM-D, YYYY-M-DD, YYYY-MM-DD
        if not re.match(r'^\d{4}-(0?[1-9]|1[0-2])-(0?[1-9]|[12][0-9]|3[01])$', text):
            return ""
        try:
            from datetime import datetime
            # This will raise for invalid dates (e.g., 2025-02-30)
            datetime.strptime(text, '%Y-%m-%d')
            return text
        except Exception:
            return ""
    
    def keyPressEvent(self, event):
        """Handle key press events for better UX."""
        # Allow navigation keys, backspace, delete, etc.
        if event.key() in [Qt.Key_Left, Qt.Key_Right, Qt.Key_Backspace, Qt.Key_Delete, 
                          Qt.Key_Home, Qt.Key_End, Qt.Key_Tab, Qt.Key_Return]:
            super().keyPressEvent(event)
            return
        
        # Only allow digits
        if event.text().isdigit():
            super().keyPressEvent(event)
        # Ignore other characters
