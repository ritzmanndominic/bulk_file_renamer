# Bulk File Renamer - Test Suite

This directory contains comprehensive tests for the Bulk File Renamer application. The test suite covers all major features and components of the application.

## Test Structure

The test suite is organized into several categories:

### Core Functionality Tests
- **`test_file_operations.py`** - Tests for file operations (add, rename, delete)
- **`test_naming_utilities.py`** - Tests for naming patterns and preview generation
- **`test_settings_management.py`** - Tests for settings management
- **`test_profile_management.py`** - Tests for profile management

### UI Component Tests
- **`test_ui_components.py`** - Tests for all UI components and widgets

### Integration Tests
- **`test_integration.py`** - Tests for component integration and workflows
- **`test_bulk_renamer.py`** - Tests for the main application (existing)

## Running Tests

### Prerequisites

Install the required testing dependencies:

```bash
pip install -r requirements-test.txt
```

### Basic Test Execution

Run all tests:
```bash
python run_tests.py
```

Run tests with verbose output:
```bash
python run_tests.py -v
```

Run specific test categories:
```bash
python run_tests.py -k file_operations
python run_tests.py -k naming
python run_tests.py -k settings
python run_tests.py -k profiles
python run_tests.py -k ui
python run_tests.py -k integration
```

### Advanced Options

Run tests with coverage reporting:
```bash
python run_tests.py --coverage
```

Run tests in parallel (faster execution):
```bash
python run_tests.py --parallel
```

List available test files:
```bash
python run_tests.py --list
```

List test categories:
```bash
python run_tests.py --categories
```

### Direct pytest Usage

You can also run tests directly with pytest:

```bash
# Run all tests
pytest

# Run specific test file
pytest test_file_operations.py

# Run specific test function
pytest test_file_operations.py::TestFileOperationWorker::test_successful_rename_operation

# Run with coverage
pytest --cov=app --cov-report=html

# Run in parallel
pytest -n auto
```

## Test Categories

### File Operations Tests
Tests the core file manipulation functionality:
- File renaming operations
- File addition (including directory scanning)
- Error handling for file operations
- Progress tracking
- Conflict detection

### Naming Utilities Tests
Tests the naming and preview generation:
- Name cleaning and sanitization
- Preview generation with various filters
- Extension filtering
- Size filtering
- Date filtering
- Conflict detection in naming

### Settings Management Tests
Tests the settings system:
- Settings persistence
- Default settings handling
- Recent items management
- Settings validation
- Error handling

### Profile Management Tests
Tests the profile system:
- Profile saving and loading
- Profile validation
- Profile metadata handling
- Profile listing and deletion
- Error handling

### UI Component Tests
Tests all UI components:
- Custom widgets (checkboxes, comboboxes, etc.)
- Input components (date input, spinboxes, etc.)
- Notification system
- Theme application
- Component integration

### Integration Tests
Tests component interaction:
- Complete application workflows
- Settings and profile integration
- Preview generation with real files
- Worker integration
- Error handling across components

## Test Features

### Fixtures
The test suite uses pytest fixtures to provide:
- Temporary directories for test files
- Qt application instances
- Test file creation
- Main window instances

### Mocking
Tests use mocking where appropriate to:
- Isolate components under test
- Simulate file system operations
- Test error conditions
- Avoid side effects

### Coverage
The test suite aims for high code coverage:
- Unit tests for individual functions
- Integration tests for component interaction
- Edge case testing
- Error condition testing

## Writing New Tests

When adding new tests:

1. **Follow naming conventions**: Test files should start with `test_`, test classes with `Test`, and test functions with `test_`

2. **Use appropriate fixtures**: Leverage existing fixtures for common setup

3. **Test both success and failure cases**: Include tests for error conditions

4. **Add docstrings**: Document what each test is testing

5. **Use descriptive test names**: Test names should clearly indicate what is being tested

6. **Group related tests**: Use test classes to group related functionality

### Example Test Structure

```python
class TestNewFeature:
    """Test the new feature functionality."""
    
    def test_feature_basic_functionality(self, fixture):
        """Test basic functionality of the new feature."""
        # Arrange
        # Act
        # Assert
    
    def test_feature_error_handling(self, fixture):
        """Test error handling in the new feature."""
        # Test error conditions
```

## Continuous Integration

The test suite is designed to work with CI/CD systems:
- Tests are deterministic and don't depend on external state
- Temporary files are properly cleaned up
- Tests can run in parallel
- Coverage reporting is available

## Troubleshooting

### Common Issues

1. **Qt Application Errors**: Ensure PySide6 is properly installed
2. **Import Errors**: Check that the app module is in the Python path
3. **File Permission Errors**: Tests use temporary directories to avoid permission issues
4. **Test Timeouts**: Some tests may take longer on slower systems

### Debug Mode

Run tests in debug mode for more detailed output:
```bash
pytest -v -s --tb=long
```

### Test Isolation

If tests are interfering with each other, run them individually:
```bash
pytest test_file_operations.py::TestFileOperationWorker::test_successful_rename_operation -v
```

## Contributing

When contributing to the test suite:

1. Ensure all tests pass before submitting
2. Add tests for new functionality
3. Update existing tests if behavior changes
4. Follow the existing test patterns and conventions
5. Document any new test utilities or fixtures
