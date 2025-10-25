# Copyright (c) 2024 Dominic Ritzmann. All rights reserved.
# 
# This software is licensed under the Bulk File Renamer License.
# See LICENSE file for full license terms.

"""
Integration tests for the bulk file renamer application.
These tests verify that different components work together correctly.
"""

import os
import sys
import pytest
import tempfile
import shutil
from datetime import datetime, timedelta
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread

# Add the parent directory to the path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.bulk_renamer_app import BulkRenamerApp
from app.utils.generate_preview import generate_preview
from app.utils.name_cleaner import clean_filename
from app.utils.settings_manager import SettingsManager
from app.utils.profile_manager import ProfileManager
from app.workers.file_operation_worker import FileOperationWorker
from app.workers.file_add_worker import FileAddWorker


@pytest.fixture(scope="module")
def qt_app():
    """Ensure a QApplication exists for Qt-based tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_files(temp_dir):
    """Create test files in the temporary directory."""
    files = []
    for i in range(10):
        filename = f"test_file_{i:02d}.txt"
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write(f"Test content {i}")
        files.append(filepath)
    return files


class TestApplicationIntegration:
    """Test the main application integration."""

    def test_app_initialization_with_settings(self, qt_app, temp_dir):
        """Test that the app initializes correctly with settings."""
        # Create a temporary settings file
        settings_file = os.path.join(temp_dir, "test_settings.json")
        
        # Create app (this will use default settings)
        app = BulkRenamerApp()
        
        # Verify key components are initialized
        assert app.settings_manager is not None
        assert app.profile_manager is not None
        assert app.notification_manager is not None
        assert app.top_panel is not None
        assert app.tab_widget is not None

    def test_app_file_operations_workflow(self, qt_app, temp_dir, test_files):
        """Test the complete file operations workflow."""
        app = BulkRenamerApp()
        
        # Add files to the app
        app.selected_files = test_files[:5]  # Use first 5 files
        
        # Set up naming parameters
        app.top_panel.prefix_input.setText("renamed_")
        app.top_panel.suffix_input.setText("_final")
        app.top_panel.start_input.setText("1")
        
        # Generate preview
        preview_list = app.get_preview_list()
        
        # Verify preview was generated
        assert len(preview_list) == 5
        
        # Check that files are marked as "Ready"
        ready_files = [item for item in preview_list if item[2] == "Ready"]
        assert len(ready_files) == 5
        
        # Verify naming pattern
        for i, (old_name, new_name, status, file_path) in enumerate(preview_list):
            expected_name = f"renamed_test_file_{i:02d}_final.txt"
            assert new_name == expected_name
            assert status == "Ready"

    def test_app_profile_workflow(self, qt_app, temp_dir):
        """Test the complete profile workflow."""
        app = BulkRenamerApp()
        
        # Set up some settings
        app.top_panel.prefix_input.setText("profile_")
        app.top_panel.suffix_input.setText("_test")
        app.top_panel.base_input.setText("document")
        app.top_panel.start_input.setText("10")
        
        # Save profile
        profile_name = "Test Profile"
        settings = app.top_panel.get_current_settings()
        
        # Save using profile manager directly
        success = app.profile_manager.save_profile(profile_name, settings)
        assert success == True
        
        # Verify profile was saved
        assert app.profile_manager.profile_exists(profile_name)
        
        # Load profile
        loaded_settings = app.profile_manager.load_profile(profile_name)
        assert loaded_settings is not None
        assert loaded_settings["prefix"] == "profile_"
        assert loaded_settings["suffix"] == "_test"
        assert loaded_settings["base_name"] == "document"
        assert loaded_settings["start_num"] == "10"
        
        # Apply loaded settings
        app.top_panel.apply_settings(loaded_settings)
        
        # Verify settings were applied
        assert app.top_panel.prefix_input.text() == "profile_"
        assert app.top_panel.suffix_input.text() == "_test"
        assert app.top_panel.base_input.text() == "document"
        assert app.top_panel.start_input.text() == "10"

    def test_app_settings_persistence(self, qt_app, temp_dir):
        """Test that app settings persist correctly."""
        # Create a temporary settings file
        settings_file = os.path.join(temp_dir, "test_settings.json")
        
        # Create first app instance
        app1 = BulkRenamerApp()
        app1.settings_manager.settings_file = settings_file
        
        # Modify settings
        app1.settings_manager.set("show_tooltips", False)
        app1.settings_manager.set("confirm_before_rename", False)
        app1.settings_manager.save_settings()
        
        # Create second app instance
        app2 = BulkRenamerApp()
        app2.settings_manager.settings_file = settings_file
        
        # Verify settings were loaded
        assert app2.settings_manager.get("show_tooltips") == False
        assert app2.settings_manager.get("confirm_before_rename") == False

    def test_app_notification_system(self, qt_app):
        """Test the app's notification system."""
        app = BulkRenamerApp()
        
        # Test different notification types
        app.notification_manager.show_notification("Test success", "success")
        app.notification_manager.show_notification("Test error", "error")
        app.notification_manager.show_notification("Test warning", "warning")
        app.notification_manager.show_notification("Test info", "info")
        
        # Test clearing notifications
        app.notification_manager.clear_all()
        
        # Should complete without errors
        assert True


class TestPreviewGenerationIntegration:
    """Test preview generation with various combinations of settings."""

    def test_preview_with_all_filters(self, temp_dir):
        """Test preview generation with all filter types."""
        # Create files with different properties
        files = []
        
        # Create files with different extensions
        for ext in ['txt', 'jpg', 'pdf']:
            for i in range(3):
                filename = f"file_{i}.{ext}"
                filepath = os.path.join(temp_dir, filename)
                with open(filepath, 'w') as f:
                    f.write("content")
                files.append(filepath)
        
        # Create files with different sizes
        small_file = os.path.join(temp_dir, "small.txt")
        with open(small_file, 'w') as f:
            f.write("x")  # 1 byte
        
        large_file = os.path.join(temp_dir, "large.txt")
        with open(large_file, 'w') as f:
            f.write("x" * 1000)  # 1000 bytes
        
        files.extend([small_file, large_file])
        
        # Create files with different dates
        old_file = os.path.join(temp_dir, "old.txt")
        with open(old_file, 'w') as f:
            f.write("old content")
        old_time = (datetime.now() - timedelta(days=365)).timestamp()
        os.utime(old_file, (old_time, old_time))
        files.append(old_file)
        
        # Test with extension filter
        preview_list, filtered_files = generate_preview(files, extensions=['txt'])
        assert len(preview_list) == 4  # 3 txt files + small.txt + large.txt
        
        # Test with size filter
        preview_list, filtered_files = generate_preview(files, size_filter=(">", 100))
        assert len(preview_list) == 1  # Only large.txt
        
        # Test with date filter
        six_months_ago = datetime.now() - timedelta(days=180)
        preview_list, filtered_files = generate_preview(files, date_filter=("before", six_months_ago))
        assert len(preview_list) == 1  # Only old.txt

    def test_preview_with_name_cleaning(self, temp_dir):
        """Test preview generation with name cleaning options."""
        # Create files with special characters
        files = []
        for i in range(3):
            filename = f"test@file#{i}.txt"
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write("content")
            files.append(filepath)
        
        # Test with name cleaning
        preview_list, filtered_files = generate_preview(
            files,
            prefix="new_",
            suffix="_clean",
            remove_special_chars=True,
            convert_case=True,
            case_type="lowercase"
        )
        
        assert len(preview_list) == 3
        
        for i, (old_name, new_name, status, file_path) in enumerate(preview_list):
            assert old_name == f"test@file#{i}.txt"
            assert new_name == f"new_testfile{i}_clean.txt"  # Special chars removed, lowercase
            assert status == "Ready"

    def test_preview_conflict_detection(self, temp_dir):
        """Test preview generation with conflict detection."""
        # Create files that will have naming conflicts
        files = []
        for i in range(3):
            filename = f"file_{i}.txt"
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write("content")
            files.append(filepath)
        
        # Use base name without start number (will create conflicts)
        preview_list, filtered_files = generate_preview(files, base_name="conflict")
        
        assert len(preview_list) == 3
        
        # All files should have the same new name, causing conflicts
        new_names = [item[1] for item in preview_list]
        assert all(name == "conflict.txt" for name in new_names)
        
        # All should be marked as conflicts
        statuses = [item[2] for item in preview_list]
        assert all(status == "Conflict" for status in statuses)

    def test_preview_extension_lock(self, temp_dir):
        """Test preview generation with extension lock."""
        files = []
        for i in range(3):
            filename = f"file_{i}.txt"
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write("content")
            files.append(filepath)
        
        # Test with extension lock enabled
        preview_list, filtered_files = generate_preview(
            files,
            base_name="renamed",
            start_num=1,
            extension_lock=True
        )
        
        assert len(preview_list) == 3
        
        for i, (old_name, new_name, status, file_path) in enumerate(preview_list):
            assert old_name == f"file_{i}.txt"
            assert new_name == f"renamed_{i+1}.txt"  # Extension preserved
            assert status == "Ready"


class TestWorkerIntegration:
    """Test worker classes integration."""

    def test_file_operation_worker_integration(self, temp_dir, test_files):
        """Test FileOperationWorker with real file operations."""
        # Create a simple rename operation
        old_path = test_files[0]
        new_path = os.path.join(temp_dir, "renamed_file.txt")
        
        file_ops = [{"old_path": old_path, "new_path": new_path, "action": "rename"}]
        worker = FileOperationWorker(file_ops)
        
        # Connect signals to capture results
        successes = []
        errors = []
        conflicts = []
        
        def on_finished(s, e, c):
            successes.extend(s)
            errors.extend(e)
            conflicts.extend(c)
        
        worker.finished.connect(on_finished)
        worker.start()
        worker.wait()
        
        # Verify the operation succeeded
        assert len(successes) == 1
        assert len(errors) == 0
        assert len(conflicts) == 0
        assert os.path.exists(new_path)
        assert not os.path.exists(old_path)

    def test_file_add_worker_integration(self, temp_dir):
        """Test FileAddWorker with real file operations."""
        # Create test files
        test_files = []
        for i in range(3):
            filename = f"add_test_{i}.txt"
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write(f"content {i}")
            test_files.append(filepath)
        
        # Create a subdirectory with files
        subdir = os.path.join(temp_dir, "subdir")
        os.makedirs(subdir)
        for i in range(2):
            filename = f"subdir_file_{i}.txt"
            filepath = os.path.join(subdir, filename)
            with open(filepath, 'w') as f:
                f.write(f"subdir content {i}")
            test_files.append(filepath)
        
        # Test adding files
        worker = FileAddWorker(test_files)
        
        added_files = []
        duplicate_count = 0
        
        def on_finished(files, duplicates):
            added_files.extend(files)
            nonlocal duplicate_count
            duplicate_count = duplicates
        
        worker.finished.connect(on_finished)
        worker.start()
        worker.wait()
        
        # Verify all files were added
        assert len(added_files) == 5  # 3 files + 2 from subdirectory
        assert duplicate_count == 0

    def test_worker_progress_signals(self, temp_dir, test_files):
        """Test that worker progress signals work correctly."""
        # Test FileOperationWorker progress
        file_ops = []
        for i, old_path in enumerate(test_files[:3]):
            new_path = os.path.join(temp_dir, f"progress_test_{i}.txt")
            file_ops.append({"old_path": old_path, "new_path": new_path, "action": "rename"})
        
        worker = FileOperationWorker(file_ops)
        
        progress_values = []
        
        def on_progress(value):
            progress_values.append(value)
        
        worker.progress.connect(on_progress)
        worker.start()
        worker.wait()
        
        # Should have progress values
        assert len(progress_values) > 0
        assert progress_values[-1] == 100  # Final progress should be 100%


class TestSettingsProfileIntegration:
    """Test integration between settings and profile management."""

    def test_settings_profile_workflow(self, temp_dir):
        """Test the complete settings and profile workflow."""
        # Create temporary directories
        settings_file = os.path.join(temp_dir, "test_settings.json")
        profiles_dir = os.path.join(temp_dir, "profiles")
        
        # Create managers
        settings_manager = SettingsManager(settings_file)
        profile_manager = ProfileManager(profiles_dir)
        
        # Modify settings
        settings_manager.set("show_tooltips", False)
        settings_manager.set("confirm_before_rename", False)
        settings_manager.add_recent_folder("/test/folder")
        settings_manager.add_recent_profile("Test Profile")
        
        # Save settings
        assert settings_manager.save_settings() == True
        
        # Create a profile with current settings
        profile_data = {
            "prefix": "profile_",
            "suffix": "_test",
            "base_name": "document",
            "start_num": "1",
            "extension_lock": True
        }
        
        # Save profile
        assert profile_manager.save_profile("Test Profile", profile_data) == True
        
        # Verify profile was saved
        assert profile_manager.profile_exists("Test Profile")
        
        # Load profile
        loaded_profile = profile_manager.load_profile("Test Profile")
        assert loaded_profile is not None
        assert loaded_profile["prefix"] == "profile_"
        
        # Create new managers to test persistence
        new_settings_manager = SettingsManager(settings_file)
        new_profile_manager = ProfileManager(profiles_dir)
        
        # Verify settings persisted
        assert new_settings_manager.get("show_tooltips") == False
        assert new_settings_manager.get("confirm_before_rename") == False
        assert "/test/folder" in new_settings_manager.get("recent_folders")
        assert "Test Profile" in new_settings_manager.get("recent_profiles")
        
        # Verify profile persisted
        assert new_profile_manager.profile_exists("Test Profile")
        loaded_profile = new_profile_manager.load_profile("Test Profile")
        assert loaded_profile["prefix"] == "profile_"

    def test_settings_defaults_handling(self, temp_dir):
        """Test that settings defaults are handled correctly."""
        settings_file = os.path.join(temp_dir, "test_settings.json")
        
        # Create settings manager
        settings_manager = SettingsManager(settings_file)
        
        # Verify default values
        assert settings_manager.get("preview_auto_refresh") == True
        assert settings_manager.get("show_tooltips") == True
        assert settings_manager.get("confirm_before_rename") == True
        assert settings_manager.get("default_prefix") == ""
        assert settings_manager.get("default_suffix") == ""
        assert settings_manager.get("default_base_name") == ""
        assert settings_manager.get("default_start_number") == 1
        
        # Modify some settings
        settings_manager.set("show_tooltips", False)
        settings_manager.set("custom_setting", "custom_value")
        
        # Save and reload
        settings_manager.save_settings()
        new_settings_manager = SettingsManager(settings_file)
        
        # Verify modified settings
        assert new_settings_manager.get("show_tooltips") == False
        assert new_settings_manager.get("custom_setting") == "custom_value"
        
        # Verify defaults are still there
        assert new_settings_manager.get("preview_auto_refresh") == True
        assert new_settings_manager.get("confirm_before_rename") == True


class TestErrorHandlingIntegration:
    """Test error handling across different components."""

    def test_preview_generation_error_handling(self, temp_dir):
        """Test that preview generation handles errors gracefully."""
        # Test with nonexistent files
        nonexistent_files = [
            os.path.join(temp_dir, "nonexistent1.txt"),
            os.path.join(temp_dir, "nonexistent2.txt")
        ]
        
        preview_list, filtered_files = generate_preview(nonexistent_files)
        
        # Should return empty lists without crashing
        assert len(preview_list) == 0
        assert len(filtered_files) == 0
        
        # Test with mixed existing and nonexistent files
        # Create one real file
        real_file = os.path.join(temp_dir, "real_file.txt")
        with open(real_file, 'w') as f:
            f.write("content")
        
        mixed_files = [real_file] + nonexistent_files
        
        preview_list, filtered_files = generate_preview(mixed_files)
        
        # Should only process the real file
        assert len(preview_list) == 1
        assert len(filtered_files) == 1

    def test_worker_error_handling(self, temp_dir):
        """Test that workers handle errors gracefully."""
        # Test FileOperationWorker with nonexistent file
        nonexistent_file = os.path.join(temp_dir, "nonexistent.txt")
        new_path = os.path.join(temp_dir, "new_name.txt")
        
        file_ops = [{"old_path": nonexistent_file, "new_path": new_path, "action": "rename"}]
        worker = FileOperationWorker(file_ops)
        
        successes = []
        errors = []
        conflicts = []
        
        def on_finished(s, e, c):
            successes.extend(s)
            errors.extend(e)
            conflicts.extend(c)
        
        worker.finished.connect(on_finished)
        worker.start()
        worker.wait()
        
        # Should have an error, no successes
        assert len(successes) == 0
        assert len(errors) == 1
        assert len(conflicts) == 0
        assert "Failed:" in errors[0]

    def test_settings_error_handling(self, temp_dir):
        """Test that settings manager handles errors gracefully."""
        # Test with invalid file path
        invalid_path = "/nonexistent/directory/settings.json"
        settings_manager = SettingsManager(invalid_path)
        
        # Should still work with defaults
        assert settings_manager.get("preview_auto_refresh") == True
        
        # Save should fail gracefully
        result = settings_manager.save_settings()
        assert result == False

    def test_profile_error_handling(self, temp_dir):
        """Test that profile manager handles errors gracefully."""
        # Test with invalid directory
        invalid_dir = "/nonexistent/directory"
        profile_manager = ProfileManager(invalid_dir)
        
        # Operations should fail gracefully
        result = profile_manager.save_profile("test", {"data": "value"})
        assert result == False
        
        loaded = profile_manager.load_profile("test")
        assert loaded is None
        
        profiles = profile_manager.list_profiles()
        assert profiles == []
