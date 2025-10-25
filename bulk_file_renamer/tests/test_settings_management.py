# Copyright (c) 2024 Dominic Ritzmann. All rights reserved.
# 
# This software is licensed under the Bulk File Renamer License.
# See LICENSE file for full license terms.

"""
Tests for settings management functionality.
"""

import os
import sys
import pytest
import tempfile
import json
from datetime import datetime

# Add the parent directory to the path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.settings_manager import SettingsManager


class TestSettingsManager:
    """Test the SettingsManager class."""

    @pytest.fixture
    def temp_settings_file(self):
        """Create a temporary settings file for testing."""
        temp_dir = tempfile.mkdtemp()
        settings_file = os.path.join(temp_dir, "test_settings.json")
        yield settings_file
        # Cleanup is handled by tempfile

    def test_settings_manager_initialization_default(self):
        """Test SettingsManager initialization with default settings file."""
        manager = SettingsManager()
        
        # Should have default settings
        assert manager.get("preview_auto_refresh") == True
        assert manager.get("show_tooltips") == True
        assert manager.get("confirm_before_rename") == True
        assert manager.get("default_prefix") == ""
        assert manager.get("default_suffix") == ""
        assert manager.get("default_base_name") == ""
        assert manager.get("default_start_number") == 1

    def test_settings_manager_initialization_custom_file(self, temp_settings_file):
        """Test SettingsManager initialization with custom settings file."""
        manager = SettingsManager(temp_settings_file)
        
        assert manager.settings_file == temp_settings_file
        assert manager.get("preview_auto_refresh") == True

    def test_load_settings_new_file(self, temp_settings_file):
        """Test loading settings from a new (nonexistent) file."""
        manager = SettingsManager(temp_settings_file)
        
        # Should return default settings
        assert manager.get("preview_auto_refresh") == True
        assert manager.get("show_tooltips") == True

    def test_load_settings_existing_file(self, temp_settings_file):
        """Test loading settings from an existing file."""
        # Create a settings file with custom values
        custom_settings = {
            "preview_auto_refresh": False,
            "show_tooltips": False,
            "custom_setting": "custom_value"
        }
        
        with open(temp_settings_file, 'w') as f:
            json.dump(custom_settings, f)
        
        manager = SettingsManager(temp_settings_file)
        
        # Should load custom settings
        assert manager.get("preview_auto_refresh") == False
        assert manager.get("show_tooltips") == False
        assert manager.get("custom_setting") == "custom_value"
        
        # Should still have defaults for missing settings
        assert manager.get("confirm_before_rename") == True

    def test_load_settings_corrupted_file(self, temp_settings_file):
        """Test loading settings from a corrupted file."""
        # Create a corrupted JSON file
        with open(temp_settings_file, 'w') as f:
            f.write("invalid json content")
        
        manager = SettingsManager(temp_settings_file)
        
        # Should fall back to default settings
        assert manager.get("preview_auto_refresh") == True
        assert manager.get("show_tooltips") == True

    def test_save_settings(self, temp_settings_file):
        """Test saving settings to file."""
        manager = SettingsManager(temp_settings_file)
        
        # Modify some settings
        manager.set("preview_auto_refresh", False)
        manager.set("show_tooltips", False)
        manager.set("custom_setting", "test_value")
        
        # Save settings
        result = manager.save_settings()
        assert result == True
        
        # Verify file was created
        assert os.path.exists(temp_settings_file)
        
        # Load settings in a new manager to verify persistence
        new_manager = SettingsManager(temp_settings_file)
        assert new_manager.get("preview_auto_refresh") == False
        assert new_manager.get("show_tooltips") == False
        assert new_manager.get("custom_setting") == "test_value"

    def test_save_settings_error(self):
        """Test saving settings with invalid file path."""
        # Use a path that should cause an error (e.g., in a non-existent directory)
        invalid_path = "/nonexistent/directory/settings.json"
        manager = SettingsManager(invalid_path)
        
        manager.set("test_setting", "test_value")
        result = manager.save_settings()
        
        # Should return False due to error
        assert result == False

    def test_get_setting_existing(self, temp_settings_file):
        """Test getting an existing setting."""
        manager = SettingsManager(temp_settings_file)
        
        value = manager.get("preview_auto_refresh")
        assert value == True

    def test_get_setting_nonexistent(self, temp_settings_file):
        """Test getting a nonexistent setting."""
        manager = SettingsManager(temp_settings_file)
        
        value = manager.get("nonexistent_setting")
        assert value is None

    def test_get_setting_with_default(self, temp_settings_file):
        """Test getting a setting with a default value."""
        manager = SettingsManager(temp_settings_file)
        
        value = manager.get("nonexistent_setting", "default_value")
        assert value == "default_value"

    def test_set_setting(self, temp_settings_file):
        """Test setting a value."""
        manager = SettingsManager(temp_settings_file)
        
        manager.set("test_setting", "test_value")
        assert manager.get("test_setting") == "test_value"

    def test_set_setting_overwrite(self, temp_settings_file):
        """Test overwriting an existing setting."""
        manager = SettingsManager(temp_settings_file)
        
        # Set initial value
        manager.set("test_setting", "initial_value")
        assert manager.get("test_setting") == "initial_value"
        
        # Overwrite with new value
        manager.set("test_setting", "new_value")
        assert manager.get("test_setting") == "new_value"

    def test_reset_to_defaults(self, temp_settings_file):
        """Test resetting settings to defaults."""
        manager = SettingsManager(temp_settings_file)
        
        # Modify some settings
        manager.set("preview_auto_refresh", False)
        manager.set("show_tooltips", False)
        manager.set("custom_setting", "test_value")
        
        # Reset to defaults
        manager.reset_to_defaults()
        
        # Should be back to default values
        assert manager.get("preview_auto_refresh") == True
        assert manager.get("show_tooltips") == True
        assert manager.get("custom_setting") is None

    def test_add_recent_folder(self, temp_settings_file):
        """Test adding a folder to recent folders list."""
        manager = SettingsManager(temp_settings_file)
        
        # Add a folder
        manager.add_recent_folder("/test/folder1")
        
        recent_folders = manager.get("recent_folders")
        assert len(recent_folders) == 1
        assert recent_folders[0] == "/test/folder1"

    def test_add_recent_folder_duplicate(self, temp_settings_file):
        """Test adding a duplicate folder (should move to front)."""
        manager = SettingsManager(temp_settings_file)
        
        # Add folders
        manager.add_recent_folder("/test/folder1")
        manager.add_recent_folder("/test/folder2")
        manager.add_recent_folder("/test/folder1")  # Duplicate
        
        recent_folders = manager.get("recent_folders")
        assert len(recent_folders) == 2
        assert recent_folders[0] == "/test/folder1"  # Should be first
        assert recent_folders[1] == "/test/folder2"

    def test_add_recent_folder_limit(self, temp_settings_file):
        """Test that recent folders are limited to max_recent_items."""
        manager = SettingsManager(temp_settings_file)
        
        # Set a small limit for testing
        manager.set("max_recent_items", 3)
        
        # Add more folders than the limit
        for i in range(5):
            manager.add_recent_folder(f"/test/folder{i}")
        
        recent_folders = manager.get("recent_folders")
        assert len(recent_folders) == 3
        assert recent_folders[0] == "/test/folder4"  # Most recent first

    def test_add_recent_profile(self, temp_settings_file):
        """Test adding a profile to recent profiles list."""
        manager = SettingsManager(temp_settings_file)
        
        # Add a profile
        manager.add_recent_profile("Test Profile")
        
        recent_profiles = manager.get("recent_profiles")
        assert len(recent_profiles) == 1
        assert recent_profiles[0] == "Test Profile"

    def test_add_recent_profile_duplicate(self, temp_settings_file):
        """Test adding a duplicate profile (should move to front)."""
        manager = SettingsManager(temp_settings_file)
        
        # Add profiles
        manager.add_recent_profile("Profile 1")
        manager.add_recent_profile("Profile 2")
        manager.add_recent_profile("Profile 1")  # Duplicate
        
        recent_profiles = manager.get("recent_profiles")
        assert len(recent_profiles) == 2
        assert recent_profiles[0] == "Profile 1"  # Should be first
        assert recent_profiles[1] == "Profile 2"

    def test_add_recent_profile_limit(self, temp_settings_file):
        """Test that recent profiles are limited to max_recent_items."""
        manager = SettingsManager(temp_settings_file)
        
        # Set a small limit for testing
        manager.set("max_recent_items", 3)
        
        # Add more profiles than the limit
        for i in range(5):
            manager.add_recent_profile(f"Profile {i}")
        
        recent_profiles = manager.get("recent_profiles")
        assert len(recent_profiles) == 3
        assert recent_profiles[0] == "Profile 4"  # Most recent first

    def test_default_settings_structure(self, temp_settings_file):
        """Test that default settings have the expected structure."""
        manager = SettingsManager(temp_settings_file)
        
        # Check preview settings
        assert "preview_auto_refresh" in manager.settings
        assert "auto_resolve_conflicts" in manager.settings
        
        # Check default naming
        assert "default_prefix" in manager.settings
        assert "default_suffix" in manager.settings
        assert "default_base_name" in manager.settings
        assert "default_start_number" in manager.settings
        
        # Check UI settings
        assert "show_tooltips" in manager.settings
        assert "confirm_before_rename" in manager.settings
        assert "show_file_count" in manager.settings
        
        # Check file operations
        assert "backup_before_rename" in manager.settings
        assert "backup_location" in manager.settings
        assert "overwrite_existing" in manager.settings
        assert "create_backup_folder" in manager.settings
        
        # Check advanced settings
        assert "case_sensitive_sorting" in manager.settings
        assert "preserve_file_attributes" in manager.settings
        assert "log_operations" in manager.settings
        assert "log_file" in manager.settings
        
        # Check recent items
        assert "recent_folders" in manager.settings
        assert "recent_profiles" in manager.settings
        assert "max_recent_items" in manager.settings
        
        # Check history
        assert "history_file" in manager.settings
        
        # Check metadata
        assert "_metadata" in manager.settings
        assert "version" in manager.settings["_metadata"]
        assert "last_updated" in manager.settings["_metadata"]

    def test_metadata_handling(self, temp_settings_file):
        """Test that metadata is handled correctly."""
        manager = SettingsManager(temp_settings_file)
        
        # Check that metadata exists
        metadata = manager.get("_metadata")
        assert metadata is not None
        assert "version" in metadata
        assert "last_updated" in metadata
        
        # Check that metadata is not saved in the file
        manager.save_settings()
        
        with open(temp_settings_file, 'r') as f:
            saved_data = json.load(f)
        
        # Metadata should be in saved data
        assert "_metadata" in saved_data
        assert "version" in saved_data["_metadata"]
        assert "last_updated" in saved_data["_metadata"]

    def test_settings_persistence(self, temp_settings_file):
        """Test that settings persist across manager instances."""
        # Create first manager and modify settings
        manager1 = SettingsManager(temp_settings_file)
        manager1.set("test_setting", "persistent_value")
        manager1.set("preview_auto_refresh", False)
        manager1.save_settings()
        
        # Create second manager and verify settings
        manager2 = SettingsManager(temp_settings_file)
        assert manager2.get("test_setting") == "persistent_value"
        assert manager2.get("preview_auto_refresh") == False

    def test_settings_merge_with_defaults(self, temp_settings_file):
        """Test that loaded settings are merged with defaults."""
        # Create a settings file with only some settings
        partial_settings = {
            "preview_auto_refresh": False,
            "custom_setting": "custom_value"
        }
        
        with open(temp_settings_file, 'w') as f:
            json.dump(partial_settings, f)
        
        manager = SettingsManager(temp_settings_file)
        
        # Should have the custom settings
        assert manager.get("preview_auto_refresh") == False
        assert manager.get("custom_setting") == "custom_value"
        
        # Should also have default settings for missing keys
        assert manager.get("show_tooltips") == True
        assert manager.get("confirm_before_rename") == True
        assert manager.get("default_prefix") == ""

    def test_settings_file_creation(self, temp_settings_file):
        """Test that settings file is created when saving."""
        # Ensure file doesn't exist
        assert not os.path.exists(temp_settings_file)
        
        manager = SettingsManager(temp_settings_file)
        manager.set("test_setting", "test_value")
        manager.save_settings()
        
        # File should now exist
        assert os.path.exists(temp_settings_file)
        
        # Should contain the setting
        with open(temp_settings_file, 'r') as f:
            data = json.load(f)
        assert data["test_setting"] == "test_value"

    def test_settings_types(self, temp_settings_file):
        """Test that different data types are handled correctly."""
        manager = SettingsManager(temp_settings_file)
        
        # Test different types
        manager.set("string_setting", "test_string")
        manager.set("int_setting", 42)
        manager.set("float_setting", 3.14)
        manager.set("bool_setting", True)
        manager.set("list_setting", [1, 2, 3])
        manager.set("dict_setting", {"key": "value"})
        
        manager.save_settings()
        
        # Verify types are preserved
        assert manager.get("string_setting") == "test_string"
        assert manager.get("int_setting") == 42
        assert manager.get("float_setting") == 3.14
        assert manager.get("bool_setting") == True
        assert manager.get("list_setting") == [1, 2, 3]
        assert manager.get("dict_setting") == {"key": "value"}

    def test_history_file_path_generation(self, temp_settings_file):
        """Test that history file path is generated correctly."""
        manager = SettingsManager(temp_settings_file)
        
        history_file = manager.get("history_file")
        assert history_file is not None
        assert isinstance(history_file, str)
        assert history_file.endswith("history.json")
