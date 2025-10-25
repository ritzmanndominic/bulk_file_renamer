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

# app/utils/name_cleaner.py
import re
import unicodedata
from typing import Optional


def clean_filename(filename: str, 
                  remove_special_chars: bool = False,
                  replace_spaces: bool = False,
                  convert_case: bool = False,
                  case_type: str = "lowercase",
                  remove_accents: bool = False) -> str:
    """
    Clean a filename based on the specified options.
    
    Args:
        filename: The original filename
        remove_special_chars: Remove special characters
        replace_spaces: Replace spaces with underscores
        convert_case: Convert case
        case_type: Type of case conversion ("lowercase", "titlecase", "uppercase")
        remove_accents: Remove accents and normalize characters
    
    Returns:
        The cleaned filename
    """
    if not filename:
        return filename
    
    # Split filename and extension
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    
    # Remove accents first (before other operations)
    if remove_accents:
        name = unicodedata.normalize('NFD', name)
        name = ''.join(char for char in name if unicodedata.category(char) != 'Mn')
    
    # Remove special characters
    if remove_special_chars:
        # Keep alphanumeric, spaces, hyphens, underscores, and dots
        name = re.sub(r'[^\w\s\-\.]', '', name)
        # Remove multiple consecutive special characters
        name = re.sub(r'[^\w\s\-\.]+', '', name)
    
    # Replace spaces with underscores
    if replace_spaces:
        name = name.replace(' ', '_')
        # Remove multiple consecutive underscores
        name = re.sub(r'_+', '_', name)
        # Remove leading/trailing underscores
        name = name.strip('_')
    
    # Convert case
    if convert_case:
        if case_type == "lowercase":
            name = name.lower()
        elif case_type == "UPPERCASE":
            name = name.upper()
        elif case_type == "Title Case":
            name = name.title()
    
    # Clean up any remaining issues
    # Remove multiple consecutive dots
    name = re.sub(r'\.+', '.', name)
    # Remove leading/trailing dots and spaces
    name = name.strip('. ')
    
    # Reconstruct filename
    if ext:
        return f"{name}.{ext}"
    else:
        return name


def get_cleanup_preview(original_name: str, 
                       remove_special_chars: bool = False,
                       replace_spaces: bool = False,
                       convert_case: bool = False,
                       case_type: str = "lowercase",
                       remove_accents: bool = False) -> str:
    """
    Get a preview of how a filename would look after cleaning.
    This is a wrapper around clean_filename for consistency.
    """
    return clean_filename(
        original_name,
        remove_special_chars=remove_special_chars,
        replace_spaces=replace_spaces,
        convert_case=convert_case,
        case_type=case_type,
        remove_accents=remove_accents
    )
