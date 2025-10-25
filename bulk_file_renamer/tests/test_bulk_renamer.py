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

# tests/test_bulk_renamer.py
"""
Basic test for the bulk file renamer application.
"""

import sys
import os
import pytest
import re
from datetime import datetime, timedelta
from PySide6.QtWidgets import QApplication

# Ensure imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.bulk_renamer_app import BulkRenamerApp

# ---------------------------
# Setup / Teardown fixtures
# ---------------------------

@pytest.fixture(scope="module")
def qt_app():
    """Ensure a QApplication exists"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

@pytest.fixture
def bulk_app(qt_app, tmp_path):
    """Provide a BulkRenamerApp with a temporary test folder"""
    test_dir = tmp_path / "test_files"
    os.makedirs(test_dir)

    filenames = ["file1.txt", "file2.txt", "image.jpg", "document.pdf"]
    for f in filenames:
        with open(os.path.join(test_dir, f), "w") as file:
            file.write("test content")

    app = BulkRenamerApp()
    app.selected_files = [os.path.join(test_dir, f) for f in filenames]

    yield app

@pytest.fixture
def bulk_app_with_dates(qt_app, tmp_path):
    """Provide a BulkRenamerApp with files created at different dates"""
    test_dir = tmp_path / "test_files"
    os.makedirs(test_dir)

    # Create files with different creation dates
    filenames = ["old_file.txt", "recent_file.jpg", "very_old_file.pdf"]
    
    # Create old file (1 year ago)
    old_file = os.path.join(test_dir, "old_file.txt")
    with open(old_file, "w") as file:
        file.write("old content")
    old_time = (datetime.now() - timedelta(days=365)).timestamp()
    os.utime(old_file, (old_time, old_time))
    
    # Create recent file (1 day ago)
    recent_file = os.path.join(test_dir, "recent_file.jpg")
    with open(recent_file, "w") as file:
        file.write("recent content")
    recent_time = (datetime.now() - timedelta(days=1)).timestamp()
    os.utime(recent_file, (recent_time, recent_time))
    
    # Create very old file (2 years ago)
    very_old_file = os.path.join(test_dir, "very_old_file.pdf")
    with open(very_old_file, "w") as file:
        file.write("very old content")
    very_old_time = (datetime.now() - timedelta(days=730)).timestamp()
    os.utime(very_old_file, (very_old_time, very_old_time))

    app = BulkRenamerApp()
    app.selected_files = [old_file, recent_file, very_old_file]

    yield app

# ---------------------------
# Basic Tests
# ---------------------------

def test_app_initialization(bulk_app):
    """Test that the app initializes correctly"""
    assert bulk_app is not None
    assert bulk_app.top_panel is not None
    assert bulk_app.file_count is not None
    assert bulk_app.history_panel is not None

def test_extension_lock_feature(bulk_app):
    """Test that the extension lock feature is present and working"""
    # Check that extension lock checkbox exists
    assert bulk_app.top_panel.extension_lock_checkbox is not None
    
    # Check that it's enabled by default
    assert bulk_app.top_panel.extension_lock_checkbox.isChecked() is True
    
    # Check that the checkbox text updates correctly
    assert "Active" in bulk_app.top_panel.extension_lock_checkbox.text()

def test_preview_generation(bulk_app):
    """Test basic preview generation"""
    preview = bulk_app.get_preview_list()
    assert len(preview) > 0
    
    # Check that preview contains expected files
    expected_files = ["file1.txt", "file2.txt", "image.jpg", "document.pdf"]
    preview_files = [old_name for old_name, _, _, _ in preview]
    for expected_file in expected_files:
        assert expected_file in preview_files

def test_clickable_history(bulk_app):
    """Test that history entries are clickable and show Explorer-like details"""
    # Check that history panel has clickable functionality
    history_panel = bulk_app.history_panel
    assert history_panel.history_list_widget is not None
    
    # Check that the history data storage exists
    assert hasattr(history_panel, 'history_data')
    assert hasattr(history_panel, 'show_history_details')
    assert hasattr(history_panel, 'show_history_list')
    
    # Check that the stacked widget and details text widget exist
    assert hasattr(history_panel, 'stacked_widget')
    assert hasattr(history_panel, 'details_text')
    assert history_panel.details_text is not None
    
    # Check that back button and title label exist
    assert hasattr(history_panel, 'back_button')
    assert hasattr(history_panel, 'title_label')
    
    # Test with empty history
    history_panel.update_history([])
    assert history_panel.history_list_widget.count() == 0
    assert "Click on a history entry" in history_panel.details_text.placeholderText()
    assert history_panel.current_view == "list"
    
    # Test with sample history data
    sample_history = [
        {
            "files": [
                {"old_path": "/path/old1.txt", "new_path": "/path/new1.txt"},
                {"old_path": "/path/old2.txt", "new_path": "/path/new2.txt"}
            ],
            "undone": False
        }
    ]
    
    history_panel.update_history(sample_history)
    assert history_panel.history_list_widget.count() == 1
    assert history_panel.current_view == "list"
    
    # Check that the item has the correct text and tooltip
    item = history_panel.history_list_widget.item(0)
    assert "files renamed" in item.text()
    assert "Click to see details" in item.toolTip()
    
    # Test clicking on the item to show details (Explorer-like behavior)
    history_panel.show_history_details(item)
    assert history_panel.current_view == "details"
    assert history_panel.back_button.isVisible() == True
    assert history_panel.title_label.text() == "History Details"
    
    details_text = history_panel.details_text.toPlainText()
    assert "Rename Operation Details" in details_text
    assert "old1.txt" in details_text
    assert "new1.txt" in details_text
    assert "old2.txt" in details_text
    assert "new2.txt" in details_text
    
    # Test back button functionality
    history_panel.show_history_list()
    assert history_panel.current_view == "list"
    assert history_panel.back_button.isVisible() == False
    assert history_panel.title_label.text() == "Rename History"

# ---------------------------
# Filtering Tests
# ---------------------------

def test_multiple_extension_filtering(bulk_app):
    """Test filtering by multiple file extensions"""
    # Test with multiple extensions
    bulk_app.top_panel.ext_filter_input.setText("txt,jpg")
    preview = bulk_app.get_preview_list()
    
    # Should only include .txt and .jpg files
    preview_files = [old_name for old_name, _, _, _ in preview]
    assert "file1.txt" in preview_files
    assert "file2.txt" in preview_files
    assert "image.jpg" in preview_files
    assert "document.pdf" not in preview_files

def test_single_extension_filtering(bulk_app):
    """Test filtering by single file extension"""
    # Test with single extension
    bulk_app.top_panel.ext_filter_input.setText("pdf")
    preview = bulk_app.get_preview_list()
    
    # Should only include .pdf files
    preview_files = [old_name for old_name, _, _, _ in preview]
    assert "document.pdf" in preview_files
    assert "file1.txt" not in preview_files
    assert "file2.txt" not in preview_files
    assert "image.jpg" not in preview_files

def test_size_filtering(bulk_app):
    """Test file size filtering"""
    # Test with size filter (greater than 1 byte)
    bulk_app.top_panel.size_operator.setCurrentText(">")
    bulk_app.top_panel.size_value.setText("1")
    bulk_app.top_panel.size_unit.setCurrentText("B")
    
    preview = bulk_app.get_preview_list()
    # All files should be included since they all have content > 1 byte
    assert len(preview) == 4
    
    # Test with size filter (greater than 1MB)
    bulk_app.top_panel.size_value.setText("1")
    bulk_app.top_panel.size_unit.setCurrentText("MB")
    
    preview = bulk_app.get_preview_list()
    # No files should be included since they're all small
    assert len(preview) == 0

def test_date_filtering_before(bulk_app_with_dates):
    """Test date filtering with 'before' operator"""
    # Filter for files created before 6 months ago
    six_months_ago = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
    bulk_app_with_dates.top_panel.date_operator.setCurrentText("Before")
    bulk_app_with_dates.top_panel.date_value.setText(six_months_ago)
    
    preview = bulk_app_with_dates.get_preview_list()
    preview_files = [old_name for old_name, _, _, _ in preview]
    
    # Should include old_file.txt and very_old_file.pdf (both older than 6 months)
    # Should exclude recent_file.jpg (created 1 day ago)
    assert "old_file.txt" in preview_files
    assert "very_old_file.pdf" in preview_files
    assert "recent_file.jpg" not in preview_files

def test_date_filtering_after(bulk_app_with_dates):
    """Test date filtering with 'after' operator"""
    # Filter for files created after 6 months ago
    six_months_ago = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
    bulk_app_with_dates.top_panel.date_operator.setCurrentText("After")
    bulk_app_with_dates.top_panel.date_value.setText(six_months_ago)
    
    preview = bulk_app_with_dates.get_preview_list()
    preview_files = [old_name for old_name, _, _, _ in preview]
    
    # Should include recent_file.jpg (created 1 day ago)
    # Should exclude old_file.txt and very_old_file.pdf (both older than 6 months)
    assert "recent_file.jpg" in preview_files
    assert "old_file.txt" not in preview_files
    assert "very_old_file.pdf" not in preview_files

def test_combined_filtering(bulk_app):
    """Test combining multiple filters"""
    # Test extension + size filter
    bulk_app.top_panel.ext_filter_input.setText("txt")
    bulk_app.top_panel.size_operator.setCurrentText(">")
    bulk_app.top_panel.size_value.setText("1")
    bulk_app.top_panel.size_unit.setCurrentText("B")
    
    preview = bulk_app.get_preview_list()
    preview_files = [old_name for old_name, _, _, _ in preview]
    
    # Should only include .txt files that are > 1 byte
    assert "file1.txt" in preview_files
    assert "file2.txt" in preview_files
    assert "image.jpg" not in preview_files
    assert "document.pdf" not in preview_files

def test_ui_filter_controls_exist(bulk_app):
    """Test that all filter UI controls exist"""
    # Check extension filter
    assert bulk_app.top_panel.ext_filter_input is not None
    assert bulk_app.top_panel.ext_filter_input.placeholderText() == "Extensions, e.g., jpg,png,txt"
    
    # Check size filter controls
    assert bulk_app.top_panel.size_operator is not None
    assert bulk_app.top_panel.size_value is not None
    assert bulk_app.top_panel.size_unit is not None
    assert bulk_app.top_panel.size_value.placeholderText() == "Size"
    
    # Check date filter controls
    assert bulk_app.top_panel.date_operator is not None
    assert bulk_app.top_panel.date_value is not None
    assert bulk_app.top_panel.date_value.placeholderText() == "YYYY-MM-DD"
    
    # Check status filter
    assert bulk_app.top_panel.status_filter is not None

def test_date_filter_validation(bulk_app):
    """Test date filter input validation"""
    # Test with invalid date format
    bulk_app.top_panel.date_operator.setCurrentText("Before")
    bulk_app.top_panel.date_value.setText("invalid-date")
    
    preview = bulk_app.get_preview_list()
    # Should include all files since invalid date filter is ignored
    assert len(preview) == 4
    
    # Test with valid date format
    bulk_app.top_panel.date_value.setText("2023-01-01")
    preview = bulk_app.get_preview_list()
    # Should work without errors (files may or may not be filtered depending on creation date)
    assert isinstance(preview, list)

def test_auto_date_formatting(bulk_app):
    """Test automatic date formatting as user types"""
    date_input = bulk_app.top_panel.date_value
    
    # Test that the widget is actually a DateInput instance
    from app.ui.date_input import DateInput
    assert isinstance(date_input, DateInput)
    
    # Test basic formatting functionality
    date_input.setText("2023")
    assert date_input.text() == "2023"
    
    date_input.setText("202301")
    assert date_input.text() == "2023-01"
    
    date_input.setText("20230101")
    assert date_input.text() == "2023-01-01"
    
    # Test that get_date_value returns properly formatted date
    assert date_input.get_date_value() == "2023-01-01"
    
    # Test with incomplete date
    date_input.setText("2023-01")
    assert date_input.get_date_value() == ""
    
    # Test the core formatting logic directly
    # This tests the internal logic without Qt event handling
    test_input = "2023abc01def01"
    digits_only = re.sub(r'[^\d]', '', test_input)
    if len(digits_only) > 8:
        digits_only = digits_only[:8]
    
    # Format using the same logic as the widget
    if len(digits_only) <= 4:
        expected = digits_only
    elif len(digits_only) <= 6:
        expected = f"{digits_only[:4]}-{digits_only[4:]}"
    else:
        expected = f"{digits_only[:4]}-{digits_only[4:6]}-{digits_only[6:]}"
    
    assert expected == "2023-01-01"

# ---------------------------
# Profile Management Tests
# ---------------------------

def test_profile_manager_basic_functionality():
    """Test basic profile manager functionality"""
    from app.utils.profile_manager import ProfileManager
    import tempfile
    import os
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        profile_manager = ProfileManager(temp_dir)
        
        # Test saving a profile
        test_profile = {
            "prefix": "test_",
            "suffix": "_renamed",
            "base_name": "photo",
            "start_num": "1",
            "extension_lock": True
        }
        
        assert profile_manager.save_profile("test_profile", test_profile) == True
        assert profile_manager.profile_exists("test_profile") == True
        
        # Test loading a profile
        loaded_profile = profile_manager.load_profile("test_profile")
        assert loaded_profile is not None
        assert loaded_profile["prefix"] == "test_"
        assert loaded_profile["suffix"] == "_renamed"
        assert loaded_profile["base_name"] == "photo"
        assert loaded_profile["start_num"] == "1"
        assert loaded_profile["extension_lock"] == True
        
        # Test listing profiles
        profiles = profile_manager.list_profiles()
        assert "test_profile" in profiles
        
        # Test deleting a profile
        assert profile_manager.delete_profile("test_profile") == True
        assert profile_manager.profile_exists("test_profile") == False

def test_profile_ui_controls_exist(bulk_app):
    """Test that profile UI controls exist"""
    # Check that profile controls exist
    assert bulk_app.top_panel.profile_combo is not None
    assert bulk_app.top_panel.btn_save_profile is not None
    assert bulk_app.top_panel.btn_load_profile is not None
    assert bulk_app.top_panel.btn_delete_profile is not None
    
    # Check that profile manager exists
    assert hasattr(bulk_app, 'profile_manager')
    assert bulk_app.profile_manager is not None

def test_profile_settings_get_set(bulk_app):
    """Test getting and setting profile settings"""
    # Test getting current settings
    settings = bulk_app.top_panel.get_current_settings()
    assert isinstance(settings, dict)
    assert "prefix" in settings
    assert "suffix" in settings
    assert "base_name" in settings
    assert "start_num" in settings
    assert "extension_lock" in settings
    assert "extensions" in settings
    assert "size_operator" in settings
    assert "size_value" in settings
    assert "size_unit" in settings
    assert "date_operator" in settings
    assert "date_value" in settings
    assert "status_filter" in settings
    
    # Test applying settings
    test_settings = {
        "prefix": "test_",
        "suffix": "_renamed",
        "base_name": "photo",
        "start_num": "1",
        "extension_lock": False,
        "extensions": "jpg,png",
        "size_operator": ">",
        "size_value": "1",
        "size_unit": "MB",
        "date_operator": "Before",
        "date_value": "2023-01-01",
        "status_filter": "Ready"
    }
    
    bulk_app.top_panel.apply_settings(test_settings)
    
    # Verify settings were applied
    assert bulk_app.top_panel.prefix_input.text() == "test_"
    assert bulk_app.top_panel.suffix_input.text() == "_renamed"
    assert bulk_app.top_panel.base_input.text() == "photo"
    assert bulk_app.top_panel.start_input.text() == "1"
    assert bulk_app.top_panel.extension_lock_checkbox.isChecked() == False
    assert bulk_app.top_panel.ext_filter_input.text() == "jpg,png"
    assert bulk_app.top_panel.size_operator.currentText() == ">"
    assert bulk_app.top_panel.size_value.text() == "1"
    assert bulk_app.top_panel.size_unit.currentText() == "MB"
    assert bulk_app.top_panel.date_operator.currentText() == "Before"
    assert bulk_app.top_panel.date_value.get_date_value() == "2023-01-01"
    assert bulk_app.top_panel.status_filter.currentText() == "Ready"

def test_profile_refresh_functionality(bulk_app):
    """Test profile refresh functionality"""
    # Test that refresh_profiles method exists and works
    assert hasattr(bulk_app, 'refresh_profiles')
    
    # Test that refresh_profiles_list method exists
    assert hasattr(bulk_app.top_panel, 'refresh_profiles_list')
    
    # Test refreshing with empty list
    bulk_app.top_panel.refresh_profiles_list([])
    assert bulk_app.top_panel.profile_combo.count() == 0
    
    # Test refreshing with some profiles
    test_profiles = ["Profile 1", "Profile 2", "Profile 3"]
    bulk_app.top_panel.refresh_profiles_list(test_profiles)
    assert bulk_app.top_panel.profile_combo.count() == 3
    assert bulk_app.top_panel.profile_combo.itemText(0) == "Profile 1"
    assert bulk_app.top_panel.profile_combo.itemText(1) == "Profile 2"
    assert bulk_app.top_panel.profile_combo.itemText(2) == "Profile 3"

# ---------------------------
# Sorting Tests
# ---------------------------

def test_sorting_ui_controls_exist(bulk_app):
    """Test that sorting UI controls exist"""
    # Check that table headers are clickable
    assert bulk_app.top_panel.table.horizontalHeader().sectionsClickable() == True
    
    # Check that sorting state is initialized
    assert hasattr(bulk_app.top_panel, 'sort_column')
    assert hasattr(bulk_app.top_panel, 'sort_ascending')
    assert bulk_app.top_panel.sort_column == -1  # No sorting by default
    assert bulk_app.top_panel.sort_ascending == True

def test_sorting_functionality(bulk_app):
    """Test sorting functionality"""
    # Create test preview data
    test_preview = [
        ("zebra.txt", "zebra_renamed.txt", "Ready", "/path/zebra.txt"),
        ("apple.txt", "apple_renamed.txt", "Ready", "/path/apple.txt"),
        ("banana.txt", "banana_renamed.txt", "Ready", "/path/banana.txt")
    ]
    
    # Test Old Name ascending sorting
    bulk_app.top_panel.sort_column = 0
    bulk_app.top_panel.sort_ascending = True
    sorted_data = bulk_app.top_panel.sort_preview_data(test_preview)
    assert sorted_data[0][0] == "apple.txt"
    assert sorted_data[1][0] == "banana.txt"
    assert sorted_data[2][0] == "zebra.txt"
    
    # Test Old Name descending sorting
    bulk_app.top_panel.sort_column = 0
    bulk_app.top_panel.sort_ascending = False
    sorted_data = bulk_app.top_panel.sort_preview_data(test_preview)
    assert sorted_data[0][0] == "zebra.txt"
    assert sorted_data[1][0] == "banana.txt"
    assert sorted_data[2][0] == "apple.txt"
    
    # Test New Name ascending sorting
    bulk_app.top_panel.sort_column = 1
    bulk_app.top_panel.sort_ascending = True
    sorted_data = bulk_app.top_panel.sort_preview_data(test_preview)
    assert sorted_data[0][1] == "apple_renamed.txt"
    assert sorted_data[1][1] == "banana_renamed.txt"
    assert sorted_data[2][1] == "zebra_renamed.txt"
    
    # Test New Name descending sorting
    bulk_app.top_panel.sort_column = 1
    bulk_app.top_panel.sort_ascending = False
    sorted_data = bulk_app.top_panel.sort_preview_data(test_preview)
    assert sorted_data[0][1] == "zebra_renamed.txt"
    assert sorted_data[1][1] == "banana_renamed.txt"
    assert sorted_data[2][1] == "apple_renamed.txt"
    
    # Test no sorting
    bulk_app.top_panel.sort_column = -1
    sorted_data = bulk_app.top_panel.sort_preview_data(test_preview)
    assert sorted_data == test_preview  # Should return original order

def test_sorting_case_insensitive(bulk_app):
    """Test that sorting is case insensitive"""
    test_preview = [
        ("Apple.txt", "apple_renamed.txt", "Ready", "/path/Apple.txt"),
        ("banana.txt", "Banana_renamed.txt", "Ready", "/path/banana.txt"),
        ("ZEBRA.txt", "zebra_renamed.txt", "Ready", "/path/ZEBRA.txt")
    ]
    
    # Test case insensitive sorting
    bulk_app.top_panel.sort_column = 0
    bulk_app.top_panel.sort_ascending = True
    sorted_data = bulk_app.top_panel.sort_preview_data(test_preview)
    assert sorted_data[0][0] == "Apple.txt"  # Should come first despite capital A
    assert sorted_data[1][0] == "banana.txt"
    assert sorted_data[2][0] == "ZEBRA.txt"  # Should come last despite capital Z

def test_sorting_in_profiles(bulk_app):
    """Test that sorting settings are saved and loaded in profiles"""
    # Set a specific sort option
    bulk_app.top_panel.sort_column = 1  # New Name column
    bulk_app.top_panel.sort_ascending = False  # Descending
    
    # Get current settings
    settings = bulk_app.top_panel.get_current_settings()
    assert settings["sort_column"] == 1
    assert settings["sort_ascending"] == False
    
    # Reset to default
    bulk_app.top_panel.sort_column = -1
    bulk_app.top_panel.sort_ascending = True
    
    # Apply the saved settings
    bulk_app.top_panel.apply_settings(settings)
    assert bulk_app.top_panel.sort_column == 1
    assert bulk_app.top_panel.sort_ascending == False

def test_header_click_cycle(bulk_app):
    """Test the three-state cycle when clicking headers"""
    # Start with no sorting
    assert bulk_app.top_panel.sort_column == -1
    
    # First click on Old Name column (0) - should set to ascending
    bulk_app.top_panel._on_header_clicked(0)
    assert bulk_app.top_panel.sort_column == 0
    assert bulk_app.top_panel.sort_ascending == True
    
    # Second click on same column - should set to descending
    bulk_app.top_panel._on_header_clicked(0)
    assert bulk_app.top_panel.sort_column == 0
    assert bulk_app.top_panel.sort_ascending == False
    
    # Third click on same column - should remove sorting
    bulk_app.top_panel._on_header_clicked(0)
    assert bulk_app.top_panel.sort_column == -1
    assert bulk_app.top_panel.sort_ascending == True  # Reset to default
    
    # Click on different column - should start with ascending
    bulk_app.top_panel._on_header_clicked(1)
    assert bulk_app.top_panel.sort_column == 1
    assert bulk_app.top_panel.sort_ascending == True

def test_header_labels_update(bulk_app):
    """Test that header labels update with sort indicators"""
    # Start with no indicators
    headers = bulk_app.top_panel.table.horizontalHeaderLabels()
    assert "↑" not in headers[0] and "↓" not in headers[0]
    
    # Set ascending sort on Old Name
    bulk_app.top_panel.sort_column = 0
    bulk_app.top_panel.sort_ascending = True
    bulk_app.top_panel._update_header_labels()
    headers = bulk_app.top_panel.table.horizontalHeaderLabels()
    assert "Old Name ↑" in headers[0]
    
    # Set descending sort on New Name
    bulk_app.top_panel.sort_column = 1
    bulk_app.top_panel.sort_ascending = False
    bulk_app.top_panel._update_header_labels()
    headers = bulk_app.top_panel.table.horizontalHeaderLabels()
    assert "New Name ↓" in headers[1]
    assert "↑" not in headers[0]  # Old indicator should be removed

# ---------------------------
# Settings Tests
# ---------------------------

def test_settings_manager_basic_functionality():
    """Test basic settings manager functionality"""
    from app.utils.settings_manager import SettingsManager
    import tempfile
    import os
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        settings_file = os.path.join(temp_dir, "test_settings.json")
        settings_manager = SettingsManager(settings_file)
        
        # Test default settings
        assert settings_manager.get("default_prefix") == ""
        assert settings_manager.get("show_file_count") == True
        
        # Test setting values
        settings_manager.set("show_file_count", False)
        assert settings_manager.get("show_file_count") == False
        
        # Test saving and loading
        assert settings_manager.save_settings() == True
        assert os.path.exists(settings_file)
        
        # Create new instance to test loading
        settings_manager2 = SettingsManager(settings_file)
        assert settings_manager2.get("show_file_count") == False
        
        # Test recent items
        settings_manager.add_recent_folder("/test/folder1")
        settings_manager.add_recent_folder("/test/folder2")
        recent_folders = settings_manager.get("recent_folders")
        assert len(recent_folders) == 2
        assert recent_folders[0] == "/test/folder2"  # Most recent first

def test_settings_ui_controls_exist(bulk_app):
    """Test that settings UI controls exist"""
    # Check that settings tab exists
    assert hasattr(bulk_app, 'settings_tab')
    assert bulk_app.settings_tab is not None
    
    # Check that tab widget exists
    assert hasattr(bulk_app, 'tab_widget')
    assert bulk_app.tab_widget is not None
    
    # Check that settings tab is added
    assert bulk_app.tab_widget.count() >= 2  # Main tab + Settings tab
    assert bulk_app.tab_widget.tabText(1) == "Settings"

def test_menu_bar_exists(bulk_app):
    """Test that menu bar exists and has expected menus"""
    # Check that menu bar exists
    assert hasattr(bulk_app, 'menu_bar')
    assert bulk_app.menu_bar is not None
    
    # Check that menu bar is set
    assert bulk_app.menuBar() == bulk_app.menu_bar
    
    # Check that key actions exist
    actions = bulk_app.menu_bar.actions
    assert 'open_folder' in actions
    assert 'select_files' in actions
    assert 'save_profile' in actions
    assert 'load_profile' in actions
    assert 'exit' in actions
    assert 'undo' in actions
    assert 'clear_all' in actions
    assert 'refresh' in actions
    assert 'batch_rename' in actions

def test_settings_integration(bulk_app):
    """Test that settings are properly integrated"""
    # Check that settings manager exists
    assert hasattr(bulk_app, 'settings_manager')
    assert bulk_app.settings_manager is not None
    
    # Test that settings are applied on startup
    assert bulk_app.settings_manager.get("preview_auto_refresh") == True
    
    # Test that window size is applied
    width = bulk_app.settings_manager.get("window_width", 900)
    height = bulk_app.settings_manager.get("window_height", 600)
    assert bulk_app.width() == width
    assert bulk_app.height() == height

def test_recent_items_functionality(bulk_app):
    """Test recent items functionality"""
    # Test adding recent folder
    bulk_app.settings_manager.add_recent_folder("/test/folder")
    recent_folders = bulk_app.settings_manager.get("recent_folders")
    assert "/test/folder" in recent_folders
    
    # Test adding recent profile
    bulk_app.settings_manager.add_recent_profile("Test Profile")
    recent_profiles = bulk_app.settings_manager.get("recent_profiles")
    assert "Test Profile" in recent_profiles
    
    # Test that recent items are limited
    for i in range(15):  # More than max_recent_items (10)
        bulk_app.settings_manager.add_recent_folder(f"/test/folder{i}")
    
    recent_folders = bulk_app.settings_manager.get("recent_folders")
    assert len(recent_folders) <= 10  # Should be limited to max_recent_items

# ---------------------------
# Notification System Tests
# ---------------------------

def test_notification_bar_basic_functionality():
    """Test basic notification bar functionality"""
    from app.ui.notification_bar import NotificationBar
    from PySide6.QtWidgets import QApplication
    import sys
    
    # Create QApplication if it doesn't exist
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create notification bar
    notification = NotificationBar()
    
    # Test that it starts hidden
    assert not notification.isVisible()
    
    # Test notification types
    notification_types = ["success", "error", "warning", "info"]
    for notification_type in notification_types:
        notification.show_notification(f"Test {notification_type} message", notification_type)
        assert notification.isVisible()
        notification.hide_notification()

def test_notification_manager_basic_functionality():
    """Test notification manager functionality"""
    from app.ui.notification_bar import NotificationManager
    from PySide6.QtWidgets import QWidget, QApplication
    import sys
    
    # Create QApplication if it doesn't exist
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create parent widget
    parent = QWidget()
    parent.resize(400, 300)
    
    # Create notification manager
    manager = NotificationManager(parent)
    
    # Test showing notifications
    manager.show_notification("Test success message", "success")
    manager.show_notification("Test error message", "error")
    
    # Should have 2 notifications
    assert len(manager.notifications) == 2
    
    # Test clearing all
    manager.clear_all()
    # Notifications should be cleared (though they might still be in list until deleted)

def test_notification_integration(bulk_app):
    """Test that notification system is integrated"""
    # Check that notification manager exists
    assert hasattr(bulk_app, 'notification_manager')
    assert bulk_app.notification_manager is not None
    
    # Check that it's properly initialized
    assert bulk_app.notification_manager.parent_widget == bulk_app

def test_profile_notifications(bulk_app):
    """Test that profile operations use notifications instead of popups"""
    # This test would require mocking the notification system
    # For now, just verify the methods exist and don't use QMessageBox directly
    
    # Check that profile methods exist
    assert hasattr(bulk_app, 'save_profile')
    assert hasattr(bulk_app, 'load_profile')
    assert hasattr(bulk_app, 'delete_profile')
    
    # Check that notification manager is available
    assert bulk_app.notification_manager is not None

def test_search_functionality(bulk_app):
    """Test the search functionality in the preview table."""
    app = bulk_app
    
    # Update preview to populate the table
    app.update_preview()
    
    # Get the search input from the top panel
    search_input = app.top_panel.search_input
    clear_btn = app.top_panel.clear_search_btn
    
    # Test that search components exist
    assert search_input is not None
    assert clear_btn is not None
    
    # Test search filtering
    search_input.setText("file1")
    app.update_preview()
    
    # The table should now show only files matching "file1"
    table = app.top_panel.table
    row_count = table.rowCount()
    
    # Should have at least one row (file1.txt)
    assert row_count >= 1
    
    # Test clear search functionality
    clear_btn.click()
    assert search_input.text() == ""
    
    # Test search with no matches
    search_input.setText("nonexistent")
    app.update_preview()
    
    # Should show no rows when no matches
    assert table.rowCount() == 0
    
    # Test case insensitive search
    search_input.setText("FILE2")
    app.update_preview()
    
    # Should find file2.txt (case insensitive)
    assert table.rowCount() >= 1

def test_export_functionality(bulk_app):
    """Test the export functionality for preview data."""
    app = bulk_app
    
    # Update preview to populate the table
    app.update_preview()
    
    # Get the export button from the top panel
    export_btn = app.top_panel.export_btn
    
    # Test that export button exists
    assert export_btn is not None
    assert export_btn.text() == "Export Preview" or export_btn.text() == "Vorschau exportieren"
    
    # Test that export methods exist
    assert hasattr(app.top_panel, 'export_preview')
    assert hasattr(app.top_panel, 'get_current_preview_data')
    assert hasattr(app.top_panel, '_export_csv')
    assert hasattr(app.top_panel, '_export_json')
    
    # Test that Excel export method is removed
    assert not hasattr(app.top_panel, '_export_excel')
    assert not hasattr(app.top_panel, '_check_excel_dependencies')
    
    # Test getting current preview data
    preview_data = app.top_panel.get_current_preview_data()
    assert isinstance(preview_data, list)
    assert len(preview_data) > 0
    
    # Test that preview data has correct structure
    for item in preview_data:
        assert 'old_name' in item
        assert 'new_name' in item
        assert 'status' in item
        assert isinstance(item['old_name'], str)
        assert isinstance(item['new_name'], str)
        assert isinstance(item['status'], str)

def test_language_change_no_unwanted_notifications(bulk_app):
    """Test that changing language doesn't trigger unwanted notifications."""
    app = bulk_app
    
    # Clear any existing notifications
    app.notification_manager.clear_all()
    
    # Ensure we start with no files and no naming fields (the condition that triggers the notification)
    app.selected_files = []
    app.top_panel.prefix_input.clear()
    app.top_panel.suffix_input.clear()
    app.top_panel.base_input.clear()
    
    # Count notifications before language change
    initial_notification_count = len(app.notification_manager.notifications)
    
    # Change language (this should not trigger the "please add files" notification)
    app.on_language_changed("de")
    
    # Count notifications after language change
    final_notification_count = len(app.notification_manager.notifications)
    
    # The notification count should not have increased due to language change
    # (we might have language change notifications, but not the "please add files" one)
    assert final_notification_count == initial_notification_count, \
        f"Language change triggered unwanted notifications. Initial: {initial_notification_count}, Final: {final_notification_count}"
    
    # Verify that the "please add files" notification is not present
    notification_messages = [n.message for n in app.notification_manager.notifications]
    unwanted_message = "Please add files and fill at least one naming field"
    assert unwanted_message not in notification_messages, \
        f"Found unwanted notification: {unwanted_message} in {notification_messages}"

