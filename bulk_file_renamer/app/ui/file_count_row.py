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

import os
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout
from app.utils.translation_manager import get_translation_manager


class FileCountRow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("FileCountRow")
        self.tr_manager = get_translation_manager()
        layout = QHBoxLayout()
        self.label = QLabel(self.tr_manager.tr("main.files_selected") + ": 0 | " + self.tr_manager.tr("main.files_filtered") + ": 0")
        self.label.setObjectName("FileCountLabel")
        layout.addWidget(self.label)
        self.setLayout(layout)

    def update_count(self, selected_count, filtered_count):
        self.label.setText(f"{self.tr_manager.tr('main.files_selected')}: {selected_count} | {self.tr_manager.tr('main.files_filtered')}: {filtered_count}")
    
    def update_language(self):
        """Update text with current language."""
        # Update the label with current language
        self.label.setText(self.tr_manager.tr("main.files_selected") + ": 0 | " + self.tr_manager.tr("main.files_filtered") + ": 0")
