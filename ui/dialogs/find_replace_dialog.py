"""
Find and replace dialog for BookWriter application.
Provides text search and replacement functionality.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLineEdit, 
    QPushButton, QLabel, QCheckBox, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QKeySequence, QShortcut


class FindReplaceDialog(QDialog):
    """Dialog for find and replace operations."""
    
    # Signals
    find_requested = pyqtSignal(str, bool, bool)  # text, case_sensitive, whole_words
    replace_requested = pyqtSignal(str, str, bool, bool)  # find_text, replace_text, case_sensitive, whole_words
    replace_all_requested = pyqtSignal(str, str, bool, bool)  # find_text, replace_text, case_sensitive, whole_words
    
    def __init__(self, parent=None):
        """Initialize the find and replace dialog."""
        super().__init__(parent)
        
        self.setWindowTitle("Find and Replace")
        self.setModal(False)  # Allow interaction with main window
        self.setFixedSize(400, 200)
        
        self.setup_ui()
        self.setup_shortcuts()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Find and replace inputs
        input_group = QGroupBox("Find and Replace")
        input_layout = QGridLayout(input_group)
        
        # Find field
        input_layout.addWidget(QLabel("Find:"), 0, 0)
        self.find_edit = QLineEdit()
        self.find_edit.setPlaceholderText("Enter text to find...")
        input_layout.addWidget(self.find_edit, 0, 1)
        
        # Replace field
        input_layout.addWidget(QLabel("Replace:"), 1, 0)
        self.replace_edit = QLineEdit()
        self.replace_edit.setPlaceholderText("Enter replacement text...")
        input_layout.addWidget(self.replace_edit, 1, 1)
        
        layout.addWidget(input_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        self.case_sensitive_cb = QCheckBox("Case sensitive")
        options_layout.addWidget(self.case_sensitive_cb)
        
        self.whole_words_cb = QCheckBox("Whole words only")
        options_layout.addWidget(self.whole_words_cb)
        
        layout.addWidget(options_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.find_button = QPushButton("Find Next")
        self.find_button.clicked.connect(self.find_next)
        button_layout.addWidget(self.find_button)
        
        self.replace_button = QPushButton("Replace")
        self.replace_button.clicked.connect(self.replace_current)
        button_layout.addWidget(self.replace_button)
        
        self.replace_all_button = QPushButton("Replace All")
        self.replace_all_button.clicked.connect(self.replace_all)
        button_layout.addWidget(self.replace_all_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Set focus to find field
        self.find_edit.setFocus()
        
        # Connect Enter key to find
        self.find_edit.returnPressed.connect(self.find_next)
        self.replace_edit.returnPressed.connect(self.replace_current)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # F3 for find next
        find_next_shortcut = QShortcut(QKeySequence("F3"), self)
        find_next_shortcut.activated.connect(self.find_next)
        
        # Ctrl+H for replace
        replace_shortcut = QShortcut(QKeySequence("Ctrl+H"), self)
        replace_shortcut.activated.connect(self.replace_current)
        
        # Escape to close
        close_shortcut = QShortcut(QKeySequence("Escape"), self)
        close_shortcut.activated.connect(self.close)
    
    def find_next(self):
        """Find the next occurrence of the search text."""
        find_text = self.find_edit.text()
        if not find_text:
            return
        
        case_sensitive = self.case_sensitive_cb.isChecked()
        whole_words = self.whole_words_cb.isChecked()
        
        self.find_requested.emit(find_text, case_sensitive, whole_words)
    
    def replace_current(self):
        """Replace the current selection."""
        find_text = self.find_edit.text()
        replace_text = self.replace_edit.text()
        
        if not find_text:
            return
        
        case_sensitive = self.case_sensitive_cb.isChecked()
        whole_words = self.whole_words_cb.isChecked()
        
        self.replace_requested.emit(find_text, replace_text, case_sensitive, whole_words)
    
    def replace_all(self):
        """Replace all occurrences."""
        find_text = self.find_edit.text()
        replace_text = self.replace_edit.text()
        
        if not find_text:
            return
        
        case_sensitive = self.case_sensitive_cb.isChecked()
        whole_words = self.whole_words_cb.isChecked()
        
        self.replace_all_requested.emit(find_text, replace_text, case_sensitive, whole_words)
    
    def set_find_text(self, text: str):
        """Set the find text field."""
        self.find_edit.setText(text)
        self.find_edit.selectAll()
    
    def get_find_text(self) -> str:
        """Get the current find text."""
        return self.find_edit.text()
    
    def get_replace_text(self) -> str:
        """Get the current replace text."""
        return self.replace_edit.text()
    
    def is_case_sensitive(self) -> bool:
        """Check if case sensitive option is enabled."""
        return self.case_sensitive_cb.isChecked()
    
    def is_whole_words(self) -> bool:
        """Check if whole words option is enabled."""
        return self.whole_words_cb.isChecked()