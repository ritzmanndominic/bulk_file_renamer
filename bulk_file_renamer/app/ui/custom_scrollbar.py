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

from PySide6.QtWidgets import QScrollBar
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve


class CustomScrollBar(QScrollBar):
    """A thin, modern, minimal scrollbar that can be reused across the app.

    Usage:
        widget.setVerticalScrollBar(CustomScrollBar(Qt.Vertical))
        widget.setHorizontalScrollBar(CustomScrollBar(Qt.Horizontal))
    """

    def __init__(self, orientation: Qt.Orientation = Qt.Vertical, parent=None):
        super().__init__(orientation, parent)

        # Use a consistent width/height depending on orientation
        thickness = 8
        if orientation == Qt.Vertical:
            self.setFixedWidth(thickness + 2)
        else:
            self.setFixedHeight(thickness + 2)

        # Minimal, rounded handle with subtle hover/pressed states
        # Colors chosen to look good on both light/dark themes
        self.setStyleSheet(
            """
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 2px 2px 2px 2px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: rgba(120, 120, 120, 0.35);
                border-radius: 5px; /* rounded top/bottom */
                min-height: 24px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(120, 120, 120, 0.55);
            }
            QScrollBar::handle:vertical:pressed {
                background: rgba(120, 120, 120, 0.75);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }

            QScrollBar:horizontal {
                background: transparent;
                height: 10px;
                margin: 2px 2px 2px 2px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal {
                background: rgba(120, 120, 120, 0.35);
                border-radius: 5px;
                min-width: 24px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgba(120, 120, 120, 0.55);
            }
            QScrollBar::handle:horizontal:pressed {
                background: rgba(120, 120, 120, 0.75);
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
                background: transparent;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: transparent;
            }
            """
        )

        # Smooth scrolling animation setup
        self._anim = QPropertyAnimation(self, b"value")
        self._anim.setDuration(160)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def wheelEvent(self, event):  # type: ignore[override]
        """Animate wheel scrolling for smoother feel."""
        # Determine delta based on orientation
        pd = event.pixelDelta()
        ad = event.angleDelta()
        if self.orientation() == Qt.Vertical:
            delta = pd.y() if not pd.isNull() else ad.y()
        else:
            delta = pd.x() if not pd.isNull() else ad.x()

        if delta == 0:
            return super().wheelEvent(event)

        # Translate delta (120 units per wheel step) into slider steps
        steps = delta / 120.0
        step_size = max(1, self.singleStep())
        # Scale step for a more natural feel
        pixels = int(round(steps * step_size * 3))

        target = self.value() - pixels
        target = max(self.minimum(), min(self.maximum(), target))

        # Animate to target
        if self._anim.state() == QPropertyAnimation.Running:
            self._anim.stop()
        self._anim.setStartValue(self.value())
        self._anim.setEndValue(target)
        self._anim.start()
        event.accept()


