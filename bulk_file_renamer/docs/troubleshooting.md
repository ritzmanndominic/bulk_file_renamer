# 🛠️ Troubleshooting Guide

Common issues and solutions for Bulk File Renamer.

## 📋 Quick Diagnosis

### Before You Start
1. **Check the preview** - Look for red warnings or errors
2. **Use Validate** - Click the "Validate" button to check for issues
3. **Check file permissions** - Ensure you have write access to files
4. **Verify file paths** - Make sure files aren't locked by other applications

### Common Warning Colors
- **🟢 Green**: Files will be renamed successfully
- **🟡 Yellow**: Warnings or special cases
- **🔴 Red**: Errors or conflicts that need attention

## 🚀 Installation Issues

### Python Not Found
**Error**: `'python' is not recognized as an internal or external command`

**Solutions**:
1. **Install Python**: Download from [python.org](https://python.org)
2. **Add to PATH**: Check "Add Python to PATH" during installation
3. **Use python3**: Try `python3` instead of `python`
4. **Check installation**: Run `python --version` to verify

### Virtual Environment Issues
**Error**: `venv module not found` or virtual environment activation fails

**Solutions**:
1. **Update pip**: `python -m pip install --upgrade pip`
2. **Install venv**: `python -m pip install virtualenv`
3. **Use different method**: Try `python -m venv .venv`
4. **Check Python version**: Ensure Python 3.8+ is installed

### Dependencies Installation Fails
**Error**: `pip install -r requirements.txt` fails

**Solutions**:
1. **Update pip**: `python -m pip install --upgrade pip`
2. **Use specific Python**: `python3 -m pip install -r requirements.txt`
3. **Install individually**: Install packages one by one to identify issues
4. **Check internet connection**: Ensure stable internet connection
5. **Use different index**: `pip install -r requirements.txt -i https://pypi.org/simple/`

## 🖥️ Application Issues

### Application Won't Start
**Error**: Application crashes on startup or won't launch

**Solutions**:
1. **Check Python version**: Ensure Python 3.8+ is installed
2. **Reinstall dependencies**: `pip install -r requirements.txt --force-reinstall`
3. **Check file permissions**: Ensure you have read access to all files
4. **Run from terminal**: Check for error messages in console
5. **Check system requirements**: Ensure your system meets minimum requirements

### GUI Not Displaying
**Error**: Application starts but GUI doesn't appear

**Solutions**:
1. **Check display settings**: Ensure proper display configuration
2. **Update graphics drivers**: Update your graphics card drivers
3. **Try windowed mode**: Check if application is minimized
4. **Restart application**: Close and restart the application
5. **Check system resources**: Ensure sufficient RAM and CPU

### Slow Performance
**Issue**: Application is slow or unresponsive

**Solutions**:
1. **Reduce file count**: Process files in smaller batches
2. **Close other applications**: Free up system resources
3. **Check disk space**: Ensure sufficient free disk space
4. **Use filters**: Filter files to reduce processing load
5. **Restart application**: Close and restart to clear memory

## 📁 File Operation Issues

### Files Not Adding
**Issue**: Files don't appear in the file list

**Solutions**:
1. **Check file permissions**: Ensure read access to files/folders
2. **Try different method**: Use drag & drop instead of buttons
3. **Check file types**: Ensure files are not corrupted
4. **Restart application**: Close and restart the application
5. **Check folder contents**: Verify folder contains files

### Rename Operation Fails
**Error**: Files are not being renamed

**Solutions**:
1. **Check file permissions**: Ensure write access to files
2. **Close other applications**: Files might be locked by other programs
3. **Check disk space**: Ensure sufficient free space
4. **Use preview first**: Always preview before applying changes
5. **Check for conflicts**: Look for naming conflicts in preview

### Permission Denied
**Error**: `Permission denied` or `Access denied`

**Solutions**:
1. **Run as administrator**: Right-click and "Run as administrator" (Windows)
2. **Check file ownership**: Ensure you own the files
3. **Close file managers**: Close Windows Explorer/Finder
4. **Check antivirus**: Temporarily disable antivirus scanning
5. **Move files**: Copy files to a location you have full access to

### Files Locked by Other Applications
**Issue**: Files are being used by another program

**Solutions**:
1. **Close other applications**: Close all programs that might use the files
2. **Check file managers**: Close Windows Explorer/Finder
3. **Restart computer**: If files are still locked
4. **Use Task Manager**: End processes that might be using files
5. **Copy files**: Copy files to a new location

## 🔍 Preview and Validation Issues

### Preview Not Updating
**Issue**: Preview doesn't change when settings are modified

**Solutions**:
1. **Check settings**: Ensure settings are properly configured
2. **Refresh preview**: Click "Refresh" or modify a setting
3. **Restart application**: Close and restart the application
4. **Check file list**: Ensure files are loaded in the list
5. **Clear and reload**: Clear file list and reload files

### Validation Errors
**Error**: Validation shows errors or warnings

**Solutions**:
1. **Read error messages**: Check what the validation is reporting
2. **Fix naming conflicts**: Resolve duplicate names
3. **Check file paths**: Ensure paths are valid
4. **Adjust settings**: Modify naming patterns to avoid conflicts
5. **Use filters**: Filter out problematic files

### Red Warnings in Preview
**Issue**: Files show in red in the preview

**Solutions**:
1. **Check error messages**: Hover over red files for details
2. **Resolve conflicts**: Fix naming conflicts
3. **Check permissions**: Ensure write access to files
4. **Validate changes**: Use the "Validate" button
5. **Adjust settings**: Modify naming patterns

## 💾 Profile and Settings Issues

### Profiles Not Saving
**Issue**: Profiles are not being saved or loaded

**Solutions**:
1. **Check file permissions**: Ensure write access to profile directory
2. **Use descriptive names**: Avoid special characters in profile names
3. **Check disk space**: Ensure sufficient free space
4. **Restart application**: Close and restart the application
5. **Clear profiles**: Delete old profiles and create new ones

### Settings Not Persisting
**Issue**: Settings are reset when application restarts

**Solutions**:
1. **Check file permissions**: Ensure write access to settings directory
2. **Save profiles**: Use the profile system to save settings
3. **Check disk space**: Ensure sufficient free space
4. **Restart application**: Close and restart the application
5. **Check antivirus**: Ensure antivirus isn't blocking settings files

## 🔄 Undo Issues

### Undo Not Working
**Issue**: Undo operations are not working

**Solutions**:
1. **Check operation history**: Ensure operations were logged
2. **Use correct undo type**: Try "Undo Last" vs "Undo Selected"
3. **Check file permissions**: Ensure write access to files
4. **Restart application**: Close and restart the application
5. **Check backup files**: Ensure backup files exist

### Undo History Lost
**Issue**: Undo history is not available

**Solutions**:
1. **Check operation logging**: Ensure logging was enabled
2. **Check disk space**: Ensure sufficient free space for logs
3. **Restart application**: Close and restart the application
4. **Check file permissions**: Ensure write access to log directory
5. **Enable logging**: Ensure operation logging is enabled

## 🌍 Localization Issues

### Language Not Changing
**Issue**: Language setting is not being applied

**Solutions**:
1. **Restart application**: Language changes require restart
2. **Check language files**: Ensure language files exist
3. **Check file permissions**: Ensure read access to language files
4. **Reinstall application**: Reinstall to ensure all files are present
5. **Check system locale**: Ensure system supports the language

### Missing Translations
**Issue**: Some text is not translated

**Solutions**:
1. **Check language files**: Ensure language files are complete
2. **Update application**: Use the latest version
3. **Report issue**: Use the translation request template
4. **Check system locale**: Ensure proper system locale settings
5. **Restart application**: Close and restart the application

## 🔧 Build and Development Issues

### PyInstaller Build Fails
**Error**: PyInstaller build fails with errors

**Solutions**:
1. **Update PyInstaller**: `pip install --upgrade pyinstaller`
2. **Check dependencies**: Ensure all dependencies are installed
3. **Use virtual environment**: Build in a clean virtual environment
4. **Check file paths**: Ensure all referenced files exist
5. **Check Python version**: Ensure compatible Python version

### Executable Not Working
**Issue**: Built executable doesn't work on other systems

**Solutions**:
1. **Test on clean system**: Test on system without Python
2. **Check dependencies**: Ensure all dependencies are included
3. **Use static linking**: Consider static linking for dependencies
4. **Check system requirements**: Ensure target system meets requirements
5. **Include runtime libraries**: Ensure runtime libraries are included

## 🆘 Getting Additional Help

### Before Asking for Help
1. **Check this guide**: Look for your specific issue
2. **Try basic solutions**: Restart application, check permissions
3. **Gather information**: Note error messages and system details
4. **Test with small files**: Try with a small test set first
5. **Check system requirements**: Ensure your system meets requirements

### When Reporting Issues
Include the following information:
- **Operating System**: Windows/macOS/Linux version
- **Python Version**: `python --version` output
- **Application Version**: Version from About dialog
- **Error Messages**: Exact error messages
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **System Information**: RAM, disk space, other relevant details

### Support Channels
- **GitHub Issues**: [Report bugs and issues](https://github.com/dominic-ritzmann/bulk-file-renamer/issues)
- **GitHub Discussions**: [Ask questions and get help](https://github.com/dominic-ritzmann/bulk-file-renamer/discussions)
- **Documentation**: Check other documentation files
- **Community**: Help other users in discussions

## 📝 Common Solutions Summary

### Quick Fixes
1. **Restart application**: Solves many temporary issues
2. **Check file permissions**: Ensure read/write access
3. **Close other applications**: Free up file locks
4. **Use preview**: Always preview before applying changes
5. **Check disk space**: Ensure sufficient free space

### Prevention Tips
1. **Always backup**: Enable backup options for important files
2. **Test with small sets**: Try with a few files first
3. **Use profiles**: Save settings for repeated workflows
4. **Keep updated**: Use the latest version of the application
5. **Read documentation**: Familiarize yourself with features

---

**Still having issues?** Check our [FAQ](faq.md) or [report the issue](https://github.com/dominic-ritzmann/bulk-file-renamer/issues)!
