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

import json
import os
from typing import Dict, Any
from datetime import datetime


class SettingsManager:
    """Manages application settings with persistence."""
    
    def __init__(self, settings_file: str = None):
        if settings_file is None:
            # Use user's AppData directory for settings
            import sys
            if sys.platform == "win32":
                appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
                settings_dir = os.path.join(appdata, 'BulkFileRenamer')
                os.makedirs(settings_dir, exist_ok=True)
                self.settings_file = os.path.join(settings_dir, 'settings.json')
            else:
                # For macOS/Linux, use user's home directory
                settings_dir = os.path.join(os.path.expanduser('~'), '.bulk_file_renamer')
                os.makedirs(settings_dir, exist_ok=True)
                self.settings_file = os.path.join(settings_dir, 'settings.json')
        else:
            self.settings_file = settings_file
        self.default_settings = {
            # Preview Settings
            "preview_auto_refresh": True,
            "auto_resolve_conflicts": False,
            
            # Default Naming
            "default_prefix": "",
            "default_suffix": "",
            "default_base_name": "",
            "default_start_number": 1,
            
            # UI Settings
            # "theme": "Light",  # Light or Dark - No default, must be set by installer
            "show_tooltips": True,
            "confirm_before_rename": True,
            "show_file_count": True,
            
            # File Operations
            "backup_before_rename": False,
            "backup_location": "backups/",
            "overwrite_existing": False,
            "create_backup_folder": False,
            
            # Advanced Settings
            "case_sensitive_sorting": True,
            "preserve_file_attributes": True,
            "log_operations": False,
            "log_file": "bulk_renamer.log",
            # "language": "en",  # No default, must be set by installer
            
            # Recent Files/Folders
            "recent_folders": [],
            "recent_profiles": [],
            "max_recent_items": 10,
            
            # History
            "history_file": None,  # Will be set to user data directory
            
            # Metadata
            "_metadata": {
                "version": "1.0",
                "last_updated": datetime.now().isoformat()
            }
        }
        # Set history file path to user data directory
        if self.default_settings["history_file"] is None:
            import sys
            if sys.platform == "win32":
                appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
                history_dir = os.path.join(appdata, 'BulkFileRenamer')
                os.makedirs(history_dir, exist_ok=True)
                self.default_settings["history_file"] = os.path.join(history_dir, 'history.json')
            else:
                history_dir = os.path.join(os.path.expanduser('~'), '.bulk_file_renamer')
                os.makedirs(history_dir, exist_ok=True)
                self.default_settings["history_file"] = os.path.join(history_dir, 'history.json')
        
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file or return defaults."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # Merge with defaults to handle new settings
                settings = self.default_settings.copy()
                settings.update(loaded_settings)
                
                # Update metadata
                settings["_metadata"]["last_updated"] = datetime.now().isoformat()
                
                return settings
            else:
                return self.default_settings.copy()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.default_settings.copy()
    
    def save_settings(self) -> bool:
        """Save current settings to file."""
        try:
            # Create a copy without metadata for saving
            settings_to_save = {k: v for k, v in self.settings.items() if k != "_metadata"}
            settings_to_save["_metadata"] = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_to_save, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key: str, default=None):
        """Get a setting value."""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a setting value."""
        self.settings[key] = value
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        self.settings = self.default_settings.copy()
    
    def add_recent_folder(self, folder_path: str):
        """Add a folder to recent folders list."""
        recent = self.settings.get("recent_folders", [])
        if folder_path in recent:
            recent.remove(folder_path)
        recent.insert(0, folder_path)
        
        # Limit to max_recent_items
        max_items = self.settings.get("max_recent_items", 10)
        self.settings["recent_folders"] = recent[:max_items]
    
    def add_recent_profile(self, profile_name: str):
        """Add a profile to recent profiles list."""
        recent = self.settings.get("recent_profiles", [])
        if profile_name in recent:
            recent.remove(profile_name)
        recent.insert(0, profile_name)
        
        # Limit to max_recent_items
        max_items = self.settings.get("max_recent_items", 10)
        self.settings["recent_profiles"] = recent[:max_items]
