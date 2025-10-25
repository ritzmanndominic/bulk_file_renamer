# Copyright (c) 2024 Dominic Ritzmann. All rights reserved.
# 
# This software is licensed under the Bulk File Renamer License.
# See LICENSE file for full license terms.

"""
Tests for file operations including add, rename, and delete functionality.
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
    for i in range(5):
        filename = f"test_file_{i}.txt"
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write(f"Test content {i}")
        files.append(filepath)
    return files


class TestFileOperationWorker:
    """Test the FileOperationWorker class for file renaming operations."""

    def test_file_operation_worker_initialization(self):
        """Test that FileOperationWorker initializes correctly."""
        file_ops = [
            {"old_path": "/old/path.txt", "new_path": "/new/path.txt", "action": "rename"}
        ]
        worker = FileOperationWorker(file_ops)
        assert worker.file_ops == file_ops
        assert isinstance(worker, QThread)

    def test_successful_rename_operation(self, temp_dir, test_files):
        """Test successful file rename operation."""
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
        
        # Verify the file was renamed
        assert os.path.exists(new_path)
        assert not os.path.exists(old_path)
        assert len(successes) == 1
        assert len(errors) == 0
        assert len(conflicts) == 0

    def test_rename_nonexistent_file(self, temp_dir):
        """Test renaming a file that doesn't exist."""
        old_path = os.path.join(temp_dir, "nonexistent.txt")
        new_path = os.path.join(temp_dir, "new_name.txt")
        
        file_ops = [{"old_path": old_path, "new_path": new_path, "action": "rename"}]
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
        
        assert len(successes) == 0
        assert len(errors) == 1
        assert "Failed:" in errors[0]

    def test_rename_to_existing_file(self, temp_dir, test_files):
        """Test renaming to a file that already exists."""
        old_path = test_files[0]
        existing_path = test_files[1]
        
        file_ops = [{"old_path": old_path, "new_path": existing_path, "action": "rename"}]
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
        
        assert len(successes) == 0
        assert len(errors) == 0
        assert len(conflicts) == 1
        assert "Conflict:" in conflicts[0]

    def test_case_only_rename(self, temp_dir):
        """Test case-only rename (should succeed on case-insensitive filesystems)."""
        # Create a file with lowercase name
        original_path = os.path.join(temp_dir, "testfile.txt")
        with open(original_path, 'w') as f:
            f.write("test content")
        
        # Try to rename to uppercase
        new_path = os.path.join(temp_dir, "TESTFILE.txt")
        
        file_ops = [{"old_path": original_path, "new_path": new_path, "action": "rename"}]
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
        
        # Should succeed (case-only change)
        assert len(successes) == 1
        assert len(errors) == 0
        assert len(conflicts) == 0

    def test_multiple_file_operations(self, temp_dir, test_files):
        """Test multiple file operations in one worker."""
        file_ops = []
        for i, old_path in enumerate(test_files[:3]):
            new_path = os.path.join(temp_dir, f"batch_renamed_{i}.txt")
            file_ops.append({"old_path": old_path, "new_path": new_path, "action": "rename"})
        
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
        
        assert len(successes) == 3
        assert len(errors) == 0
        assert len(conflicts) == 0
        
        # Verify all files were renamed
        for i in range(3):
            new_path = os.path.join(temp_dir, f"batch_renamed_{i}.txt")
            assert os.path.exists(new_path)

    def test_progress_signal(self, temp_dir, test_files):
        """Test that progress signal is emitted correctly."""
        file_ops = []
        for old_path in test_files:
            new_path = os.path.join(temp_dir, f"progress_test_{os.path.basename(old_path)}")
            file_ops.append({"old_path": old_path, "new_path": new_path, "action": "rename"})
        
        worker = FileOperationWorker(file_ops)
        
        progress_values = []
        
        def on_progress(value):
            progress_values.append(value)
        
        worker.progress.connect(on_progress)
        worker.start()
        worker.wait()
        
        # Should have progress values from 0 to 100
        assert len(progress_values) > 0
        assert progress_values[-1] == 100  # Final progress should be 100%


class TestFileAddWorker:
    """Test the FileAddWorker class for adding files to the application."""

    def test_file_add_worker_initialization(self):
        """Test that FileAddWorker initializes correctly."""
        paths = ["/test/path1.txt", "/test/path2.txt"]
        existing_files = ["/existing/file.txt"]
        worker = FileAddWorker(paths, existing_files)
        
        assert worker.paths == paths
        assert len(worker.existing_files) == 1
        assert "/existing/file.txt" in worker.existing_files

    def test_add_single_file(self, temp_dir):
        """Test adding a single file."""
        # Create a test file
        test_file = os.path.join(temp_dir, "single_file.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        worker = FileAddWorker([test_file])
        
        added_files = []
        duplicate_count = 0
        
        def on_finished(files, duplicates):
            added_files.extend(files)
            nonlocal duplicate_count
            duplicate_count = duplicates
        
        worker.finished.connect(on_finished)
        worker.start()
        worker.wait()
        
        assert len(added_files) == 1
        assert added_files[0] == test_file
        assert duplicate_count == 0

    def test_add_multiple_files(self, temp_dir):
        """Test adding multiple files."""
        # Create multiple test files
        test_files = []
        for i in range(3):
            test_file = os.path.join(temp_dir, f"multi_file_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"test content {i}")
            test_files.append(test_file)
        
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
        
        assert len(added_files) == 3
        assert duplicate_count == 0

    def test_add_directory(self, temp_dir):
        """Test adding files from a directory."""
        # Create a subdirectory with files
        subdir = os.path.join(temp_dir, "subdir")
        os.makedirs(subdir)
        
        test_files = []
        for i in range(3):
            test_file = os.path.join(subdir, f"dir_file_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"test content {i}")
            test_files.append(test_file)
        
        worker = FileAddWorker([subdir])
        
        added_files = []
        duplicate_count = 0
        
        def on_finished(files, duplicates):
            added_files.extend(files)
            nonlocal duplicate_count
            duplicate_count = duplicates
        
        worker.finished.connect(on_finished)
        worker.start()
        worker.wait()
        
        assert len(added_files) == 3
        assert duplicate_count == 0

    def test_duplicate_detection(self, temp_dir):
        """Test that duplicate files are detected correctly."""
        # Create a test file
        test_file = os.path.join(temp_dir, "duplicate_test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # Add the same file twice
        worker = FileAddWorker([test_file, test_file])
        
        added_files = []
        duplicate_count = 0
        
        def on_finished(files, duplicates):
            added_files.extend(files)
            nonlocal duplicate_count
            duplicate_count = duplicates
        
        worker.finished.connect(on_finished)
        worker.start()
        worker.wait()
        
        assert len(added_files) == 1  # Only added once
        assert duplicate_count == 1  # One duplicate detected

    def test_duplicate_with_existing_files(self, temp_dir):
        """Test duplicate detection with existing files list."""
        # Create a test file
        test_file = os.path.join(temp_dir, "existing_test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # Add file with existing files list containing the same file
        worker = FileAddWorker([test_file], existing_files=[test_file])
        
        added_files = []
        duplicate_count = 0
        
        def on_finished(files, duplicates):
            added_files.extend(files)
            nonlocal duplicate_count
            duplicate_count = duplicates
        
        worker.finished.connect(on_finished)
        worker.start()
        worker.wait()
        
        assert len(added_files) == 0  # Not added (already exists)
        assert duplicate_count == 1  # One duplicate detected

    def test_nonexistent_file(self, temp_dir):
        """Test adding a file that doesn't exist."""
        nonexistent_file = os.path.join(temp_dir, "nonexistent.txt")
        
        worker = FileAddWorker([nonexistent_file])
        
        added_files = []
        duplicate_count = 0
        
        def on_finished(files, duplicates):
            added_files.extend(files)
            nonlocal duplicate_count
            duplicate_count = duplicates
        
        worker.finished.connect(on_finished)
        worker.start()
        worker.wait()
        
        assert len(added_files) == 0  # No files added
        assert duplicate_count == 0

    def test_mixed_paths(self, temp_dir):
        """Test adding mix of files and directories."""
        # Create a file
        test_file = os.path.join(temp_dir, "mixed_file.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # Create a directory with files
        subdir = os.path.join(temp_dir, "mixed_dir")
        os.makedirs(subdir)
        dir_file = os.path.join(subdir, "dir_file.txt")
        with open(dir_file, 'w') as f:
            f.write("dir content")
        
        # Create a nonexistent file
        nonexistent = os.path.join(temp_dir, "nonexistent.txt")
        
        worker = FileAddWorker([test_file, subdir, nonexistent])
        
        added_files = []
        duplicate_count = 0
        
        def on_finished(files, duplicates):
            added_files.extend(files)
            nonlocal duplicate_count
            duplicate_count = duplicates
        
        worker.finished.connect(on_finished)
        worker.start()
        worker.wait()
        
        assert len(added_files) == 2  # One file + one from directory
        assert duplicate_count == 0

    def test_progress_signal(self, temp_dir):
        """Test that progress signal is emitted correctly."""
        # Create multiple test files
        test_files = []
        for i in range(5):
            test_file = os.path.join(temp_dir, f"progress_file_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"test content {i}")
            test_files.append(test_file)
        
        worker = FileAddWorker(test_files)
        
        progress_values = []
        
        def on_progress(value):
            progress_values.append(value)
        
        worker.progress.connect(on_progress)
        worker.start()
        worker.wait()
        
        # Should have progress values
        assert len(progress_values) > 0
        assert progress_values[-1] == 100  # Final progress should be 100%

    def test_nested_directory_structure(self, temp_dir):
        """Test adding files from nested directory structure."""
        # Create nested directories
        level1 = os.path.join(temp_dir, "level1")
        level2 = os.path.join(level1, "level2")
        level3 = os.path.join(level2, "level3")
        os.makedirs(level3)
        
        # Create files at different levels
        files = []
        for i, level in enumerate([level1, level2, level3]):
            test_file = os.path.join(level, f"nested_file_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"nested content {i}")
            files.append(test_file)
        
        worker = FileAddWorker([level1])
        
        added_files = []
        duplicate_count = 0
        
        def on_finished(files, duplicates):
            added_files.extend(files)
            nonlocal duplicate_count
            duplicate_count = duplicates
        
        worker.finished.connect(on_finished)
        worker.start()
        worker.wait()
        
        assert len(added_files) == 3  # All nested files should be found
        assert duplicate_count == 0
