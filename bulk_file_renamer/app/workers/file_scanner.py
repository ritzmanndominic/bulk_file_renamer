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


class FileScanner(QThread):
    progress = Signal(int)
    finished = Signal(list)

    def __init__(self, paths):
        super().__init__()
        self.paths = paths
        self._abort = False

    def abort(self):
        self._abort = True

    def run(self):
        collected_files = []
        total = len(self.paths)
        for idx, path in enumerate(self.paths, start=1):
            if self._abort:
                break
            if os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for f in files:
                        if self._abort:
                            break
                        collected_files.append(os.path.join(root, f))
            else:
                collected_files.append(path)
            self.progress.emit(int(idx / total * 100))
        self.finished.emit(collected_files)
