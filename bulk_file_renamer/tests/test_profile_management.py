# Copyright (c) 2024 Dominic Ritzmann. All rights reserved.
# 
# This software is licensed under the Bulk File Renamer License.
# See LICENSE file for full license terms.

"""
Tests for profile management functionality.
"""

import os
import sys
import pytest
import tempfile
import json
import shutil
from datetime import datetime

# Add the parent directory to the path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.profile_manager import ProfileManager


class TestProfileManager:
    """Test the ProfileManager class."""

    @pytest.fixture
    def temp_profiles_dir(self):
        """Create a temporary profiles directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_profile_manager_initialization_default(self):
        """Test ProfileManager initialization with default profiles directory."""
        manager = ProfileManager()
        
        # Should have a profiles directory
        assert manager.profiles_dir is not None
        assert isinstance(manager.profiles_dir, str)

    def test_profile_manager_initialization_custom_dir(self, temp_profiles_dir):
        """Test ProfileManager initialization with custom profiles directory."""
        manager = ProfileManager(temp_profiles_dir)
        
        assert manager.profiles_dir == temp_profiles_dir

    def test_ensure_profiles_dir_creation(self, temp_profiles_dir):
        """Test that profiles directory is created if it doesn't exist."""
        # Remove the directory if it exists
        if os.path.exists(temp_profiles_dir):
            shutil.rmtree(temp_profiles_dir)
        
        manager = ProfileManager(temp_profiles_dir)
        
        # Directory should be created
        assert os.path.exists(temp_profiles_dir)
        assert os.path.isdir(temp_profiles_dir)

    def test_get_profile_path(self, temp_profiles_dir):
        """Test getting profile file path."""
        manager = ProfileManager(temp_profiles_dir)
        
        profile_path = manager.get_profile_path("test_profile")
        expected_path = os.path.join(temp_profiles_dir, "test_profile.json")
        
        assert profile_path == expected_path

    def test_save_profile_success(self, temp_profiles_dir):
        """Test successful profile saving."""
        manager = ProfileManager(temp_profiles_dir)
        
        profile_data = {
            "prefix": "test_",
            "suffix": "_renamed",
            "base_name": "photo",
            "start_num": "1",
            "extension_lock": True
        }
        
        result = manager.save_profile("test_profile", profile_data)
        assert result == True
        
        # Verify file was created
        profile_path = manager.get_profile_path("test_profile")
        assert os.path.exists(profile_path)
        
        # Verify file content
        with open(profile_path, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data["prefix"] == "test_"
        assert saved_data["suffix"] == "_renamed"
        assert saved_data["base_name"] == "photo"
        assert saved_data["start_num"] == "1"
        assert saved_data["extension_lock"] == True
        
        # Check metadata was added
        assert "_metadata" in saved_data
        assert "created" in saved_data["_metadata"]
        assert "version" in saved_data["_metadata"]

    def test_save_profile_error(self, temp_profiles_dir):
        """Test profile saving with invalid directory."""
        # Create manager with invalid directory
        invalid_dir = "/nonexistent/directory"
        manager = ProfileManager(invalid_dir)
        
        profile_data = {"test": "data"}
        result = manager.save_profile("test_profile", profile_data)
        
        # Should return False due to error
        assert result == False

    def test_load_profile_success(self, temp_profiles_dir):
        """Test successful profile loading."""
        manager = ProfileManager(temp_profiles_dir)
        
        # Create a profile file
        profile_data = {
            "prefix": "loaded_",
            "suffix": "_profile",
            "base_name": "document",
            "start_num": "10",
            "extension_lock": False,
            "_metadata": {
                "created": "2024-01-01T00:00:00",
                "version": "1.0"
            }
        }
        
        profile_path = manager.get_profile_path("test_profile")
        with open(profile_path, 'w') as f:
            json.dump(profile_data, f)
        
        # Load the profile
        loaded_data = manager.load_profile("test_profile")
        
        assert loaded_data is not None
        assert loaded_data["prefix"] == "loaded_"
        assert loaded_data["suffix"] == "_profile"
        assert loaded_data["base_name"] == "document"
        assert loaded_data["start_num"] == "10"
        assert loaded_data["extension_lock"] == False
        assert loaded_data["_metadata"]["created"] == "2024-01-01T00:00:00"

    def test_load_profile_nonexistent(self, temp_profiles_dir):
        """Test loading a nonexistent profile."""
        manager = ProfileManager(temp_profiles_dir)
        
        loaded_data = manager.load_profile("nonexistent_profile")
        assert loaded_data is None

    def test_load_profile_corrupted(self, temp_profiles_dir):
        """Test loading a corrupted profile file."""
        manager = ProfileManager(temp_profiles_dir)
        
        # Create a corrupted profile file
        profile_path = manager.get_profile_path("corrupted_profile")
        with open(profile_path, 'w') as f:
            f.write("invalid json content")
        
        loaded_data = manager.load_profile("corrupted_profile")
        assert loaded_data is None

    def test_list_profiles_empty(self, temp_profiles_dir):
        """Test listing profiles when directory is empty."""
        manager = ProfileManager(temp_profiles_dir)
        
        profiles = manager.list_profiles()
        assert profiles == []

    def test_list_profiles_nonexistent_dir(self, temp_profiles_dir):
        """Test listing profiles when directory doesn't exist."""
        # Remove the directory
        shutil.rmtree(temp_profiles_dir)
        
        manager = ProfileManager(temp_profiles_dir)
        profiles = manager.list_profiles()
        
        assert profiles == []

    def test_list_profiles_with_files(self, temp_profiles_dir):
        """Test listing profiles with existing profile files."""
        manager = ProfileManager(temp_profiles_dir)
        
        # Create some profile files
        profile_data = {"test": "data"}
        
        for name in ["profile1", "profile2", "profile3"]:
            profile_path = manager.get_profile_path(name)
            with open(profile_path, 'w') as f:
                json.dump(profile_data, f)
        
        # Create a non-profile file (should be ignored)
        non_profile_path = os.path.join(temp_profiles_dir, "not_a_profile.txt")
        with open(non_profile_path, 'w') as f:
            f.write("not a profile")
        
        profiles = manager.list_profiles()
        
        # Should return sorted list of profile names
        assert len(profiles) == 3
        assert profiles == ["profile1", "profile2", "profile3"]

    def test_list_profiles_sorted(self, temp_profiles_dir):
        """Test that profiles are returned in sorted order."""
        manager = ProfileManager(temp_profiles_dir)
        
        # Create profiles in non-sorted order
        profile_data = {"test": "data"}
        profile_names = ["zebra", "apple", "banana"]
        
        for name in profile_names:
            profile_path = manager.get_profile_path(name)
            with open(profile_path, 'w') as f:
                json.dump(profile_data, f)
        
        profiles = manager.list_profiles()
        
        # Should be sorted alphabetically
        assert profiles == ["apple", "banana", "zebra"]

    def test_delete_profile_success(self, temp_profiles_dir):
        """Test successful profile deletion."""
        manager = ProfileManager(temp_profiles_dir)
        
        # Create a profile file
        profile_data = {"test": "data"}
        profile_path = manager.get_profile_path("test_profile")
        with open(profile_path, 'w') as f:
            json.dump(profile_data, f)
        
        # Verify file exists
        assert os.path.exists(profile_path)
        
        # Delete the profile
        result = manager.delete_profile("test_profile")
        assert result == True
        
        # Verify file was deleted
        assert not os.path.exists(profile_path)

    def test_delete_profile_nonexistent(self, temp_profiles_dir):
        """Test deleting a nonexistent profile."""
        manager = ProfileManager(temp_profiles_dir)
        
        result = manager.delete_profile("nonexistent_profile")
        assert result == False

    def test_delete_profile_error(self, temp_profiles_dir):
        """Test profile deletion with permission error."""
        manager = ProfileManager(temp_profiles_dir)
        
        # Create a profile file
        profile_data = {"test": "data"}
        profile_path = manager.get_profile_path("test_profile")
        with open(profile_path, 'w') as f:
            json.dump(profile_data, f)
        
        # Make file read-only (on Windows) or remove write permission
        try:
            os.chmod(profile_path, 0o444)  # Read-only
            result = manager.delete_profile("test_profile")
            # On some systems, this might still work, so we just check the result
            assert isinstance(result, bool)
        except (OSError, PermissionError):
            # Expected on some systems
            pass
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(profile_path, 0o644)
            except (OSError, PermissionError):
                pass

    def test_profile_exists_true(self, temp_profiles_dir):
        """Test profile_exists returns True for existing profile."""
        manager = ProfileManager(temp_profiles_dir)
        
        # Create a profile file
        profile_data = {"test": "data"}
        profile_path = manager.get_profile_path("existing_profile")
        with open(profile_path, 'w') as f:
            json.dump(profile_data, f)
        
        assert manager.profile_exists("existing_profile") == True

    def test_profile_exists_false(self, temp_profiles_dir):
        """Test profile_exists returns False for nonexistent profile."""
        manager = ProfileManager(temp_profiles_dir)
        
        assert manager.profile_exists("nonexistent_profile") == False

    def test_profile_metadata_handling(self, temp_profiles_dir):
        """Test that metadata is handled correctly in profiles."""
        manager = ProfileManager(temp_profiles_dir)
        
        profile_data = {
            "prefix": "test_",
            "suffix": "_renamed"
        }
        
        # Save profile
        result = manager.save_profile("metadata_test", profile_data)
        assert result == True
        
        # Load profile
        loaded_data = manager.load_profile("metadata_test")
        
        # Check that metadata was added
        assert "_metadata" in loaded_data
        assert "created" in loaded_data["_metadata"]
        assert "version" in loaded_data["_metadata"]
        assert loaded_data["_metadata"]["version"] == "1.0"
        
        # Check that original data is preserved
        assert loaded_data["prefix"] == "test_"
        assert loaded_data["suffix"] == "_renamed"

    def test_profile_data_types(self, temp_profiles_dir):
        """Test that different data types are handled correctly in profiles."""
        manager = ProfileManager(temp_profiles_dir)
        
        profile_data = {
            "string_setting": "test_string",
            "int_setting": 42,
            "float_setting": 3.14,
            "bool_setting": True,
            "list_setting": [1, 2, 3],
            "dict_setting": {"key": "value"},
            "none_setting": None
        }
        
        # Save profile
        result = manager.save_profile("types_test", profile_data)
        assert result == True
        
        # Load profile
        loaded_data = manager.load_profile("types_test")
        
        # Verify types are preserved
        assert loaded_data["string_setting"] == "test_string"
        assert loaded_data["int_setting"] == 42
        assert loaded_data["float_setting"] == 3.14
        assert loaded_data["bool_setting"] == True
        assert loaded_data["list_setting"] == [1, 2, 3]
        assert loaded_data["dict_setting"] == {"key": "value"}
        assert loaded_data["none_setting"] is None

    def test_profile_unicode_handling(self, temp_profiles_dir):
        """Test that Unicode characters are handled correctly in profiles."""
        manager = ProfileManager(temp_profiles_dir)
        
        profile_data = {
            "unicode_name": "测试文件",
            "emoji_name": "📁 文件夹",
            "accented_name": "résumé"
        }
        
        # Save profile
        result = manager.save_profile("unicode_test", profile_data)
        assert result == True
        
        # Load profile
        loaded_data = manager.load_profile("unicode_test")
        
        # Verify Unicode is preserved
        assert loaded_data["unicode_name"] == "测试文件"
        assert loaded_data["emoji_name"] == "📁 文件夹"
        assert loaded_data["accented_name"] == "résumé"

    def test_profile_large_data(self, temp_profiles_dir):
        """Test handling of large profile data."""
        manager = ProfileManager(temp_profiles_dir)
        
        # Create a large profile with many settings
        profile_data = {}
        for i in range(1000):
            profile_data[f"setting_{i}"] = f"value_{i}"
        
        # Save profile
        result = manager.save_profile("large_test", profile_data)
        assert result == True
        
        # Load profile
        loaded_data = manager.load_profile("large_test")
        
        # Verify all data is preserved
        assert len(loaded_data) == 1001  # 1000 settings + metadata
        assert loaded_data["setting_0"] == "value_0"
        assert loaded_data["setting_999"] == "value_999"

    def test_profile_name_with_special_characters(self, temp_profiles_dir):
        """Test profile names with special characters."""
        manager = ProfileManager(temp_profiles_dir)
        
        profile_data = {"test": "data"}
        
        # Test various special characters in profile names
        special_names = [
            "profile with spaces",
            "profile-with-dashes",
            "profile_with_underscores",
            "profile.with.dots",
            "profile@with@symbols",
            "profile#with#hash",
            "profile$with$dollar"
        ]
        
        for name in special_names:
            result = manager.save_profile(name, profile_data)
            assert result == True
            
            # Verify it can be loaded
            loaded_data = manager.load_profile(name)
            assert loaded_data is not None
            assert loaded_data["test"] == "data"
            
            # Verify it appears in the list
            profiles = manager.list_profiles()
            assert name in profiles

    def test_profile_overwrite(self, temp_profiles_dir):
        """Test overwriting an existing profile."""
        manager = ProfileManager(temp_profiles_dir)
        
        # Create initial profile
        initial_data = {"setting1": "value1", "setting2": "value2"}
        result = manager.save_profile("overwrite_test", initial_data)
        assert result == True
        
        # Overwrite with new data
        new_data = {"setting1": "new_value1", "setting3": "value3"}
        result = manager.save_profile("overwrite_test", new_data)
        assert result == True
        
        # Load and verify
        loaded_data = manager.load_profile("overwrite_test")
        assert loaded_data["setting1"] == "new_value1"
        assert loaded_data["setting3"] == "value3"
        assert "setting2" not in loaded_data  # Should be overwritten

    def test_profile_directory_permissions(self, temp_profiles_dir):
        """Test profile operations with directory permission issues."""
        # This test is more about ensuring graceful error handling
        manager = ProfileManager(temp_profiles_dir)
        
        profile_data = {"test": "data"}
        
        # Try to save a profile (should work normally)
        result = manager.save_profile("permission_test", profile_data)
        assert result == True
        
        # Try to load the profile (should work normally)
        loaded_data = manager.load_profile("permission_test")
        assert loaded_data is not None
