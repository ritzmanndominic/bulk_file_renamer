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


class FileOperationWorker(QThread):
    progress = Signal(int)
    finished = Signal(list, list, list)  # successes, errors, conflicts

    def __init__(self, file_ops):
        super().__init__()
        self.file_ops = file_ops

    def run(self):
        successes, errors, conflicts = [], [], []
        total = len(self.file_ops)

        for idx, op in enumerate(self.file_ops, start=1):
            old_path, new_path = op["old_path"], op["new_path"]
            try:
                # Check if it's a case-only change on case-insensitive filesystem
                is_case_only_change = (os.path.normcase(old_path) == os.path.normcase(new_path) and 
                                     old_path != new_path)
                
                # Only check for conflicts if it's not a case-only change
                if not is_case_only_change and os.path.exists(new_path) and new_path != old_path:
                    conflicts.append(f"Conflict: {new_path} already exists")
                    continue
                os.rename(old_path, new_path)
                successes.append(op)
            except Exception as e:
                errors.append(f"Failed: {old_path} → {new_path} ({e})")

            self.progress.emit(int(idx / total * 100))

        self.finished.emit(successes, errors, conflicts)
