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

from PySide6.QtWidgets import QCheckBox, QStyle, QStyleOptionButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QBrush, QColor


class CustomCheckBox(QCheckBox):
    """Custom checkbox with themed styling that integrates properly with the app."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.check_color = "#1E63E9"  # Default to blue (light theme)
        self.border_color = "#D5D5D5"  # Default border color
        self.background_color = "#FFFFFF"  # Default background color
    
    def set_check_color(self, color):
        """Set the check mark color for theming."""
        self.check_color = color
        self.update()  # Trigger repaint
    
    def set_border_color(self, color):
        """Set the border color for theming."""
        self.border_color = color
        self.update()  # Trigger repaint
    
    def set_background_color(self, color):
        """Set the background color for theming."""
        self.background_color = color
        self.update()  # Trigger repaint
    
    def paintEvent(self, event):
        """Custom paint event to draw our themed checkbox."""
        super().paintEvent(event)
        
        # Get the checkbox indicator area
        opt = QStyleOptionButton()
        self.initStyleOption(opt)
        
        # Get the checkbox indicator rectangle
        indicator_rect = self.style().subElementRect(
            QStyle.SubElement.SE_CheckBoxIndicator,
            opt,
            self
        )
        
        # Draw custom checkbox
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw checkbox background
        bg_brush = QBrush(QColor(self.background_color))
        border_pen = QPen(QColor(self.border_color), 1)
        painter.setBrush(bg_brush)
        painter.setPen(border_pen)
        
        # Draw rounded rectangle for checkbox
        painter.drawRoundedRect(indicator_rect, 3, 3)
        
        # Draw check mark if checked
        if self.isChecked():
            check_pen = QPen(QColor(self.check_color), 2)
            painter.setPen(check_pen)
            painter.setBrush(Qt.NoBrush)
            
            # Draw check mark (simple V shape)
            center_x = indicator_rect.center().x()
            center_y = indicator_rect.center().y()
            size = min(indicator_rect.width(), indicator_rect.height()) // 3
            
            # Check mark points
            points = [
                (center_x - size//2, center_y),           # Left point
                (center_x, center_y + size//2),           # Bottom center
                (center_x + size, center_y - size//2)     # Top right
            ]
            
            # Draw the check mark
            from PySide6.QtCore import QPoint
            check_points = [QPoint(x, y) for x, y in points]
            from PySide6.QtGui import QPolygon
            painter.drawPolyline(QPolygon(check_points))
        
        painter.end()
