"""
New book dialog for BookWriter application.
Allows users to create a new book with metadata.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, 
    QTextEdit, QComboBox, QPushButton, QLabel, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class NewBookDialog(QDialog):
    """Dialog for creating a new book."""
    
    def __init__(self, parent=None):
        """Initialize the new book dialog."""
        super().__init__(parent)
        
        self.setWindowTitle("New Book")
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Create New Book")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Book title
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter book title...")
        form_layout.addRow("Title:", self.title_edit)
        
        # Author
        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("Enter author name...")
        form_layout.addRow("Author:", self.author_edit)
        
        # Genre
        self.genre_combo = QComboBox()
        self.genre_combo.setEditable(True)
        self.genre_combo.addItems([
            "Fiction",
            "Non-Fiction",
            "Fantasy",
            "Science Fiction",
            "Mystery",
            "Romance",
            "Thriller",
            "Horror",
            "Biography",
            "History",
            "Self-Help",
            "Poetry",
            "Drama",
            "Adventure",
            "Young Adult",
            "Children's",
            "Other"
        ])
        form_layout.addRow("Genre:", self.genre_combo)
        
        layout.addLayout(form_layout)
        
        # Description
        description_label = QLabel("Description (optional):")
        layout.addWidget(description_label)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Brief description of your book...")
        layout.addWidget(self.description_edit)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Set focus to title field
        self.title_edit.setFocus()
    
    def accept(self):
        """Accept the dialog if title is provided."""
        if not self.title_edit.text().strip():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Missing Title", "Please enter a book title.")
            self.title_edit.setFocus()
            return
        
        super().accept()
    
    def get_book_info(self):
        """Get the book information from the dialog."""
        return {
            'title': self.title_edit.text().strip(),
            'author': self.author_edit.text().strip(),
            'genre': self.genre_combo.currentText().strip(),
            'description': self.description_edit.toPlainText().strip()
        }