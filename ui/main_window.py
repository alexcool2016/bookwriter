"""
Main window for BookWriter application.
Provides the primary user interface with menu bar, toolbar, and main editing area.
"""

import os
from typing import Dict
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QToolBar, QStatusBar, QTextEdit, QTreeWidget, QTreeWidgetItem,
    QTabWidget, QLabel, QPushButton, QFileDialog, QMessageBox, QInputDialog,
    QProgressBar, QDockWidget, QDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QFont, QPixmap

from core.book import Book, StoryNote
from core.file_manager import FileManager
from utils.markdown_processor import MarkdownProcessor
from ui.editor_widget import EditorWidget
from ui.navigator import ProjectNavigator
from ui.dialogs.new_book_dialog import NewBookDialog
from ui.dialogs.password_dialog import PasswordDialog


class MainWindow(QMainWindow):
    """Main application window."""
    
    # Signals
    book_opened = pyqtSignal(Book)
    book_saved = pyqtSignal(str)
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Initialize components
        self.current_book: Book = None
        self.current_book_password: str = None  # Store password for encrypted books
        self.open_books: Dict[str, Dict[str, any]] = {}  # Store multiple open books
        self.file_manager = FileManager()
        self.markdown_processor = MarkdownProcessor()
        
        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        
        # Setup UI
        self.setup_ui()
        self.setup_menus()
        self.setup_toolbar()
        self.setup_status_bar()
        self.setup_shortcuts()
        
        # Load preferences
        self.load_preferences()
        
        # Show welcome screen
        self.show_welcome_screen()
    
    def setup_ui(self):
        """Setup the main user interface."""
        self.setWindowTitle("BookWriter")
        self.setMinimumSize(1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create main splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # Create project navigator
        self.navigator = ProjectNavigator()
        self.navigator.item_selected.connect(self.on_navigator_item_selected)
        
        # Create navigator dock
        self.navigator_dock = QDockWidget("Project", self)
        self.navigator_dock.setObjectName("ProjectDock")
        self.navigator_dock.setWidget(self.navigator)
        self.navigator_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable |
                                 QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.navigator_dock)
        
        # Create editor area
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.tabCloseRequested.connect(self.close_tab)
        self.main_splitter.addWidget(self.editor_tabs)
        
        # Create properties panel
        self.properties_panel = QWidget()
        self.setup_properties_panel()
        
        # Create properties dock
        self.properties_dock = QDockWidget("Properties", self)
        self.properties_dock.setObjectName("PropertiesDock")
        self.properties_dock.setWidget(self.properties_panel)
        self.properties_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable |
                                   QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_dock)
        
        # Set splitter proportions
        self.main_splitter.setSizes([250, 700, 250])
    
    def setup_properties_panel(self):
        """Setup the properties panel."""
        layout = QVBoxLayout(self.properties_panel)
        
        # Book info section
        self.book_info_label = QLabel("No book open")
        self.book_info_label.setWordWrap(True)
        layout.addWidget(self.book_info_label)
        
        # Character count section
        self.word_count_label = QLabel("Characters: 0")
        layout.addWidget(self.word_count_label)
        
        layout.addStretch()
    
    def setup_menus(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # New book action
        new_action = QAction("&New Book...", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_book)
        file_menu.addAction(new_action)
        
        # Open book action
        open_action = QAction("&Open Book...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_book)
        file_menu.addAction(open_action)
        
        # Recent files submenu
        self.recent_menu = file_menu.addMenu("Recent Books")
        self.update_recent_menu()
        
        file_menu.addSeparator()
        
        # Save action
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.triggered.connect(self.save_book)
        self.save_action.setEnabled(False)
        file_menu.addAction(self.save_action)
        
        # Save as action
        self.save_as_action = QAction("Save &As...", self)
        self.save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.save_as_action.triggered.connect(self.save_book_as)
        self.save_as_action.setEnabled(False)
        file_menu.addAction(self.save_as_action)
        
        file_menu.addSeparator()
        
        # Export action
        self.export_action = QAction("&Export to Markdown...", self)
        self.export_action.triggered.connect(self.export_book)
        self.export_action.setEnabled(False)
        file_menu.addAction(self.export_action)
        
        file_menu.addSeparator()
        
        # Change password action
        self.change_password_action = QAction("Change &Password...", self)
        self.change_password_action.triggered.connect(self.change_password)
        self.change_password_action.setEnabled(False)
        file_menu.addAction(self.change_password_action)
        
        file_menu.addSeparator()
        
        # Book switching submenu
        self.books_menu = file_menu.addMenu("Select Open &Books")
        self.update_books_menu()
        
        # Close book action
        self.close_book_action = QAction("&Close Book", self)
        self.close_book_action.setShortcut(QKeySequence("Ctrl+W"))
        self.close_book_action.triggered.connect(self.close_current_book)
        self.close_book_action.setEnabled(False)
        file_menu.addAction(self.close_book_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        # Undo/Redo actions
        self.undo_action = QAction("&Undo", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.undo_action.triggered.connect(self.undo)
        self.undo_action.setEnabled(False)
        edit_menu.addAction(self.undo_action)
        
        self.redo_action = QAction("&Redo", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.redo_action.triggered.connect(self.redo)
        self.redo_action.setEnabled(False)
        edit_menu.addAction(self.redo_action)
        
        edit_menu.addSeparator()
        
        # Cut/Copy/Paste actions
        self.cut_action = QAction("Cu&t", self)
        self.cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        self.cut_action.triggered.connect(self.cut)
        self.cut_action.setEnabled(False)
        edit_menu.addAction(self.cut_action)
        
        self.copy_action = QAction("&Copy", self)
        self.copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        self.copy_action.triggered.connect(self.copy)
        self.copy_action.setEnabled(False)
        edit_menu.addAction(self.copy_action)
        
        self.paste_action = QAction("&Paste", self)
        self.paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        self.paste_action.triggered.connect(self.paste)
        self.paste_action.setEnabled(False)
        edit_menu.addAction(self.paste_action)
        
        edit_menu.addSeparator()
        
        # Find/Replace action
        self.find_action = QAction("&Find and Replace...", self)
        self.find_action.setShortcut(QKeySequence.StandardKey.Find)
        self.find_action.triggered.connect(self.show_find_replace)
        self.find_action.setEnabled(False)
        edit_menu.addAction(self.find_action)
        
        # Format menu
        format_menu = menubar.addMenu("F&ormat")
        
        # Bold action
        self.bold_action = QAction("&Bold", self)
        self.bold_action.setShortcut(QKeySequence("Ctrl+B"))
        self.bold_action.triggered.connect(lambda: self.apply_formatting("bold"))
        self.bold_action.setEnabled(False)
        format_menu.addAction(self.bold_action)
        
        # Italic action
        self.italic_action = QAction("&Italic", self)
        self.italic_action.setShortcut(QKeySequence("Ctrl+I"))
        self.italic_action.triggered.connect(lambda: self.apply_formatting("italic"))
        self.italic_action.setEnabled(False)
        format_menu.addAction(self.italic_action)
        
        format_menu.addSeparator()
        
        # Header actions
        self.header1_action = QAction("Header &1", self)
        self.header1_action.setShortcut(QKeySequence("Ctrl+1"))
        self.header1_action.triggered.connect(lambda: self.apply_formatting("header1"))
        self.header1_action.setEnabled(False)
        format_menu.addAction(self.header1_action)
        
        self.header2_action = QAction("Header &2", self)
        self.header2_action.setShortcut(QKeySequence("Ctrl+2"))
        self.header2_action.triggered.connect(lambda: self.apply_formatting("header2"))
        self.header2_action.setEnabled(False)
        format_menu.addAction(self.header2_action)
        
        self.header3_action = QAction("Header &3", self)
        self.header3_action.setShortcut(QKeySequence("Ctrl+3"))
        self.header3_action.triggered.connect(lambda: self.apply_formatting("header3"))
        self.header3_action.setEnabled(False)
        format_menu.addAction(self.header3_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Toggle panels
        view_menu.addAction(self.navigator_dock.toggleViewAction())
        view_menu.addAction(self.properties_dock.toggleViewAction())
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        # About action
        about_action = QAction("&About BookWriter", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """Setup the toolbar."""
        toolbar = self.addToolBar("Main")
        toolbar.setObjectName("MainToolBar")
        toolbar.setMovable(False)
        
        # Add actions to toolbar
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
        toolbar.addAction(self.bold_action)
        toolbar.addAction(self.italic_action)
        toolbar.addSeparator()
        toolbar.addAction(self.header1_action)
        toolbar.addAction(self.header2_action)
        toolbar.addAction(self.header3_action)
    
    def setup_status_bar(self):
        """Setup the status bar."""
        self.status_bar = self.statusBar()
        
        # Character count label
        self.status_word_count = QLabel("Characters: 0")
        self.status_bar.addPermanentWidget(self.status_word_count)
        
        # Encryption status
        self.status_encryption = QLabel("Not encrypted")
        self.status_bar.addPermanentWidget(self.status_encryption)
        
        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Additional shortcuts not covered by menu actions
        pass
    
    def load_preferences(self):
        """Load application preferences."""
        preferences = self.file_manager.load_preferences()
        
        # Apply window geometry
        if preferences.get('window_geometry'):
            try:
                geometry_data = bytes.fromhex(preferences['window_geometry'])
                self.restoreGeometry(geometry_data)
            except (ValueError, TypeError):
                pass  # Invalid geometry data, skip
        
        if preferences.get('window_state'):
            try:
                state_data = bytes.fromhex(preferences['window_state'])
                self.restoreState(state_data)
            except (ValueError, TypeError):
                pass  # Invalid state data, skip
        
        # Setup auto-save
        auto_save_interval = preferences.get('auto_save_interval', 30) * 1000  # Convert to ms
        self.auto_save_timer.start(auto_save_interval)
    
    def save_preferences(self):
        """Save application preferences."""
        preferences = self.file_manager.load_preferences()
        preferences['window_geometry'] = self.saveGeometry().data().hex()
        preferences['window_state'] = self.saveState().data().hex()
        self.file_manager.save_preferences(preferences)
    
    def show_welcome_screen(self):
        """Show welcome screen when no book is open."""
        welcome_widget = QWidget()
        layout = QVBoxLayout(welcome_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Welcome message
        welcome_label = QLabel("Welcome to BookWriter")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        welcome_label.setFont(font)
        layout.addWidget(welcome_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        new_button = QPushButton("New Book")
        new_button.clicked.connect(self.new_book)
        button_layout.addWidget(new_button)
        
        open_button = QPushButton("Open Book")
        open_button.clicked.connect(self.open_book)
        button_layout.addWidget(open_button)
        
        layout.addLayout(button_layout)
        
        # Recent files
        recent_files = self.file_manager.get_recent_files()
        if recent_files:
            recent_label = QLabel("Recent Books:")
            layout.addWidget(recent_label)
            
            for file_info in recent_files[:5]:  # Show only first 5
                recent_button = QPushButton(file_info['title'])
                recent_button.clicked.connect(
                    lambda checked, path=file_info['path']: self.open_recent_book(path)
                )
                layout.addWidget(recent_button)
        
        self.editor_tabs.addTab(welcome_widget, "Welcome")
    
    def new_book(self):
        """Create a new book."""
        dialog = NewBookDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            book_info = dialog.get_book_info()
            
            # Create new book
            new_book = Book(
                title=book_info['title'],
                author=book_info['author'],
                genre=book_info['genre']
            )
            
            # Add to open books
            book_key = f"new_book_{len(self.open_books)}"
            self.open_books[book_key] = {
                'book': new_book,
                'password': None,
                'file_path': None
            }
            
            # Switch to new book
            self.switch_to_book(book_key)
            
            # Add initial chapter
            chapter = new_book.add_chapter("Chapter 1")
            # Update word count with markdown processor
            chapter.update_word_count(self.markdown_processor)
            self.open_chapter_editor(chapter)
    
    def open_book(self):
        """Open an existing book."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Book", "", "Book Files (*.book);;All Files (*)"
        )
        
        if file_path:
            self.open_book_file(file_path)
    
    def open_book_file(self, file_path: str):
        """Open a book file with password prompt if needed."""
        # Check if book is already open
        for book_key, book_info in self.open_books.items():
            if book_info.get('file_path') == file_path:
                self.switch_to_book(book_key)
                return
        
        try:
            # Try to determine if file is encrypted
            with open(file_path, 'rb') as f:
                header = f.read(4)
            
            book = None
            password = None
            
            if header == b"BOOK":
                # File is encrypted, prompt for password
                password_dialog = PasswordDialog(self, "Enter Password",
                                               "Enter the password to open this book:")
                if password_dialog.exec() == QDialog.DialogCode.Accepted:
                    password = password_dialog.get_password()
                    try:
                        book = Book.load_from_file(file_path, password)
                    except ValueError as e:
                        QMessageBox.critical(self, "Error", f"Failed to open book: {e}")
                        return
                else:
                    return  # User cancelled password dialog
            else:
                # Try to open as unencrypted
                book = Book.load_from_file(file_path)
            
            if book:
                # Refresh word counts with markdown processor
                book.refresh_word_counts(self.markdown_processor)
                self.file_manager.add_recent_file(file_path, book.title)
                
                # Add to open books
                book_key = file_path
                self.open_books[book_key] = {
                    'book': book,
                    'password': password,
                    'file_path': file_path
                }
                
                # Switch to the opened book
                self.switch_to_book(book_key)
                self.status_bar.showMessage(f"Opened: {book.title}", 3000)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open book: {e}")
    
    def open_recent_book(self, file_path: str):
        """Open a recent book file."""
        if os.path.exists(file_path):
            self.open_book_file(file_path)
        else:
            QMessageBox.warning(self, "File Not Found", 
                              f"The file {file_path} no longer exists.")
            self.file_manager.remove_recent_file(file_path)
            self.update_recent_menu()
    
    def save_book(self):
        """Save the current book."""
        if not self.current_book:
            return
        
        if not self.current_book.file_path:
            self.save_book_as()
        else:
            try:
                # Use stored password for encrypted books
                if self.current_book.is_encrypted and self.current_book_password:
                    self.current_book.save_to_file(self.current_book.file_path, self.current_book_password)
                elif self.current_book.is_encrypted:
                    # Fallback: prompt for password if not stored (shouldn't happen normally)
                    password_dialog = PasswordDialog(self, "Enter Password",
                                                   "Enter the password to save this book:")
                    if password_dialog.exec() == QDialog.DialogCode.Accepted:
                        password = password_dialog.get_password()
                        self.current_book_password = password  # Store for future use
                        # Update the stored password in open_books
                        self._update_book_password(password)
                        self.current_book.save_to_file(self.current_book.file_path, password)
                    else:
                        return  # User cancelled password dialog
                else:
                    # Save without encryption
                    self.current_book.save_to_file(self.current_book.file_path)
                
                # Mark all editor tabs as saved
                self._mark_all_tabs_saved()
                
                self.status_bar.showMessage("Book saved", 3000)
                self.book_saved.emit(self.current_book.file_path)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save book: {e}")
    
    def save_book_as(self):
        """Save the current book with a new name/location."""
        if not self.current_book:
            return
        
        # Get file path
        suggested_name = self.file_manager.get_safe_filename(self.current_book.title)
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Book As", suggested_name, "Book Files (*.book);;All Files (*)"
        )
        
        if file_path:
            # Ask if user wants to encrypt
            reply = QMessageBox.question(
                self, "Encryption", 
                "Do you want to encrypt this book with a password?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            password = None
            if reply == QMessageBox.StandardButton.Yes:
                password_dialog = PasswordDialog(self, "Set Password",
                                               "Enter a password to encrypt this book:")
                if password_dialog.exec() == QDialog.DialogCode.Accepted:
                    password = password_dialog.get_password()
                    self.current_book_password = password  # Store password for future saves
                else:
                    return  # User cancelled password dialog
            else:
                self.current_book_password = None  # No password for unencrypted books
            
            try:
                self.current_book.save_to_file(file_path, password)
                self.file_manager.add_recent_file(file_path, self.current_book.title)
                
                # Update the book info in open_books
                self._update_book_file_path(file_path)
                self.current_book_password = password
                self._update_book_password(password)
                
                # Mark all editor tabs as saved
                self._mark_all_tabs_saved()
                
                self.status_bar.showMessage("Book saved", 3000)
                self.update_ui_for_book()
                self.update_books_menu()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save book: {e}")
    
    def export_book(self):
        """Export the current book to markdown."""
        if not self.current_book:
            return
        
        suggested_name = f"{self.current_book.title}.md"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export to Markdown", suggested_name, "Markdown Files (*.md);;All Files (*)"
        )
        
        if file_path:
            try:
                book_data = self.current_book.to_dict()
                if self.file_manager.export_to_markdown(book_data, file_path):
                    self.status_bar.showMessage("Book exported", 3000)
                    QMessageBox.information(self, "Export Complete", 
                                          f"Book exported to {file_path}")
                else:
                    QMessageBox.critical(self, "Error", "Failed to export book")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export book: {e}")
    
    def change_password(self):
        """Change the password of the current book."""
        if not self.current_book or not self.current_book.file_path:
            return
        
        if not self.current_book.is_encrypted:
            QMessageBox.information(self, "Not Encrypted", 
                                  "This book is not encrypted. Use 'Save As' to encrypt it.")
            return
        
        # Get old password
        old_password_dialog = PasswordDialog(self, "Current Password", 
                                           "Enter the current password:")
        if old_password_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        old_password = old_password_dialog.get_password()
        
        # Get new password
        new_password_dialog = PasswordDialog(self, "New Password", 
                                           "Enter the new password:")
        if new_password_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        new_password = new_password_dialog.get_password()
        
        try:
            self.current_book.change_password(old_password, new_password)
            self.current_book_password = new_password  # Update stored password
            self.status_bar.showMessage("Password changed", 3000)
            QMessageBox.information(self, "Success", "Password changed successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to change password: {e}")
    
    def update_ui_for_book(self):
        """Update UI elements when a book is opened."""
        if self.current_book:
            # Enable actions
            self.save_action.setEnabled(True)
            self.save_as_action.setEnabled(True)
            self.export_action.setEnabled(True)
            self.change_password_action.setEnabled(True)
            self.close_book_action.setEnabled(True)
            
            # Update window title
            self.setWindowTitle(f"BookWriter - {self.current_book.title}")
            
            # Update book info
            info_text = f"<b>{self.current_book.title}</b><br>"
            info_text += f"Author: {self.current_book.author}<br>"
            info_text += f"Genre: {self.current_book.genre}<br>"
            info_text += f"Chapters: {len(self.current_book.chapters)}<br>"
            info_text += f"Characters: {len(self.current_book.characters)}<br>"
            info_text += f"Story Notes: {len(self.current_book.story_notes)}<br>"
            info_text += f"Total Characters: {self.current_book.get_total_word_count()}"
            self.book_info_label.setText(info_text)
            
            # Update encryption status
            if self.current_book.is_encrypted:
                self.status_encryption.setText("Encrypted")
            else:
                self.status_encryption.setText("Not encrypted")
            
            # Clear welcome screen
            if self.editor_tabs.count() > 0 and self.editor_tabs.tabText(0) == "Welcome":
                self.editor_tabs.removeTab(0)
        else:
            # Disable actions
            self.save_action.setEnabled(False)
            self.save_as_action.setEnabled(False)
            self.export_action.setEnabled(False)
            self.change_password_action.setEnabled(False)
            self.close_book_action.setEnabled(False)
            
            # Reset window title
            self.setWindowTitle("BookWriter")
            
            # Reset book info
            self.book_info_label.setText("No book open")
            self.status_encryption.setText("Not encrypted")
            
            # Clear stored password
            self.current_book_password = None
    
    def update_recent_menu(self):
        """Update the recent files menu."""
        self.recent_menu.clear()
        
        recent_files = self.file_manager.get_recent_files()
        if recent_files:
            for file_info in recent_files:
                action = QAction(file_info['title'], self)
                action.triggered.connect(
                    lambda checked, path=file_info['path']: self.open_recent_book(path)
                )
                self.recent_menu.addAction(action)
        else:
            no_recent_action = QAction("No recent files", self)
            no_recent_action.setEnabled(False)
            self.recent_menu.addAction(no_recent_action)
    
    def on_navigator_item_selected(self, item_type: str, item_id: str):
        """Handle navigator item selection."""
        if not self.current_book:
            return
        
        if item_type == "chapter":
            # Find and open chapter
            for chapter in self.current_book.chapters:
                if chapter.id == item_id:
                    self.open_chapter_editor(chapter)
                    break
        elif item_type == "character":
            # Find and open character
            for character in self.current_book.characters:
                if character.id == item_id:
                    self.open_character_editor(character)
                    break
        elif item_type == "world_building":
            # Find and open world building
            for wb in self.current_book.world_building:
                if wb.id == item_id:
                    self.open_world_building_editor(wb)
                    break
        elif item_type == "story_note":
            # Find and open story note
            for note in self.current_book.story_notes:
                if note.id == item_id:
                    self.open_story_note_editor(note)
                    break
        elif item_type == "story_element":
            # Handle story elements (notes, background, plot, timeline)
            self.open_story_element_editor(item_id)
    
    def open_chapter_editor(self, chapter):
        """Open a chapter in the editor."""
        # Check if already open
        for i in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(i)
            if hasattr(widget, 'chapter') and widget.chapter.id == chapter.id:
                self.editor_tabs.setCurrentIndex(i)
                return
        
        # Create new editor
        editor = EditorWidget(chapter, self.markdown_processor)
        editor.content_changed.connect(self.on_content_changed)
        
        self.editor_tabs.addTab(editor, chapter.title or "Untitled Chapter")
        self.editor_tabs.setCurrentWidget(editor)
        
        # Enable edit actions
        self.update_edit_actions(True)
    
    def open_character_editor(self, character):
        """Open a character in the editor."""
        # Implementation for character editing
        pass
    
    def open_world_building_editor(self, world_building):
        """Open world building in the editor."""
        # Implementation for world building editing
        pass
    
    def open_story_note_editor(self, story_note: StoryNote):
        """Open a story note in the editor."""
        # Check if already open
        for i in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(i)
            if hasattr(widget, 'story_note') and widget.story_note.id == story_note.id:
                self.editor_tabs.setCurrentIndex(i)
                return
        
        # Create a simple text editor for story notes
        from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QLabel, QLineEdit
        
        editor_widget = QWidget()
        layout = QVBoxLayout(editor_widget)
        
        # Title editor
        title_label = QLabel("Title:")
        layout.addWidget(title_label)
        
        title_editor = QLineEdit()
        title_editor.setText(story_note.title)
        title_editor.textChanged.connect(
            lambda text: self.save_story_note_title(story_note, text)
        )
        layout.addWidget(title_editor)
        
        # Content editor
        content_label = QLabel("Content:")
        layout.addWidget(content_label)
        
        text_editor = QTextEdit()
        text_editor.setFont(QFont("Consolas", 12))
        text_editor.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        text_editor.setPlainText(story_note.content)
        
        # Connect text changes to save content
        text_editor.textChanged.connect(
            lambda: self.save_story_note_content(story_note, text_editor.toPlainText())
        )
        
        layout.addWidget(text_editor)
        
        # Add editor methods for compatibility
        editor_widget.undo = text_editor.undo
        editor_widget.redo = text_editor.redo
        editor_widget.cut = text_editor.cut
        editor_widget.copy = text_editor.copy
        editor_widget.paste = text_editor.paste
        editor_widget.has_unsaved_changes = lambda: False  # Auto-saves on change
        editor_widget.story_note = story_note  # Store reference for tab management
        
        tab_title = story_note.title or "Untitled Note"
        self.editor_tabs.addTab(editor_widget, tab_title)
        self.editor_tabs.setCurrentWidget(editor_widget)
        
        # Enable edit actions
        self.update_edit_actions(True)
    
    def open_story_element_editor(self, element_type: str):
        """Open a story element editor (notes, background, plot, timeline)."""
        if not self.current_book:
            return
        
        # Check if already open
        tab_title = self.get_story_element_title(element_type)
        for i in range(self.editor_tabs.count()):
            if self.editor_tabs.tabText(i) == tab_title:
                self.editor_tabs.setCurrentIndex(i)
                return
        
        # Create a simple text editor for story elements
        from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QLabel
        
        editor_widget = QWidget()
        layout = QVBoxLayout(editor_widget)
        
        # Title label
        title_label = QLabel(tab_title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(title_label)
        
        # Text editor
        text_editor = QTextEdit()
        text_editor.setFont(QFont("Consolas", 12))
        text_editor.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        # Load existing content
        content = self.get_story_element_content(element_type)
        text_editor.setPlainText(content)
        
        # Connect text changes to save content
        text_editor.textChanged.connect(
            lambda: self.save_story_element_content(element_type, text_editor.toPlainText())
        )
        
        layout.addWidget(text_editor)
        
        # Add editor methods for compatibility
        editor_widget.undo = text_editor.undo
        editor_widget.redo = text_editor.redo
        editor_widget.cut = text_editor.cut
        editor_widget.copy = text_editor.copy
        editor_widget.paste = text_editor.paste
        editor_widget.has_unsaved_changes = lambda: False  # Auto-saves on change
        
        self.editor_tabs.addTab(editor_widget, tab_title)
        self.editor_tabs.setCurrentWidget(editor_widget)
        
        # Enable edit actions
        self.update_edit_actions(True)
    
    def get_story_element_title(self, element_type: str) -> str:
        """Get the display title for a story element type."""
        titles = {
            "background": "Story Background",
            "plot": "Plot Outline",
            "notes": "Research Notes",
            "timeline": "Timeline"
        }
        return titles.get(element_type, "Story Element")
    
    def get_story_element_content(self, element_type: str) -> str:
        """Get the content for a story element type."""
        if not self.current_book:
            return ""
        
        content_map = {
            "background": self.current_book.story_background,
            "plot": self.current_book.plot_outline,
            "notes": self.current_book.research_notes,
            "timeline": self.current_book.timeline
        }
        return content_map.get(element_type, "")
    
    def save_story_element_content(self, element_type: str, content: str):
        """Save content for a story element type."""
        if not self.current_book:
            return
        
        if element_type == "background":
            self.current_book.story_background = content
        elif element_type == "plot":
            self.current_book.plot_outline = content
        elif element_type == "notes":
            self.current_book.research_notes = content
        elif element_type == "timeline":
            self.current_book.timeline = content
        
        # Update modified time
        from datetime import datetime
        self.current_book.modified = datetime.now()
        
        # Refresh navigator to show/hide story elements
        self.navigator.refresh_tree()
    
    def save_story_note_title(self, story_note: StoryNote, title: str):
        """Save title for a story note."""
        if not self.current_book:
            return
        
        from datetime import datetime
        story_note.title = title
        story_note.modified = datetime.now()
        
        # Update modified time
        self.current_book.modified = datetime.now()
        
        # Update tab title
        for i in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(i)
            if hasattr(widget, 'story_note') and widget.story_note.id == story_note.id:
                self.editor_tabs.setTabText(i, title or "Untitled Note")
                break
        
        # Refresh navigator to update the tree
        self.navigator.refresh_tree()
    
    def save_story_note_content(self, story_note: StoryNote, content: str):
        """Save content for a story note."""
        if not self.current_book:
            return
        
        from datetime import datetime
        story_note.content = content
        story_note.modified = datetime.now()
        
        # Update modified time
        self.current_book.modified = datetime.now()
    
    def close_tab(self, index: int):
        """Close a tab in the editor."""
        widget = self.editor_tabs.widget(index)
        if widget:
            # Check if content has unsaved changes
            if hasattr(widget, 'has_unsaved_changes') and widget.has_unsaved_changes():
                reply = QMessageBox.question(
                    self, "Unsaved Changes", 
                    "This document has unsaved changes. Do you want to save before closing?",
                    QMessageBox.StandardButton.Save | 
                    QMessageBox.StandardButton.Discard | 
                    QMessageBox.StandardButton.Cancel
                )
                
                if reply == QMessageBox.StandardButton.Save:
                    self.save_book()
                elif reply == QMessageBox.StandardButton.Cancel:
                    return
            
            self.editor_tabs.removeTab(index)
            
            # Update edit actions
            if self.editor_tabs.count() == 0:
                self.update_edit_actions(False)
    
    def update_edit_actions(self, enabled: bool):
        """Update edit action states."""
        self.undo_action.setEnabled(enabled)
        self.redo_action.setEnabled(enabled)
        self.cut_action.setEnabled(enabled)
        self.copy_action.setEnabled(enabled)
        self.paste_action.setEnabled(enabled)
        self.find_action.setEnabled(enabled)
        self.bold_action.setEnabled(enabled)
        self.italic_action.setEnabled(enabled)
        self.header1_action.setEnabled(enabled)
        self.header2_action.setEnabled(enabled)
        self.header3_action.setEnabled(enabled)
    
    def on_content_changed(self):
        """Handle content changes in editors."""
        # Update word count
        total_words = 0
        if self.current_book:
            total_words = self.current_book.get_total_word_count()
        
        self.word_count_label.setText(f"Characters: {total_words}")
        self.status_word_count.setText(f"Characters: {total_words}")
        
        # Update book info
        if self.current_book:
            self.update_ui_for_book()
    
    def auto_save(self):
        """Auto-save the current book."""
        if self.current_book and self.current_book.file_path:
            try:
                self.save_book()
            except Exception as e:
                print(f"Auto-save failed: {e}")
    
    def undo(self):
        """Undo last action in current editor."""
        current_widget = self.editor_tabs.currentWidget()
        if hasattr(current_widget, 'undo'):
            current_widget.undo()
    
    def redo(self):
        """Redo last action in current editor."""
        current_widget = self.editor_tabs.currentWidget()
        if hasattr(current_widget, 'redo'):
            current_widget.redo()
    
    def cut(self):
        """Cut selected text in current editor."""
        current_widget = self.editor_tabs.currentWidget()
        if hasattr(current_widget, 'cut'):
            current_widget.cut()
    
    def copy(self):
        """Copy selected text in current editor."""
        current_widget = self.editor_tabs.currentWidget()
        if hasattr(current_widget, 'copy'):
            current_widget.copy()
    
    def paste(self):
        """Paste text in current editor."""
        current_widget = self.editor_tabs.currentWidget()
        if hasattr(current_widget, 'paste'):
            current_widget.paste()
    
    def apply_formatting(self, format_type: str):
        """Apply markdown formatting to current editor."""
        current_widget = self.editor_tabs.currentWidget()
        if hasattr(current_widget, 'apply_formatting'):
            current_widget.apply_formatting(format_type)
    
    def show_find_replace(self):
        """Show find and replace dialog."""
        current_widget = self.editor_tabs.currentWidget()
        if hasattr(current_widget, 'show_find_replace'):
            current_widget.show_find_replace()
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, "About BookWriter",
            "<h3>BookWriter 1.0</h3>"
            "<p>A professional book writing application with markdown support and encryption.</p>"
            "<p>Built with Python and PyQt6.</p>"
        )
    
    def closeEvent(self, event):
        """Handle application close event."""
        # Check for unsaved changes
        if self.current_book:
            reply = QMessageBox.question(
                self, "Exit BookWriter",
                "Do you want to save your work before exiting?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_book()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
        
        # Save preferences
        self.save_preferences()
        
        # Accept the close event
        event.accept()
    
    def switch_to_book(self, book_key: str):
        """Switch to a specific book."""
        if book_key not in self.open_books:
            return
        
        book_info = self.open_books[book_key]
        self.current_book = book_info['book']
        self.current_book_password = book_info['password']
        
        # Update UI
        self.update_ui_for_book()
        self.navigator.set_book(self.current_book)
        self.update_books_menu()
        
        # Close all editor tabs and reopen them for the current book
        self.close_all_tabs()
    
    def close_current_book(self):
        """Close the current book."""
        if not self.current_book:
            return
        
        # Find the current book key
        current_book_key = None
        for book_key, book_info in self.open_books.items():
            if book_info['book'] == self.current_book:
                current_book_key = book_key
                break
        
        if current_book_key:
            # Check for unsaved changes in editor tabs or if book needs saving
            has_unsaved = self.has_unsaved_changes()
            
            # Always ask user if they want to save before closing
            if has_unsaved or self.current_book.file_path:
                reply = QMessageBox.question(
                    self, "Close Book",
                    f"Do you want to save '{self.current_book.title}' before closing?",
                    QMessageBox.StandardButton.Save |
                    QMessageBox.StandardButton.Discard |
                    QMessageBox.StandardButton.Cancel
                )
                
                if reply == QMessageBox.StandardButton.Save:
                    # Save the book
                    if not self.current_book.file_path:
                        # New book, need to save as
                        self.save_book_as()
                        # Check if save was cancelled
                        if not self.current_book.file_path:
                            return  # User cancelled save dialog
                    else:
                        self.save_book()
                elif reply == QMessageBox.StandardButton.Cancel:
                    return
                # If Discard is selected, continue with closing
            
            # Remove from open books
            del self.open_books[current_book_key]
            
            # Close all tabs
            self.close_all_tabs()
            
            # Switch to another book if available
            if self.open_books:
                next_book_key = list(self.open_books.keys())[0]
                self.switch_to_book(next_book_key)
            else:
                # No books open, reset UI
                self.current_book = None
                self.current_book_password = None
                self.update_ui_for_book()
                self.navigator.set_book(None)
                self.show_welcome_screen()
            
            self.update_books_menu()
    
    def close_all_tabs(self):
        """Close all editor tabs."""
        while self.editor_tabs.count() > 0:
            self.editor_tabs.removeTab(0)
        self.update_edit_actions(False)
    
    def update_books_menu(self):
        """Update the books menu with currently open books."""
        self.books_menu.clear()
        
        if not self.open_books:
            no_books_action = QAction("No books open", self)
            no_books_action.setEnabled(False)
            self.books_menu.addAction(no_books_action)
            return
        
        for book_key, book_info in self.open_books.items():
            book = book_info['book']
            action_text = book.title or "Untitled Book"
            
            # Add indicator for current book
            if book == self.current_book:
                action_text = f"● {action_text}"
            
            action = QAction(action_text, self)
            action.triggered.connect(lambda checked, key=book_key: self.switch_to_book(key))
            self.books_menu.addAction(action)
    
    def has_unsaved_changes(self) -> bool:
        """Check if the current book has unsaved changes."""
        # Check all open editor tabs for unsaved changes
        for i in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(i)
            if hasattr(widget, 'has_unsaved_changes') and widget.has_unsaved_changes():
                return True
        return False
    
    def _update_book_password(self, password: str):
        """Update the password for the current book in open_books."""
        for book_key, book_info in self.open_books.items():
            if book_info['book'] == self.current_book:
                book_info['password'] = password
                break
    
    def _mark_all_tabs_saved(self):
        """Mark all editor tabs as saved."""
        for i in range(self.editor_tabs.count()):
            widget = self.editor_tabs.widget(i)
            if hasattr(widget, 'mark_saved'):
                widget.mark_saved()
    
    def _update_book_file_path(self, file_path: str):
        """Update the file path for the current book in open_books."""
        for book_key, book_info in self.open_books.items():
            if book_info['book'] == self.current_book:
                book_info['file_path'] = file_path
                break