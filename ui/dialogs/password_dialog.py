"""
Password dialog for BookWriter application.
Handles password input for encryption/decryption operations.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
    QLabel, QDialogButtonBox, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class PasswordDialog(QDialog):
    """Dialog for password input."""
    
    def __init__(self, parent=None, title="Password", message="Enter password:"):
        """Initialize the password dialog."""
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(350, 150)
        
        self.message = message
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Message label
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Password input
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Enter password...")
        layout.addWidget(self.password_edit)
        
        # Show password checkbox
        self.show_password_cb = QCheckBox("Show password")
        self.show_password_cb.toggled.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password_cb)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Set focus to password field
        self.password_edit.setFocus()
        
        # Connect Enter key to accept
        self.password_edit.returnPressed.connect(self.accept)
    
    def toggle_password_visibility(self, checked):
        """Toggle password visibility."""
        if checked:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
    
    def accept(self):
        """Accept the dialog if password is provided."""
        if not self.password_edit.text():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Missing Password", "Please enter a password.")
            self.password_edit.setFocus()
            return
        
        super().accept()
    
    def get_password(self):
        """Get the password from the dialog."""
        return self.password_edit.text()