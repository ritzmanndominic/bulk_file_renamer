# 📖 User Guide

Complete guide to all features and functionality in Bulk File Renamer.

## 📋 Table of Contents

1. [Interface Overview](#interface-overview)
2. [Adding Files](#adding-files)
3. [Naming Options](#naming-options)
4. [Auto-Clean Features](#auto-clean-features)
5. [Advanced Filters](#advanced-filters)
6. [Preview System](#preview-system)
7. [Profile Management](#profile-management)
8. [Undo System](#undo-system)
9. [Backup & Logging](#backup--logging)
10. [Export & Validation](#export--validation)
11. [Keyboard Shortcuts](#keyboard-shortcuts)
12. [Localization](#localization)

## 🖥️ Interface Overview

### Main Window Layout

```
┌─────────────────┬─────────────────┬─────────────────┐
│   File List     │    Preview      │    Settings     │
│                 │                 │                 │
│ • Add Folder    │ • Live Preview  │ • Naming        │
│ • Add Files     │ • Color Coding  │ • Auto-clean    │
│ • Drag & Drop   │ • Search        │ • Filters       │
│ • File Info     │ • Sorting       │ • Profiles      │
└─────────────────┴─────────────────┴─────────────────┘
```

### Toolbar
- **Add Folder**: Select a folder to add all files
- **Add Files**: Select individual files
- **Clear All**: Remove all files from the list
- **Apply Changes**: Execute the rename operation
- **Undo Last**: Reverse the most recent operation
- **Validate**: Check for potential issues
- **Export Preview**: Save preview as CSV/JSON

## 📁 Adding Files

### Supported Methods

#### 1. Add Folder
- **Purpose**: Add all files from a selected folder
- **Recursive**: Includes files from subfolders
- **File Types**: All file types supported
- **Use Case**: Bulk processing of photo collections, document folders

#### 2. Add Individual Files
- **Purpose**: Select specific files to rename
- **Multi-select**: Use Ctrl+Click or Shift+Click
- **Mixed Types**: Can select different file types
- **Use Case**: Selective renaming of specific files

#### 3. Drag & Drop
- **Purpose**: Quick file addition
- **Supports**: Files, folders, mixed selections
- **Visual Feedback**: Shows drop zones
- **Use Case**: Quick workflow integration

### File Information Display
- **Original Name**: Current filename
- **File Size**: Human-readable format (KB, MB, GB)
- **File Date**: Creation/modification date
- **File Extension**: File type indicator
- **Status**: Processing status and warnings

## 🏷️ Naming Options

### Basic Naming Components

#### Prefix
- **Purpose**: Add text at the beginning of filenames
- **Examples**: 
  - `IMG_` → `IMG_photo1.jpg`
  - `2025_` → `2025_document.pdf`
- **Use Cases**: Date stamps, project codes, categories

#### Suffix
- **Purpose**: Add text at the end of filenames (before extension)
- **Examples**:
  - `_edited` → `photo1_edited.jpg`
  - `_backup` → `document_backup.pdf`
- **Use Cases**: Version indicators, status markers

#### Base Name
- **Purpose**: Replace the entire filename (excluding extension)
- **Examples**:
  - `Invoice` → `Invoice_001.pdf`, `Invoice_002.pdf`
  - `Photo` → `Photo_001.jpg`, `Photo_002.jpg`
- **Use Cases**: Standardized naming, sequential numbering

#### Start Number
- **Purpose**: Starting number for sequential naming
- **Range**: 1 to 999999
- **Increment**: Automatically increments for each file
- **Padding**: Automatically adds leading zeros
- **Examples**:
  - Start: 1 → `001`, `002`, `003`
  - Start: 100 → `100`, `101`, `102`

#### Extension Lock
- **Purpose**: Preserve original file extensions
- **Default**: Enabled (recommended)
- **Disable**: Only if you need to change extensions
- **Warning**: Disabling can break file associations

### Advanced Naming Patterns

#### Sequential Numbering
```
Base Name: "Photo"
Start Number: 1
Result: IMG_001.jpg → Photo_001.jpg
         IMG_002.jpg → Photo_002.jpg
         IMG_003.jpg → Photo_003.jpg
```

#### Date-Based Naming
```
Prefix: "2025-01-15_"
Result: document.pdf → 2025-01-15_document.pdf
```

#### Project-Based Naming
```
Prefix: "ProjectAlpha_"
Suffix: "_v1"
Result: file.txt → ProjectAlpha_file_v1.txt
```

## 🧹 Auto-Clean Features

### Remove Special Characters
- **Purpose**: Clean filenames of problematic characters
- **Removes**: `<>:"/\|?*` and other special characters
- **Replaces With**: Underscore `_` or removes entirely
- **Use Case**: Cross-platform compatibility, web uploads

### Replace Spaces
- **Options**:
  - **Underscore**: `my file.txt` → `my_file.txt`
  - **Hyphen**: `my file.txt` → `my-file.txt`
  - **Remove**: `my file.txt` → `myfile.txt`
- **Use Case**: URL-friendly filenames, programming compatibility

### Convert Case
- **Options**:
  - **Lowercase**: `MyFile.txt` → `myfile.txt`
  - **Uppercase**: `MyFile.txt` → `MYFILE.txt`
  - **Title Case**: `my file.txt` → `My File.txt`
  - **Camel Case**: `my file.txt` → `MyFile.txt`
- **Use Case**: Consistent naming conventions

### Remove Accents
- **Purpose**: Convert accented characters to ASCII
- **Examples**:
  - `café.txt` → `cafe.txt`
  - `naïve.pdf` → `naive.pdf`
  - `résumé.doc` → `resume.doc`
- **Use Case**: International compatibility, legacy systems

### Auto-Clean Combinations
```
Original: "My Café Photo (2025)!.jpg"
Remove Special: "My Café Photo 2025.jpg"
Replace Spaces: "My_Café_Photo_2025.jpg"
Remove Accents: "My_Cafe_Photo_2025.jpg"
Convert Case: "my_cafe_photo_2025.jpg"
```

## 🔍 Advanced Filters

### Extension Filter
- **Purpose**: Process only specific file types
- **Format**: Comma-separated list
- **Examples**:
  - `jpg,png,gif` - Image files only
  - `pdf,doc,docx` - Document files only
  - `mp3,wav,flac` - Audio files only
- **Case Insensitive**: `JPG` matches `jpg`

### Size Filter
- **Conditions**:
  - **Greater than (>)** - Files larger than specified size
  - **Less than (<)** - Files smaller than specified size
  - **Equal to (=)** - Files exactly the specified size
- **Units**: B, KB, MB, GB
- **Examples**:
  - `> 1MB` - Files larger than 1 megabyte
  - `< 500KB` - Files smaller than 500 kilobytes
  - `= 2MB` - Files exactly 2 megabytes

### Date Filter
- **Before Date**: Process files created before specified date
- **After Date**: Process files created after specified date
- **Date Format**: YYYY-MM-DD
- **Use Cases**:
  - Archive old files: `Before 2023-01-01`
  - Process recent files: `After 2024-12-01`

### Status Filter
- **All Files**: Process all files in the list
- **Selected Only**: Process only manually selected files
- **Unselected Only**: Process only unselected files
- **Use Case**: Selective processing within a large file set

### Filter Combinations
```
Extension: jpg,png
Size: > 1MB
Date: After 2024-01-01
Result: Only large image files from 2024 onwards
```

## 👁️ Preview System

### Color Coding
- **Green**: Files that will be renamed successfully
- **Red**: Files with conflicts or errors
- **Yellow**: Files with warnings or special cases
- **Blue**: Files that match current filters

### Live Preview
- **Real-time Updates**: Preview changes as you type
- **Instant Feedback**: See results immediately
- **Error Detection**: Identifies potential issues
- **Conflict Resolution**: Shows naming conflicts

### Preview Features
- **Search**: Find specific files in the preview
- **Sorting**: Sort by name, size, date, status
- **Lazy Loading**: Efficient handling of large file lists
- **Export**: Save preview as CSV or JSON

### Preview Information
- **Original Name**: Current filename
- **New Name**: Proposed new filename
- **Status**: Processing status
- **Warnings**: Any issues or conflicts
- **File Info**: Size, date, extension

## 💾 Profile Management

### Creating Profiles
1. **Configure Settings**: Set up naming, filters, auto-clean options
2. **Save Profile**: Click "Save Profile" button
3. **Enter Name**: Give the profile a descriptive name
4. **Profile Saved**: Settings stored for future use

### Loading Profiles
1. **Load Profile**: Click "Load Profile" button
2. **Select Profile**: Choose from saved profiles
3. **Settings Restored**: All options loaded instantly
4. **Ready to Use**: Apply to current file list

### Profile Features
- **Recent Profiles**: Quick access to recently used profiles
- **Configurable Limit**: Set how many recent profiles to remember
- **Profile Management**: Rename, delete, or organize profiles
- **Export/Import**: Share profiles between installations

### Common Profile Examples

#### Photo Organization
```
Name: "Photo Organization"
Prefix: "IMG_"
Auto-clean: Remove special characters, Replace spaces with underscore
Filters: jpg,png,gif,tiff
```

#### Document Management
```
Name: "Document Cleanup"
Base Name: "Document"
Start Number: 1
Auto-clean: Remove accents, Convert to lowercase
Filters: pdf,doc,docx,txt
```

#### Music Files
```
Name: "Music Cleanup"
Auto-clean: Remove special characters, Replace spaces with underscore, Remove accents
Filters: mp3,wav,flac,aac
```

## ↩️ Undo System

### Undo Last Operation
- **Purpose**: Reverse the most recent rename operation
- **Scope**: All files from the last operation
- **Safety**: Works even after closing and reopening the app
- **Limitation**: Only the most recent operation

### Undo Selected Operations
- **Purpose**: Choose specific operations to reverse
- **History**: Shows all previous operations
- **Selective**: Choose which operations to undo
- **Order**: Operations are undone in reverse chronological order

### Undo Safety Features
- **Operation Logging**: All operations are logged
- **File Tracking**: Original names are preserved
- **Conflict Detection**: Warns about potential conflicts
- **Backup Integration**: Works with backup system

### Undo Limitations
- **File System Changes**: Cannot undo if files were moved outside the app
- **Manual Changes**: Cannot undo manual file system changes
- **Backup Dependency**: Requires backup files for complete restoration

## 💾 Backup & Logging

### Automatic Backups
- **Purpose**: Create copies of original files before renaming
- **Location**: Subfolder within the original directory
- **Naming**: `backup_YYYY-MM-DD_HH-MM-SS/`
- **Safety**: Original files preserved in backup folder

### Operation Logging
- **Purpose**: Record all rename operations
- **Format**: Detailed log with timestamps
- **Location**: Application data directory
- **Content**: Original names, new names, timestamps, status

### Backup Options
- **Enable/Disable**: Toggle backup creation
- **Backup Location**: Choose backup directory
- **Backup Naming**: Customize backup folder names
- **Cleanup**: Automatic cleanup of old backups

### Log Management
- **Log Rotation**: Automatic log file rotation
- **Log Retention**: Configurable retention period
- **Log Export**: Export logs for analysis
- **Log Search**: Search through operation history

## 📊 Export & Validation

### Export Preview
- **Formats**: CSV, JSON
- **Content**: Original names, new names, file info, status
- **Use Case**: Documentation, analysis, sharing
- **Integration**: Works with spreadsheet applications

### Validation System
- **Purpose**: Check for potential issues before applying changes
- **Checks**:
  - Naming conflicts
  - Invalid characters
  - File system limitations
  - Permission issues
- **Report**: Detailed validation report

### Simulation Mode
- **Purpose**: Test changes without actually renaming files
- **Safety**: No actual file system changes
- **Report**: Detailed simulation report
- **Use Case**: Testing complex rename operations

## ⌨️ Keyboard Shortcuts

### File Operations
- **Ctrl+O**: Add folder
- **Ctrl+Shift+O**: Add files
- **Ctrl+A**: Select all files
- **Delete**: Remove selected files
- **F5**: Refresh file list

### Rename Operations
- **Ctrl+R**: Apply changes
- **Ctrl+Z**: Undo last operation
- **Ctrl+Shift+Z**: Undo selected operations
- **F9**: Validate changes
- **Ctrl+E**: Export preview

### Navigation
- **Ctrl+F**: Search in preview
- **Ctrl+G**: Go to next search result
- **Ctrl+Shift+G**: Go to previous search result
- **Tab**: Move between interface sections
- **Shift+Tab**: Move backwards

### Profile Management
- **Ctrl+S**: Save current profile
- **Ctrl+L**: Load profile
- **Ctrl+Shift+S**: Save profile as
- **Ctrl+Shift+L**: Load recent profile

## 🌍 Localization

### Supported Languages
- **English**: Default language
- **Deutsch (German)**: Complete translation
- **Language Selection**: Choose at startup or in settings

### Localized Elements
- **Interface**: All buttons, menus, and dialogs
- **Messages**: Error messages and notifications
- **Help Text**: Tooltips and help content
- **Date/Time**: Localized date and time formats

### Language Switching
- **Startup**: Choose language when first launching
- **Settings**: Change language in application settings
- **Restart Required**: Language changes require application restart

### Contributing Translations
- **Translation Files**: JSON format in `languages/` directory
- **Contributing**: Submit translation improvements via GitHub
- **Testing**: Test translations with the application
- **Documentation**: Translation guidelines available

## 🎯 Best Practices

### File Management
1. **Always backup** important files before bulk operations
2. **Test with small sets** before processing large collections
3. **Use preview** to verify changes before applying
4. **Save profiles** for repeated workflows
5. **Validate changes** before applying

### Performance
1. **Process in batches** for very large file collections
2. **Use filters** to reduce the number of files processed
3. **Close other applications** during large operations
4. **Monitor system resources** during processing

### Safety
1. **Enable backups** for critical operations
2. **Use undo features** to reverse unwanted changes
3. **Check file permissions** before processing
4. **Verify file system** has sufficient space

---

**Need More Help?** Check our [FAQ](faq.md) or [Troubleshooting Guide](troubleshooting.md)!
