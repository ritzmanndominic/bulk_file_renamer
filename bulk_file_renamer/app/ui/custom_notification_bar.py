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
from PySide6.QtGui import QColor, QPalette, QPainter, QPen, QBrush
from PySide6.QtCore import Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve, QRect
import logging


class CustomNotificationBar(QWidget):
    """A custom notification bar with rounded corners that appears at the top center of the screen."""
    
    notification_closed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = "Light"
        self.setup_ui()
        self.setup_animations()
        
        # Ensure notification stays on top and never grabs focus
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # Suppress Qt geometry warnings for this widget
        self.setObjectName("CustomNotificationBar")
        
        # Initially hidden
        self.hide()
    
    def resizeEvent(self, event):
        """Override resize event to prevent geometry warnings."""
        # Call parent resize event
        super().resizeEvent(event)
        
        # Ensure size constraints are respected
        size = event.size()
        if size.height() < 50:
            self.setMinimumHeight(50)
        if size.height() > 50:
            self.setMaximumHeight(50)
        if size.width() < 400:
            self.setMinimumWidth(400)
        if size.width() > 500:
            self.setMaximumWidth(500)
    
    def moveEvent(self, event):
        """Override move event to prevent geometry warnings."""
        # Call parent move event
        super().moveEvent(event)
        
        # Ensure position is valid
        pos = event.pos()
        if pos.x() < 0:
            self.move(0, pos.y())
        if pos.y() < 0:
            self.move(pos.x(), 0)
    
    def setup_ui(self):
        """Setup the notification UI."""
        self.setMinimumHeight(50)
        self.setMaximumHeight(50)
        self.setMinimumWidth(400)
        self.setMaximumWidth(500)  # Allow some flexibility in width
        
        # Main layout
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Icon label
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(20, 20)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.icon_label)
        
        # Message label
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 13px;
                font-weight: 500;
                line-height: 1.3;
            }
        """)
        layout.addWidget(self.message_label, 1)
        
        # Close button
        self.close_button = QPushButton("×")
        self.close_button.setFocusPolicy(Qt.NoFocus)
        self.close_button.setFixedSize(24, 24)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 12px;
                color: white;
                font-size: 16px;
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
        
        # Auto-hide timer
        self.auto_hide_timer = QTimer()
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self.hide_notification)
    
    def setup_animations(self):
        """Setup slide and fade animations."""
        # Slide down and fade in animation
        self.slide_in_animation = QPropertyAnimation(self, b"pos")
        self.slide_in_animation.setDuration(300)
        self.slide_in_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Fade in animation
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Slide up and fade out animation
        self.slide_out_animation = QPropertyAnimation(self, b"pos")
        self.slide_out_animation.setDuration(250)
        self.slide_out_animation.setEasingCurve(QEasingCurve.InCubic)
        
        # Fade out animation
        self.fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_animation.setDuration(250)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.InCubic)
        self.fade_out_animation.finished.connect(self._on_fade_out_finished)
    
    def paintEvent(self, event):
        """Custom paint event for rounded corners and shadow."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get the current background color from stylesheet
        bg_color = self._get_background_color()
        
        # Draw shadow (subtle)
        shadow_rect = QRect(2, 4, self.width() - 4, self.height() - 4)
        shadow_color = QColor(0, 0, 0, 30)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(shadow_color))
        painter.drawRoundedRect(shadow_rect, 12, 12)
        
        # Draw main background
        main_rect = QRect(0, 0, self.width(), self.height() - 2)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(main_rect, 12, 12)
        
        painter.end()
    
    def _get_background_color(self):
        """Get the current background color based on notification type."""
        # This will be set by the notification type
        return getattr(self, '_bg_color', QColor("#1E63E9"))
    
    def show_notification(self, message: str, notification_type: str = "primary", auto_hide: bool = True, duration: int = 3000):
        """Show a notification."""
        # Set message
        self.message_label.setText(message)
        
        # Set style based on type
        self.set_notification_style(notification_type)
        
        # Set icon based on type
        self.set_notification_icon(notification_type)
        
        # Position at top center (on the correct screen for the main window)
        self._position_at_top_center()
        
        # Show the notification with animations without stealing focus
        self.show()
        self.raise_()
        # Do not call activateWindow() to avoid stealing focus from inputs
        
        # Start animations
        self._animate_in()
        
        # Setup auto-hide if enabled
        if auto_hide:
            self.auto_hide_timer.start(duration)
    
    def _position_at_top_center(self):
        """Position the notification at the top center of the screen."""
        # Ensure we have a valid size before positioning
        self.adjustSize()
        
        # Get the main window (parent of parent) for proper centering
        main_window = None
        if self.parent():
            # Try to find the main window
            widget = self.parent()
            while widget and not hasattr(widget, 'isWindow') or not widget.isWindow():
                widget = widget.parent()
            if widget and widget.isWindow():
                main_window = widget
        
        if main_window:
            # Get screen where the main window currently is
            from PySide6.QtGui import QGuiApplication
            screen = main_window.screen() or QGuiApplication.screenAt(main_window.pos()) or QGuiApplication.primaryScreen()
            screen_geo = screen.availableGeometry()
            # Center relative to the main window rectangle
            window_rect = main_window.frameGeometry()
            x_position = window_rect.x() + (window_rect.width() - self.width()) // 2
            y_position = window_rect.y() + 20
            # Clamp to current screen bounds
            x_position = max(screen_geo.x(), min(x_position, screen_geo.x() + screen_geo.width() - self.width()))
            y_position = max(screen_geo.y(), y_position)
        else:
            # Fallback to screen center if no main window found
            from PySide6.QtGui import QGuiApplication
            screen = QGuiApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()
            x_position = screen_geometry.x() + (screen_geometry.width() - self.width()) // 2
            y_position = screen_geometry.y() + 20
        
        # Set initial position (off-screen for slide-in animation)
        self.move(x_position, y_position - self.height())
        self._target_position = (x_position, y_position)
    
    def _animate_in(self):
        """Animate the notification sliding in from top."""
        if hasattr(self, '_target_position'):
            x, y = self._target_position
            from PySide6.QtCore import QPoint
            self.slide_in_animation.setStartValue(self.pos())
            self.slide_in_animation.setEndValue(QPoint(x, y))
            
            self.setWindowOpacity(0.0)
            self.slide_in_animation.start()
            self.fade_in_animation.start()
    
    def hide_notification(self):
        """Hide the notification with slide up and fade out."""
        self.auto_hide_timer.stop()
        self._animate_out()
    
    def _animate_out(self):
        """Animate the notification sliding out to top."""
        current_pos = self.pos()
        from PySide6.QtCore import QPoint
        target_pos = QPoint(current_pos.x(), current_pos.y() - self.height())
        
        self.slide_out_animation.setStartValue(current_pos)
        self.slide_out_animation.setEndValue(target_pos)
        
        self.slide_out_animation.start()
        self.fade_out_animation.start()
    
    def _on_fade_out_finished(self):
        """Handle fade out animation finished."""
        self.hide()
        self.notification_closed.emit()
    
    def set_theme(self, theme: str):
        """Set the theme for the notification."""
        self.theme = theme or "Light"
    
    def _colors_for_type(self, notification_type: str):
        """Get colors for notification type."""
        light = self.theme.lower() != "dark"
        if notification_type in ("neutral", "info"):
            bg = "#6B7280" if light else "#4B5563"
            fg = "#FFFFFF"
        elif notification_type in ("error", "delete"):
            bg = "#EF4444"
            fg = "#FFFFFF"
        elif notification_type == "warning":
            bg = "#F59E0B"
            fg = "#000000"
        elif notification_type in ("success", "save"):
            # Darker green for better contrast
            bg = "#166534"
            fg = "#FFFFFF"
        elif notification_type in ("primary", "load"):
            bg = "#1E63E9" if light else "#3C82F6"
            fg = "#FFFFFF"
        else:  # fallback primary
            bg = "#1E63E9" if light else "#3C82F6"
            fg = "#FFFFFF"
        return bg, fg
    
    def set_notification_style(self, notification_type: str):
        """Set the notification style based on type and current theme."""
        bg, fg = self._colors_for_type(notification_type)
        self._bg_color = QColor(bg)
        
        indicator_bg = "rgba(255,255,255,0.2)" if fg == "#FFFFFF" else "rgba(0,0,0,0.12)"
        style = f"""
            QLabel {{ color: {fg}; background: transparent; }}
            QPushButton {{ color: {fg}; background-color: {indicator_bg}; border: none; border-radius: 12px; }}
            QPushButton:hover {{ background-color: rgba(255,255,255,0.25); }}
        """
        self.setStyleSheet(style)
    
    def set_notification_icon(self, notification_type: str):
        """Set the notification icon based on type."""
        icons = {
            "success": "✓",
            "error": "✕",
            "warning": "⚠",
            "info": "ℹ",
            "primary": "ℹ",
            "neutral": "ℹ"
        }
        
        icon = icons.get(notification_type, "ℹ")
        self.icon_label.setText(icon)


class CustomNotificationManager:
    """Custom notification manager for the rounded notification bar."""
    
    def __init__(self, parent_widget):
        self.parent_widget = parent_widget
        self.current_notification = None
        self._last_message = None
        self._last_when_ms = 0
    
    def show_notification(self, message: str, notification_type: str = "primary", auto_hide: bool = True, duration: int = 3000):
        """Show a new notification (replaces any existing one)."""
        try:
            # Deduplicate identical notifications within a short window
            from PySide6.QtCore import QTime
            now_ms = QTime.currentTime().msecsSinceStartOfDay()
            if self._last_message == message and (now_ms - self._last_when_ms) < 1500:
                return
            self._last_message = message
            self._last_when_ms = now_ms
        except Exception:
            pass
        # Hide current notification if exists
        if self.current_notification:
            self.current_notification.hide_notification()
        
        # Create new notification
        self.current_notification = CustomNotificationBar(self.parent_widget)
        
        # Set theme based on parent's theme
        try:
            from app.utils.settings_manager import SettingsManager
            theme = SettingsManager().get("theme", "Light")
            self.current_notification.set_theme(theme)
        except Exception:
            pass
        
        # Connect close signal
        self.current_notification.notification_closed.connect(self._on_notification_closed)
        
        # Show the notification
        self.current_notification.show_notification(message, notification_type, auto_hide, duration)
    
    def _on_notification_closed(self):
        """Handle notification closed."""
        if self.current_notification:
            self.current_notification.deleteLater()
            self.current_notification = None
    
    def hide_current(self):
        """Hide the current notification."""
        if self.current_notification:
            self.current_notification.hide_notification()
    
    def reposition_notifications(self):
        """Reposition notifications (compatibility method for resize events)."""
        # For the custom notification bar, we only have one notification at a time
        # and it's automatically positioned, so this method can be empty
        # or we can reposition the current notification if it exists
        if self.current_notification and self.current_notification.isVisible():
            self.current_notification._position_at_top_center()
    
    def clear_all(self):
        """Clear all notifications (compatibility method)."""
        # For the custom notification bar, we only have one notification at a time
        if self.current_notification:
            self.current_notification.hide_notification()
