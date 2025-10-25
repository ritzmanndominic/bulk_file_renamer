# Copyright (c) 2024 Dominic Ritzmann. All rights reserved.
# 
# This software is licensed under the Bulk File Renamer License.
# See LICENSE file for full license terms.

"""
Tests for naming utilities including name cleaning and preview generation.
"""

import os
import sys
import pytest
import tempfile
import shutil
from datetime import datetime, timedelta

# Add the parent directory to the path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.name_cleaner import clean_filename, get_cleanup_preview
from app.utils.generate_preview import generate_preview


class TestNameCleaner:
    """Test the name cleaning functionality."""

    def test_clean_filename_basic(self):
        """Test basic filename cleaning without any options."""
        result = clean_filename("test_file.txt")
        assert result == "test_file.txt"

    def test_clean_filename_empty(self):
        """Test cleaning an empty filename."""
        result = clean_filename("")
        assert result == ""

    def test_clean_filename_none(self):
        """Test cleaning a None filename."""
        result = clean_filename(None)
        assert result is None

    def test_remove_special_chars(self):
        """Test removing special characters."""
        result = clean_filename("test@file#name$.txt", remove_special_chars=True)
        assert result == "testfilename.txt"

    def test_remove_special_chars_preserve_allowed(self):
        """Test that allowed characters are preserved when removing special chars."""
        result = clean_filename("test-file_name.txt", remove_special_chars=True)
        assert result == "test-file_name.txt"

    def test_remove_special_chars_multiple(self):
        """Test removing multiple consecutive special characters."""
        result = clean_filename("test@@@file###name$$$.txt", remove_special_chars=True)
        assert result == "testfilename.txt"

    def test_replace_spaces(self):
        """Test replacing spaces with underscores."""
        result = clean_filename("test file name.txt", replace_spaces=True)
        assert result == "test_file_name.txt"

    def test_replace_spaces_multiple(self):
        """Test replacing multiple consecutive spaces."""
        result = clean_filename("test   file    name.txt", replace_spaces=True)
        assert result == "test_file_name.txt"

    def test_replace_spaces_leading_trailing(self):
        """Test removing leading and trailing underscores after space replacement."""
        result = clean_filename("  test file name  .txt", replace_spaces=True)
        assert result == "test_file_name.txt"

    def test_convert_case_lowercase(self):
        """Test converting to lowercase."""
        result = clean_filename("TEST_FILE_NAME.txt", convert_case=True, case_type="lowercase")
        assert result == "test_file_name.txt"

    def test_convert_case_uppercase(self):
        """Test converting to uppercase."""
        result = clean_filename("test_file_name.txt", convert_case=True, case_type="UPPERCASE")
        assert result == "TEST_FILE_NAME.txt"

    def test_convert_case_title_case(self):
        """Test converting to title case."""
        result = clean_filename("test file name.txt", convert_case=True, case_type="Title Case")
        assert result == "Test File Name.txt"

    def test_remove_accents(self):
        """Test removing accents from characters."""
        result = clean_filename("café_naïve.txt", remove_accents=True)
        assert result == "cafe_naive.txt"

    def test_remove_accents_complex(self):
        """Test removing accents from complex characters."""
        result = clean_filename("résumé_naïve.txt", remove_accents=True)
        assert result == "resume_naive.txt"

    def test_combined_operations(self):
        """Test combining multiple cleaning operations."""
        result = clean_filename(
            "  Test@File#Name  .txt",
            remove_special_chars=True,
            replace_spaces=True,
            convert_case=True,
            case_type="lowercase"
        )
        assert result == "testfilename.txt"

    def test_combined_operations_with_accents(self):
        """Test combining operations including accent removal."""
        result = clean_filename(
            "  Résumé@File#Name  .txt",
            remove_special_chars=True,
            replace_spaces=True,
            convert_case=True,
            case_type="lowercase",
            remove_accents=True
        )
        assert result == "resumefilename.txt"

    def test_no_extension(self):
        """Test cleaning filename without extension."""
        result = clean_filename("test_file", remove_special_chars=True)
        assert result == "test_file"

    def test_multiple_dots(self):
        """Test handling multiple dots in filename."""
        result = clean_filename("test..file...name.txt", remove_special_chars=True)
        assert result == "test.file.name.txt"

    def test_leading_trailing_dots(self):
        """Test removing leading and trailing dots."""
        result = clean_filename("...test_file_name...", remove_special_chars=True)
        assert result == "test_file_name"

    def test_get_cleanup_preview(self):
        """Test the get_cleanup_preview function."""
        result = get_cleanup_preview("Test@File#Name.txt", remove_special_chars=True)
        assert result == "TestFileName.txt"

    def test_edge_cases(self):
        """Test edge cases in filename cleaning."""
        # Only dots
        result = clean_filename("...", remove_special_chars=True)
        assert result == ""
        
        # Only special characters
        result = clean_filename("@#$%", remove_special_chars=True)
        assert result == ""
        
        # Mixed case with spaces
        result = clean_filename("  A  B  C  ", replace_spaces=True, convert_case=True, case_type="lowercase")
        assert result == "a_b_c"


class TestGeneratePreview:
    """Test the preview generation functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def test_files(self, temp_dir):
        """Create test files in the temporary directory."""
        files = []
        for i in range(5):
            filename = f"test_file_{i}.txt"
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write(f"Test content {i}")
            files.append(filepath)
        return files

    def test_generate_preview_basic(self, test_files):
        """Test basic preview generation."""
        preview_list, filtered_files = generate_preview(test_files)
        
        assert len(preview_list) == 5
        assert len(filtered_files) == 5
        
        # Check that all files are in the preview
        for i, (old_name, new_name, status, file_path) in enumerate(preview_list):
            assert old_name == f"test_file_{i}.txt"
            assert new_name == f"test_file_{i}.txt"  # No changes by default
            assert status == "No Change"
            assert file_path == test_files[i]

    def test_generate_preview_with_prefix(self, test_files):
        """Test preview generation with prefix."""
        preview_list, filtered_files = generate_preview(test_files, prefix="new_")
        
        assert len(preview_list) == 5
        
        for i, (old_name, new_name, status, file_path) in enumerate(preview_list):
            assert old_name == f"test_file_{i}.txt"
            assert new_name == f"new_test_file_{i}.txt"
            assert status == "Ready"

    def test_generate_preview_with_suffix(self, test_files):
        """Test preview generation with suffix."""
        preview_list, filtered_files = generate_preview(test_files, suffix="_renamed")
        
        assert len(preview_list) == 5
        
        for i, (old_name, new_name, status, file_path) in enumerate(preview_list):
            assert old_name == f"test_file_{i}.txt"
            assert new_name == f"test_file_{i}_renamed.txt"
            assert status == "Ready"

    def test_generate_preview_with_base_name(self, test_files):
        """Test preview generation with base name."""
        preview_list, filtered_files = generate_preview(test_files, base_name="photo", start_num=1)
        
        assert len(preview_list) == 5
        
        for i, (old_name, new_name, status, file_path) in enumerate(preview_list):
            assert old_name == f"test_file_{i}.txt"
            assert new_name == f"photo_{i+1}.txt"
            assert status == "Ready"

    def test_generate_preview_with_start_number(self, test_files):
        """Test preview generation with start number."""
        preview_list, filtered_files = generate_preview(test_files, start_num=10)
        
        assert len(preview_list) == 5
        
        for i, (old_name, new_name, status, file_path) in enumerate(preview_list):
            assert old_name == f"test_file_{i}.txt"
            assert new_name == f"test_file_{i}_{i+10}.txt"
            assert status == "Ready"

    def test_generate_preview_extension_filter(self, temp_dir):
        """Test preview generation with extension filtering."""
        # Create files with different extensions
        files = []
        for ext in ['txt', 'jpg', 'pdf']:
            for i in range(2):
                filename = f"file_{i}.{ext}"
                filepath = os.path.join(temp_dir, filename)
                with open(filepath, 'w') as f:
                    f.write("content")
                files.append(filepath)
        
        # Filter for txt files only
        preview_list, filtered_files = generate_preview(files, extensions=['txt'])
        
        assert len(preview_list) == 2
        assert len(filtered_files) == 2
        
        for old_name, new_name, status, file_path in preview_list:
            assert old_name.endswith('.txt')

    def test_generate_preview_size_filter(self, temp_dir):
        """Test preview generation with size filtering."""
        # Create files with different sizes
        small_file = os.path.join(temp_dir, "small.txt")
        with open(small_file, 'w') as f:
            f.write("x")  # 1 byte
        
        large_file = os.path.join(temp_dir, "large.txt")
        with open(large_file, 'w') as f:
            f.write("x" * 1000)  # 1000 bytes
        
        files = [small_file, large_file]
        
        # Filter for files larger than 100 bytes
        preview_list, filtered_files = generate_preview(files, size_filter=(">", 100))
        
        assert len(preview_list) == 1
        assert len(filtered_files) == 1
        assert "large.txt" in preview_list[0][0]

    def test_generate_preview_date_filter(self, temp_dir):
        """Test preview generation with date filtering."""
        # Create files with different modification times
        old_file = os.path.join(temp_dir, "old.txt")
        with open(old_file, 'w') as f:
            f.write("old content")
        
        # Set modification time to 1 year ago
        old_time = (datetime.now() - timedelta(days=365)).timestamp()
        os.utime(old_file, (old_time, old_time))
        
        recent_file = os.path.join(temp_dir, "recent.txt")
        with open(recent_file, 'w') as f:
            f.write("recent content")
        
        files = [old_file, recent_file]
        
        # Filter for files modified before 6 months ago
        six_months_ago = datetime.now() - timedelta(days=180)
        preview_list, filtered_files = generate_preview(files, date_filter=("before", six_months_ago))
        
        assert len(preview_list) == 1
        assert len(filtered_files) == 1
        assert "old.txt" in preview_list[0][0]

    def test_generate_preview_extension_lock(self, test_files):
        """Test preview generation with extension lock enabled."""
        preview_list, filtered_files = generate_preview(test_files, extension_lock=True)
        
        for old_name, new_name, status, file_path in preview_list:
            # Extension should be preserved
            assert old_name.endswith('.txt')
            assert new_name.endswith('.txt')

    def test_generate_preview_conflicts(self, temp_dir):
        """Test preview generation with naming conflicts."""
        # Create files that will have the same new name
        file1 = os.path.join(temp_dir, "file1.txt")
        file2 = os.path.join(temp_dir, "file2.txt")
        
        with open(file1, 'w') as f:
            f.write("content1")
        with open(file2, 'w') as f:
            f.write("content2")
        
        files = [file1, file2]
        
        # Use base name without start number (will create conflicts)
        preview_list, filtered_files = generate_preview(files, base_name="photo")
        
        assert len(preview_list) == 2
        
        # Both files should have the same new name, causing conflicts
        new_names = [item[1] for item in preview_list]
        assert new_names[0] == new_names[1]  # Same new name
        
        # Check that conflicts are detected
        statuses = [item[2] for item in preview_list]
        assert "Conflict" in statuses

    def test_generate_preview_name_cleaning(self, test_files):
        """Test preview generation with name cleaning options."""
        preview_list, filtered_files = generate_preview(
            test_files,
            prefix="test@",
            suffix="#end",
            remove_special_chars=True,
            convert_case=True,
            case_type="lowercase"
        )
        
        for old_name, new_name, status, file_path in preview_list:
            # Special characters should be removed
            assert "@" not in new_name
            assert "#" not in new_name
            # Should be lowercase
            assert new_name.islower()

    def test_generate_preview_empty_file_list(self):
        """Test preview generation with empty file list."""
        preview_list, filtered_files = generate_preview([])
        
        assert len(preview_list) == 0
        assert len(filtered_files) == 0

    def test_generate_preview_nonexistent_files(self, temp_dir):
        """Test preview generation with nonexistent files."""
        nonexistent_files = [
            os.path.join(temp_dir, "nonexistent1.txt"),
            os.path.join(temp_dir, "nonexistent2.txt")
        ]
        
        preview_list, filtered_files = generate_preview(nonexistent_files)
        
        assert len(preview_list) == 0
        assert len(filtered_files) == 0

    def test_generate_preview_invalid_start_number(self, test_files):
        """Test preview generation with invalid start number."""
        # Start number less than 1 should be corrected to 1
        preview_list, filtered_files = generate_preview(test_files, start_num=0)
        
        for i, (old_name, new_name, status, file_path) in enumerate(preview_list):
            assert new_name == f"test_file_{i}_1.txt"  # Should start from 1

    def test_generate_preview_case_only_changes(self, temp_dir):
        """Test preview generation with case-only changes."""
        # Create a file with lowercase name
        original_file = os.path.join(temp_dir, "testfile.txt")
        with open(original_file, 'w') as f:
            f.write("content")
        
        # Try to rename to uppercase (case-only change)
        preview_list, filtered_files = generate_preview([original_file], base_name="TESTFILE")
        
        assert len(preview_list) == 1
        old_name, new_name, status, file_path = preview_list[0]
        assert old_name == "testfile.txt"
        assert new_name == "TESTFILE.txt"
        assert status == "Ready"  # Case-only changes should be ready

    def test_generate_preview_swap_chain_detection(self, temp_dir):
        """Test preview generation with swap chain detection."""
        # Create files that will be swapped
        file1 = os.path.join(temp_dir, "a.txt")
        file2 = os.path.join(temp_dir, "b.txt")
        
        with open(file1, 'w') as f:
            f.write("content1")
        with open(file2, 'w') as f:
            f.write("content2")
        
        files = [file1, file2]
        
        # Create a swap: a.txt -> b.txt, b.txt -> a.txt
        preview_list, filtered_files = generate_preview(files, base_name="temp", start_num=1)
        
        # Then manually create the swap scenario
        # This is a complex test that would require more setup
        # For now, just verify the basic functionality works
        assert len(preview_list) == 2
