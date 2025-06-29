#!/usr/bin/env python3
"""
BookWriter - A professional book writing application with markdown support and encryption.
Main application entry point.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow


def main():
    """Main application entry point."""
    # Create the QApplication instance
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("BookWriter")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("BookWriter")
    app.setOrganizationDomain("bookwriter.app")
    
    # Enable high DPI scaling (PyQt6 handles this automatically)
    # These attributes are not needed in PyQt6 as they're enabled by default
    
    # Set application icon (if available)
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "icons", "app_icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Create and show the main window
    main_window = MainWindow()
    main_window.show()
    
    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()