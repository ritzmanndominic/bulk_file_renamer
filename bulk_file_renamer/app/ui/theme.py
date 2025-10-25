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

from PySide6.QtWidgets import QWidget
from app.ui.custom_combobox import CustomComboBox
from app.ui.custom_checkbox import CustomCheckBox
from app.ui.custom_spinbox import CustomSpinBox
from app.ui.plus_minus_spinbox import PlusMinusSpinBox


def _apply_arrow_colors(widget: QWidget, color: str) -> None:
    """Apply arrow color to all CustomComboBox widgets in the widget tree."""
    # Apply to the widget itself if it's a CustomComboBox
    if isinstance(widget, CustomComboBox):
        widget.set_arrow_color(color)
    
    # Recursively apply to all child widgets
    for child in widget.findChildren(CustomComboBox):
        child.set_arrow_color(color)


def _apply_checkbox_colors(widget: QWidget, check_color: str, border_color: str, bg_color: str) -> None:
    """Apply colors to all CustomCheckBox widgets in the widget tree."""
    # Apply to the widget itself if it's a CustomCheckBox
    if isinstance(widget, CustomCheckBox):
        widget.set_check_color(check_color)
        widget.set_border_color(border_color)
        widget.set_background_color(bg_color)
    
    # Recursively apply to all child widgets
    for child in widget.findChildren(CustomCheckBox):
        child.set_check_color(check_color)
        child.set_border_color(border_color)
        child.set_background_color(bg_color)


def _apply_spinbox_colors(widget: QWidget, arrow_color: str, button_bg: str, button_border: str, hover_bg: str, hover_border: str) -> None:
    """Apply colors to all CustomSpinBox and PlusMinusSpinBox widgets in the widget tree."""
    # Apply to the widget itself if it's a CustomSpinBox
    if isinstance(widget, CustomSpinBox):
        widget.set_arrow_color(arrow_color)
        widget.set_button_colors(button_bg, button_border, hover_bg, hover_border)
    
    # Apply to the widget itself if it's a PlusMinusSpinBox
    if isinstance(widget, PlusMinusSpinBox):
        widget.set_theme_colors(button_bg, button_border, hover_bg, hover_border, hover_bg, arrow_color, arrow_color)
    
    # Recursively apply to all child widgets
    for child in widget.findChildren(CustomSpinBox):
        child.set_arrow_color(arrow_color)
        child.set_button_colors(button_bg, button_border, hover_bg, hover_border)
    
    for child in widget.findChildren(PlusMinusSpinBox):
        child.set_theme_colors(button_bg, button_border, hover_bg, hover_border, hover_bg, arrow_color, arrow_color)


LIGHT_STYLESHEET = """
/* App Light Theme (custom palette) */
/* Palette: bg #FFFFFF, text #000000, border #D5D5D5, primary #1E63E9, hover #8EB2F6 */
QWidget { background: #FFFFFF; color: #000000; }
QMainWindow { background: #F8F9FA; }
QLabel { color: #000000; }
QLineEdit, QComboBox, QTextEdit, QSpinBox {
  background: #FFFFFF; border: 1px solid #D5D5D5; border-radius: 4px; padding: 4px 6px; color: #000000;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QSpinBox:focus { border: 1px solid #1E63E9; }
/* Standard/native checkbox - compact */
QCheckBox { spacing: 4px; }

/* Buttons - compact */
QPushButton#PrimaryButton {
  background: #1E63E9; color: #FFFFFF; border: 1px solid #1E63E9; border-radius: 6px; padding: 4px 10px; font-weight: 600;
}
QPushButton#PrimaryButton:hover { background: #8EB2F6; border-color: #8EB2F6; color: #000000; }
QPushButton#SecondaryButton {
  background: #FFFFFF; color: #000000; border: 1px solid #D5D5D5; border-radius: 6px; padding: 4px 10px; font-weight: 600;
}
QPushButton#SecondaryButton:hover { background: #F5F7FF; border-color: #8EB2F6; }

/* Table */
QTableWidget { background: #F8F9FA; border: 1px solid #D5D5D5; border-radius: 8px; gridline-color: #D5D5D5; color: #000000; }
QTableWidget::item { padding: 8px; background: #F8F9FA; }
QTableWidget::item:selected { background: #E3F2FD; color: #000000; }
QTableWidget::item:selected:focus { background: #BBDEFB; color: #000000; }
QTableWidget::item:alternate { background: #F8F9FA; }
QHeaderView::section { background: #F8F9FA; color: #000000; padding: 8px; border: 0px; border-bottom: 1px solid #D5D5D5; font-weight: 600; }
QTableCornerButton::section { background: #F8F9FA; border: 0px; border-bottom: 1px solid #D5D5D5; }
/* Vertical header (row numbers) styling */
QHeaderView::section:vertical { background: #F8F9FA; color: #6B7280; border: 0px; border-right: 1px solid #D5D5D5; font-weight: 500; }
/* Vertical header background area */
QTableWidget QHeaderView::section:vertical { background: #F8F9FA; }
QHeaderView:vertical { background: #F8F9FA; }

/* Group containers for settings/history - compact */
QGroupBox { border: 1px solid #D5D5D5; border-radius: 6px; margin-top: 8px; }
QGroupBox::title { subcontrol-origin: margin; left: 6px; padding: 0 3px; }
QTabWidget::pane { border: 1px solid #D5D5D5; border-radius: 6px; }
QListWidget { background: #FFFFFF; border: 1px solid #D5D5D5; border-radius: 6px; color: #000000; }

/* Main content areas */
QWidget#MainContentArea { background: #F8F9FA; }
QWidget#PreviewArea { background: #F8F9FA; }
QWidget#HistoryArea { background: #F8F9FA; }

/* File count and status labels */
QWidget#FileCountRow { background: #F8F9FA; }
QLabel#FileCountLabel { background: #F8F9FA; color: #000000; }

/* History specific */
QLabel#HistoryTitle { background: #F8F9FA; color: #000000; }
QScrollArea#HistoryScrollArea { background: #F8F9FA; border: none; }
QWidget#HistoryContainer { background: #F8F9FA; }
QFrame#HistoryEntry { 
    background: #FFFFFF; 
    border: 1px solid #E5E7EB; 
    border-radius: 8px; 
    margin: 2px;
}
QFrame#HistoryEntry:hover { 
    background: #F3F4F6; 
    border-color: #D1D5DB;
}
QLabel#HistoryEntryText { 
    color: #000000; 
    font-weight: 500;
}
QTextEdit#HistoryDetails { background: #FFFFFF; border: 1px solid #D5D5D5; color: #000000; }

/* Tab styling - compact */
QTabWidget::tab-bar {
    alignment: left;
    border-bottom: 1px solid #D5D5D5;
}
QTabBar::tab {
    background: #F8F9FA;
    border: 1px solid #D5D5D5;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 4px 10px;
    margin-right: 1px;
    color: #6B7280;
    font-weight: 500;
    min-width: 60px;
}
QTabBar::tab:selected {
    background: #FFFFFF;
    color: #1E63E9;
    font-weight: 600;
    border-bottom: 2px solid #1E63E9;
}
QTabBar::tab:hover:!selected {
    background: #F3F4F6;
    color: #374151;
}

/* Combobox popup + dropdown - remove any raised/shadow look */
QComboBox::drop-down { 
  border: none; 
  padding-right: 8px; 
  background: transparent;
}
QComboBox QAbstractItemView { background: #FFFFFF; border: 1px solid #D5D5D5; outline: 0; color: #000000; }

/* Generic buttons (for any without objectName) - compact */
QPushButton { padding: 4px 10px; border-radius: 6px; }
QPushButton:hover { background: #F3F4F6; }

/* Clear search button */
QPushButton#ClearSearchButton {
  background: transparent;
  border: none;
  color: #6B7280;
  font-size: 16px;
  font-weight: bold;
  padding: 0px;
  margin: 0px;
  border-radius: 10px;
}
QPushButton#ClearSearchButton:hover {
  background: rgba(107, 114, 128, 0.2);
  color: #374151;
}
"""


def get_light_stylesheet() -> str:
    return LIGHT_STYLESHEET


def apply_light_theme(widget: QWidget) -> None:
    """Apply the shared light theme to a root widget."""
    widget.setStyleSheet(LIGHT_STYLESHEET)
    _apply_arrow_colors(widget, "#000000")  # Black arrows for light theme
    _apply_checkbox_colors(widget, "#1E63E9", "#D5D5D5", "#FFFFFF")  # Blue check, light border, white bg
    _apply_spinbox_colors(widget, "#000000", "#FFFFFF", "#D5D5D5", "#F3F4F6", "#1E63E9")  # Black arrows, white bg, light border


# -------------------- Dark Theme --------------------
DARK_STYLESHEET = """
/* App Dark Theme (custom palette) */
/* Palette: bg #0D1117, text #FFFFFF, surface/border #2C2F33, primary #3C82F6, hover #AFC8FF */
QWidget { background: #0D1117; color: #FFFFFF; }
QLabel { color: #FFFFFF; }
QLineEdit, QComboBox, QTextEdit, QSpinBox {
  background: #2C2F33; border: 1px solid #2C2F33; border-radius: 4px; padding: 4px 6px; color: #FFFFFF;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QSpinBox:focus { border: 1px solid #3C82F6; }
QCheckBox { spacing: 4px; color: #FFFFFF; }
/* Ensure native checkbox is visible against dark bg */
QCheckBox::indicator { width: 16px; height: 16px; }

/* Buttons - compact */
QPushButton#PrimaryButton {
  background: #3C82F6; color: #0D1117; border: 1px solid #3C82F6; border-radius: 6px; padding: 4px 10px; font-weight: 600;
}
QPushButton#PrimaryButton:hover { background: #AFC8FF; border-color: #AFC8FF; color: #0D1117; }
QPushButton#SecondaryButton {
  background: #2C2F33; color: #FFFFFF; border: 1px solid #3A3F45; border-radius: 6px; padding: 4px 10px; font-weight: 600;
}
QPushButton#SecondaryButton:hover { background: #394047; }

/* Table */
QTableWidget { background: #2C2F33; border: 1px solid #2C2F33; border-radius: 8px; gridline-color: #2C2F33; color: #FFFFFF; }
QTableWidget::item { padding: 8px; background: #2C2F33; }
QTableWidget::item:selected { background: #1E3A8A; color: #FFFFFF; }
QTableWidget::item:selected:focus { background: #1D4ED8; color: #FFFFFF; }
QTableWidget::item:alternate { background: #2C2F33; }
QHeaderView::section { background: #2C2F33; color: #FFFFFF; padding: 8px; border: 0px; border-bottom: 1px solid #2C2F33; font-weight: 600; }
QTableCornerButton::section { background: #2C2F33; border: 0px; border-bottom: 1px solid #2C2F33; }
/* Vertical header (row numbers) styling */
QHeaderView::section:vertical { background: #2C2F33; color: #9CA3AF; border: 0px; border-right: 1px solid #2C2F33; font-weight: 500; }
/* Vertical header background area */
QTableWidget QHeaderView::section:vertical { background: #2C2F33; }
QHeaderView:vertical { background: #2C2F33; }

/* Group containers - compact */
QGroupBox { border: 1px solid #2C2F33; border-radius: 6px; margin-top: 8px; color: #FFFFFF; }
QGroupBox::title { subcontrol-origin: margin; left: 6px; padding: 0 3px; }
QTabWidget::pane { border: 1px solid #2C2F33; border-radius: 6px; }
QListWidget { background: #2C2F33; border: 1px solid #2C2F33; border-radius: 6px; color: #FFFFFF; }
QWidget#qt_tabwidget_stackedwidget { background: #2C2F33; }

/* Tab styling for dark theme - compact */
QTabWidget::tab-bar {
    alignment: left;
    border-bottom: 1px solid #2C2F33;
}
QTabBar::tab {
    background: #1A1D21;
    border: 1px solid #2C2F33;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 4px 10px;
    margin-right: 1px;
    color: #9CA3AF;
    font-weight: 500;
    min-width: 60px;
}
QTabBar::tab:selected {
    background: #2C2F33;
    color: #3C82F6;
    font-weight: 600;
    border-bottom: 2px solid #3C82F6;
}
QTabBar::tab:hover:!selected {
    background: #252930;
    color: #D1D5DB;
}

/* Combobox dropdown arrow for dark mode */
QComboBox::drop-down { 
  border: none; 
  padding-right: 8px; 
  background: transparent;
}
QComboBox QAbstractItemView { background: #2C2F33; border: 1px solid #2C2F33; outline: 0; color: #FFFFFF; }

/* File count and status labels */
QWidget#FileCountRow { background: #0D1117; }
QLabel#FileCountLabel { background: #0D1117; color: #FFFFFF; }

/* History specific */
QLabel#HistoryTitle { background: #0D1117; color: #FFFFFF; }
QScrollArea#HistoryScrollArea { background: #0D1117; border: none; }
QWidget#HistoryContainer { background: #0D1117; }
QFrame#HistoryEntry { 
    background: #2C2F33; 
    border: 1px solid #3A3F45; 
    border-radius: 8px; 
    margin: 2px;
}
QFrame#HistoryEntry:hover { 
    background: #394047; 
    border-color: #4B5563;
}
QLabel#HistoryEntryText { 
    color: #FFFFFF; 
    font-weight: 500;
}
QTextEdit#HistoryDetails { background: #2C2F33; border: 1px solid #2C2F33; color: #FFFFFF; }

/* Clear search button */
QPushButton#ClearSearchButton {
  background: transparent;
  border: none;
  color: #9CA3AF;
  font-size: 16px;
  font-weight: bold;
  padding: 0px;
  margin: 0px;
  border-radius: 10px;
}
QPushButton#ClearSearchButton:hover {
  background: rgba(156, 163, 175, 0.2);
  color: #D1D5DB;
}
"""


def get_dark_stylesheet() -> str:
    return DARK_STYLESHEET


def apply_dark_theme(widget: QWidget) -> None:
    widget.setStyleSheet(DARK_STYLESHEET)
    _apply_arrow_colors(widget, "#FFFFFF")  # White arrows for dark theme
    _apply_checkbox_colors(widget, "#3C82F6", "#4B5563", "#2C2F33")  # Blue check, lighter border, dark bg
    _apply_spinbox_colors(widget, "#FFFFFF", "#2C2F33", "#2C2F33", "#394047", "#3C82F6")  # White arrows, dark bg, dark border


def apply_theme(widget: QWidget, theme_name: str) -> None:
    name = (theme_name or "Light").strip().lower()
    # Smooth transition: fade in after stylesheet change
    try:
        from PySide6.QtWidgets import QGraphicsOpacityEffect
        from PySide6.QtCore import QPropertyAnimation
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        effect.setOpacity(0.0)
    except Exception:
        effect = None

    if name == "dark":
        apply_dark_theme(widget)
    else:
        apply_light_theme(widget)

    if effect is not None:
        try:
            from PySide6.QtCore import QEasingCurve
            anim = QPropertyAnimation(effect, b"opacity", widget)
            anim.setDuration(180)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.InOutSine)
            anim.start()
        except Exception:
            # If animation fails, remove effect immediately
            widget.setGraphicsEffect(None)


