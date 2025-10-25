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

import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
import os
from PySide6.QtCore import qInstallMessageHandler, QtMsgType
from app.bulk_renamer_app import BulkRenamerApp

def qt_message_handler(msg_type, context, message):
    """Filter out Qt geometry warnings for notification bar."""
    # Suppress geometry warnings for notification bar
    if "QWindowsWindow::setGeometry" in message and "CustomNotificationBar" in message:
        return
    
    # Suppress other common Qt warnings that are not critical
    if "QWindowsWindow::setGeometry" in message and "Unable to set geometry" in message:
        return
    
    # Log other messages normally
    if msg_type == QtMsgType.QtDebugMsg:
        logging.debug(message)
    elif msg_type == QtMsgType.QtWarningMsg:
        logging.warning(message)
    elif msg_type == QtMsgType.QtCriticalMsg:
        logging.critical(message)
    elif msg_type == QtMsgType.QtFatalMsg:
        logging.fatal(message)

if __name__ == "__main__":
    # Install custom message handler to filter Qt warnings
    qInstallMessageHandler(qt_message_handler)
    
    app = QApplication(sys.argv)
    # Set application icon for taskbar/dock
    try:
        base = os.path.join(os.path.dirname(__file__), 'assets')
        for fname in ('app.ico', 'app.png', 'app.icns', 'app.svg'):
            p = os.path.join(base, fname)
            if os.path.exists(p):
                app.setWindowIcon(QIcon(p))
                break
    except Exception:
        pass
    window = BulkRenamerApp()
    window.show()
    sys.exit(app.exec())
