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

from PySide6.QtWidgets import QSpinBox, QStyle, QStyleOptionSpinBox
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPolygon


class CustomSpinBox(QSpinBox):
    """Custom QSpinBox with properly drawn arrows that are visible in all themes."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.arrow_color = "#000000"  # Default to black for light theme
        self.button_bg_color = "#FFFFFF"
        self.button_border_color = "#D5D5D5"
        self.hover_bg_color = "#F3F4F6"
        self.hover_border_color = "#1E63E9"
    
    def set_arrow_color(self, color):
        """Set the arrow color for theming."""
        self.arrow_color = color
        self.update()
    
    def set_button_colors(self, bg_color, border_color, hover_bg_color, hover_border_color):
        """Set button colors for theming."""
        self.button_bg_color = bg_color
        self.button_border_color = border_color
        self.hover_bg_color = hover_bg_color
        self.hover_border_color = hover_border_color
        self.update()
    
    def paintEvent(self, event):
        """Custom paint event to draw our themed spinbox with visible arrows."""
        # Let the base class handle the main spinbox painting
        super().paintEvent(event)
        
        # Get the style option for the spinbox
        opt = QStyleOptionSpinBox()
        self.initStyleOption(opt)
        
        # Get the button rectangles
        up_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_SpinBox,
            opt,
            QStyle.SubControl.SC_SpinBoxUp,
            self
        )
        down_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_SpinBox,
            opt,
            QStyle.SubControl.SC_SpinBoxDown,
            self
        )
        
        # Draw custom buttons and arrows
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Determine layout: if buttons are side by side (Windows) or stacked (Mac)
        is_horizontal_layout = (up_rect.x() != down_rect.x()) or (up_rect.width() != down_rect.width())
        
        # Draw up button
        self._draw_button(painter, up_rect, True, is_horizontal_layout)
        
        # Draw down button
        self._draw_button(painter, down_rect, False, is_horizontal_layout)
        
        painter.end()
    
    def _draw_button(self, painter, rect, is_up_arrow, is_horizontal_layout):
        """Draw a custom button with arrow."""
        if rect.isEmpty():
            return
        
        # Determine colors based on hover state
        # For simplicity, we'll use the normal colors
        # In a more advanced implementation, you could track mouse position
        bg_color = self.button_bg_color
        border_color = self.button_border_color
        
        # Draw button background
        bg_brush = QBrush(QColor(bg_color))
        border_pen = QPen(QColor(border_color), 1)
        painter.setBrush(bg_brush)
        painter.setPen(border_pen)
        
        # Draw rounded rectangle for button
        painter.drawRoundedRect(rect, 2, 2)
        
        # Draw arrow
        arrow_pen = QPen(QColor(self.arrow_color), 2)
        painter.setPen(arrow_pen)
        painter.setBrush(Qt.NoBrush)
        
        # Calculate arrow size and position
        center_x = rect.center().x()
        center_y = rect.center().y()
        arrow_size = min(rect.width(), rect.height()) // 3
        
        if is_horizontal_layout:
            # Windows layout: buttons are side by side
            if is_up_arrow:
                # Draw leftward-pointing triangle (for up button on the left, pointing outward)
                points = [
                    (center_x - arrow_size // 2, center_y),  # Left point (tip)
                    (center_x + arrow_size // 2, center_y - arrow_size // 2),  # Top right
                    (center_x + arrow_size // 2, center_y + arrow_size // 2)   # Bottom right
                ]
            else:
                # Draw rightward-pointing triangle (for down button on the right, pointing outward)
                points = [
                    (center_x + arrow_size // 2, center_y),  # Right point (tip)
                    (center_x - arrow_size // 2, center_y - arrow_size // 2),  # Top left
                    (center_x - arrow_size // 2, center_y + arrow_size // 2)   # Bottom left
                ]
        else:
            # Mac layout: buttons are stacked vertically
            if is_up_arrow:
                # Draw upward-pointing triangle
                points = [
                    (center_x, center_y - arrow_size // 2),  # Top point
                    (center_x - arrow_size // 2, center_y + arrow_size // 2),  # Bottom left
                    (center_x + arrow_size // 2, center_y + arrow_size // 2)   # Bottom right
                ]
            else:
                # Draw downward-pointing triangle
                points = [
                    (center_x, center_y + arrow_size // 2),  # Bottom point
                    (center_x - arrow_size // 2, center_y - arrow_size // 2),  # Top left
                    (center_x + arrow_size // 2, center_y - arrow_size // 2)   # Top right
                ]
        
        # Convert to QPoint and draw
        from PySide6.QtCore import QPoint
        arrow_points = [QPoint(x, y) for x, y in points]
        painter.drawPolygon(QPolygon(arrow_points))
