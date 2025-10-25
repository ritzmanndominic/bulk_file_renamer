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

from PySide6.QtWidgets import QMenuBar
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Qt
from app.utils.translation_manager import get_translation_manager


class MenuBar(QMenuBar):
    """Custom menu bar for the application."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tr_manager = get_translation_manager()
        self.connection_callbacks = {}  # Store connection callbacks
        self.setup_menus()
    
    def setup_menus(self):
        """Setup all menus and actions."""
        # File Menu
        file_menu = self.addMenu(self.tr_manager.tr("app.menu.file"))
        
        # New Profile
        new_profile_action = QAction(self.tr_manager.tr("app.menu.new_profile"), self)
        new_profile_action.setShortcut(QKeySequence("Ctrl+N"))
        new_profile_action.setStatusTip("Create a new rename profile")
        file_menu.addAction(new_profile_action)
        
        file_menu.addSeparator()
        
        # Save Profile
        save_profile_action = QAction(self.tr_manager.get_menu_text("save_profile"), self)
        save_profile_action.setShortcut(QKeySequence("Ctrl+S"))
        save_profile_action.setStatusTip("Save current settings as a profile")
        file_menu.addAction(save_profile_action)
        
        # Load Profile
        load_profile_action = QAction(self.tr_manager.get_menu_text("load_profile"), self)
        load_profile_action.setShortcut(QKeySequence("Ctrl+L"))
        load_profile_action.setStatusTip("Load a saved profile")
        file_menu.addAction(load_profile_action)
        
        file_menu.addSeparator()
        
        # Recent Profiles submenu
        recent_profiles_menu = file_menu.addMenu(self.tr_manager.get_menu_text("recent_profiles"))
        self.recent_profiles_menu = recent_profiles_menu
        
        file_menu.addSeparator()
        
        # Open Folder (added to align with tests expecting this action)
        open_folder_action = QAction(self.tr_manager.tr("main.browse_folder"), self)
        open_folder_action.setShortcut(QKeySequence("Ctrl+O"))
        open_folder_action.setStatusTip("Open a folder and add files")
        file_menu.addAction(open_folder_action)

        # Select Files (added to align with tests)
        select_files_action = QAction(self.tr_manager.tr("main.select_files"), self)
        select_files_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        select_files_action.setStatusTip("Select files to add")
        file_menu.addAction(select_files_action)

        file_menu.addSeparator()

        # Exit
        exit_action = QAction(self.tr_manager.get_menu_text("exit"), self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.setStatusTip("Exit the application")
        file_menu.addAction(exit_action)
        
        # Edit Menu
        edit_menu = self.addMenu(self.tr_manager.get_menu_text("edit"))
        
        # Undo
        undo_action = QAction(self.tr_manager.get_menu_text("undo"), self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.setStatusTip("Undo the last rename operation")
        edit_menu.addAction(undo_action)
        
        edit_menu.addSeparator()
        
        # Clear All
        clear_all_action = QAction(self.tr_manager.get_menu_text("clear_all"), self)
        clear_all_action.setShortcut(QKeySequence("Ctrl+Shift+C"))
        clear_all_action.setStatusTip("Clear all selected files")
        edit_menu.addAction(clear_all_action)
        
        # View Menu
        view_menu = self.addMenu(self.tr_manager.get_menu_text("view"))
        
        # Refresh Preview
        refresh_action = QAction(self.tr_manager.get_menu_text("refresh"), self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.setStatusTip("Refresh the file preview")
        view_menu.addAction(refresh_action)
        
        view_menu.addSeparator()
        
        # Show/Hide File Count
        self.toggle_file_count_action = QAction(self.tr_manager.get_menu_text("show_file_count"), self)
        self.toggle_file_count_action.setCheckable(True)
        self.toggle_file_count_action.setChecked(True)
        self.toggle_file_count_action.setShortcut(QKeySequence("Ctrl+F"))
        self.toggle_file_count_action.setStatusTip("Toggle file count display")
        view_menu.addAction(self.toggle_file_count_action)
        
        # Show/Hide History
        self.toggle_history_action = QAction(self.tr_manager.get_menu_text("show_history"), self)
        self.toggle_history_action.setCheckable(True)
        self.toggle_history_action.setChecked(True)
        self.toggle_history_action.setShortcut(QKeySequence("Ctrl+H"))
        self.toggle_history_action.setStatusTip("Toggle history panel display")
        view_menu.addAction(self.toggle_history_action)
        
        
        # Tools Menu
        tools_menu = self.addMenu(self.tr_manager.get_menu_text("tools"))
        
        # Batch Rename
        batch_rename_action = QAction(self.tr_manager.get_menu_text("batch_rename"), self)
        batch_rename_action.setShortcut(QKeySequence("Ctrl+R"))
        batch_rename_action.setStatusTip("Start batch rename operation")
        tools_menu.addAction(batch_rename_action)
        
        tools_menu.addSeparator()
        
        # Validate Names
        validate_action = QAction(self.tr_manager.get_menu_text("validate_names"), self)
        validate_action.setShortcut(QKeySequence("Ctrl+V"))
        validate_action.setStatusTip("Check for invalid file names")
        tools_menu.addAction(validate_action)
        
        # Preview Changes (removed - not needed)
        # preview_action = QAction(self.tr_manager.get_menu_text("preview_changes"), self)
        # preview_action.setShortcut(QKeySequence("Ctrl+P"))
        # preview_action.setStatusTip("Preview all changes before applying")
        # tools_menu.addAction(preview_action)
        
        # Help Menu
        help_menu = self.addMenu(self.tr_manager.get_menu_text("help"))
        
        # User Guide
        user_guide_action = QAction(self.tr_manager.get_menu_text("user_guide"), self)
        user_guide_action.setShortcut(QKeySequence("F1"))
        user_guide_action.setStatusTip("Open user guide")
        help_menu.addAction(user_guide_action)
        
        # Keyboard Shortcuts
        shortcuts_action = QAction(self.tr_manager.get_menu_text("keyboard_shortcuts"), self)
        shortcuts_action.setShortcut(QKeySequence("Ctrl+?"))
        shortcuts_action.setStatusTip("Show keyboard shortcuts")
        help_menu.addAction(shortcuts_action)
        
        help_menu.addSeparator()
        
        # Legal items
        eula_action = QAction(self.tr_manager.tr("legal.eula_title"), self)
        privacy_action = QAction(self.tr_manager.tr("legal.privacy_title"), self)
        terms_text = self.tr_manager.tr("legal.terms_title").replace("&", "&&")
        terms_action = QAction(terms_text, self)
        help_menu.addSeparator()
        help_menu.addAction(eula_action)
        help_menu.addAction(privacy_action)
        help_menu.addAction(terms_action)

        # About (ensure visible on macOS by using AboutRole)
        about_action = QAction(self.tr_manager.get_menu_text("about"), self)
        about_action.setStatusTip("About Bulk File Renamer")
        try:
            # This moves the action to the application menu on macOS
            about_action.setMenuRole(QAction.AboutRole)
        except Exception:
            pass
        help_menu.addAction(about_action)
        
        # Store actions for external access
        self.actions = {
            'open_folder': open_folder_action,
            'select_files': select_files_action,
            'new_profile': new_profile_action,
            'save_profile': save_profile_action,
            'load_profile': load_profile_action,
            'exit': exit_action,
            'undo': undo_action,
            'clear_all': clear_all_action,
            'refresh': refresh_action,
            'toggle_file_count': self.toggle_file_count_action,
            'toggle_history': self.toggle_history_action,
            'batch_rename': batch_rename_action,
            'validate': validate_action,
            'user_guide': user_guide_action,
            'shortcuts': shortcuts_action,
            'about': about_action
        }
        # Expose legal entries
        self.actions['eula'] = eula_action
        self.actions['privacy'] = privacy_action
        self.actions['terms'] = terms_action
    
    
    def update_recent_profiles(self, profiles):
        """Update recent profiles menu."""
        self.recent_profiles_menu.clear()
        
        if not profiles:
            no_profiles_action = QAction("No recent profiles", self)
            no_profiles_action.setEnabled(False)
            self.recent_profiles_menu.addAction(no_profiles_action)
        else:
            for profile in profiles[:10]:  # Limit to 10 recent items
                profile_action = QAction(profile, self)
                profile_action.triggered.connect(lambda checked, p=profile: self.load_recent_profile(p))
                self.recent_profiles_menu.addAction(profile_action)
    
    
    def load_recent_profile(self, profile_name):
        """Load a recent profile."""
        # This will be connected to the main app's load_profile method
        if hasattr(self, 'recent_profile_callback'):
            self.recent_profile_callback(profile_name)
    
    def set_recent_callbacks(self, profile_callback):
        """Set callbacks for recent items."""
        self.recent_profile_callback = profile_callback
    
    def set_connection_callbacks(self, callbacks):
        """Store connection callbacks for reconnecting after language change."""
        self.connection_callbacks = callbacks
    
    def update_language(self):
        """Update all menu text with current language."""
        # Clear and rebuild menus with new language
        self.clear()
        self.setup_menus()
        
        # Reconnect all actions if callbacks are stored
        if self.connection_callbacks:
            for action_name, callback in self.connection_callbacks.items():
                if action_name in self.actions:
                    self.actions[action_name].triggered.connect(callback)
