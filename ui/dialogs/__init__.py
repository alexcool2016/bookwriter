"""
Dialog module for BookWriter application.
Contains all dialog windows and forms.
"""

from .new_book_dialog import NewBookDialog
from .password_dialog import PasswordDialog
from .find_replace_dialog import FindReplaceDialog

__all__ = ['NewBookDialog', 'PasswordDialog', 'FindReplaceDialog']