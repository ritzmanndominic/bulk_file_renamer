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

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QGraphicsOpacityEffect
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve


class SimpleNotification(QWidget):
    """A simple notification widget without complex animations."""
    
    notification_closed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = "Light"
        self.setup_ui()
        self.setup_animations()
        
        # Ensure notification stays on top
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        
        # Initially hidden
        self.hide()
    
    def setup_ui(self):
        """Setup the notification UI."""
        self.setAutoFillBackground(True)
        self.setFixedHeight(60)  # Slightly taller for better proportions
        
        # Main layout
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)  # More padding
        layout.setSpacing(15)  # More spacing between elements
        
        # Icon label with better styling
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)  # Slightly larger
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.icon_label)
        
        # Message label with better typography
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: 500;
                line-height: 1.4;
            }
        """)
        layout.addWidget(self.message_label, 1)
        
        # Close button with modern design
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(28, 28)  # Slightly larger
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 14px;
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        self.close_button.clicked.connect(self.hide_notification)
        layout.addWidget(self.close_button)
        
        self.setLayout(layout)
        
        # Base style; colors set per type/theme in set_notification_style
        self.setStyleSheet("""
            SimpleNotification { border: none; border-radius: 10px; }
        """)
        
        # Remove previous gradient/shadow approach for a clean, flat bar
        
        # Auto-hide timer
        self.auto_hide_timer = QTimer()
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self.hide_notification)
    
    def setup_animations(self):
        """Setup fade animations."""
        # Fade in animation
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Fade out animation
        self.fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_animation.setDuration(200)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.InCubic)
        self.fade_out_animation.finished.connect(self._on_fade_out_finished)
    
    # (shadow effect removed)
    
    def show_notification(self, message: str, notification_type: str = "primary", auto_hide: bool = True, duration: int = 3000):
        """Show a notification."""
        # Set message
        self.message_label.setText(message)
        
        # Set style based on type
        self.set_notification_style(notification_type)
        
        # Set icon based on type
        self.set_notification_icon(notification_type)
        
        # Show the notification with fade in
        self.show()
        self.raise_()
        self.activateWindow()
        self.setWindowOpacity(0.0)  # Start transparent
        self.fade_in_animation.start()
        
        # Setup auto-hide if enabled
        if auto_hide:
            self.auto_hide_timer.start(duration)
    
    def hide_notification(self):
        """Hide the notification with fade out."""
        self.auto_hide_timer.stop()
        self.fade_out_animation.start()
    
    def _on_fade_out_finished(self):
        """Handle fade out animation finished."""
        self.hide()
        self.notification_closed.emit()
    
    def set_theme(self, theme: str):
        self.theme = theme or "Light"

    def _colors_for_type(self, notification_type: str):
        light = self.theme.lower() != "dark"
        if notification_type in ("neutral", "info"):
            bg = "#D5D5D5" if light else "#2C2F33"
            fg = "#000000" if light else "#FFFFFF"
        elif notification_type in ("error", "delete"):
            bg = "#EF4444"; fg = "#FFFFFF"
        elif notification_type == "warning":
            bg = "#F59E0B"; fg = "#000000"
        elif notification_type in ("success", "save"):
            bg = "#22C55E"; fg = "#FFFFFF"
        elif notification_type in ("primary", "load"):
            bg = "#1E63E9" if light else "#1B4CA8"; fg = "#FFFFFF"
        else:  # fallback primary
            bg = "#1E63E9" if light else "#1B4CA8"  # darker blue in dark mode
            fg = "#FFFFFF"
        return bg, fg

    def set_notification_style(self, notification_type: str):
        """Set the notification style based on type and current theme."""
        bg, fg = self._colors_for_type(notification_type)
        indicator_bg = "rgba(255,255,255,0.2)" if fg == "#FFFFFF" else "rgba(0,0,0,0.12)"
        style = f"""
            SimpleNotification {{ background: {bg}; border-radius: 10px; }}
            QLabel {{ color: {fg}; background: transparent; }}
            QPushButton {{ color: {fg}; background-color: {indicator_bg}; border: none; border-radius: 14px; }}
            QPushButton:hover {{ background-color: rgba(255,255,255,0.25); }}
        """
        self.setStyleSheet(style)
    
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


class SimpleNotificationManager:
    """Simple notification manager."""
    
    def __init__(self, parent_widget):
        self.parent_widget = parent_widget
        self.notifications = []
        self.spacing = 10  # More spacing between notifications
    
    def show_notification(self, message: str, notification_type: str = "primary", auto_hide: bool = True, duration: int = 3000):
        """Show a new notification."""
        notification = SimpleNotification(self.parent_widget)
        # Set theme based on parent's stylesheet guess (checks main app theme name if available)
        try:
            from app.utils.settings_manager import SettingsManager
            theme = SettingsManager().get("theme", "Light")
            notification.set_theme(theme)
        except Exception:
            pass
        notification.notification_closed.connect(lambda: self.remove_notification(notification))
        
        # Add to list
        self.notifications.append(notification)
        
        # Position the notification
        self.position_notification(notification)
        
        # Show the notification
        notification.show_notification(message, notification_type, auto_hide, duration)
    
    def position_notification(self, notification):
        """Position a notification in the stack."""
        # Get parent widget's global position
        parent_global_pos = self.parent_widget.mapToGlobal(self.parent_widget.rect().topLeft())
        parent_width = self.parent_widget.width()
        # Fixed width, centered, slight stacking offset vertically
        width = max(420, min(720, int(parent_width * 0.6)))
        # Calculate Y position with stacking for multiple toasts
        y_position = parent_global_pos.y() + 20
        for existing_notification in self.notifications:
            if existing_notification.isVisible():
                y_position += existing_notification.height() + self.spacing
        # Center horizontally
        x_position = parent_global_pos.x() + (parent_width - width) // 2
        notification.move(x_position, y_position)
        notification.setFixedWidth(width)
        # Persist chosen width for future repositions
        try:
            notification._fixed_width = width
        except Exception:
            pass
        notification.raise_()
        notification.activateWindow()
    
    def remove_notification(self, notification):
        """Remove a notification from the stack."""
        if notification in self.notifications:
            self.notifications.remove(notification)
            notification.deleteLater()
            
            # Reposition remaining notifications
            self.reposition_notifications()
    
    def reposition_notifications(self):
        """Reposition all visible notifications."""
        # Get parent widget's global position
        parent_global_pos = self.parent_widget.mapToGlobal(self.parent_widget.rect().topLeft())
        parent_width = self.parent_widget.width()
        y_position = parent_global_pos.y() + 20
        for notification in self.notifications:
            if notification.isVisible():
                # Keep previous fixed width if set; otherwise compute once
                width = getattr(notification, "_fixed_width", None)
                if width is None:
                    width = max(420, min(720, int(parent_width * 0.6)))
                    try:
                        notification._fixed_width = width
                    except Exception:
                        pass
                x_position = parent_global_pos.x() + (parent_width - width) // 2
                notification.move(x_position, y_position)
                notification.setFixedWidth(width)
                notification.raise_()
                notification.activateWindow()
                y_position += notification.height() + self.spacing
    
    def clear_all(self):
        """Clear all notifications."""
        for notification in self.notifications[:]:
            notification.hide_notification()
