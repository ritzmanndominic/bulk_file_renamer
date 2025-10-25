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

import os
from typing import List, Tuple, Optional
from datetime import datetime
from .name_cleaner import clean_filename

def _detect_extension_change(old_name: str, new_name: str) -> bool:
    """Check if the file extension has changed between old and new names."""
    old_ext = os.path.splitext(old_name)[1].lower()
    new_ext = os.path.splitext(new_name)[1].lower()
    return old_ext != new_ext and old_ext != "" and new_ext != ""

def generate_preview(
    file_paths: List[str],
    prefix: str = "",
    suffix: str = "",
    base_name: str = "",
    start_num: Optional[int] = None,
    extensions: Optional[List[str]] = None,
    size_filter: Optional[Tuple[str, float]] = None,
    date_filter: Optional[Tuple[str, datetime]] = None,
    extension_lock: bool = True,
    remove_special_chars: bool = False,
    replace_spaces: bool = False,
    convert_case: bool = False,
    case_type: str = "lowercase",
    remove_accents: bool = False
) -> List[Tuple[str, str, str, str]]:
    
    # Input validation
    if not file_paths:
        return [], []
    
    # Ensure start_num is valid
    if start_num is not None and start_num < 1:
        start_num = 1
    
    # No limit on files - lazy loading will handle performance
    
    # Additional validation: if base_name is provided but no start_num, 
    # we need to handle potential conflicts gracefully
    if base_name and start_num is None:
        # This will create conflicts, but we'll handle them in the preview
        pass

    filtered_files = []
    for fpath in file_paths:
        if not os.path.exists(fpath):
            continue
        if extensions:
            fname = os.path.basename(fpath).lower()
            if not any(fname.endswith(f".{ext}") for ext in extensions):
                continue
        if size_filter:
            fsize = os.path.getsize(fpath)
            op, threshold = size_filter
            if (op == ">" and fsize <= threshold) or \
               (op == "<" and fsize >= threshold) or \
               (op == "=" and fsize != threshold):
                continue
        
        if date_filter:
            op, threshold_date = date_filter
            # Use modification time as it's more reliable across platforms
            file_time = datetime.fromtimestamp(os.path.getmtime(fpath))
            if (op == "before" and file_time >= threshold_date) or \
               (op == "after" and file_time <= threshold_date):
                continue
        
        filtered_files.append(fpath)

    preview_list = []
    # Track planned names case-insensitively to avoid conflicts on Windows/macOS
    planned_names = {}
    planned_names_norm = {}
    # Map each source path to its planned destination (normalized)
    old_to_new_norm = {}

    # Temporarily disable auto-resolve while the feature is in progress
    auto_resolve = False

    # First pass: build planned names dictionary
    temp_count = start_num if start_num is not None else 1
    for fpath in filtered_files:
        try:
            old_name = os.path.basename(fpath)
            # Always use base name if provided, regardless of start number
            # This ensures the preview shows what the user expects
            name_body = base_name if base_name else os.path.splitext(old_name)[0]
            number_part = f"_{temp_count}" if start_num is not None else ""
            
            # Handle extension locking
            if extension_lock:
                # Always preserve the original extension
                ext = os.path.splitext(fpath)[1]
                new_name = f"{prefix}{name_body}{number_part}{suffix}{ext}"
            else:
                # Allow extension changes (original behavior)
                ext = os.path.splitext(fpath)[1]
                new_name = f"{prefix}{name_body}{number_part}{suffix}{ext}"

            # Apply auto-clean transformations
            if any([remove_special_chars, replace_spaces, convert_case, remove_accents]):
                new_name = clean_filename(
                    new_name,
                    remove_special_chars=remove_special_chars,
                    replace_spaces=replace_spaces,
                    convert_case=convert_case,
                    case_type=case_type,
                    remove_accents=remove_accents
                )

            # Ensure new_name is valid
            if not new_name or new_name.strip() == "":
                new_name = old_name  # Fallback to original name

            # Safely add to planned names dictionaries
            if new_name not in planned_names:
                planned_names[new_name] = []
            planned_names[new_name].append(fpath)
            
            key_norm = os.path.normcase(new_name)
            if key_norm not in planned_names_norm:
                planned_names_norm[key_norm] = []
            planned_names_norm[key_norm].append(fpath)
            # Store planned destination path (normalized) for swap-chain detection
            dest_norm = os.path.normcase(os.path.join(os.path.dirname(fpath), new_name))
            old_to_new_norm[fpath] = dest_norm
            if start_num is not None:
                temp_count += 1
        except Exception:
            # Skip problematic files to prevent crashes
            continue

    # Second pass: create preview list with proper numbering
    count = start_num if start_num is not None else 1
    for fpath in filtered_files:
        try:
            old_name = os.path.basename(fpath)
            # Always use base name if provided, regardless of start number
            # This ensures the preview shows what the user expects
            name_body = base_name if base_name else os.path.splitext(old_name)[0]
            number_part = f"_{count}" if start_num is not None else ""
        
            # Handle extension locking (same logic as above)
            if extension_lock:
                # Always preserve the original extension
                ext = os.path.splitext(fpath)[1]
                new_name = f"{prefix}{name_body}{number_part}{suffix}{ext}"
            else:
                # Allow extension changes (original behavior)
                ext = os.path.splitext(fpath)[1]
                new_name = f"{prefix}{name_body}{number_part}{suffix}{ext}"

            # Apply auto-clean transformations (same as in first loop)
            if any([remove_special_chars, replace_spaces, convert_case, remove_accents]):
                new_name = clean_filename(
                    new_name,
                    remove_special_chars=remove_special_chars,
                    replace_spaces=replace_spaces,
                    convert_case=convert_case,
                    case_type=case_type,
                    remove_accents=remove_accents
                )
            
            # Ensure new_name is valid
            if not new_name or new_name.strip() == "":
                new_name = old_name  # Fallback to original name
                
            new_path = os.path.join(os.path.dirname(fpath), new_name)

            # Treat case-only changes as valid (especially on case-insensitive filesystems)
            if os.path.normcase(old_name) == os.path.normcase(new_name) and old_name != new_name:
                status = "Ready"
            elif old_name == new_name:
                status = "No Change"
            elif extension_lock and _detect_extension_change(old_name, new_name):
                status = "Extension Locked"
            elif os.path.normcase(new_name) in planned_names_norm and len(planned_names_norm[os.path.normcase(new_name)]) > 1:
                # If duplicates exist, ensure they are not just this same file reported multiple times
                entries = planned_names_norm[os.path.normcase(new_name)]
                unique_sources = set()
                for p in entries:
                    try:
                        unique_sources.add(os.path.realpath(p))
                    except Exception:
                        unique_sources.add(p)
                if len(unique_sources) == 1 and os.path.realpath(fpath) in unique_sources:
                    status = "Ready"
                else:
                    status = "Conflict"
            elif os.path.exists(new_path) and os.path.normcase(new_path) != os.path.normcase(fpath):
                # If only case differs and file exists (Windows), allow as Ready
                try:
                    if os.path.samefile(new_path, fpath):
                        status = "Ready"
                    else:
                        # If the path is currently occupied by another source file that will be renamed away
                        norm_target = os.path.normcase(new_path)
                        occupied_planned = None
                        for src, planned_norm in old_to_new_norm.items():
                            if os.path.normcase(src) == norm_target:
                                occupied_planned = planned_norm
                                break
                        if occupied_planned is not None and occupied_planned != norm_target:
                            status = "Ready"  # swap-chain, safe
                        else:
                            status = "Conflict"
                except Exception:
                    # Fallback: treat as potential swap-chain before marking conflict
                    norm_target = os.path.normcase(new_path)
                    occupied_planned = None
                    for src, planned_norm in old_to_new_norm.items():
                        if os.path.normcase(src) == norm_target:
                            occupied_planned = planned_norm
                            break
                    if occupied_planned is not None and occupied_planned != norm_target:
                        status = "Ready"
                    else:
                        status = "Conflict"
            else:
                status = "Ready"

            # Optional auto-resolve: append counter suggestion for conflicts or no-change
            if status in ("Conflict", "No Change") and auto_resolve:
                base, ext = os.path.splitext(new_name)
                counter = 1
                while True:
                    candidate = f"{base} ({counter}){ext}"
                    candidate_path = os.path.join(os.path.dirname(fpath), candidate)
                    # Check against planned names and filesystem (case-insensitive)
                    if os.path.normcase(candidate) not in planned_names_norm and not os.path.exists(candidate_path):
                        status_with_suggestion = "Conflict|" + candidate
                        preview_list.append((old_name, new_name, status_with_suggestion, fpath))
                        break
                    counter += 1
            else:
                preview_list.append((old_name, new_name, status, fpath))
            if start_num is not None:
                count += 1
        except Exception:
            # Skip problematic files to prevent crashes
            continue

    return preview_list, filtered_files
