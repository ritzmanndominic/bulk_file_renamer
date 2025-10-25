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

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QCheckBox, QSizePolicy, QGroupBox,
    QScrollArea, QSplitter
)
from app.ui.custom_scrollbar import CustomScrollBar
from .custom_combobox import CustomComboBox
from .custom_checkbox import CustomCheckBox
from .custom_search_field import CustomSearchField
from PySide6.QtGui import QColor, QBrush
from PySide6.QtCore import Qt, Signal
from app.ui.history_panel import HistoryPanel
from app.ui.file_count_row import FileCountRow
from .date_input import DateInput
from app.utils.translation_manager import get_translation_manager
# Theme is applied at the main window level; avoid forcing a specific theme here

class TopPanel(QWidget):
    remove_selected = Signal(list)
    def __init__(self, browse_folder_cb, select_files_cb, clear_all_cb, preview_callback,
                 save_profile_cb=None, load_profile_cb=None, delete_profile_cb=None, refresh_profiles_cb=None,
                 rename_cb=None, undo_cb=None, undo_selected_cb=None, validate_cb=None):
        super().__init__()
        self.setAcceptDrops(False)  # Don't accept drops - let them bubble up to main window
        self.browse_folder_cb = browse_folder_cb
        self.select_files_cb = select_files_cb
        self.clear_all_cb = clear_all_cb
        self.preview_callback = preview_callback
        self.save_profile_cb = save_profile_cb
        self.load_profile_cb = load_profile_cb
        self.delete_profile_cb = delete_profile_cb
        self.refresh_profiles_cb = refresh_profiles_cb
        
        # Get translation manager
        self.tr_manager = get_translation_manager()

        # Root two-column layout
        root = QHBoxLayout()
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)
        # Left sidebar (controls) and right content (preview + history)
        left_sidebar = QVBoxLayout()
        left_sidebar.setSpacing(8)
        left_sidebar.setContentsMargins(0, 0, 0, 0)
        right_panel = QVBoxLayout()
        right_panel.setSpacing(8)

        # Helper for localized titles with sensible fallbacks
        def _t_title(key: str, fallback: str) -> str:
            try:
                val = self.tr_manager.tr(key)
                return val if val and val != key else fallback
            except Exception:
                return fallback

        # Theme is applied by parent via app.ui.theme.apply_theme

        # Naming Section - Inputs arranged to match mockup
        # Row1: Prefix + Suffix side-by-side (placeholders, no labels)
        naming_row1 = QHBoxLayout()
        naming_row1.setSpacing(8)
        
        def _strip_colon(text: str) -> str:
            return text.replace(":", "") if isinstance(text, str) else text

        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText(_strip_colon(self.tr_manager.tr("top_panel.naming.prefix")))
        self.prefix_input.setToolTip(self.tr_manager.tr("ui.tooltip_prefix"))
        self.suffix_input = QLineEdit()
        self.suffix_input.setPlaceholderText(_strip_colon(self.tr_manager.tr("top_panel.naming.suffix")))
        self.suffix_input.setToolTip(self.tr_manager.tr("ui.tooltip_suffix"))
        self.base_input = QLineEdit()
        self.base_input.setPlaceholderText(_strip_colon(self.tr_manager.tr("top_panel.naming.base_name")))
        self.base_input.setToolTip(self.tr_manager.tr("ui.tooltip_base_name"))
        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText(_strip_colon(self.tr_manager.tr("top_panel.naming.start_number")))
        # Start number is required when renaming files
        self.start_input.setToolTip(self.tr_manager.tr("ui.tooltip_start_number"))
        # Set a custom object name for specific styling
        self.start_input.setObjectName("startNumberField")
        # Add visual indicator that this field is required
        self.start_input.setStyleSheet("QLineEdit#startNumberField { border: 2px solid #ff6b6b !important; }")  # Red border to indicate required
        
        # Track focus state for better focus maintenance
        self._start_input_has_focus = False
        
        naming_row1.addWidget(self.prefix_input)
        naming_row1.addWidget(self.suffix_input)
        
        # Right side: Extension Lock
        self.extension_lock_checkbox = CustomCheckBox("🔒 " + self.tr_manager.tr("top_panel.naming.extension_lock"))
        self.extension_lock_checkbox.setChecked(True)
        self.extension_lock_checkbox.setToolTip(self.tr_manager.tr("ui.extension_lock_tooltip"))
        
        # Add a callback to update the checkbox text based on state
        def update_checkbox_text():
            if self.extension_lock_checkbox.isChecked():
                self.extension_lock_checkbox.setText("🔒 " + self.tr_manager.tr("top_panel.naming.extension_lock_active"))
            else:
                self.extension_lock_checkbox.setText("🔓 " + self.tr_manager.tr("top_panel.naming.extension_lock_disabled"))
        
        self.extension_lock_checkbox.stateChanged.connect(update_checkbox_text)
        update_checkbox_text()  # Set initial text
        
        # (Extension lock will be placed on its own row below)
        # --- Naming group ---
        self.naming_group = QGroupBox(_t_title("top_panel.naming.title", "Naming"))
        self.naming_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        naming_group_layout = QVBoxLayout()
        naming_group_layout.setSpacing(8)
        # Row1: Prefix + Suffix
        naming_group_layout.addLayout(naming_row1)
        # Row2: Base Name full width
        base_row = QHBoxLayout()
        base_row.setSpacing(8)
        base_row.addWidget(self.base_input)
        naming_group_layout.addLayout(base_row)
        # Row3: Start Number full width
        start_row = QHBoxLayout()
        start_row.setSpacing(8)
        start_row.addWidget(self.start_input)
        naming_group_layout.addLayout(start_row)

        # Row4: Extension lock line
        lock_row = QHBoxLayout()
        lock_row.setSpacing(8)
        lock_row.addWidget(self.extension_lock_checkbox)
        lock_row.addStretch()
        naming_group_layout.addLayout(lock_row)

        # Auto-clean controls (nested group inside Naming)
        # Title becomes the group header to visually look like a sub-section
        auto_clean_title = _t_title("top_panel.auto_clean.title", "Auto-clean")
        
        # Auto-clean checkboxes
        self.remove_special_chars_check = CustomCheckBox(self.tr_manager.tr("top_panel.auto_clean.remove_special_chars"))
        self.replace_spaces_check = CustomCheckBox(self.tr_manager.tr("top_panel.auto_clean.replace_spaces"))
        self.convert_case_check = CustomCheckBox(self.tr_manager.tr("top_panel.auto_clean.convert_case"))
        self.remove_accents_check = CustomCheckBox(self.tr_manager.tr("top_panel.auto_clean.remove_accents"))
        
        # Case conversion dropdown
        self.case_type_combo = CustomComboBox()
        self.case_type_combo.addItems([
            self.tr_manager.tr("top_panel.auto_clean.case_types.lowercase"),
            self.tr_manager.tr("top_panel.auto_clean.case_types.titlecase"),
            self.tr_manager.tr("top_panel.auto_clean.case_types.uppercase")
        ])
        # Default to Titlecase
        try:
            _title_txt = self.tr_manager.tr("top_panel.auto_clean.case_types.titlecase")
            _idx = self.case_type_combo.findText(_title_txt)
            if _idx >= 0:
                self.case_type_combo.setCurrentIndex(_idx)
        except Exception:
            pass
        # Set size policy to prevent cutoff
        self.case_type_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # Keep dropdown enabled always; selecting a value can auto-enable the checkbox
        
        # Connect case checkbox (no longer controls enabled state of dropdown)
        self.convert_case_check.stateChanged.connect(self.preview_callback)
        
        # Row1 inside auto-clean: Special Chars
        ac_row1 = QHBoxLayout()
        ac_row1.setSpacing(8)
        ac_row1.addWidget(self.remove_special_chars_check)

        # Row2: Replace Spaces
        ac_row2 = QHBoxLayout()
        ac_row2.setSpacing(8)
        ac_row2.addWidget(self.replace_spaces_check)

        # Row3: Remove Accents
        ac_row3 = QHBoxLayout()
        ac_row3.setSpacing(8)
        ac_row3.addWidget(self.remove_accents_check)

        # Row4: Convert Case + case type dropdown
        ac_row4 = QHBoxLayout()
        ac_row4.setSpacing(8)
        ac_row4.addWidget(self.convert_case_check)
        ac_row4.addWidget(self.case_type_combo)
        ac_row4.addStretch()

        # Compose nested auto-clean group and add to Naming section
        self.auto_group = QGroupBox(auto_clean_title)
        auto_group_layout = QVBoxLayout()
        auto_group_layout.setSpacing(8)
        auto_group_layout.addLayout(ac_row1)
        auto_group_layout.addLayout(ac_row2)
        auto_group_layout.addLayout(ac_row3)
        auto_group_layout.addLayout(ac_row4)
        self.auto_group.setLayout(auto_group_layout)
        naming_group_layout.addWidget(self.auto_group)

        # Files section (buttons)
        files_row = QHBoxLayout()
        files_row.setSpacing(8)
        self.btn_browse_folder = QPushButton(self.tr_manager.tr("main.browse_folder"))
        self.btn_browse_folder.setObjectName("PrimaryButton")
        self.btn_browse_files = QPushButton(self.tr_manager.tr("main.select_files"))
        self.btn_browse_files.setObjectName("PrimaryButton")
        # Keep button height constant across resizes
        try:
            fixed_h = max(self.btn_browse_folder.sizeHint().height(), 1)
            self.btn_browse_folder.setFixedHeight(fixed_h)
            self.btn_browse_files.setFixedHeight(fixed_h)
        except Exception:
            pass
        # Make them share the row equally
        try:
            self.btn_browse_folder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            self.btn_browse_files.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        except Exception:
            pass
        self.btn_browse_folder.clicked.connect(lambda: self.browse_folder_cb(None))
        self.btn_browse_files.clicked.connect(lambda: self.select_files_cb(None))
        # Give each button equal stretch so each takes half the width
        files_row.addWidget(self.btn_browse_folder, 1)
        files_row.addWidget(self.btn_browse_files, 1)
        # --- Files group ---
        self.files_group = QGroupBox(_t_title("top_panel.files.title", "Files"))
        self.files_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        files_group_layout = QVBoxLayout()
        files_group_layout.setSpacing(8)
        # Place both buttons on the same row, each occupying half width
        files_group_layout.addLayout(files_row)
        self.files_group.setLayout(files_group_layout)

        # Profile Management
        profile_layout = QHBoxLayout()
        profile_layout.setSpacing(8)
        self.profile_combo = CustomComboBox()
        self.profile_combo.setPlaceholderText(self.tr_manager.tr("top_panel.profiles.select_profile_placeholder"))
        # Set size policy to prevent cutoff
        self.profile_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_save_profile = QPushButton(self.tr_manager.tr("top_panel.profiles.save"))
        self.btn_save_profile.setObjectName("SecondaryButton")
        self.btn_load_profile = QPushButton(self.tr_manager.tr("top_panel.profiles.load"))
        self.btn_load_profile.setObjectName("SecondaryButton")
        self.btn_delete_profile = QPushButton(self.tr_manager.tr("top_panel.profiles.delete"))
        self.btn_delete_profile.setObjectName("SecondaryButton")
        
        profile_label = QLabel(self.tr_manager.tr("top_panel.profiles.profile"))
        profile_layout.addWidget(profile_label)
        profile_layout.addWidget(self.profile_combo, 1)
        profile_layout.addWidget(self.btn_save_profile)
        profile_layout.addWidget(self.btn_load_profile)
        profile_layout.addWidget(self.btn_delete_profile)
        
        # Connect profile buttons
        self.btn_save_profile.clicked.connect(self._on_save_profile)
        self.btn_load_profile.clicked.connect(self._on_load_profile)
        self.btn_delete_profile.clicked.connect(self._on_delete_profile)
        
        # --- Profiles group ---
        self.profiles_group = QGroupBox(_t_title("top_panel.profiles.title", "Profiles"))
        self.profiles_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        profiles_group_layout = QVBoxLayout()
        profiles_group_layout.setSpacing(8)
        # Row1: profile combo full width
        profile_row1 = QHBoxLayout()
        profile_row1.setSpacing(8)
        profile_row1.addWidget(self.profile_combo, 1)
        profiles_group_layout.addLayout(profile_row1)
        # Row2: Save + Load
        profile_row2 = QHBoxLayout()
        profile_row2.setSpacing(8)
        profile_row2.addWidget(self.btn_save_profile)
        profile_row2.addWidget(self.btn_load_profile)
        profiles_group_layout.addLayout(profile_row2)
        # Row3: Delete full width
        profiles_group_layout.addWidget(self.btn_delete_profile)
        self.profiles_group.setLayout(profiles_group_layout)

        # Row 3: Filters - organized in logical groups
        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)
        
        # Extension filter
        self.ext_filter_input = QLineEdit()
        self.ext_filter_input.setPlaceholderText(self.tr_manager.tr("top_panel.filters.extension_placeholder"))
        filter_row.addWidget(QLabel(self.tr_manager.tr("top_panel.filters.extension_filter")))
        filter_row.addWidget(self.ext_filter_input)
        
        # Size filter group
        self.size_operator = CustomComboBox()
        # Use human-readable operators in UI
        self.size_operator.addItems([
            self.tr_manager.tr("ui.size_operators.greater_than"),
            self.tr_manager.tr("ui.size_operators.less_than"),
            self.tr_manager.tr("ui.size_operators.equal")
        ])
        # Set size policy to prevent cutoff
        self.size_operator.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.size_value = QLineEdit()
        self.size_value.setPlaceholderText(self.tr_manager.tr("top_panel.filters.size_placeholder"))
        # Allow the size value field to expand on smaller displays
        self.size_value.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.size_unit = CustomComboBox()
        # Use standard abbreviations to match tests
        self.size_unit.addItems(["B", "KB", "MB", "GB"])
        # Set minimum width to prevent text truncation
        self.size_unit.setMinimumWidth(60)
        # Set size policy to prevent cutoff
        self.size_unit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        filter_row.addWidget(QLabel(self.tr_manager.tr("top_panel.filters.size_filter")))
        filter_row.addWidget(self.size_operator)
        filter_row.addWidget(self.size_value)
        
        # Date filter group
        self.date_operator = CustomComboBox()
        self.date_operator.addItems([
            self.tr_manager.tr("top_panel.filters.date_operators.before"),
            self.tr_manager.tr("top_panel.filters.date_operators.after")
        ])
        # Set size policy to prevent cutoff
        self.date_operator.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.date_value = DateInput()
        # Connect date validation signal to show notifications
        self.date_value.date_validation_changed.connect(self._on_date_validation_changed)
        filter_row.addWidget(QLabel(self.tr_manager.tr("top_panel.filters.date_filter")))
        filter_row.addWidget(self.date_operator)
        filter_row.addWidget(self.date_value)
        
        # Status filter
        self.status_filter = CustomComboBox()
        # Use status values consistent with preview statuses and tests
        self.status_filter.addItems([
            self.tr_manager.tr("top_panel.filters.status_options.all"),
            self.tr_manager.tr("ui.status_options.ready"),
            self.tr_manager.tr("ui.status_options.conflict"),
            self.tr_manager.tr("ui.status_options.no_change"),
            self.tr_manager.tr("ui.status_options.extension_locked")
        ])
        # Set size policy to prevent cutoff
        self.status_filter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.status_filter.setCurrentIndex(0)  # Set to "All" by default
        filter_row.addWidget(QLabel(self.tr_manager.tr("top_panel.filters.status_filter")))
        filter_row.addWidget(self.status_filter)
        
        # --- Filters group ---
        self.filters_group = QGroupBox(_t_title("top_panel.filters.title", "Filters"))
        self.filters_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        filters_group_layout = QVBoxLayout()
        filters_group_layout.setSpacing(8)
        # Row1: Extension filter full width
        ext_row = QHBoxLayout()
        ext_row.setSpacing(8)
        ext_row.addWidget(self.ext_filter_input, 1)
        filters_group_layout.addLayout(ext_row)
        # Row2: Size operator + value (unit moved to status row for space)
        size_row = QHBoxLayout()
        size_row.setSpacing(8)
        size_row.addWidget(self.size_operator)
        size_row.addWidget(self.size_value, 1)
        # Row3: Date operator + value
        date_row = QHBoxLayout()
        date_row.setSpacing(8)
        date_row.addWidget(self.date_operator)
        date_row.addWidget(self.date_value, 1)
        # Add Date row before Size row
        filters_group_layout.addLayout(date_row)
        # Now add Size row
        filters_group_layout.addLayout(size_row)
        # Row4: Status filter with unit dropdown to the right
        status_row = QHBoxLayout()
        status_row.setSpacing(8)
        status_row.addWidget(self.status_filter, 1)
        status_row.addWidget(self.size_unit)
        filters_group_layout.addLayout(status_row)
        self.filters_group.setLayout(filters_group_layout)

        # Add groups to sidebar
        self.naming_group.setLayout(naming_group_layout)
        left_sidebar.addWidget(self.naming_group)
        left_sidebar.addWidget(self.files_group)
        left_sidebar.addWidget(self.filters_group)
        left_sidebar.addWidget(self.profiles_group)
        left_sidebar.addStretch(1)

        # Row 4: Search, Clear All, and Export - compact layout
        search_row = QHBoxLayout()
        search_row.setSpacing(8)
        
        # Search section with integrated clear button
        self.search_input = CustomSearchField(self.tr_manager.tr("top_panel.preview.search_placeholder"))
        
        search_row.addWidget(self.search_input)
        
        # Clear All and Export buttons on the right
        search_row.addStretch()
        self.btn_clear = QPushButton(self.tr_manager.tr("main.clear_all"))
        self.btn_clear.setObjectName("SecondaryButton")
        # Remove fixed width to allow responsive sizing
        self.btn_clear.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.btn_clear.clicked.connect(self.clear_all_cb)
        search_row.addWidget(self.btn_clear)
        
        self.export_btn = QPushButton(self.tr_manager.tr("top_panel.preview.export_preview"))
        self.export_btn.setObjectName("PrimaryButton")
        # Remove fixed width to allow responsive sizing
        self.export_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        search_row.addWidget(self.export_btn)
        
        right_panel.addLayout(search_row)

        # Preview Table
        # QTableWidget subclass to expose horizontalHeaderLabels() for tests
        class PreviewTable(QTableWidget):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.tr_manager = get_translation_manager()
                self.setAcceptDrops(False)  # Don't accept drops - let them bubble up to main window
            
            def horizontalHeaderLabels(self):
                return [self.horizontalHeaderItem(i).text() if self.horizontalHeaderItem(i) else "" for i in range(self.columnCount())]
            
            def resizeEvent(self, event):
                super().resizeEvent(event)
                # Reposition empty overlay if present
                try:
                    if hasattr(self, "_reposition_overlay") and callable(self._reposition_overlay):
                        self._reposition_overlay()
                except Exception:
                    pass

            def mousePressEvent(self, event):
                # Support range (Shift), additive toggle (Ctrl/Cmd), and simple toggle (no modifier)
                try:
                    if event is not None and event.buttons() == Qt.LeftButton:
                        idx = self.indexAt(event.pos())
                        if idx.isValid():
                            from PySide6.QtCore import QItemSelectionModel
                            sel = self.selectionModel()
                            mods = event.modifiers()
                            if mods & Qt.ShiftModifier and hasattr(self, "_anchor_row") and self._anchor_row is not None:
                                start = min(self._anchor_row, idx.row())
                                end = max(self._anchor_row, idx.row())
                                for r in range(start, end + 1):
                                    mi = self.model().index(r, 0)
                                    sel.select(mi, QItemSelectionModel.Select | QItemSelectionModel.Rows)
                                return
                            # On macOS use Command (Meta) as multi-select modifier
                            elif (mods & Qt.ControlModifier) or (mods & Qt.MetaModifier):
                                sel.select(idx, QItemSelectionModel.Toggle | QItemSelectionModel.Rows)
                                # Keep anchor as first selected row for future shift selection
                                if not hasattr(self, "_anchor_row") or self._anchor_row is None:
                                    self._anchor_row = idx.row()
                                return
                            else:
                                # Plain click toggles the row selection (easier multi-select without Ctrl)
                                sel.select(idx, QItemSelectionModel.Toggle | QItemSelectionModel.Rows)
                                if not hasattr(self, "_anchor_row") or self._anchor_row is None:
                                    self._anchor_row = idx.row()
                                return
                except Exception:
                    pass
                super().mousePressEvent(event)
            
            def show_loading(self, show: bool):
                if not hasattr(self, "_loading_overlay"):
                    from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
                    self._loading_overlay = QWidget(self.viewport())
                    self._loading_overlay.setAttribute(Qt.WA_TransparentForMouseEvents, True)
                    lay = QVBoxLayout(self._loading_overlay)
                    lay.setContentsMargins(0, 0, 0, 0)
                    lay.setAlignment(Qt.AlignCenter)
                    lbl = QLabel(self.tr_manager.tr("ui.loading"))
                    lbl.setStyleSheet("QLabel { color: #6B7280; font-size: 13px; }")
                    lay.addWidget(lbl)
                    self._loading_overlay.hide()
                r = self.viewport().rect()
                height = 56
                self._loading_overlay.setGeometry(r.x(), r.y() + r.height() - height, r.width(), height)
                self._loading_overlay.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 rgba(0,0,0,0.0), stop:1 rgba(0,0,0,0.04)); border: none;")
                self._loading_overlay.setVisible(show)

        self.table = PreviewTable(0, 3)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.MultiSelection)
        self.table.setHorizontalHeaderLabels([
            self.tr_manager.tr("top_panel.preview.old_name"),
            self.tr_manager.tr("top_panel.preview.new_name"),
            self.tr_manager.tr("top_panel.preview.status")
        ])
        # Responsive columns: use full width on large screens; allow scroll on small
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Interactive)    # Old Name (compact)
        header.setSectionResizeMode(1, QHeaderView.Stretch)        # New Name (flex)
        header.setSectionResizeMode(2, QHeaderView.Interactive)    # Status (fixed-ish)
        header.setMinimumSectionSize(60)
        # Ensure header captions align above left-aligned cell text
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # Add a small left padding so header text aligns with cell content
        try:
            # Small left padding so header aligns visually with left-aligned badges in cells
            header.setStyleSheet("QHeaderView::section { padding-left: 8px; }")
        except Exception:
            pass
        # Provide sensible minimums so columns don't collapse on narrow windows
        try:
            self.table.setColumnWidth(0, 180)
            self.table.setColumnWidth(1, 520)
            # Status column smaller (about half of before)
            self.table.setColumnWidth(2, 160)
        except Exception:
            pass
        # Increase default row height so inline buttons fit
        try:
            self.table.verticalHeader().setDefaultSectionSize(34)
        except Exception:
            pass
        self.table.setAlternatingRowColors(False)
        self.table.setShowGrid(False)
        self.table.setWordWrap(False)
        # Make the table expand to fill available space within TopPanel
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Smooth scrolling behavior
        from PySide6.QtWidgets import QAbstractItemView
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        # Apply custom scrollbars to the preview table
        self.table.setVerticalScrollBar(CustomScrollBar(Qt.Vertical))
        self.table.setHorizontalScrollBar(CustomScrollBar(Qt.Horizontal))
        
        # Initialize sorting state
        self.sort_column = -1  # -1 means no sorting
        self.sort_ascending = True
        
        # Lazy loading state
        self._full_preview_data = []
        self._rendered_rows = 0
        # Fixed batch size for lazy loading - no longer depends on max files setting
        self._batch_size = 100
        
        # Load more on scroll near bottom
        self.table.verticalScrollBar().valueChanged.connect(self._maybe_load_more_rows)
        self.table.itemSelectionChanged.connect(self._on_table_selection_changed)
        
        # Make headers clickable
        self.table.horizontalHeader().sectionClicked.connect(self._on_header_clicked)
        self.table.horizontalHeader().setSectionsClickable(True)
        
        # Add table to right panel (will be added to splitter later)
        # right_panel.addWidget(self.table, 2)  # Moved to splitter

        # Empty-state drag & drop overlay (container with icon + text)
        self.table._empty_overlay = QWidget(self.table.viewport())
        self.table._empty_overlay.setObjectName("EmptyOverlay")
        self.table._empty_overlay.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._empty_layout = QVBoxLayout()
        self._empty_layout.setContentsMargins(24, 16, 24, 16)
        self._empty_layout.setSpacing(8)
        self._empty_layout.setAlignment(Qt.AlignCenter)
        self._empty_icon = QLabel("📂")
        self._empty_icon.setAlignment(Qt.AlignCenter)
        self._empty_icon.setStyleSheet("QLabel { font-size: 28px; color: #9CA3AF; border: none; background: transparent; }")
        self._empty_text = QLabel()
        self._empty_text.setAlignment(Qt.AlignCenter)
        self._empty_text.setWordWrap(True)
        self._empty_text.setStyleSheet("QLabel { color: #6B7280; font-size: 14px; border: none; background: transparent; }")
        self._empty_text.setTextFormat(Qt.PlainText)
        self._empty_layout.addWidget(self._empty_icon)
        self._empty_layout.addWidget(self._empty_text)
        self.table._empty_overlay.setLayout(self._empty_layout)
        self.table._empty_overlay.setStyleSheet(
            "#EmptyOverlay {\n"
            "  border: 2px dashed #D1D5DB;\n"
            "  border-radius: 10px;\n"
            "  background: rgba(0,0,0,0.02);\n"
            "}"
        )
        self.table._empty_overlay.hide()

        # Helper to center and size the overlay nicely
        def _reposition_overlay():
            vp = self.table.viewport().rect()
            # Compute a content-aware minimum height
            try:
                m = self._empty_layout.contentsMargins()
                content_h = self._empty_icon.sizeHint().height() + self._empty_text.sizeHint().height() + self._empty_layout.spacing() + m.top() + m.bottom()
            except Exception:
                content_h = 120
            width = max(min(int(vp.width() * 0.8), 600), 260)
            height = max(min(int(vp.height() * 0.6), 220), content_h)
            x = vp.x() + max((vp.width() - width) // 2, 0)
            y = vp.y() + max((vp.height() - height) // 2, 0)
            self.table._empty_overlay.setGeometry(x, y, width, height)
        self.table._reposition_overlay = _reposition_overlay
        # initial text set after helper definition below

        # Create file count and action buttons (will be added between table and history)
        self.file_count = FileCountRow()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.rename_button = QPushButton(self.tr_manager.tr("main.rename_files"))
        self.rename_button.setObjectName("PrimaryButton")
        self.undo_button = QPushButton(self.tr_manager.tr("main.undo_last_rename"))
        self.undo_button.setObjectName("SecondaryButton")
        self.undo_button.setEnabled(False)
        self.undo_selected_button = QPushButton(self.tr_manager.tr("ui.undo_selected"))
        self.undo_selected_button.setObjectName("SecondaryButton")
        if callable(rename_cb):
            self.rename_button.clicked.connect(rename_cb)
        if callable(undo_cb):
            self.undo_button.clicked.connect(undo_cb)
        if callable(undo_selected_cb):
            self.undo_selected_button.clicked.connect(undo_selected_cb)
        # Validate/Simulate button
        self.validate_button = QPushButton(self.tr_manager.tr("ui.validate_simulate"))
        self.validate_button.setObjectName("SecondaryButton")
        if callable(validate_cb):
            self.validate_button.clicked.connect(validate_cb)
        # Remove selected button (hidden until selection)
        self.remove_selected_btn = QPushButton(self.tr_manager.tr("ui.remove_selected"))
        self.remove_selected_btn.setObjectName("SecondaryButton")
        self.remove_selected_btn.setVisible(False)
        self.remove_selected_btn.clicked.connect(self._on_remove_selected_clicked)

        btn_row.addWidget(self.rename_button)
        btn_row.addWidget(self.undo_button)
        btn_row.addWidget(self.undo_selected_button)
        btn_row.addWidget(self.validate_button)
        btn_row.addWidget(self.remove_selected_btn)
        btn_row.addStretch()

        # History panel below actions
        self.history_panel = HistoryPanel()
        
        # Create a container for file count, buttons, and history
        from PySide6.QtWidgets import QWidget as _QWidget
        bottom_container = _QWidget()
        bottom_container.setObjectName("HistoryArea")
        bottom_layout = QVBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 8, 0, 0)  # Small top margin for spacing
        bottom_layout.setSpacing(8)
        
        # Add file count, buttons, and history to the bottom container
        bottom_layout.addWidget(self.file_count)
        bottom_layout.addLayout(btn_row)
        bottom_layout.addWidget(self.history_panel, 1)  # History gets stretch factor
        
        # Create vertical splitter for table and bottom container
        vertical_splitter = QSplitter(Qt.Vertical)
        vertical_splitter.addWidget(self.table)
        vertical_splitter.addWidget(bottom_container)
        
        # Set stretch factors - table gets more space initially
        vertical_splitter.setStretchFactor(0, 3)  # Table gets 3/4 of space
        vertical_splitter.setStretchFactor(1, 1)  # Bottom container gets 1/4 of space
        
        # Set initial sizes for better default layout
        vertical_splitter.setSizes([500, 200])  # 500px for table, 200px for bottom container
        
        # Prevent panels from collapsing completely
        vertical_splitter.setChildrenCollapsible(False)
        
        # Add the vertical splitter to the right panel
        right_panel.addWidget(vertical_splitter, 1)

        # Assemble two-column layout with resizable sidebar
        from PySide6.QtWidgets import QWidget as _QW
        left_container = _QW()
        left_container.setLayout(left_sidebar)
        left_container.setMinimumWidth(400)  # Increased minimum width to prevent text truncation
        # Allow sidebar to expand up to half the screen width (no maximum width constraint)
        left_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        right_container = _QW()
        right_container.setObjectName("PreviewArea")
        right_container.setLayout(right_panel)
        right_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Use a splitter for responsive horizontal resizing
        splitter = QSplitter(Qt.Horizontal)
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QScrollArea.NoFrame)
        left_scroll.setWidget(left_container)
        # Apply custom scrollbars
        left_scroll.setVerticalScrollBar(CustomScrollBar(Qt.Vertical))
        left_scroll.setHorizontalScrollBar(CustomScrollBar(Qt.Horizontal))

        splitter.addWidget(left_scroll)
        splitter.addWidget(right_container)
        # Allow both panels to be resizable with equal stretch factors
        splitter.setStretchFactor(0, 1)  # Left sidebar can grow/shrink
        splitter.setStretchFactor(1, 1)  # Right panel can also grow/shrink equally
        # Set initial sizes for better default layout - sidebar takes about 1/3 of screen width
        splitter.setSizes([300, 700])  # 300px for sidebar (1/3), 700px for main content (2/3)
        # Allow the splitter to be resized to any proportion
        splitter.setChildrenCollapsible(False)  # Prevent panels from collapsing completely

        root.addWidget(splitter)
        self.setLayout(root)

        # Connect preview updates
        for widget in [
            self.prefix_input, self.suffix_input, self.base_input, self.start_input,
            self.ext_filter_input, self.size_value, self.date_value
        ]:
            widget.textChanged.connect(self.preview_callback)
        
        # Connect start number field to update visual styling
        self.start_input.textChanged.connect(self._update_start_number_styling)
        # Connect to maintain focus when text changes
        self.start_input.textChanged.connect(self._maintain_start_number_focus)
        # Connect focus events
        self.start_input.focusInEvent = self._start_input_focus_in
        self.start_input.focusOutEvent = self._start_input_focus_out
        # Track previous text for focus maintenance
        self._previous_start_text = self.start_input.text()
        # Update initial styling
        self._update_start_number_styling()

        self.size_operator.currentIndexChanged.connect(self.preview_callback)
        self.size_unit.currentIndexChanged.connect(self.preview_callback)
        self.date_operator.currentIndexChanged.connect(self.preview_callback)
        self.status_filter.currentIndexChanged.connect(self.preview_callback)
        self.extension_lock_checkbox.stateChanged.connect(self.preview_callback)
        
        # Connect auto-clean controls
        self.remove_special_chars_check.stateChanged.connect(self.preview_callback)
        self.replace_spaces_check.stateChanged.connect(self.preview_callback)
        self.convert_case_check.stateChanged.connect(self.preview_callback)
        self.remove_accents_check.stateChanged.connect(self.preview_callback)
        self.case_type_combo.currentIndexChanged.connect(self._on_case_type_changed)
        
        # Connect search functionality
        self.search_input.textChanged.connect(self.preview_callback)
        
        # Connect export functionality
        self.export_btn.clicked.connect(self.export_preview)
        
        # Helper: set localized empty overlay text
        self._empty_state = "no_files"
        def _set_empty_overlay_text_local():
            try:
                # Choose copy by empty state
                if getattr(self, "_empty_state", "no_files") == "no_matches":
                    text = self.tr_manager.tr("top_panel.preview.no_files_found")
                    if text == "top_panel.preview.no_files_found":
                        text = self.tr_manager.tr("ui.no_files_found")
                    # hide icon for no results
                    if hasattr(self, "_empty_icon"):
                        self._empty_icon.setVisible(False)
                else:
                    text = self.tr_manager.tr("top_panel.preview.empty_hint")
                    if text == "top_panel.preview.empty_hint":
                        text = self.tr_manager.tr("ui.empty_hint")
                    if hasattr(self, "_empty_icon"):
                        self._empty_icon.setText("📂")
                        self._empty_icon.setVisible(True)
                if hasattr(self, "_empty_text"):
                    self._empty_text.setText(text)
            except Exception:
                if hasattr(self, "_empty_text"):
                    self._empty_text.setText(self.tr_manager.tr("ui.empty_hint"))
        self._set_empty_overlay_text = _set_empty_overlay_text_local
        # Set initial text now that helper exists
        self._set_empty_overlay_text()

    def set_empty_state(self, state: str):
        """Set the empty overlay state.
        Allowed: 'no_files' (drag-drop), 'no_matches' (not found), 'hidden' (suppress overlay).
        """
        state = state if state in ("no_files", "no_matches", "hidden") else "no_files"
        if getattr(self, "_empty_state", None) != state:
            self._empty_state = state
            try:
                self._set_empty_overlay_text()
            except Exception:
                pass

    # Public: enable/disable tooltips globally for this panel
    def apply_tooltips(self, enabled: bool):
        self._tooltips_enabled = bool(enabled)
        try:
            if self._tooltips_enabled:
                self.prefix_input.setToolTip(self.tr_manager.tr("ui.tooltip_prefix"))
                self.suffix_input.setToolTip(self.tr_manager.tr("ui.tooltip_suffix"))
                self.base_input.setToolTip(self.tr_manager.tr("ui.tooltip_base_name"))
                self.start_input.setToolTip(self.tr_manager.tr("ui.tooltip_start_number"))
                self.extension_lock_checkbox.setToolTip(self.tr_manager.tr("ui.extension_lock_tooltip"))
            else:
                self.prefix_input.setToolTip("")
                self.suffix_input.setToolTip("")
                self.base_input.setToolTip("")
                self.start_input.setToolTip("")
                self.extension_lock_checkbox.setToolTip("")
        except Exception:
            pass
    
    def _create_status_badge(self, status_text):
        """Create a minimal colored badge for Status: simple and effective."""
        badge = QLabel(status_text)
        badge.setAlignment(Qt.AlignCenter)
        badge.setProperty("status_text", status_text)
        
        # Map both English and German status values to colors
        color_map = {
            # English status values
            "Ready": ("#16A34A", "#FFFFFF"),            # green
            "Conflict": ("#DC2626", "#FFFFFF"),         # red
            "No Change": ("#D97706", "#111827"),        # amber
            "Extension Locked": ("#F59E0B", "#111827"), # orange
            # German status values
            "Bereit": ("#16A34A", "#FFFFFF"),           # green
            "Konflikt": ("#DC2626", "#FFFFFF"),         # red
            "Keine Änderung": ("#D97706", "#111827"),   # amber
            "Erweiterung gesperrt": ("#F59E0B", "#111827") # orange
        }
        bg, fg = color_map.get(status_text, ("#E5E7EB", "#111827"))
        badge.setStyleSheet(
            f"QLabel {{ background: {bg}; color: {fg}; border-radius: 6px; padding: 2px 6px; font-weight: 500; }}"
        )
        return badge
    
    def update_language(self):
        """Update all text with current language."""
        # Temporarily disconnect signals to prevent preview updates during language change
        self._disconnect_preview_signals()
        
        # Update buttons
        self.btn_browse_folder.setText(self.tr_manager.tr("main.browse_folder"))
        self.btn_browse_files.setText(self.tr_manager.tr("main.select_files"))
        self.btn_clear.setText(self.tr_manager.tr("main.clear_all"))
        
        # Update action buttons
        self.undo_selected_button.setText(self.tr_manager.tr("ui.undo_selected"))
        self.validate_button.setText(self.tr_manager.tr("ui.validate_simulate"))
        self.remove_selected_btn.setText(self.tr_manager.tr("ui.remove_selected"))
        # Update tooltips if enabled
        try:
            if getattr(self, "_tooltips_enabled", True):
                self.prefix_input.setToolTip(self.tr_manager.tr("ui.tooltip_prefix"))
                self.suffix_input.setToolTip(self.tr_manager.tr("ui.tooltip_suffix"))
                self.base_input.setToolTip(self.tr_manager.tr("ui.tooltip_base_name"))
                self.start_input.setToolTip(self.tr_manager.tr("ui.tooltip_start_number"))
                self.extension_lock_checkbox.setToolTip(self.tr_manager.tr("ui.extension_lock_tooltip"))
        except Exception:
            pass
        # Update group titles
        try:
            self.naming_group.setTitle(self.tr_manager.tr("top_panel.naming.title"))
            # Auto-clean subgroup title
            if hasattr(self, "auto_group"):
                self.auto_group.setTitle(self.tr_manager.tr("top_panel.auto_clean.title"))
            self.files_group.setTitle(self.tr_manager.tr("top_panel.files.title"))
            self.filters_group.setTitle(self.tr_manager.tr("top_panel.filters.title"))
            self.profiles_group.setTitle(self.tr_manager.tr("top_panel.profiles.title"))
        except Exception:
            pass
        
        # Update profile buttons
        self.btn_save_profile.setText(self.tr_manager.tr("top_panel.profiles.save"))
        self.btn_load_profile.setText(self.tr_manager.tr("top_panel.profiles.load"))
        self.btn_delete_profile.setText(self.tr_manager.tr("top_panel.profiles.delete"))
        
        # Update placeholders
        self.profile_combo.setPlaceholderText(self.tr_manager.tr("top_panel.profiles.select_profile_placeholder"))
        self.ext_filter_input.setPlaceholderText(self.tr_manager.tr("top_panel.filters.extension_placeholder"))
        self.size_value.setPlaceholderText(self.tr_manager.tr("top_panel.filters.size_placeholder"))
        
        # Update extension lock checkbox
        if self.extension_lock_checkbox.isChecked():
            self.extension_lock_checkbox.setText("🔒 " + self.tr_manager.tr("top_panel.naming.extension_lock_active"))
        else:
            self.extension_lock_checkbox.setText("🔓 " + self.tr_manager.tr("top_panel.naming.extension_lock_disabled"))
        
        # Update auto-clean controls
        self.remove_special_chars_check.setText(self.tr_manager.tr("top_panel.auto_clean.remove_special_chars"))
        self.replace_spaces_check.setText(self.tr_manager.tr("top_panel.auto_clean.replace_spaces"))
        self.convert_case_check.setText(self.tr_manager.tr("top_panel.auto_clean.convert_case"))
        self.remove_accents_check.setText(self.tr_manager.tr("top_panel.auto_clean.remove_accents"))
        
        # Update case type combo
        prev_case = self.case_type_combo.currentText() if hasattr(self, "case_type_combo") else ""
        self.case_type_combo.clear()
        items = [
            self.tr_manager.tr("top_panel.auto_clean.case_types.lowercase"),
            self.tr_manager.tr("top_panel.auto_clean.case_types.titlecase"),
            self.tr_manager.tr("top_panel.auto_clean.case_types.uppercase")
        ]
        self.case_type_combo.addItems(items)
        # Restore previous selection if possible; otherwise default to Titlecase
        try:
            restore_txt = prev_case if prev_case in items else self.tr_manager.tr("top_panel.auto_clean.case_types.titlecase")
            idx = self.case_type_combo.findText(restore_txt)
            if idx >= 0:
                self.case_type_combo.setCurrentIndex(idx)
        except Exception:
            pass
        
        # Update table headers
        self.table.setHorizontalHeaderLabels([
            self.tr_manager.tr("top_panel.preview.old_name"),
            self.tr_manager.tr("top_panel.preview.new_name"),
            self.tr_manager.tr("top_panel.preview.status")
        ])
        
        # Update search bar
        self.search_input.setPlaceholderText(self.tr_manager.tr("top_panel.preview.search_placeholder"))
        
        # Update export button
        self.export_btn.setText(self.tr_manager.tr("top_panel.preview.export_preview"))
        
        # Update empty-state text if overlay exists
        try:
            self._set_empty_overlay_text()
        except Exception:
            pass
        
        # Update filter options
        self.size_operator.clear()
        self.size_operator.addItems([
            self.tr_manager.tr("ui.size_operators.greater_than"),
            self.tr_manager.tr("ui.size_operators.less_than"),
            self.tr_manager.tr("ui.size_operators.equal")
        ])
        
        self.size_unit.clear()
        self.size_unit.addItems(["B", "KB", "MB", "GB"])
        
        self.date_operator.clear()
        self.date_operator.addItems([
            self.tr_manager.tr("top_panel.filters.date_operators.before"),
            self.tr_manager.tr("top_panel.filters.date_operators.after")
        ])
        
        self.status_filter.clear()
        self.status_filter.addItems([
            self.tr_manager.tr("top_panel.filters.status_options.all"),
            self.tr_manager.tr("ui.status_options.ready"),
            self.tr_manager.tr("ui.status_options.conflict"),
            self.tr_manager.tr("ui.status_options.no_change"),
            self.tr_manager.tr("ui.status_options.extension_locked")
        ])
        
        # Reconnect signals after language update is complete
        self._reconnect_preview_signals()

    def _disconnect_preview_signals(self):
        """Temporarily disconnect only our preview-callback bindings.
        Avoid removing internal handlers (e.g., DateInput auto-format).
        """
        # Disconnect combo box signals (preview only)
        try: self.size_operator.currentIndexChanged.disconnect(self.preview_callback)
        except Exception: pass
        try: self.size_unit.currentIndexChanged.disconnect(self.preview_callback)
        except Exception: pass
        try: self.date_operator.currentIndexChanged.disconnect(self.preview_callback)
        except Exception: pass
        try: self.status_filter.currentIndexChanged.disconnect(self.preview_callback)
        except Exception: pass
        try: self.case_type_combo.currentIndexChanged.disconnect(self._on_case_type_changed)
        except Exception: pass

        # Disconnect checkbox signals (preview only)
        try: self.extension_lock_checkbox.stateChanged.disconnect(self.preview_callback)
        except Exception: pass
        try: self.remove_special_chars_check.stateChanged.disconnect(self.preview_callback)
        except Exception: pass
        try: self.replace_spaces_check.stateChanged.disconnect(self.preview_callback)
        except Exception: pass
        try: self.convert_case_check.stateChanged.disconnect(self.preview_callback)
        except Exception: pass
        try: self.remove_accents_check.stateChanged.disconnect(self.preview_callback)
        except Exception: pass

        # Disconnect text input signals (preview only) — don't nuke internal handlers
        try: self.prefix_input.textChanged.disconnect(self.preview_callback)
        except Exception: pass
        try: self.suffix_input.textChanged.disconnect(self.preview_callback)
        except Exception: pass
        try: self.base_input.textChanged.disconnect(self.preview_callback)
        except Exception: pass
        try: self.start_input.textChanged.disconnect(self.preview_callback)
        except Exception: pass
        try: self.ext_filter_input.textChanged.disconnect(self.preview_callback)
        except Exception: pass
        try: self.size_value.textChanged.disconnect(self.preview_callback)
        except Exception: pass
        try: self.date_value.textChanged.disconnect(self.preview_callback)
        except Exception: pass
        try: self.search_input.textChanged.disconnect(self.preview_callback)
        except Exception: pass
    
    def _reconnect_preview_signals(self):
        """Reconnect signals that trigger preview updates."""
        # Reconnect combo box signals
        self.size_operator.currentIndexChanged.connect(self.preview_callback)
        self.size_unit.currentIndexChanged.connect(self.preview_callback)
        self.date_operator.currentIndexChanged.connect(self.preview_callback)
        self.status_filter.currentIndexChanged.connect(self.preview_callback)
        self.case_type_combo.currentIndexChanged.connect(self._on_case_type_changed)
        
        # Reconnect checkbox signals
        self.extension_lock_checkbox.stateChanged.connect(self.preview_callback)
        self.remove_special_chars_check.stateChanged.connect(self.preview_callback)
        self.replace_spaces_check.stateChanged.connect(self.preview_callback)
        self.convert_case_check.stateChanged.connect(self.preview_callback)
        self.remove_accents_check.stateChanged.connect(self.preview_callback)
        
        # Reconnect text input signals
        for widget in [
            self.prefix_input, self.suffix_input, self.base_input, self.start_input,
            self.ext_filter_input, self.size_value, self.date_value
        ]:
            widget.textChanged.connect(self.preview_callback)
        
        # Reconnect search input
        self.search_input.textChanged.connect(self.preview_callback)
        
        # Reconnect start number specific signals
        self.start_input.textChanged.connect(self._update_start_number_styling)
        self.start_input.textChanged.connect(self._maintain_start_number_focus)

    def update_preview(self, preview_list):
        # Apply search filter
        search_term = self.search_input.text().strip().lower()
        if search_term:
            filtered_preview_list = []
            for item in preview_list:
                old_name, new_name, status, _ = item
                if (search_term in old_name.lower() or 
                    search_term in new_name.lower() or 
                    self._matches_status(search_term, status)):
                    filtered_preview_list.append(item)
            preview_list = filtered_preview_list
        
        # Sort the preview data
        sorted_preview_list = self.sort_preview_data(preview_list)
        
        # Store full list and reset rendered rows for lazy loading
        self._full_preview_data = sorted_preview_list
        self._rendered_rows = 0
        self.table.setRowCount(0)
        # Toggle empty-state overlay visibility for both no files and filters yielding no rows
        try:
            if hasattr(self.table, "_empty_overlay") and self.table._empty_overlay is not None:
                if hasattr(self.table, "_reposition_overlay") and callable(self.table._reposition_overlay):
                    self.table._reposition_overlay()
                # Show overlay only when state is not 'hidden'
                show = getattr(self, "_empty_state", "no_files") != "hidden" and len(self._full_preview_data) == 0
                self.table._empty_overlay.setVisible(show)
        except Exception:
            pass
        # Render first batch
        self._append_rows()

    def _matches_status(self, search_term: str, status: str) -> bool:
        """Check if search term matches status in any language."""
        # Define status mappings for both languages
        status_mappings = {
            # English status values
            "renamed": ["renamed", "umbenannt"],
            "unchanged": ["unchanged", "unverändert"], 
            "error": ["error", "fehler"],
            "duplicate": ["duplicate", "duplikat"],
            "invalid": ["invalid", "ungültig"],
            "ready": ["ready", "bereit"],
            "no change": ["no change", "keine änderung"],
            "conflict": ["conflict", "konflikt"],
            "extension locked": ["extension locked", "erweiterung gesperrt"],
            # German status values
            "umbenannt": ["renamed", "umbenannt"],
            "unverändert": ["unchanged", "unverändert"],
            "fehler": ["error", "fehler"],
            "duplikat": ["duplicate", "duplikat"],
            "ungültig": ["invalid", "ungültig"],
            "bereit": ["ready", "bereit"],
            "keine änderung": ["no change", "keine änderung"],
            "konflikt": ["conflict", "konflikt"],
            "erweiterung gesperrt": ["extension locked", "erweiterung gesperrt"]
        }
        
        # Check if search term matches any of the status values
        status_lower = status.lower()
        for key, values in status_mappings.items():
            if search_term in key and status_lower in values:
                return True
            if search_term in status_lower:
                return True
        
        return False

    def _translate_status(self, status: str) -> str:
        """Translate status value to current language."""
        from app.utils.translation_manager import get_translation_manager
        tr_manager = get_translation_manager()
        
        # Map English status values to translation keys
        status_map = {
            "Ready": "status.ready",
            "Conflict": "status.conflict", 
            "No Change": "status.no_change",
            "Extension Locked": "status.extension_locked",
            "Error": "status.error",
            "Duplicate": "status.duplicate",
            "Invalid": "status.invalid"
        }
        
        # Return translated status or original if no translation found
        return tr_manager.tr(status_map.get(status, status))

    def _append_rows(self):
        if not self._full_preview_data:
            return
        start = self._rendered_rows
        end = min(len(self._full_preview_data), start + self._batch_size)
        if start >= end:
            self.table.show_loading(False)
            return
        self.table.show_loading(True)
        self.table.setRowCount(end)
        extension_locked = self.extension_lock_checkbox.isChecked()
        for row in range(start, end):
            old_name, new_name, status, _ = self._full_preview_data[row]
            old_item = QTableWidgetItem(old_name)
            new_item = QTableWidgetItem(new_name)
            old_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            new_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            # Parse status and optional auto-resolved suggestion
            suggestion = None
            status_text = status
            if isinstance(status, str) and "|" in status:
                parts = status.split("|", 1)
                status_text = parts[0]
                suggestion = parts[1]
            
            # Translate status text
            status_text = self._translate_status(status_text)
            # Keep the status as widget-only to avoid duplicate text rendering
            status_item = QTableWidgetItem("")
            # Attach original file path to the first column for removal
            try:
                old_item.setData(Qt.UserRole, _)
            except Exception:
                pass

            old_item.setFlags(old_item.flags() & ~Qt.ItemIsEditable)
            new_item.setFlags(new_item.flags() & ~Qt.ItemIsEditable)
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)

            # Apply colors based on original status (before translation)
            if status == "Ready":
                new_item.setForeground(QBrush(QColor(0, 128, 0)))
                if extension_locked:
                    new_item.setToolTip("🔒 Extension preserved automatically")
            elif status == "Conflict":
                new_item.setForeground(QBrush(QColor(200, 0, 0)))
            elif status == "No Change":
                new_item.setForeground(QBrush(QColor(180, 150, 0)))
            elif status == "Extension Locked":
                new_item.setForeground(QBrush(QColor(255, 140, 0)))
                new_item.setToolTip("🔒 Extension lock is enabled - extension changes are not allowed")

            self.table.setItem(row, 0, old_item)
            self.table.setItem(row, 1, new_item)
            # Status column (now at index 2)
            # Ensure the textual item is empty, and use a widget for the visual badge
            self.table.setItem(row, 2, status_item)
            # Put the badge inside a container; only the badge text should appear
            try:
                from PySide6.QtWidgets import QWidget, QHBoxLayout
                wrap = QWidget()
                wrap.setStyleSheet("background: transparent;")
                hl = QHBoxLayout(wrap)
                hl.setContentsMargins(0, 0, 0, 0)
                hl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                badge = self._create_status_badge(status_text)
                # Size badge to fit text (with padding) so it doesn't cut off (e.g., "No Change")
                try:
                    fm = badge.fontMetrics()
                    text_w = fm.horizontalAdvance(status_text) + 18  # padding from stylesheet
                    max_w = max(80, self.table.columnWidth(2) - 12)
                    badge.setFixedWidth(min(max_w, text_w))
                except Exception:
                    pass
                hl.addWidget(badge)
                # expose status text on the wrapper so export logic can read it
                wrap.setProperty("status_text", status_text)
                self.table.setCellWidget(row, 2, wrap)
            except Exception:
                w = self._create_status_badge(status_text)
                w.setProperty("status_text", status_text)
                self.table.setCellWidget(row, 2, w)
            # If suggestion exists, show crossed original new name; suggestion text is only in Suggestion column
            if suggestion and status_text == "Conflict":
                try:
                    from PySide6.QtWidgets import QWidget, QHBoxLayout
                    cont = QWidget()
                    hl = QHBoxLayout(cont)
                    hl.setContentsMargins(0, 0, 0, 0)
                    hl.setSpacing(8)
                    lbl_old = QLabel(new_name)
                    lbl_old.setStyleSheet("QLabel { color: #DC2626; text-decoration: line-through; }")
                    hl.addWidget(lbl_old)
                    # Accept/Decline buttons
                    from PySide6.QtWidgets import QPushButton
                    from functools import partial
                    accept_btn = QPushButton("✓")
                    accept_btn.setObjectName("SecondaryButton")
                    decline_btn = QPushButton("✕")
                    decline_btn.setObjectName("SecondaryButton")
                    try:
                        accept_btn.setFixedWidth(28)
                        decline_btn.setFixedWidth(28)
                        accept_btn.setStyleSheet("QPushButton { padding: 0 4px; }")
                        decline_btn.setStyleSheet("QPushButton { padding: 0 4px; }")
                    except Exception:
                        pass
                    accept_btn.clicked.connect(partial(self._accept_suggestion, row, suggestion))
                    decline_btn.clicked.connect(partial(self._decline_suggestion, row, new_name))
                    btn_wrap = QWidget()
                    btn_wrap.setMinimumWidth(140)
                    bl = QHBoxLayout(btn_wrap)
                    bl.setContentsMargins(0, 0, 0, 0)
                    bl.setSpacing(6)
                    bl.addWidget(accept_btn)
                    bl.addWidget(decline_btn)
                    hl.addWidget(btn_wrap)
                    self.table.setCellWidget(row, 1, cont)
                except Exception:
                    pass
        self._rendered_rows = end
        self.table.show_loading(False)

    def _maybe_load_more_rows(self):
        sb = self.table.verticalScrollBar()
        if sb.maximum() <= 0:
            return
        if sb.value() > sb.maximum() * 0.8:
            self._append_rows()

    def _accept_suggestion(self, row_idx: int, suggestion: str):
        try:
            self.table.setCellWidget(row_idx, 1, None)
            item = self.table.item(row_idx, 1)
            if item is None:
                item = QTableWidgetItem(suggestion)
                self.table.setItem(row_idx, 1, item)
            else:
                item.setText(suggestion)
            item.setForeground(QBrush(QColor(0, 128, 0)))
            self.table.setCellWidget(row_idx, 2, None)
            self.table.setItem(row_idx, 2, QTableWidgetItem(""))
            self.table.setCellWidget(row_idx, 3, self._create_status_badge("Ready"))
            self.table.setItem(row_idx, 3, QTableWidgetItem("Ready"))
        except Exception:
            pass

    def _decline_suggestion(self, row_idx: int, original_new_name: str):
        try:
            self.table.setCellWidget(row_idx, 1, None)
            item = self.table.item(row_idx, 1)
            if item is None:
                item = QTableWidgetItem(original_new_name)
                self.table.setItem(row_idx, 1, item)
            item.setText(original_new_name)
            item.setForeground(QBrush(QColor(200, 0, 0)))
            self.table.setCellWidget(row_idx, 2, None)
            self.table.setItem(row_idx, 2, QTableWidgetItem(""))
            # keep status as-is
        except Exception:
            pass

    def _on_table_selection_changed(self):
        sel = self.table.selectionModel()
        count = len(sel.selectedRows()) if sel else 0
        self.remove_selected_btn.setVisible(count > 0)
        if count > 0:
            self.remove_selected_btn.setText(f"{self.tr_manager.tr('ui.remove_selected')} ({count})")

    def _on_remove_selected_clicked(self):
        sel = self.table.selectionModel()
        if not sel:
            return
        rows = sorted({idx.row() for idx in sel.selectedRows()})
        file_paths = []
        for r in rows:
            item = self.table.item(r, 0)
            if item is not None:
                fp = item.data(Qt.UserRole)
                if fp:
                    file_paths.append(fp)
        if file_paths:
            self.remove_selected.emit(file_paths)
        self.table.clearSelection()
        self.remove_selected_btn.setVisible(False)
    
    
    def _on_header_clicked(self, column):
        """Handle header click for sorting."""
        if column == self.sort_column:
            # Same column clicked - cycle through: asc -> desc -> no sort
            if self.sort_ascending:
                self.sort_ascending = False  # Switch to descending
            else:
                self.sort_column = -1  # No sorting
                self.sort_ascending = True
        else:
            # Different column clicked - start with ascending
            self.sort_column = column
            self.sort_ascending = True
        
        # Update header labels with sort indicators
        self._update_header_labels()
        
        # Trigger preview update
        self.preview_callback()

    def _on_case_type_changed(self):
        """Auto-enable convert-case when user picks a case type."""
        try:
            if not self.convert_case_check.isChecked():
                self.convert_case_check.setChecked(True)
        except Exception:
            pass
        self.preview_callback()
    
    def _on_date_validation_changed(self, is_valid, message):
        """Handle date validation changes and show notifications."""
        try:
            # Get the notification manager from the main app
            # This is a bit of a hack, but we need access to the notification system
            main_window = self.window()
            if hasattr(main_window, 'notification_manager'):
                if not is_valid and message:
                    main_window.notification_manager.show_notification(message, "error")
                # Note: We don't show a success notification for valid dates as requested
        except Exception:
            pass
    
    def _update_header_labels(self):
        """Update header labels with sort indicators."""
        headers = ["Old Name", "New Name", "Status"]
        
        for i, header in enumerate(headers):
            if i == self.sort_column:
                if self.sort_ascending:
                    headers[i] = f"{header} ↑"
                else:
                    headers[i] = f"{header} ↓"
        
        self.table.setHorizontalHeaderLabels(headers)
    
    def _update_start_number_styling(self):
        """Update the visual styling of the start number field based on its content."""
        text = self.start_input.text().strip()
        
        # More robust validation - check if text is a valid positive integer
        is_valid = False
        if text:
            try:
                # Try to convert to int and check if it's positive
                num = int(text)
                is_valid = num > 0
            except ValueError:
                is_valid = False
        
        if is_valid:
            # Field is filled with a valid number - use theme styling with specific selector
            self.start_input.setStyleSheet("QLineEdit#startNumberField { border: 1px solid #D5D5D5; }")
        else:
            # Field is empty or invalid - red border to indicate required
            self.start_input.setStyleSheet("QLineEdit#startNumberField { border: 2px solid #ff6b6b !important; }")
    
    def _maintain_start_number_focus(self):
        """Maintain focus on start number field when text changes."""
        current_text = self.start_input.text()
        previous_text = self._previous_start_text
        
        # Only maintain focus if:
        # 1. The field currently has focus (tracked by our custom focus events)
        # 2. The text became empty (user deleted content)
        # 3. The text was not empty before
        has_focus = self._start_input_has_focus
        if has_focus and not current_text and previous_text:
            # Use a longer delay to ensure it's after all other events
            from PySide6.QtCore import QTimer
            QTimer.singleShot(10, lambda: self.start_input.setFocus())
        
        # Update previous text for next comparison
        self._previous_start_text = current_text
    
    def _start_input_focus_in(self, event):
        """Handle focus in event for start number field."""
        self._start_input_has_focus = True
        # Call the original focusInEvent
        from PySide6.QtWidgets import QLineEdit
        QLineEdit.focusInEvent(self.start_input, event)
    
    def _start_input_focus_out(self, event):
        """Handle focus out event for start number field."""
        self._start_input_has_focus = False
        # Call the original focusOutEvent
        from PySide6.QtWidgets import QLineEdit
        QLineEdit.focusOutEvent(self.start_input, event)
    
    def sort_preview_data(self, preview_list):
        """Sort preview data based on the current sort column and direction."""
        if self.sort_column == -1:
            return preview_list  # No sorting
        
        # Determine sort key based on column
        if self.sort_column == 0:  # Old Name
            key_func = lambda x: x[0].lower()
        elif self.sort_column == 1:  # New Name
            key_func = lambda x: x[1].lower()
        elif self.sort_column == 2:  # Status
            key_func = lambda x: x[2].lower()
        else:
            return preview_list
        
        # Sort with appropriate direction
        return sorted(preview_list, key=key_func, reverse=not self.sort_ascending)
    
    def _on_save_profile(self):
        """Handle save profile button click."""
        if self.save_profile_cb:
            self.save_profile_cb()
    
    def _on_load_profile(self):
        """Handle load profile button click."""
        if self.load_profile_cb:
            selected_profile = self.profile_combo.currentText()
            if selected_profile:
                self.load_profile_cb(selected_profile)
    
    def _on_delete_profile(self):
        """Handle delete profile button click."""
        if self.delete_profile_cb:
            selected_profile = self.profile_combo.currentText()
            if selected_profile:
                self.delete_profile_cb(selected_profile)
    
    def refresh_profiles_list(self, profiles):
        """Refresh the profiles dropdown list."""
        self.profile_combo.clear()
        for profile in profiles:
            self.profile_combo.addItem(profile)
    
    def get_current_settings(self):
        """Get current settings for saving as profile."""
        return {
            "prefix": self.prefix_input.text(),
            "suffix": self.suffix_input.text(),
            "base_name": self.base_input.text(),
            "start_num": self.start_input.text(),
            "extension_lock": self.extension_lock_checkbox.isChecked(),
            "extensions": self.ext_filter_input.text(),
            "size_operator": self.size_operator.currentText(),
            "size_value": self.size_value.text(),
            "size_unit": self.size_unit.currentText(),
            "date_operator": self.date_operator.currentText(),
            "date_value": self.date_value.get_date_value(),
            "status_filter": self.status_filter.currentText(),
            "sort_column": self.sort_column,
            "sort_ascending": self.sort_ascending,
            "remove_special_chars": self.remove_special_chars_check.isChecked(),
            "replace_spaces": self.replace_spaces_check.isChecked(),
            "convert_case": self.convert_case_check.isChecked(),
            "case_type": self.case_type_combo.currentText(),
            "remove_accents": self.remove_accents_check.isChecked(),
            "search_term": self.search_input.text()
        }
    
    def apply_settings(self, settings):
        """Apply settings from a loaded profile."""
        self.prefix_input.setText(settings.get("prefix", ""))
        self.suffix_input.setText(settings.get("suffix", ""))
        self.base_input.setText(settings.get("base_name", ""))
        self.start_input.setText(settings.get("start_num", ""))
        # Update styling after setting text
        self._update_start_number_styling()
        self.extension_lock_checkbox.setChecked(settings.get("extension_lock", True))
        self.ext_filter_input.setText(settings.get("extensions", ""))
        
        # Set size filter
        size_op = settings.get("size_operator", "")
        if size_op:
            index = self.size_operator.findText(size_op)
            if index >= 0:
                self.size_operator.setCurrentIndex(index)
        self.size_value.setText(settings.get("size_value", ""))
        size_unit = settings.get("size_unit", "")
        if size_unit:
            index = self.size_unit.findText(size_unit)
            if index >= 0:
                self.size_unit.setCurrentIndex(index)
        
        # Set date filter
        date_op = settings.get("date_operator", "")
        if date_op:
            index = self.date_operator.findText(date_op)
            if index >= 0:
                self.date_operator.setCurrentIndex(index)
        self.date_value.setText(settings.get("date_value", ""))
        
        # Set status filter
        status_filter = settings.get("status_filter", "All")
        index = self.status_filter.findText(status_filter)
        if index >= 0:
            self.status_filter.setCurrentIndex(index)
        
        # Set sort settings
        self.sort_column = settings.get("sort_column", -1)
        self.sort_ascending = settings.get("sort_ascending", True)
        self._update_header_labels()
        
        # Set auto-clean settings
        self.remove_special_chars_check.setChecked(settings.get("remove_special_chars", False))
        self.replace_spaces_check.setChecked(settings.get("replace_spaces", False))
        self.convert_case_check.setChecked(settings.get("convert_case", False))
        self.remove_accents_check.setChecked(settings.get("remove_accents", False))
        
        # Set case type
        case_type = settings.get("case_type", "")
        if case_type:
            index = self.case_type_combo.findText(case_type)
            if index >= 0:
                self.case_type_combo.setCurrentIndex(index)
        
        # Set search term
        self.search_input.setText(settings.get("search_term", ""))
        
        # Enable/disable case type combo based on convert_case setting
        self.case_type_combo.setEnabled(self.convert_case_check.isChecked())
    
    
    def clear_search(self):
        """Clear the search input."""
        self.search_input.clear()
    
    
    def export_preview(self):
        """Export the current preview data to a file."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QFileDialog, QMessageBox
        import csv
        import json
        import os
        from datetime import datetime
        
        # Get current preview data
        preview_data = self.get_current_preview_data()
        if not preview_data:
            QMessageBox.information(self, "No Data", "No preview data to export.")
            return
        
        # Create export dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr_manager.tr("top_panel.preview.export_dialog_title"))
        dialog.setModal(True)
        dialog.resize(400, 150)
        
        layout = QVBoxLayout()
        
        # Format selection
        format_layout = QHBoxLayout()
        format_label = QLabel(self.tr_manager.tr("top_panel.preview.export_format"))
        self.format_combo = CustomComboBox()
        
        # Add format options (CSV and JSON only)
        self.format_combo.addItems([
            self.tr_manager.tr("top_panel.preview.export_formats.csv"),
            self.tr_manager.tr("top_panel.preview.export_formats.json")
        ])
        
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        export_btn = QPushButton("Export")
        cancel_btn = QPushButton("Cancel")
        
        export_btn.clicked.connect(lambda: self._perform_export(dialog, preview_data))
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(export_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def get_current_preview_data(self):
        """Get the current preview data from the table."""
        preview_data = []
        for row in range(self.table.rowCount()):
            old_name = self.table.item(row, 0).text() if self.table.item(row, 0) else ""
            new_name = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
            # Prefer badge's status_text property if present
            status_widget = self.table.cellWidget(row, 2)
            if status_widget is not None and status_widget.property("status_text"):
                status = status_widget.property("status_text")
            else:
                status = self.table.item(row, 2).text() if self.table.item(row, 2) else ""
            preview_data.append({
                "old_name": old_name,
                "new_name": new_name,
                "status": status
            })
        return preview_data
    
    def _perform_export(self, dialog, preview_data):
        """Perform the actual export operation."""
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        import csv
        import json
        import os
        from datetime import datetime
        
        # Get selected format
        format_text = self.format_combo.currentText()
        if "CSV" in format_text:
            file_format = "csv"
            file_extension = "csv"
        elif "JSON" in format_text:
            file_format = "json"
            file_extension = "json"
        else:
            file_format = "csv"
            file_extension = "csv"
        
        # Get save location
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"bulk_renamer_preview_{timestamp}.{file_extension}"
        
        file_path, _ = QFileDialog.getSaveFileName(
            dialog,
            f"Save {file_format.upper()} File",
            default_filename,
            f"{file_format.upper()} Files (*.{file_extension})"
        )
        
        if not file_path:
            return
        
        try:
            if file_format == "csv":
                self._export_csv(file_path, preview_data)
            elif file_format == "json":
                self._export_json(file_path, preview_data)
            
            dialog.accept()
            QMessageBox.information(
                self,
                "Export Successful",
                self.tr_manager.tr("top_panel.preview.export_success", file=file_path)
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                self.tr_manager.tr("top_panel.preview.export_failed", error=str(e))
            )
    
    def _export_csv(self, file_path, preview_data):
        """Export data to CSV format."""
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['old_name', 'new_name', 'status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in preview_data:
                writer.writerow(row)
    
    def _export_json(self, file_path, preview_data):
        """Export data to JSON format."""
        import json
        from datetime import datetime
        
        export_data = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "total_files": len(preview_data),
                "exported_by": "Bulk File Renamer"
            },
            "preview_data": preview_data
        }
        
        with open(file_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
