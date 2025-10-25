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

from PySide6.QtWidgets import QComboBox, QStyle, QStyleOptionComboBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QBrush, QColor


class CustomComboBox(QComboBox):
    """Custom combobox with themed arrow that integrates properly with the dropdown."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.arrow_color = "#000000"  # Default to black (light theme)
        # Disable mouse wheel scrolling to avoid accidental changes when scrolling the page
        self.setFocusPolicy(Qt.StrongFocus)
    
    def set_arrow_color(self, color):
        """Set the arrow color for theming."""
        self.arrow_color = color
        self.update()  # Trigger repaint
    
    def paintEvent(self, event):
        """Custom paint event to draw our themed arrow."""
        super().paintEvent(event)
        
        # Get the dropdown button area
        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)
        
        # Get the dropdown button rectangle
        button_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_ComboBox,
            opt,
            QStyle.SubControl.SC_ComboBoxArrow,
            self
        )
        
        # Draw custom arrow
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set arrow color
        pen = QPen(Qt.NoPen)
        brush = QBrush(QColor(self.arrow_color))
        painter.setPen(pen)
        painter.setBrush(brush)
        
        # Calculate triangle points (downward pointing)
        center_x = button_rect.center().x()
        center_y = button_rect.center().y()
        size = 4  # Triangle size
        
        # Triangle points: top-left, top-right, bottom-center
        points = [
            (center_x - size, center_y - size//2),  # Top-left
            (center_x + size, center_y - size//2),  # Top-right
            (center_x, center_y + size//2)          # Bottom-center
        ]
        
        # Draw the triangle
        from PySide6.QtCore import QPoint
        triangle_points = [QPoint(x, y) for x, y in points]
        from PySide6.QtGui import QPolygon
        painter.drawPolygon(QPolygon(triangle_points))
        
        painter.end()

    def wheelEvent(self, event):  # type: ignore[override]
        """Prevent wheel from changing selection unless the combo has focus and is open."""
        if self.view().isVisible() and self.hasFocus():
            return super().wheelEvent(event)
        # Otherwise, ignore to let the parent scroll area handle it
        event.ignore()
