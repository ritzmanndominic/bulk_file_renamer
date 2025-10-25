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
import json
from collections import deque
from datetime import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QProgressBar, QFileDialog, QMessageBox, QTabWidget, QMainWindow, QHBoxLayout, QLabel
from PySide6.QtGui import QColor, QIcon
from PySide6.QtCore import Qt, QTimer
from app.ui.top_panel import TopPanel
from app.ui.file_count_row import FileCountRow
from app.ui.history_panel import HistoryPanel
from app.ui.settings_tab import SettingsTab
from app.ui.menu_bar import MenuBar
from app.ui.custom_notification_bar import CustomNotificationManager
from app.utils.generate_preview import generate_preview
from app.utils.profile_manager import ProfileManager
from app.utils.settings_manager import SettingsManager
from app.utils.translation_manager import get_translation_manager, set_language
from app.ui.theme import apply_theme
from app.workers.file_operation_worker import FileOperationWorker
from app.workers.file_add_worker import FileAddWorker
import mimetypes
import shutil
from app import __version__

# MAX_PREVIEW_FILES will be loaded from settings

class BulkRenamerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("")
        # Increase minimum width to accommodate longer German text
        self.setMinimumSize(1000, 600)
        
        # Enable drag & drop for the entire application
        self.setAcceptDrops(True)
        
        # Set drag drop mode to ensure proper handling
        from PySide6.QtCore import Qt
        self.setAttribute(Qt.WA_AcceptDrops, True)
        
        # Note: UIPI fix removed since app no longer runs elevated

        self.selected_files = []
        self.filtered_files = []
        self.history = []
        self.profile_manager = ProfileManager()
        self.settings_manager = SettingsManager()
        self.notification_manager = CustomNotificationManager(self)
        
        # Initialize translation manager
        self.translation_manager = get_translation_manager()
        # Set language from settings (no default - must be set by installer)
        saved_language = self.settings_manager.get("language")
        if saved_language:
            set_language(saved_language)
        else:
            # Fallback to English if not set (shouldn't happen with proper installer)
            set_language("en")
        
        # Set initial window title
        self.update_window_title()
        # Set window/dock icon during runtime (dev and packaged)
        try:
            import sys, os
            base = os.path.dirname(os.path.dirname(__file__))
            candidates = [
                os.path.join(base, 'assets', 'app.png'),
                os.path.join(base, 'assets', 'app.ico'),
                os.path.join(base, 'assets', 'app.icns'),
                os.path.join(base, 'assets', 'app.svg'),
            ]
            for p in candidates:
                if os.path.exists(p):
                    self.setWindowIcon(QIcon(p))
                    break
        except Exception:
            pass

        self.rename_worker: FileOperationWorker | None = None
        self.undo_worker: FileOperationWorker | None = None

        self._file_add_queue = deque()
        self._file_add_worker: FileAddWorker | None = None
        self._is_initial_load = True  # Track if this is the initial app load
        self._is_clearing_files = False  # Track if we're clearing files to prevent notifications
        self._is_applying_settings = False  # Track if we're applying settings to prevent notifications
        # Prevent spamming info notifications while typing with no files
        self._notified_no_files_tip = False

        # Load history from previous session (delay to ensure UI is ready)
        QTimer.singleShot(100, self._load_history)

        # Setup menu bar
        self.setup_menu_bar()
        
        # Create central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ensure the main window is properly set up for notifications
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)
        
        layout = QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Main tab (existing functionality)
        class MainContentWidget(QWidget):
            def __init__(self):
                super().__init__()
                self.setObjectName("MainContentArea")
                self.setAcceptDrops(False)  # Don't accept drops - let them bubble up to main window
        
        main_tab = MainContentWidget()
        main_layout = QVBoxLayout()
        
        self.top_panel = TopPanel(
            browse_folder_cb=self.browse_folder,
            select_files_cb=self.select_files,
            clear_all_cb=self.clear_all_files,
            preview_callback=self.update_preview,
            save_profile_cb=self.save_profile,
            load_profile_cb=self.load_profile,
            delete_profile_cb=self.delete_profile,
            refresh_profiles_cb=self.refresh_profiles,
            rename_cb=self.rename_files,
            undo_cb=self.undo_last_rename,
            undo_selected_cb=self.undo_selected_history,
            validate_cb=self.validate_names
        )
        # Remove selected files from preview and internal selection
        def on_remove_selected(file_paths: list):
            if not file_paths:
                return
            # Remove from selected_files
            self.selected_files = [f for f in self.selected_files if f not in file_paths]
            # Update preview after removal
            self.update_preview()
        self.top_panel.remove_selected.connect(on_remove_selected)
        # Top panel now contains sidebar, preview, actions, and history
        main_layout.addWidget(self.top_panel, 1)

        # Progress bar remains in the main window
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        main_tab.setLayout(main_layout)
        self.tab_widget.addTab(main_tab, self.translation_manager.tr("main.rename_files"))
        
        # Settings tab
        self.settings_tab = SettingsTab(self.settings_manager)
        self.settings_tab.settings_changed.connect(self.on_settings_changed)
        self.settings_tab.settings_error.connect(self.on_settings_error)
        self.settings_tab.language_changed.connect(self.on_language_changed)
        self.tab_widget.addTab(self.settings_tab, self.translation_manager.tr("settings.tabs.settings"))
        
        layout.addWidget(self.tab_widget)
        central_widget.setLayout(layout)
        
        # Initialize profiles list
        self.refresh_profiles()
        
        # Apply initial settings
        self.apply_settings()
        # Apply theme based on settings (no default - must be set by installer)
        app_theme = self.settings_manager.get("theme")
        if app_theme:
            apply_theme(self, app_theme)
        else:
            # Fallback to Light if not set (shouldn't happen with proper installer)
            apply_theme(self, "Light")
        
        # Test notification system (remove this after testing)
        # self.test_notifications()

        # Prepare language change overlay (hidden by default)
        self._lang_overlay = QLabel(self)
        self._lang_overlay.setObjectName("LanguageOverlay")
        self._lang_overlay.setAlignment(Qt.AlignCenter)
        self._lang_overlay.setStyleSheet(
            "#LanguageOverlay { background: rgba(0,0,0,0.5); color: white;"
            " font-size: 18px; border-radius: 8px; padding: 24px; }"
        )
        self._lang_overlay.hide()
        
        # Mark initial load as complete
        self._is_initial_load = False
        
        # Start in fullscreen mode for better usability on smaller displays
        self.showMaximized()

    # ---------------- File Selection ----------------
    def browse_folder(self, folder=None):
        if folder is None:
            folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.settings_manager.add_recent_folder(folder)
            self.update_recent_items()
            self.add_files([folder])
    
    def browse_folder_from_path(self, folder_path):
        """Browse for a folder from a given path (for recent folders)."""
        if folder_path and os.path.exists(folder_path):
            self.browse_folder(folder_path)

    def select_files(self, files=None):
        if files is None:
            files, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        if files:
            self.add_files(files)

    def clear_all_files(self):
        self.selected_files = []
        # Set flag to prevent notification when clearing files
        self._is_clearing_files = True
        self.update_preview()
        self._is_clearing_files = False

    # ---------------- Preview ----------------
    def update_preview(self):
        # Get full list; TopPanel handles lazy rendering in batches
        preview_list = self.get_preview_list()

        # Apply status filter (index-based to avoid translation mismatches)
        status_idx = self.top_panel.status_filter.currentIndex()
        if status_idx > 0:
            # Map fixed indices to internal status codes used by preview
            # 1: Ready, 2: Conflict, 3: No Change, 4: Extension Locked
            status_map = {
                1: "Ready",
                2: "Conflict",
                3: "No Change",
                4: "Extension Locked",
            }
            wanted = status_map.get(status_idx)
            if wanted:
                preview_list = [f for f in preview_list if f[2] == wanted]

        # Update empty overlay state before rendering
        try:
            if len(self.selected_files) == 0:
                # No files selected yet: only show drag & drop
                self.top_panel.set_empty_state("no_files")
            elif len(preview_list) == 0:
                # Files exist; show 'no_matches' only if a valid extension was typed
                ext_text = self.top_panel.ext_filter_input.text().strip().lower()
                tokens = [t.strip().lstrip('.') for t in ext_text.split(',') if t.strip()]
                # Build a basic known extension set (fallback if mimetypes has no map)
                known_exts = set([
                    'txt','csv','json','xml','yaml','yml','log','md','rtf',
                    'jpg','jpeg','png','gif','bmp','tiff','webp','heic',
                    'mp3','wav','flac','aac','ogg','m4a',
                    'mp4','mkv','avi','mov','wmv','webm',
                    'pdf','doc','docx','xls','xlsx','ppt','pptx',
                    'zip','rar','7z','gz','tar','bz2','xz',
                    'py','js','ts','html','css','c','cpp','java','go','rs'
                ])
                # Augment with extensions from mimetypes
                try:
                    for ext, _ in mimetypes.types_map.items():
                        if ext.startswith('.'):
                            known_exts.add(ext[1:])
                except Exception:
                    pass

                any_valid = any(tok in known_exts for tok in tokens)
                if any_valid:
                    self.top_panel.set_empty_state("no_matches")
                else:
                    # Not a recognized extension yet (user typing) – suppress overlay
                    self.top_panel.set_empty_state("hidden")
            else:
                # Rows visible – suppress overlay
                self.top_panel.set_empty_state("hidden")
        except Exception:
            pass

        self.top_panel.update_preview(preview_list)
        self._color_preview(preview_list)
        self.top_panel.file_count.update_count(len(self.selected_files), len(self.filtered_files))

    def _color_preview(self, preview_list):
        show_tooltips = bool(self.settings_manager.get("show_tooltips", True))
        for row, (_, new_name, status, _) in enumerate(preview_list):
            color = QColor("black")
            tooltip = ""
            if status == "Ready":
                color = QColor("green")
                tooltip = self.translation_manager.tr("ui.status_ready_tooltip") if show_tooltips else ""
            elif status == "Conflict":
                color = QColor("red")
                tooltip = self.translation_manager.tr("ui.status_conflict_tooltip") if show_tooltips else ""
            elif status == "No Change":
                color = QColor("red")
                tooltip = self.translation_manager.tr("ui.status_no_change_tooltip") if show_tooltips else ""
            elif status == "Extension Locked":
                color = QColor(255, 140, 0)  # Orange color
                tooltip = self.translation_manager.tr("ui.status_extension_locked_tooltip") if show_tooltips else ""

            item = self.top_panel.table.item(row, 1)
            if item:
                item.setForeground(color)
                # Apply or clear tooltip based on setting
                try:
                    item.setToolTip(tooltip if show_tooltips else "")
                except Exception:
                    pass

    def get_preview_list(self):
        prefix = self.top_panel.prefix_input.text().strip()
        suffix = self.top_panel.suffix_input.text().strip()
        base_name = self.top_panel.base_input.text().strip()
        start_text = self.top_panel.start_input.text().strip()
        try:
            start_num = int(start_text) if start_text.isdigit() else None
        except (ValueError, AttributeError):
            start_num = None
        extension_lock = self.top_panel.extension_lock_checkbox.isChecked()
        
        # Validation: Require start number when there are files to prevent conflicts
        if self.selected_files and start_num is None:
            # If there are files but no start number, show error
            self.notification_manager.show_notification(
                "Start number is required when renaming files to prevent conflicts", 
                "error"
            )
            return []
        
        # Validation: Require at least one optional naming field to be filled (when no files are selected)
        # Only show notification once until conditions change (avoid spam while typing filters)
        no_files_and_no_naming = (not self.selected_files and not any([prefix, suffix, base_name]))
        if no_files_and_no_naming and not self._is_initial_load and not self._is_clearing_files and not self._is_applying_settings:
            if not self._notified_no_files_tip:
                self.notification_manager.show_notification(
                    "Please add files and fill at least one naming field (prefix, suffix, or base name)",
                    "info"
                )
                self._notified_no_files_tip = True
            return []
        else:
            # Reset flag when condition no longer holds (files added or naming filled)
            self._notified_no_files_tip = False

        ext_text = self.top_panel.ext_filter_input.text().strip().lower()
        extensions = [e.strip().lstrip(".") for e in ext_text.split(",")] if ext_text else None

        size_filter = None
        # Map size operator by index to avoid translation dependence
        size_idx = self.top_panel.size_operator.currentIndex()
        idx_to_op = {0: ">", 1: "<", 2: "="}
        op = idx_to_op.get(size_idx)
        # Fallback: if index mapping not found, try symbol/text directly
        if not op:
            op_text = self.top_panel.size_operator.currentText()
            op_map = {
                # English
                "Greater Than": ">", "Less Than": "<", "Equal": "=",
                # German
                "Größer als": ">", "Kleiner als": "<", "Gleich": "=",
                # Symbols
                ">": ">", "<": "<", "=": "="
            }
            op = op_map.get(op_text)
        val_text = self.top_panel.size_value.text().strip()
        unit = self.top_panel.size_unit.currentText().strip().upper() or "B"
        if op and val_text:
            try:
                val = float(val_text)
                multiplier = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}.get(unit, 1)
                size_filter = (op, val * multiplier)
            except ValueError:
                size_filter = None

        date_filter = None
        # Map date operator by index to stable codes
        date_idx = self.top_panel.date_operator.currentIndex()
        idx_to_date = {0: "before", 1: "after"}
        date_op = idx_to_date.get(date_idx)
        date_text = self.top_panel.date_value.get_date_value()
        if date_op and date_text:
            try:
                # Parse date in YYYY-MM-DD format
                threshold_date = datetime.strptime(date_text, "%Y-%m-%d")
                date_filter = (date_op, threshold_date)
            except ValueError:
                date_filter = None

        # Process all files - lazy loading will handle performance
        files_to_process = self.selected_files
        
        try:
            preview_list, filtered_files = generate_preview(
                file_paths=files_to_process,
                prefix=prefix,
                suffix=suffix,
                base_name=base_name,
                start_num=start_num,
                extensions=extensions,
                size_filter=size_filter,
                date_filter=date_filter,
                extension_lock=extension_lock,
                remove_special_chars=self.top_panel.remove_special_chars_check.isChecked(),
                replace_spaces=self.top_panel.replace_spaces_check.isChecked(),
                convert_case=self.top_panel.convert_case_check.isChecked(),
                # Map case type by index to internal codes expected by cleaner
                case_type={
                    0: "lowercase",
                    1: "Title Case",
                    2: "UPPERCASE",
                }.get(self.top_panel.case_type_combo.currentIndex(), "lowercase"),
                remove_accents=self.top_panel.remove_accents_check.isChecked()
            )
        except Exception as e:
            # If preview generation fails, return empty list and show error
            print(f"Preview generation error: {e}")
            self.notification_manager.show_notification(
                f"Preview generation failed: {str(e)}", "error"
            )
            return []

        self.filtered_files = filtered_files
        return preview_list
    # ---------------- Rename ----------------
    def rename_files(self):
        if not self.filtered_files:
            QMessageBox.information(self, "No files", "No files to rename.")
            return

        preview_list = self.get_preview_list()
        # Only include files that are "Ready" (exclude "Extension Locked", "Conflict", "No Change")
        file_ops = [
            {"old_path": f[3], "new_path": os.path.join(os.path.dirname(f[3]), f[1]), "action": "rename"}
            for f in preview_list if f[2] == "Ready"
        ]

        if not file_ops:
            # Check if there are extension locked files
            extension_locked_count = len([f for f in preview_list if f[2] == "Extension Locked"])
            if extension_locked_count > 0:
                QMessageBox.information(
                    self, 
                    "Extension Lock Active", 
                    f"No files ready to rename. {extension_locked_count} files have extension lock enabled.\n\n"
                    "To rename these files, either:\n"
                    "• Uncheck 'Lock File Extensions' to allow extension changes\n"
                    "• Or modify your naming pattern to not change extensions"
                )
            else:
                QMessageBox.information(self, "Nothing to rename", "No files marked as Ready.")
            return

        # Optional confirmation before renaming
        try:
            if bool(self.settings_manager.get("confirm_before_rename", True)):
                # Attempt translations with safe fallbacks
                title = self.translation_manager.tr("dialogs.confirm_rename.title")
                if not isinstance(title, str) or "." in title:
                    title = "Confirm Rename"
                message = self.translation_manager.tr("dialogs.confirm_rename.message", count=len(file_ops))
                if not isinstance(message, str) or "." in message:
                    message = f"Are you sure you want to rename {len(file_ops)} file(s)?"
                reply = QMessageBox.question(
                    self,
                    title,
                    message,
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
        except Exception:
            # If anything goes wrong with settings or translations, proceed safely by asking once
            reply = QMessageBox.question(
                self,
                "Confirm Rename",
                f"Are you sure you want to rename {len(file_ops)} file(s)?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        # Optional: create backups before rename
        try:
            if bool(self.settings_manager.get("backup_before_rename", False)):
                base_dir = self.settings_manager.get("backup_location", "backups/")
                # Resolve to absolute path
                if not os.path.isabs(base_dir):
                    base_dir = os.path.abspath(base_dir)

                # Determine actual target directory
                target_dir = None
                if bool(self.settings_manager.get("create_backup_folder", False)):
                    # Always create/use a subfolder named "backup" in the chosen location
                    target_dir = os.path.join(base_dir, "backup")
                    try:
                        os.makedirs(target_dir, exist_ok=True)
                    except Exception as e:
                        QMessageBox.warning(self, "Backup", f"Failed to create backup subfolder:\n{target_dir}\n\n{e}\nBackups will be skipped.")
                        target_dir = None
                else:
                    # Use base_dir as-is, but require it to exist
                    if os.path.exists(base_dir):
                        target_dir = base_dir
                    else:
                        QMessageBox.warning(self, "Backup", f"Backup folder does not exist:\n{base_dir}\nEnable 'Create backup folder automatically' or create it manually. Backups will be skipped.")
                        target_dir = None

                if target_dir:
                    backup_errors = []
                    for op in file_ops:
                        src = op["old_path"]
                        name = os.path.basename(src)
                        dest = os.path.join(target_dir, name)
                        # Avoid overwrite in backup folder by appending counter
                        if os.path.exists(dest):
                            base, ext = os.path.splitext(name)
                            counter = 1
                            while os.path.exists(dest):
                                dest = os.path.join(target_dir, f"{base} ({counter}){ext}")
                                counter += 1
                        try:
                            shutil.copy2(src, dest)
                        except Exception as e:
                            backup_errors.append(f"\n{src} -> {dest}: {e}")
                    if backup_errors:
                        QMessageBox.warning(self, "Backup", "Some files failed to backup:" + "".join(backup_errors[:10]) + ("\n..." if len(backup_errors) > 10 else ""))
        except Exception:
            # Non-fatal: continue with rename
            pass

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.top_panel.rename_button.setEnabled(False)

        self.rename_worker = FileOperationWorker(file_ops)
        self.rename_worker.progress.connect(self.progress_bar.setValue)

        def on_done(successes, errors, conflicts):
            self.progress_bar.setVisible(False)
            self.top_panel.rename_button.setEnabled(True)

            if errors:
                QMessageBox.critical(self, "Rename Failed", "\n".join(errors))
            if conflicts:
                QMessageBox.warning(self, "Rename Conflicts", "\n".join(conflicts))

            if successes:
                # Remove successfully renamed files from selected_files
                renamed_old_paths = [f["old_path"] for f in successes]
                self.selected_files = [f for f in self.selected_files if f not in renamed_old_paths]

                self.history.append({"files": successes, "undone": False})
                self.top_panel.history_panel.update_history(self.history)
                self.top_panel.undo_button.setEnabled(True)
                
                # Save history to file
                self._save_history()

            # Logging (if enabled)
            try:
                self._log_operations("rename", successes, errors, conflicts)
            except Exception:
                pass

            # Notifications summary
            try:
                total_ready = len(successes)
                total_errors = len(errors)
                total_conflicts = len(conflicts)
                if total_errors > 0:
                    self.notification_manager.show_notification(
                        self.translation_manager.tr("notifications.rename_finished_error", success=total_ready, errors=total_errors, conflicts=total_conflicts),
                        "error"
                    )
                elif total_conflicts > 0:
                    self.notification_manager.show_notification(
                        self.translation_manager.tr("notifications.rename_finished_warning", success=total_ready, conflicts=total_conflicts),
                        "warning"
                    )
                else:
                    self.notification_manager.show_notification(
                        self.translation_manager.tr("notifications.rename_finished_success", count=total_ready),
                        "success"
                    )
            except Exception:
                pass

            self.update_preview()  # Keep skipped files in preview

        self.rename_worker.finished.connect(on_done)
        self.rename_worker.start()

    # ---------------- Undo ----------------
    def undo_last_rename(self):
        last_batch = next((b for b in reversed(self.history) if not b.get("undone", False)), None)
        if not last_batch:
            QMessageBox.information(self, "Undo", "Nothing left to undo.")
            return

        # Build operations reversing the last batch first to respect chronological order
        file_ops = [{"old_path": f["new_path"], "new_path": f["old_path"], "action": "undo"}
                    for f in reversed(last_batch["files"])]

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.undo_worker = FileOperationWorker(file_ops)
        self.undo_worker.progress.connect(self.progress_bar.setValue)

        def on_undo_done(successes, errors, conflicts):
            self.progress_bar.setVisible(False)
            if errors:
                QMessageBox.critical(self, "Undo Failed", "\n".join(errors))
            if successes:
                restored_paths = [f["new_path"] for f in successes]
                self.selected_files.extend(restored_paths)

            last_batch["undone"] = True
            self.top_panel.history_panel.update_history(self.history)
            self.top_panel.undo_button.setEnabled(any(not b.get("undone", False) for b in self.history))
            self.update_preview()
            
            # Save history to file
            self._save_history()

            # Logging (if enabled)
            try:
                self._log_operations("undo_last", successes, errors, conflicts)
            except Exception:
                pass

            # Notification
            try:
                if errors:
                    self.notification_manager.show_notification(
                        self.translation_manager.tr("notifications.undo_finished_error", restored=len(successes), errors=len(errors)),
                        "error"
                    )
                else:
                    self.notification_manager.show_notification(
                        self.translation_manager.tr("notifications.undo_finished_success", restored=len(successes)),
                        "success"
                    )
            except Exception:
                pass

        self.undo_worker.finished.connect(on_undo_done)
        self.undo_worker.start()

    def undo_selected_history(self):
        """Undo all selected history batches from the HistoryPanel."""
        checked_indices = []
        try:
            checked_indices = self.top_panel.history_panel.get_checked_indices()
        except Exception:
            checked_indices = []
        if not checked_indices:
            QMessageBox.information(self, "Undo", "No history entries selected.")
            return

        # Collect ops from selected batches in reverse chronological order overall
        # This ensures multi-step renames of the same file are undone safely
        file_ops = []
        for idx in sorted(checked_indices, reverse=True):
            if idx < 0 or idx >= len(self.history):
                continue
            batch = self.history[idx]
            if batch.get("undone", False):
                continue
            file_ops.extend([{ "old_path": f["new_path"], "new_path": f["old_path"], "action": "undo" } for f in reversed(batch["files"])])

        if not file_ops:
            QMessageBox.information(self, "Undo", "Nothing to undo for selected entries.")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.undo_worker = FileOperationWorker(file_ops)
        self.undo_worker.progress.connect(self.progress_bar.setValue)

        def on_undo_done(successes, errors, conflicts):
            self.progress_bar.setVisible(False)
            if errors:
                QMessageBox.critical(self, "Undo Failed", "\n".join(errors))
            if successes:
                restored_paths = [f["new_path"] for f in successes]
                self.selected_files.extend(restored_paths)

            # Mark all selected as undone
            for idx in checked_indices:
                if 0 <= idx < len(self.history):
                    self.history[idx]["undone"] = True
            self.top_panel.history_panel.update_history(self.history)
            self.top_panel.undo_button.setEnabled(any(not b.get("undone", False) for b in self.history))
            self.update_preview()
            
            # Save history to file
            self._save_history()

            # Logging (if enabled)
            try:
                self._log_operations("undo_selected", successes, errors, conflicts)
            except Exception:
                pass

            # Notification
            try:
                if errors:
                    self.notification_manager.show_notification(
                        self.translation_manager.tr("notifications.undo_finished_error", restored=len(successes), errors=len(errors)),
                        "error"
                    )
                else:
                    self.notification_manager.show_notification(
                        self.translation_manager.tr("notifications.undo_finished_success", restored=len(successes)),
                        "success"
                    )
            except Exception:
                pass

        self.undo_worker.finished.connect(on_undo_done)
        self.undo_worker.start()

    # ---------------- Drag & Drop ----------------
    def dragEnterEvent(self, event):
        """Handle drag enter events - accept if URLs are present."""
        try:
            if event.mimeData().hasUrls():
                # Check if any of the URLs are files or directories
                urls = event.mimeData().urls()
                for url in urls:
                    if url.isLocalFile():
                        event.acceptProposedAction()
                        return
            event.ignore()
        except Exception:
            event.ignore()

    def dragMoveEvent(self, event):
        """Handle drag move events - accept if URLs are present."""
        try:
            if event.mimeData().hasUrls():
                event.acceptProposedAction()
            else:
                event.ignore()
        except Exception:
            event.ignore()

    def dropEvent(self, event):
        """Handle drop events - extract file paths and add them."""
        try:
            if event.mimeData().hasUrls():
                # Extract local file paths
                paths = []
                for url in event.mimeData().urls():
                    if url.isLocalFile():
                        local_path = url.toLocalFile()
                        if os.path.exists(local_path):
                            paths.append(local_path)
                
                if paths:
                    event.acceptProposedAction()
                    self.add_files(paths)
                else:
                    event.ignore()
            else:
                event.ignore()
        except Exception as e:
            print(f"Drop event error: {e}")  # Debug output
            event.ignore()

    # ---------------- Unified File Add ----------------
    def add_files(self, paths):
        if not paths:
            return

        # Normalize paths for consistent duplicate checking
        normalized_paths = [os.path.normpath(path) for path in paths]
        self._file_add_queue.append(normalized_paths)
        if not self._file_add_worker or not self._file_add_worker.isRunning():
            self._process_file_add_queue()

    def _process_file_add_queue(self):
        if not self._file_add_queue:
            self.progress_bar.setVisible(False)
            return

        paths = self._file_add_queue.popleft()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Always use the current selected_files to check for duplicates
        self._file_add_worker = FileAddWorker(paths, existing_files=self.selected_files)

        def on_finished(new_files, duplicate_count):
            self.selected_files.extend(new_files)
            self.update_preview()
            
            # Show notification if there were duplicates
            if duplicate_count > 0:
                self._show_duplicate_notification(len(new_files), duplicate_count)
            
            self._process_file_add_queue()

        self._file_add_worker.progress.connect(self.progress_bar.setValue)
        self._file_add_worker.finished.connect(on_finished)
        self._file_add_worker.start()
    
    def _show_duplicate_notification(self, added_count, duplicate_count):
        """Show notification about duplicate files."""
        if added_count > 0:
            # Show combined notification: files added + duplicates skipped
            message = self.translation_manager.tr("top_panel.files.files_added_notification").format(
                added=added_count, 
                duplicates=duplicate_count
            )
        else:
            # Show only duplicates notification (no new files added)
            message = self.translation_manager.tr("top_panel.files.duplicates_notification").format(
                count=duplicate_count
            )
        
        # Show as info notification (blue color)
        self.notification_manager.show_notification(message, "info")
    
    # ---------------- Profile Management ----------------
    def save_profile(self):
        """Save current settings as a profile."""
        from PySide6.QtWidgets import QInputDialog
        
        # Use translation manager to get localized text with safe fallbacks
        title = self.translation_manager.tr("dialogs.save_profile.title")
        message = self.translation_manager.tr("dialogs.save_profile.message")
        default_name = self.translation_manager.tr("dialogs.save_profile.default_name")
        # If translation lookup failed (key echoed back), fall back to English literals
        if "." in str(title):
            title = "Save Profile"
        if "." in str(message):
            message = "Name of Profile"
        if "." in str(default_name):
            default_name = "My Profile"
        profile_name, ok = QInputDialog.getText(
            self,
            title,
            message,
            text=default_name
        )
        
        if ok and profile_name.strip():
            profile_name = profile_name.strip()
            
            # Check if profile already exists
            if self.profile_manager.profile_exists(profile_name):
                reply = QMessageBox.question(
                    self,
                    self.translation_manager.tr("dialogs.overwrite_profile.title"),
                    self.translation_manager.tr("dialogs.overwrite_profile.message", name=profile_name),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
            
            # Get current settings
            settings = self.top_panel.get_current_settings()
            
            # Save profile
            if self.profile_manager.save_profile(profile_name, settings):
                self.notification_manager.show_notification(
                    self.translation_manager.tr("notifications.profile_saved", name=profile_name), 
                    "save"
                )
                self.settings_manager.add_recent_profile(profile_name)
                self.update_recent_items()
                self.refresh_profiles()
            else:
                self.notification_manager.show_notification(
                    self.translation_manager.tr("notifications.profile_save_failed", name=profile_name), 
                    "error"
                )
    
    def load_profile(self, profile_name):
        """Load a profile."""
        profile_data = self.profile_manager.load_profile(profile_name)
        
        if profile_data is None:
            self.notification_manager.show_notification(
                self.translation_manager.tr("notifications.profile_load_failed", name=profile_name), 
                "error"
            )
            return
        
        # Remove metadata before applying settings
        if "_metadata" in profile_data:
            del profile_data["_metadata"]
        
        # Apply settings
        self.top_panel.apply_settings(profile_data)
        
        # Update preview
        self.update_preview()
        
        self.notification_manager.show_notification(
            self.translation_manager.tr("notifications.profile_loaded", name=profile_name), 
            "load"
        )
        self.settings_manager.add_recent_profile(profile_name)
        self.update_recent_items()
    
    def delete_profile(self, profile_name):
        """Delete a profile."""
        reply = QMessageBox.question(
            self,
            self.translation_manager.tr("dialogs.delete_profile.title"),
            self.translation_manager.tr("dialogs.delete_profile.message", name=profile_name),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.profile_manager.delete_profile(profile_name):
                self.notification_manager.show_notification(
                    self.translation_manager.tr("notifications.profile_deleted", name=profile_name), 
                    "delete"
                )
                self.refresh_profiles()
            else:
                self.notification_manager.show_notification(
                    self.translation_manager.tr("notifications.profile_delete_failed", name=profile_name), 
                    "error"
                )
    
    def refresh_profiles(self):
        """Refresh the profiles list in the UI."""
        profiles = self.profile_manager.list_profiles()
        self.top_panel.refresh_profiles_list(profiles)
    
    # ---------------- Menu Bar and Settings ----------------
    def setup_menu_bar(self):
        """Setup the menu bar."""
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        
        # Store connection callbacks for reconnecting after language changes
        connection_callbacks = {
            'new_profile': self.new_profile,
            'save_profile': self.save_profile,
            'load_profile': self.load_profile_from_menu,
            'open_folder': lambda: self.browse_folder(None),
            'select_files': lambda: self.select_files(None),
            'exit': self.close,
            'undo': self.undo_last_rename,
            'clear_all': self.clear_all_files,
            'refresh': self.update_preview,
            'batch_rename': self.rename_files,
            'validate': self.validate_names,
            'user_guide': self.show_user_guide,
            'shortcuts': self.show_keyboard_shortcuts,
            'about': self.show_about,
            'eula': lambda: self.show_legal_doc('eula'),
            'privacy': lambda: self.show_legal_doc('privacy'),
            'terms': lambda: self.show_legal_doc('terms'),
            'toggle_file_count': self.toggle_file_count,
            'toggle_history': self.toggle_history
        }
        self.menu_bar.set_connection_callbacks(connection_callbacks)
        
        # Connect menu actions
        self.menu_bar.actions['new_profile'].triggered.connect(self.new_profile)
        self.menu_bar.actions['save_profile'].triggered.connect(self.save_profile)
        self.menu_bar.actions['load_profile'].triggered.connect(self.load_profile_from_menu)
        # Wire file open actions
        self.menu_bar.actions['open_folder'].triggered.connect(lambda _=False: self.browse_folder(None))
        self.menu_bar.actions['select_files'].triggered.connect(lambda _=False: self.select_files(None))
        self.menu_bar.actions['exit'].triggered.connect(self.close)
        self.menu_bar.actions['undo'].triggered.connect(self.undo_last_rename)
        self.menu_bar.actions['clear_all'].triggered.connect(self.clear_all_files)
        self.menu_bar.actions['refresh'].triggered.connect(self.update_preview)
        self.menu_bar.actions['batch_rename'].triggered.connect(self.rename_files)
        self.menu_bar.actions['validate'].triggered.connect(self.validate_names)
        self.menu_bar.actions['user_guide'].triggered.connect(self.show_user_guide)
        self.menu_bar.actions['shortcuts'].triggered.connect(self.show_keyboard_shortcuts)
        self.menu_bar.actions['about'].triggered.connect(self.show_about)
        # Legal
        self.menu_bar.actions['eula'].triggered.connect(lambda: self.show_legal_doc('eula'))
        self.menu_bar.actions['privacy'].triggered.connect(lambda: self.show_legal_doc('privacy'))
        self.menu_bar.actions['terms'].triggered.connect(lambda: self.show_legal_doc('terms'))
        self.menu_bar.actions['toggle_file_count'].triggered.connect(self.toggle_file_count)
        self.menu_bar.actions['toggle_history'].triggered.connect(self.toggle_history)
        
        # Set up recent item callbacks
        self.menu_bar.set_recent_callbacks(self.load_profile)
        
        # Update recent items
        self.update_recent_items()
    
    def load_profile_from_menu(self):
        """Load profile from menu (shows dialog)."""
        from PySide6.QtWidgets import QInputDialog
        
        profiles = self.profile_manager.list_profiles()
        if not profiles:
            QMessageBox.information(self, "No Profiles", "No saved profiles found.")
            return
        
        profile_name, ok = QInputDialog.getItem(
            self, 
            "Load Profile", 
            "Select a profile to load:",
            profiles,
            0,
            False
        )
        
        if ok and profile_name:
            self.load_profile(profile_name)
    
    def new_profile(self):
        """Create a new profile (clear current settings)."""
        from PySide6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            "New Profile",
            "This will clear all current settings. Are you sure?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clear all current settings
            self.top_panel.prefix_input.clear()
            self.top_panel.suffix_input.clear()
            self.top_panel.base_input.clear()
            self.top_panel.start_input.clear()
            self.top_panel.ext_filter_input.clear()
            self.top_panel.size_value.clear()
            self.top_panel.date_value.clear()
            self.top_panel.status_filter.setCurrentIndex(0)
            self.top_panel.extension_lock_checkbox.setChecked(True)
            
            # Clear files
            self.clear_all_files()
            
            self.notification_manager.show_notification(
                "New profile created - all settings cleared", 
                "success"
            )
    
    def validate_names(self):
        """Validate/Simulate: run safety checks and show a report dialog."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QFileDialog
        import shutil
        import os
        from datetime import datetime

        preview_list = self.get_preview_list()
        if not preview_list:
            self.notification_manager.show_notification("No files to simulate", "info")
            return

        issues = []
        warnings = []

        # Duplicate names (case-insensitive on Windows)
        lowered = [n[1].lower() for n in preview_list]
        dupes = sorted({n for n in lowered if lowered.count(n) > 1})
        if dupes:
            issues.append("Duplicate targets: " + ", ".join(dupes[:10]) + ("..." if len(dupes) > 10 else ""))

        # Illegal characters/reserved names (Windows)
        invalid_chars = '<>:"/\\|?*'
        reserved = {"con","prn","aux","nul","com1","com2","com3","com4","com5","com6","com7","com8","com9","lpt1","lpt2","lpt3","lpt4","lpt5","lpt6","lpt7","lpt8","lpt9"}
        for _, new_name, _, _ in preview_list:
            name_no_ext = os.path.splitext(new_name)[0].lower()
            if any(c in new_name for c in invalid_chars):
                issues.append(f"Illegal characters in '{new_name}'")
            if name_no_ext in reserved:
                issues.append(f"Reserved name: '{new_name}'")

        # Empty names
        empties = [n for _, n, _, _ in preview_list if not n.strip()]
        if empties:
            issues.append("Empty target names detected")

        # Permission/directory write check and path length
        for _, new_name, _, src in preview_list:
            target = os.path.join(os.path.dirname(src), new_name)
            try:
                if len(target) > 240 and os.name == 'nt':
                    warnings.append(f"Long path (may fail on Windows): {target}")
                # Check dir writable
                tdir = os.path.dirname(target)
                if not os.access(tdir, os.W_OK):
                    issues.append(f"No write permission: {tdir}")
                # Check if target already exists (but not for case-only changes)
                is_case_only_change = (os.path.normcase(target) == os.path.normcase(src) and target != src)
                if not is_case_only_change and os.path.exists(target) and target != src:
                    try:
                        warning_text = self.translation_manager.tr("validate.warning_target_exists")
                        if "." in str(warning_text):
                            warning_text = "Target already exists"
                    except Exception:
                        warning_text = "Target already exists"
                    warnings.append(f"{warning_text}: {new_name}")
            except Exception as e:
                issues.append(f"Validation error for '{new_name}': {str(e)}")

        # Assemble report with timestamp and summary (localized)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tr = self.translation_manager.tr
        
        # Get translated strings with fallbacks
        report_title = tr("validate.report_title")
        if "." in str(report_title):
            report_title = "Simulation Report"
        
        total_files = tr("validate.report_total_files")
        if "." in str(total_files):
            total_files = "Total files to process"
        
        blocking_issues = tr("validate.report_blocking_issues")
        if "." in str(blocking_issues):
            blocking_issues = "Blocking issues"
        
        warnings_text = tr("validate.report_warnings")
        if "." in str(warnings_text):
            warnings_text = "Warnings"
        
        file_details = tr("validate.report_file_details")
        if "." in str(file_details):
            file_details = "File Details"
        
        no_issues = tr("validate.report_no_issues")
        if "." in str(no_issues):
            no_issues = "No issues detected - rename operation should succeed."
        
        lines = [
            f"{report_title} - {timestamp}\n",
            "="*60 + "\n\n",
            f"{total_files}: {len(preview_list)}\n",
            f"{blocking_issues}: {len(issues)}\n",
            f"{warnings_text}: {len(warnings)}\n\n"
        ]
        
        # File-by-file details
        lines.append(f"{file_details}:\n" + "-"*40 + "\n")
        for old, new, status, src in preview_list:
            target = os.path.join(os.path.dirname(src), new)
            reason = ""
            if any(c in new for c in invalid_chars):
                reason = " [ILLEGAL CHARS]"
            elif not new.strip():
                reason = " [EMPTY NAME]"
            elif os.path.exists(target) and target != src:
                reason = " [EXISTS]"
            lines.append(f"{old} -> {new} [{status}]{reason}\n")
        
        # Issues and warnings
        if issues:
            issues_header = tr("validate.report_blocking_issues_found", count=len(issues))
            if "." in str(issues_header):
                issues_header = f"Blocking Issues ({len(issues)})"
            issue_prefix = tr("validate.report_issue_prefix")
            if "." in str(issue_prefix):
                issue_prefix = "❌"
            lines.append(f"\n{issues_header}:\n" + "-"*40 + "\n")
            for issue in issues:
                lines.append(f"{issue_prefix} {issue}\n")
        
        if warnings:
            warnings_header = tr("validate.report_warnings_found", count=len(warnings))
            if "." in str(warnings_header):
                warnings_header = f"Warnings ({len(warnings)})"
            warning_prefix = tr("validate.report_warning_prefix")
            if "." in str(warning_prefix):
                warning_prefix = "⚠️"
            lines.append(f"\n{warnings_header}:\n" + "-"*40 + "\n")
            for warning in warnings:
                lines.append(f"{warning_prefix}  {warning}\n")
        
        if not issues and not warnings:
            lines.append(f"\n✅ {no_issues}\n")
        
        # Show notification (localized with fallbacks)
        try:
            tr = self.translation_manager.tr
            if issues:
                msg = tr("notifications.validate_blocking_issues", count=len(issues))
                if "." in str(msg) or not isinstance(msg, str):
                    msg = f"Validate: {len(issues)} blocking issue(s) found — open report for details"
                self.notification_manager.show_notification(msg, "error")
            elif warnings:
                msg = tr("notifications.validate_warnings", count=len(warnings))
                if "." in str(msg) or not isinstance(msg, str):
                    msg = f"Validate: {len(warnings)} warning(s) found — open report for details"
                self.notification_manager.show_notification(msg, "warning")
            else:
                msg = tr("notifications.validate_clean", count=len(preview_list))
                if "." in str(msg) or not isinstance(msg, str):
                    msg = f"Validate: no issues in {len(preview_list)} file(s) - ready to rename"
                self.notification_manager.show_notification(msg, "success")
        except Exception:
            pass

        # Show dialog with report and export
        dlg = QDialog(self)
        try:
            title = self.translation_manager.tr("validate.title")
            if "." in str(title):
                title = "Validate / Simulate"
        except Exception:
            title = "Validate / Simulate"
        dlg.setWindowTitle(title)
        layout = QVBoxLayout(dlg)
        text = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText("".join(lines))
        layout.addWidget(text)
        btns = QHBoxLayout()
        try:
            export_text = self.translation_manager.tr("validate.save_report")
            if "." in str(export_text):
                export_text = "Save Report..."
        except Exception:
            export_text = "Save Report..."
        try:
            close_text = self.translation_manager.tr("settings.buttons.close")
            if "." in str(close_text):
                close_text = "Close"
        except Exception:
            close_text = "Close"
        export_btn = QPushButton(export_text)
        close_btn = QPushButton(close_text)
        btns.addStretch()
        btns.addWidget(export_btn)
        btns.addWidget(close_btn)
        layout.addLayout(btns)

        def export_report():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"validation_report_{timestamp}.txt"
            try:
                dialog_title = self.translation_manager.tr("validate.save_report_title")
                if "." in str(dialog_title):
                    dialog_title = "Save Report"
            except Exception:
                dialog_title = "Save Report"
            # Keep file type text simple; translation optional
            path, _ = QFileDialog.getSaveFileName(dlg, dialog_title, default_name, "Text Files (*.txt)")
            if path:
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(text.toPlainText())
                    try:
                        saved_msg = self.translation_manager.tr("validate.report_saved", path=path)
                        if "." in str(saved_msg):
                            saved_msg = f"Report saved to {path}"
                    except Exception:
                        saved_msg = f"Report saved to {path}"
                    # Show full path so user knows exact location
                    self.notification_manager.show_notification(saved_msg, "success")
                except Exception as e:
                    try:
                        err_msg = self.translation_manager.tr("validate.report_save_failed", error=str(e))
                        if "." in str(err_msg):
                            err_msg = f"Failed to save report: {str(e)}"
                    except Exception:
                        err_msg = f"Failed to save report: {str(e)}"
                    self.notification_manager.show_notification(err_msg, "error")
        
        export_btn.clicked.connect(export_report)
        close_btn.clicked.connect(dlg.accept)
        dlg.resize(720, 480)
        dlg.exec()
    
    def preview_changes(self):
        """Preview changes in a detailed dialog."""
        if not self.filtered_files:
            self.notification_manager.show_notification(
                "No files to preview", 
                "info"
            )
            return
        
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Preview Changes")
        dialog.setModal(True)
        dialog.resize(600, 400)
        
        layout = QVBoxLayout()
        
        # Text area showing changes
        text_area = QTextEdit()
        text_area.setReadOnly(True)
        
        preview_list = self.get_preview_list()
        text = "File Rename Preview\n"
        text += "=" * 50 + "\n\n"
        
        for i, (old_name, new_name, status, _) in enumerate(preview_list, 1):
            text += f"{i:3d}. {old_name}\n"
            text += f"     → {new_name} ({status})\n\n"
        
        text += f"\nTotal files: {len(preview_list)}"
        text_area.setPlainText(text)
        layout.addWidget(text_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def show_user_guide(self):
        """Show user guide dialog."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle(self.translation_manager.tr("help.user_guide.title"))
        dialog.setModal(True)
        dialog.resize(700, 500)
        
        layout = QVBoxLayout()
        
        # Text area with user guide
        text_area = QTextEdit()
        text_area.setReadOnly(True)
        from app.ui.custom_scrollbar import CustomScrollBar
        text_area.setVerticalScrollBar(CustomScrollBar(Qt.Vertical))
        text_area.setHorizontalScrollBar(CustomScrollBar(Qt.Horizontal))
        
        guide_text = self.translation_manager.tr("help.user_guide.content")
        text_area.setPlainText(guide_text)
        layout.addWidget(text_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        close_button = QPushButton(self.translation_manager.tr("settings.buttons.close"))
        close_button.clicked.connect(dialog.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def show_keyboard_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
        import sys
        
        dialog = QDialog(self)
        dialog.setWindowTitle(self.translation_manager.tr("help.keyboard_shortcuts.title"))
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout()
        
        # Text area with shortcuts
        text_area = QTextEdit()
        text_area.setReadOnly(True)
        from app.ui.custom_scrollbar import CustomScrollBar
        text_area.setVerticalScrollBar(CustomScrollBar(Qt.Vertical))
        text_area.setHorizontalScrollBar(CustomScrollBar(Qt.Horizontal))
        
        shortcuts_text = self.translation_manager.tr("help.keyboard_shortcuts.content")
        # Adapt to platform-specific key names for display
        try:
            if sys.platform == "darwin":
                # Replace common modifier names for macOS display
                replacements = {
                    "Ctrl+Shift+": "Cmd+Shift+",
                    "Ctrl+": "Cmd+",
                    "Alt+": "Option+",
                }
                for src, dst in replacements.items():
                    shortcuts_text = shortcuts_text.replace(src, dst)
        except Exception:
            pass
        text_area.setPlainText(shortcuts_text)
        layout.addWidget(text_area)
        
        # Buttons
        button_layout = QHBoxLayout()
        close_button = QPushButton(self.translation_manager.tr("settings.buttons.close"))
        close_button.clicked.connect(dialog.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def show_about(self):
        """Show about dialog."""
        from PySide6.QtWidgets import QMessageBox
        
        about_content = self.translation_manager.tr("help.about.content")
        about_content = about_content.replace("Version 1.0", f"Version {__version__}")
        
        QMessageBox.about(
            self,
            self.translation_manager.tr("help.about.title"),
            about_content.replace('\n', '<br>').replace('•', '&bull;')
        )

    def show_legal_doc(self, kind: str):
        """Display legal documents (EULA/Privacy/Terms) with localized title and content.
        Loads text from legal/<lang>/<kind>.txt if available, otherwise shows placeholder."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
        import os
        from datetime import date
        lang = self.settings_manager.get("language", "en")
        titles = {
            'eula': self.translation_manager.tr("legal.eula_title"),
            'privacy': self.translation_manager.tr("legal.privacy_title"),
            'terms': self.translation_manager.tr("legal.terms_title")
        }
        title = titles.get(kind, "Legal")
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setModal(True)
        dialog.resize(720, 560)
        layout = QVBoxLayout(dialog)
        text = QTextEdit()
        text.setReadOnly(True)
        # Apply custom scrollbars for consistency
        from app.ui.custom_scrollbar import CustomScrollBar
        text.setVerticalScrollBar(CustomScrollBar(Qt.Vertical))
        text.setHorizontalScrollBar(CustomScrollBar(Qt.Horizontal))
        # Try to load external file first
        base = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'legal', lang)
        path = os.path.join(base, f"{kind}.txt")
        content = ""
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
        except Exception:
            content = ""
        if not content:
            # Minimal placeholder
            content = f"{title}\n\nThis document will be provided by the publisher."
        # Replace simple placeholders like {today}
        try:
            today_str = date.today().isoformat()
            content = content.replace("{today}", today_str)
        except Exception:
            pass
        text.setPlainText(content)
        layout.addWidget(text)
        btns = QHBoxLayout()
        close_btn = QPushButton(self.translation_manager.tr("legal.close"))
        close_btn.clicked.connect(dialog.accept)
        btns.addStretch()
        btns.addWidget(close_btn)
        layout.addLayout(btns)
        dialog.exec()
    
    def toggle_file_count(self):
        """Toggle file count display."""
        show_count = self.menu_bar.actions['toggle_file_count'].isChecked()
        self.top_panel.file_count.setVisible(show_count)
        self.settings_manager.set("show_file_count", show_count)
    
    def toggle_history(self):
        """Toggle history panel display."""
        show_history = self.menu_bar.actions['toggle_history'].isChecked()
        self.top_panel.history_panel.setVisible(show_history)
    
    def update_recent_items(self):
        """Update recent profiles in menu."""
        recent_profiles = self.settings_manager.get("recent_profiles", [])
        # Enforce limit from settings when displaying
        max_items = int(self.settings_manager.get("max_recent_items", 10) or 10)
        recent_profiles = recent_profiles[:max_items]
        self.menu_bar.update_recent_profiles(recent_profiles)
    
    def apply_settings(self):
        """Apply settings from settings manager."""
        # Set flag to prevent notifications during settings application
        self._is_applying_settings = True
        
        # File count visibility
        show_count = self.settings_manager.get("show_file_count", True)
        self.top_panel.file_count.setVisible(show_count)
        self.menu_bar.actions['toggle_file_count'].setChecked(show_count)
        
        # History visibility
        show_history = self.settings_manager.get("show_history", True)
        self.top_panel.history_panel.setVisible(show_history)
        self.menu_bar.actions['toggle_history'].setChecked(show_history)
        
        # Tooltips
        show_tooltips = bool(self.settings_manager.get("show_tooltips", True))
        try:
            self.top_panel.apply_tooltips(show_tooltips)
        except Exception:
            pass
        
        # Only apply default naming settings to UI if they haven't been set by user yet
        # This preserves user's current input when changing other settings
        if not self.top_panel.prefix_input.text().strip():
            self.top_panel.prefix_input.setText(self.settings_manager.get("default_prefix", ""))
        if not self.top_panel.suffix_input.text().strip():
            self.top_panel.suffix_input.setText(self.settings_manager.get("default_suffix", ""))
        if not self.top_panel.base_input.text().strip():
            self.top_panel.base_input.setText(self.settings_manager.get("default_base_name", ""))
        if not self.top_panel.start_input.text().strip():
            self.top_panel.start_input.setText(str(self.settings_manager.get("default_start_number", 1)))
        # Apply theme live if changed via settings tab
        app_theme = self.settings_manager.get("theme")
        if app_theme:
            apply_theme(self, app_theme)
        # Update history panel theme
        if app_theme:
            self.top_panel.history_panel.update_theme(app_theme)
        # Update start number styling after theme is applied (use QTimer to ensure it's last)
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, self.top_panel._update_start_number_styling)
        
        # Reset flag after settings are applied
        self._is_applying_settings = False
    
    def _save_history(self):
        """Save history to file."""
        try:
            history_file = self.settings_manager.get("history_file", "history.json")
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            # Silently fail - history persistence is not critical
            pass
    
    def _load_history(self):
        """Load history from file."""
        try:
            history_file = self.settings_manager.get("history_file", "history.json")
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
                # Update UI with loaded history
                if self.history:
                    self.top_panel.history_panel.update_history(self.history)
                    self.top_panel.undo_button.setEnabled(any(not b.get("undone", False) for b in self.history))
        except Exception as e:
            # Silently fail - start with empty history
            self.history = []
    
    def closeEvent(self, event):
        """Handle application close event."""
        # Save history before closing
        self._save_history()
        event.accept()
    
    def on_settings_changed(self):
        """Handle settings changes."""
        # Show a confirmation notification
        self.notification_manager.show_notification(
            self.translation_manager.tr("notifications.settings_saved"),
            "save"
        )
        # Apply theme immediately on settings save
        self.apply_settings()
        self.update_recent_items()
    
    def on_settings_error(self, error_message):
        """Handle settings errors."""
        self.notification_manager.show_notification(
            error_message, 
            "error"
        )
    
    def on_language_changed(self, language_code):
        """Handle language change."""
        set_language(language_code)
        self.update_window_title()
        # Show a lightweight overlay while updating UI text
        self._show_language_overlay()
        
        # Update all UI components with new language
        self.update_all_ui_text()
        
        # Flip overlay to done state and hide shortly after
        self._finish_language_overlay()
    
    def update_window_title(self):
        """Update window title with current language."""
        # Use localized application title
        try:
            self.setWindowTitle(self.translation_manager.tr("app.title"))
        except Exception:
            self.setWindowTitle("Bulk File Renamer")
    
    def update_all_ui_text(self):
        """Update all UI text with current language."""
        # Update main buttons
        self.top_panel.rename_button.setText(self.translation_manager.tr("main.rename_files"))
        self.top_panel.undo_button.setText(self.translation_manager.tr("main.undo_last_rename"))
        
        # Update tab names
        self.tab_widget.setTabText(0, self.translation_manager.tr("main.rename_files"))
        self.tab_widget.setTabText(1, self.translation_manager.tr("settings.tabs.settings"))
        
        # Update top panel
        self.top_panel.update_language()
        
        # Update file count row
        self.top_panel.file_count.update_language()
        
        # Update history panel
        self.top_panel.history_panel.update_language()
        
        # Update settings tab
        self.settings_tab.update_language()
        
        # Update menu bar
        self.menu_bar.update_language()

    # ---------------- Language overlay helpers ----------------
    def _show_language_overlay(self):
        try:
            r = self.rect()
            self._lang_overlay.setGeometry(0, 0, r.width(), r.height())
            # Simple two-state indicator: loading spinner -> checkmark
            self._lang_overlay.setText("⏳  " + self.translation_manager.tr("ui.language_updating"))
            self._lang_overlay.show()
        except Exception:
            pass

    def _finish_language_overlay(self):
        try:
            self._lang_overlay.setText("✅  " + self.translation_manager.tr("ui.language_changed"))
            QTimer.singleShot(1200, lambda: self._lang_overlay.hide())
        except Exception:
            pass
    
    def moveEvent(self, event):
        """Handle window move event to reposition notifications."""
        super().moveEvent(event)
        # Reposition notifications when window moves
        self.notification_manager.reposition_notifications()
    
    def resizeEvent(self, event):
        """Handle window resize event to reposition notifications."""
        super().resizeEvent(event)
        # Reposition notifications when window resizes
        self.notification_manager.reposition_notifications()
        # Keep language overlay full-screen over the central area
        try:
            if hasattr(self, "_lang_overlay") and self._lang_overlay.isVisible():
                r = self.rect()
                self._lang_overlay.setGeometry(0, 0, r.width(), r.height())
        except Exception:
            pass
    
    def closeEvent(self, event):
        """Handle application close event."""
        # Clear all notifications before closing
        self.notification_manager.clear_all()
        
        # Save settings
        self.settings_manager.save_settings()
        event.accept()

    # ---------------- Internal logging helper ----------------
    def _log_operations(self, kind: str, successes: list, errors: list, conflicts: list) -> None:
        """Append rename/undo results to the configured log file when logging is enabled."""
        try:
            if not bool(self.settings_manager.get("log_operations", False)):
                return
            log_path = self.settings_manager.get("log_file", "bulk_renamer.log")
            # Resolve relative log path
            if not os.path.isabs(log_path):
                log_path = os.path.abspath(log_path)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            lines = []
            lines.append(f"[{timestamp}] {kind} summary: {len(successes)} successes, {len(errors)} errors, {len(conflicts)} conflicts\n")
            if successes:
                lines.append("  Successes:\n")
                for op in successes[:200]:  # avoid giant logs
                    lines.append(f"    {op.get('old_path')} -> {op.get('new_path')}\n")
                if len(successes) > 200:
                    lines.append(f"    ... ({len(successes)-200} more)\n")
            if errors:
                lines.append("  Errors:\n")
                for e in errors[:200]:
                    lines.append(f"    {e}\n")
                if len(errors) > 200:
                    lines.append(f"    ... ({len(errors)-200} more)\n")
            if conflicts:
                lines.append("  Conflicts:\n")
                for c in conflicts[:200]:
                    lines.append(f"    {c}\n")
                if len(conflicts) > 200:
                    lines.append(f"    ... ({len(conflicts)-200} more)\n")
            with open(log_path, "a", encoding="utf-8") as f:
                f.writelines(lines)
        except Exception:
            # Swallow logging errors to avoid disrupting UX
            pass
    
    def test_notifications(self):
        """Test method to verify notifications work."""
        from PySide6.QtCore import QTimer
        
        # Test different notification types
        QTimer.singleShot(1000, lambda: self.notification_manager.show_notification("Test success notification", "success"))
        QTimer.singleShot(2000, lambda: self.notification_manager.show_notification("Test error notification", "error"))
        QTimer.singleShot(3000, lambda: self.notification_manager.show_notification("Test warning notification", "warning"))
        QTimer.singleShot(4000, lambda: self.notification_manager.show_notification("Test info notification", "info"))
