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

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QColor, QPalette, QFont
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, Signal, QRect


class NotificationBar(QWidget):
    """A notification bar with smooth slide animations."""
    
    notification_closed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_animations()
        
        # Initially hidden
        self.hide()
        self.setFixedHeight(0)
    
    def setup_ui(self):
        """Setup the notification bar UI."""
        self.setAutoFillBackground(True)
        
        # Main layout
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)
        
        # Icon label (for status indicator)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(20, 20)
        self.icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_label)
        
        # Message label
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("color: white; font-weight: 500;")
        layout.addWidget(self.message_label, 1)
        
        # Close button
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(25, 25)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 12px;
            }
        """)
        self.close_button.clicked.connect(self.hide_notification)
        layout.addWidget(self.close_button)
        
        self.setLayout(layout)
        
        # Set default style
        self.setStyleSheet("""
            NotificationBar {
                background-color: #2E7D32;
                border: none;
                border-radius: 4px;
            }
        """)
    
    def setup_animations(self):
        """Setup slide animations."""
        # Slide in animation
        self.slide_in_animation = QPropertyAnimation(self, b"geometry")
        self.slide_in_animation.setDuration(300)
        self.slide_in_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Slide out animation
        self.slide_out_animation = QPropertyAnimation(self, b"geometry")
        self.slide_out_animation.setDuration(250)
        self.slide_out_animation.setEasingCurve(QEasingCurve.InCubic)
        self.slide_out_animation.finished.connect(self._on_slide_out_finished)
        
        # Auto-hide timer
        self.auto_hide_timer = QTimer()
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self.hide_notification)
    
    def show_notification(self, message: str, notification_type: str = "success", auto_hide: bool = True, duration: int = 3000):
        """
        Show a notification with smooth animation.
        
        Args:
            message: The notification message
            notification_type: "success", "error", "warning", "info"
            auto_hide: Whether to auto-hide after duration
            duration: Auto-hide duration in milliseconds
        """
        # Set message
        self.message_label.setText(message)
        
        # Set style based on type
        self.set_notification_style(notification_type)
        
        # Set icon based on type
        self.set_notification_icon(notification_type)
        
        # Calculate target height
        self.adjustSize()
        target_height = self.sizeHint().height()
        
        # Get current geometry
        current_rect = self.geometry()
        if current_rect.width() == 0:
            current_rect.setWidth(400)  # Default width if not set
        
        target_rect = QRect(current_rect.x(), current_rect.y(), current_rect.width(), target_height)
        
        # Setup slide in animation
        start_rect = QRect(current_rect.x(), current_rect.y(), current_rect.width(), 0)
        self.slide_in_animation.setStartValue(start_rect)
        self.slide_in_animation.setEndValue(target_rect)
        
        # Show and animate in
        self.show()
        self.raise_()  # Bring to front
        self.slide_in_animation.start()
        
        # Setup auto-hide if enabled
        if auto_hide:
            self.auto_hide_timer.start(duration)
    
    def hide_notification(self):
        """Hide the notification with smooth animation."""
        if not self.isVisible():
            return
        
        # Stop auto-hide timer
        self.auto_hide_timer.stop()
        
        # Get current geometry
        current_rect = self.geometry()
        
        # Setup slide out animation
        self.slide_out_animation.setStartValue(current_rect)
        self.slide_out_animation.setEndValue(QRect(current_rect.x(), current_rect.y(), current_rect.width(), 0))
        
        # Animate out
        self.slide_out_animation.start()
    
    def _on_slide_out_finished(self):
        """Handle slide out animation finished."""
        self.hide()
        self.notification_closed.emit()
    
    def set_notification_style(self, notification_type: str):
        """Set the notification style based on type."""
        styles = {
            "success": """
                NotificationBar {
                    background-color: #2E7D32;
                    border: none;
                    border-radius: 4px;
                }
            """,
            "error": """
                NotificationBar {
                    background-color: #C62828;
                    border: none;
                    border-radius: 4px;
                }
            """,
            "warning": """
                NotificationBar {
                    background-color: #F57C00;
                    border: none;
                    border-radius: 4px;
                }
            """,
            "info": """
                NotificationBar {
                    background-color: #1976D2;
                    border: none;
                    border-radius: 4px;
                }
            """
        }
        
        self.setStyleSheet(styles.get(notification_type, styles["info"]))
    
    def set_notification_icon(self, notification_type: str):
        """Set the notification icon based on type."""
        icons = {
            "success": "✓",
            "error": "✕",
            "warning": "⚠",
            "info": "ℹ"
        }
        
        icon = icons.get(notification_type, "ℹ")
        self.icon_label.setText(icon)
        self.icon_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")


class NotificationManager:
    """Manages multiple notification bars."""
    
    def __init__(self, parent_widget):
        self.parent_widget = parent_widget
        self.notifications = []
        self.notification_height = 50  # Approximate height per notification
        self.spacing = 5
    
    def show_notification(self, message: str, notification_type: str = "success", auto_hide: bool = True, duration: int = 3000):
        """Show a new notification."""
        notification = NotificationBar(self.parent_widget)
        notification.notification_closed.connect(lambda: self.remove_notification(notification))
        
        # Add to list first
        self.notifications.append(notification)
        
        # Position the notification
        self.position_notification(notification)
        
        # Show the notification
        notification.show_notification(message, notification_type, auto_hide, duration)
    
    def position_notification(self, notification):
        """Position a notification in the stack."""
        # Calculate position based on existing notifications
        y_position = 10  # Start from top with margin
        
        for existing_notification in self.notifications:
            if existing_notification.isVisible():
                y_position += existing_notification.height() + self.spacing
        
        # Set position - ensure it's positioned relative to the parent
        width = max(300, self.parent_widget.width() - 20)
        notification.move(10, y_position)
        notification.setFixedWidth(width)
        notification.raise_()  # Bring to front
    
    def remove_notification(self, notification):
        """Remove a notification from the stack."""
        if notification in self.notifications:
            self.notifications.remove(notification)
            notification.deleteLater()
            
            # Reposition remaining notifications
            self.reposition_notifications()
    
    def reposition_notifications(self):
        """Reposition all visible notifications."""
        y_position = 10
        
        for notification in self.notifications:
            if notification.isVisible():
                notification.move(10, y_position)
                notification.setFixedWidth(max(300, self.parent_widget.width() - 20))
                notification.raise_()  # Bring to front
                y_position += notification.height() + self.spacing
    
    def clear_all(self):
        """Clear all notifications."""
        for notification in self.notifications[:]:  # Copy list to avoid modification during iteration
            notification.hide_notification()
