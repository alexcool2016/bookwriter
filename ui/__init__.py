"""
User interface module for BookWriter application.
Contains all GUI components and dialogs.
"""

from .main_window import MainWindow
from .editor_widget import EditorWidget
from .navigator import ProjectNavigator

__all__ = ['MainWindow', 'EditorWidget', 'ProjectNavigator']