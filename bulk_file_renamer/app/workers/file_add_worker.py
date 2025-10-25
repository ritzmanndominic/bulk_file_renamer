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
from PySide6.QtCore import QThread, Signal

class FileAddWorker(QThread):
    progress = Signal(int)  # emits progress percentage
    finished = Signal(list, int)  # emits list of newly added file paths and duplicate count

    def __init__(self, paths, existing_files=None):
        super().__init__()
        self.paths = paths
        # Normalize existing files for consistent comparison
        self.existing_files = set(os.path.normpath(f) for f in (existing_files or []))

    def run(self):
        added_files = []
        duplicate_count = 0
        total_paths = len(self.paths)
        
        for idx, path in enumerate(self.paths, start=1):
            if os.path.isfile(path):
                # Normalize path for consistent comparison
                normalized_path = os.path.normpath(path)
                if normalized_path not in self.existing_files:
                    added_files.append(normalized_path)
                    self.existing_files.add(normalized_path)
                else:
                    duplicate_count += 1
            elif os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for f in files:
                        full_path = os.path.join(root, f)
                        # Normalize path for consistent comparison
                        normalized_path = os.path.normpath(full_path)
                        if normalized_path not in self.existing_files:
                            added_files.append(normalized_path)
                            self.existing_files.add(normalized_path)
                        else:
                            duplicate_count += 1
            
            # Emit progress
            progress_percent = int((idx / total_paths) * 100)
            self.progress.emit(progress_percent)

        # ✅ Emit *all files at once* (no per-file updates) and duplicate count
        self.finished.emit(added_files, duplicate_count)
