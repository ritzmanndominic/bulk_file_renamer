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

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QSizePolicy
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QPainter, QPen, QBrush, QColor


class PlusMinusSpinBox(QWidget):
    """Custom spinbox widget with + and - buttons instead of arrows."""
    
    valueChanged = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._minimum = 0
        self._maximum = 99
        self._step = 1
        self._suffix = ""
        
        # Colors for theming
        self.button_bg_color = "#FFFFFF"
        self.button_border_color = "#D5D5D5"
        self.button_hover_bg_color = "#F3F4F6"
        self.button_hover_border_color = "#1E63E9"
        self.button_pressed_bg_color = "#E5E7EB"
        self.text_color = "#000000"
        self.plus_minus_color = "#000000"
        self.is_dark_theme = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components."""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Minus button
        self.minus_button = QPushButton(chr(45))  # ASCII code 45 for '-'
        self.minus_button.setFixedSize(32, 24)
        self.minus_button.setObjectName("MinusButton")
        self.minus_button.clicked.connect(self.decrement)
        
        # Value label
        self.value_label = QLabel("0")
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setMinimumWidth(60)  # Minimum width for basic text
        self.value_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.value_label.setObjectName("ValueLabel")
        
        # Plus button
        self.plus_button = QPushButton(chr(43))  # ASCII code 43 for '+'
        self.plus_button.setFixedSize(32, 24)
        self.plus_button.setObjectName("PlusButton")
        self.plus_button.clicked.connect(self.increment)
        
        # Ensure proper font rendering for the + symbol
        font = self.plus_button.font()
        font.setBold(True)
        font.setPointSize(12)
        self.plus_button.setFont(font)
        
        font_minus = self.minus_button.font()
        font_minus.setBold(True)
        font_minus.setPointSize(12)
        self.minus_button.setFont(font_minus)
        
        # Add widgets to layout
        layout.addWidget(self.minus_button)
        layout.addWidget(self.value_label)
        layout.addWidget(self.plus_button)
        
        self.setLayout(layout)
        self.update_display()
        self.update_button_states()
        self.apply_styling()
    
    def apply_styling(self):
        """Apply styling to the buttons and label."""
        # Use the same grey colors for both light and dark themes
        button_bg = "#6B7280"  # Grey background for both themes
        button_hover = "#4B5563"  # Darker grey on hover
        button_pressed = "#374151"  # Even darker grey when pressed
        button_disabled = "#D1D5DB"  # Light grey when disabled
        button_text = "#FFFFFF"  # White text on both themes
        
        button_style = f"""
            QPushButton {{
                background-color: {button_bg};
                border: none;
                border-radius: 8px;
                color: {button_text};
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {button_hover};
            }}
            QPushButton:pressed {{
                background-color: {button_pressed};
            }}
            QPushButton:disabled {{
                background-color: {button_disabled};
                color: #666666;
            }}
        """
        
        label_style = f"""
            QLabel {{
                color: {self.text_color};
                font-size: 14px;
                font-weight: 500;
                border: 1px solid {self.button_border_color};
                border-radius: 3px;
                background-color: {self.button_bg_color};
                padding: 2px;
            }}
        """
        
        self.minus_button.setStyleSheet(button_style)
        self.plus_button.setStyleSheet(button_style)
        self.value_label.setStyleSheet(label_style)
    
    def set_theme_colors(self, button_bg, button_border, button_hover_bg, button_hover_border, 
                        button_pressed_bg, text_color, plus_minus_color):
        """Set theme colors for the widget."""
        self.button_bg_color = button_bg
        self.button_border_color = button_border
        self.button_hover_bg_color = button_hover_bg
        self.button_hover_border_color = button_hover_border
        self.button_pressed_bg_color = button_pressed_bg
        self.text_color = text_color
        self.plus_minus_color = plus_minus_color
        
        # Since we use the same button colors for both themes, we don't need to track theme state
        # But keep the flag for potential future use
        self.is_dark_theme = text_color in ["#FFFFFF", "#FFFFFF", "#F9FAFB", "#D1D5DB"]
        
        self.apply_styling()
    
    def value(self):
        """Get the current value."""
        return self._value
    
    def setValue(self, value):
        """Set the current value."""
        new_value = max(self._minimum, min(self._maximum, value))
        if new_value != self._value:
            self._value = new_value
            self.update_display()
            self.update_button_states()
            self.valueChanged.emit(self._value)
    
    def minimum(self):
        """Get the minimum value."""
        return self._minimum
    
    def setMinimum(self, minimum):
        """Set the minimum value."""
        self._minimum = minimum
        if self._value < self._minimum:
            self.setValue(self._minimum)
        self.update_button_states()
    
    def maximum(self):
        """Get the maximum value."""
        return self._maximum
    
    def setMaximum(self, maximum):
        """Set the maximum value."""
        self._maximum = maximum
        if self._value > self._maximum:
            self.setValue(self._maximum)
        self.update_button_states()
    
    def setRange(self, minimum, maximum):
        """Set both minimum and maximum values."""
        self.setMinimum(minimum)
        self.setMaximum(maximum)
    
    def singleStep(self):
        """Get the step size."""
        return self._step
    
    def setSingleStep(self, step):
        """Set the step size."""
        self._step = step
    
    def suffix(self):
        """Get the suffix text."""
        return self._suffix
    
    def setSuffix(self, suffix):
        """Set the suffix text."""
        self._suffix = suffix
        self.update_display()
    
    def increment(self):
        """Increment the value by the step size."""
        self.setValue(self._value + self._step)
    
    def decrement(self):
        """Decrement the value by the step size."""
        self.setValue(self._value - self._step)
    
    def update_display(self):
        """Update the display text."""
        display_text = str(self._value)
        if self._suffix:
            display_text += self._suffix
        self.value_label.setText(display_text)
    
    def update_button_states(self):
        """Update the enabled state of the buttons based on current value."""
        self.minus_button.setEnabled(self._value > self._minimum)
        self.plus_button.setEnabled(self._value < self._maximum)
    
    def sizeHint(self):
        """Return the preferred size of the widget."""
        # Calculate width based on content
        text_width = self.value_label.fontMetrics().boundingRect(self.value_label.text()).width()
        button_width = 32 * 2  # Two buttons
        spacing = 4  # Layout spacing
        padding = 16  # Extra padding for better appearance
        total_width = max(100, text_width + button_width + spacing + padding)  # Minimum 100, but expand for longer text
        return QSize(total_width, 24)
