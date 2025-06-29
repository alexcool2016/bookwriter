"""
Editor widget for BookWriter application.
Provides rich text editing with markdown support and formatting tools.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QToolBar, 
    QPushButton, QLabel, QSplitter, QTextBrowser, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QAction, QIcon

from core.book import Chapter
from utils.markdown_processor import MarkdownProcessor


class EditorWidget(QWidget):
    """Rich text editor widget with markdown support."""
    
    # Signals
    content_changed = pyqtSignal()
    
    def __init__(self, chapter: Chapter, markdown_processor: MarkdownProcessor):
        """Initialize the editor widget."""
        super().__init__()
        
        self.chapter = chapter
        self.markdown_processor = markdown_processor
        self._unsaved_changes = False
        
        # Setup UI
        self.setup_ui()
        self.setup_toolbar()
        
        # Load chapter content
        self.text_editor.setPlainText(self.chapter.content)
        
        # Connect signals
        self.text_editor.textChanged.connect(self.on_text_changed)
        self.markdown_processor.markdown_processed.connect(self.update_preview)
        
        # Auto-update timer for preview
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.update_preview_delayed)
        
        # Initial preview update
        self.update_preview_delayed()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter for editor and preview
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.splitter)
        
        # Create editor panel
        editor_panel = QWidget()
        editor_layout = QVBoxLayout(editor_panel)
        editor_layout.setContentsMargins(5, 5, 5, 5)
        
        # Editor title
        self.title_label = QLabel(self.chapter.title or "Untitled Chapter")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        editor_layout.addWidget(self.title_label)
        
        # Text editor
        self.text_editor = QTextEdit()
        self.text_editor.setFont(QFont("Consolas", 12))
        self.text_editor.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        editor_layout.addWidget(self.text_editor)
        
        # Character count label (updated to reflect new counting method)
        self.word_count_label = QLabel(f"Characters: {self.chapter.word_count}")
        self.word_count_label.setStyleSheet("color: gray; font-size: 10px; padding: 2px;")
        editor_layout.addWidget(self.word_count_label)
        
        self.splitter.addWidget(editor_panel)
        
        # Create preview panel
        preview_panel = QWidget()
        preview_layout = QVBoxLayout(preview_panel)
        preview_layout.setContentsMargins(5, 5, 5, 5)
        
        # Preview title
        preview_title = QLabel("Preview")
        preview_title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        preview_layout.addWidget(preview_title)
        
        # Preview browser
        self.preview_browser = QTextBrowser()
        self.preview_browser.setOpenExternalLinks(True)
        preview_layout.addWidget(self.preview_browser)
        
        self.splitter.addWidget(preview_panel)
        
        # Set splitter proportions (60% editor, 40% preview)
        self.splitter.setSizes([600, 400])
    
    def setup_toolbar(self):
        """Setup the formatting toolbar."""
        # Insert toolbar at the top
        toolbar_layout = QHBoxLayout()
        
        # Bold button
        self.bold_btn = QPushButton("B")
        self.bold_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.bold_btn.setFixedSize(30, 30)
        self.bold_btn.setToolTip("Bold (Ctrl+B)")
        self.bold_btn.clicked.connect(lambda: self.apply_formatting("bold"))
        toolbar_layout.addWidget(self.bold_btn)
        
        # Italic button
        self.italic_btn = QPushButton("I")
        self.italic_btn.setFont(QFont("Arial", 10, QFont.Weight.Normal))
        self.italic_btn.setStyleSheet("font-style: italic;")
        self.italic_btn.setFixedSize(30, 30)
        self.italic_btn.setToolTip("Italic (Ctrl+I)")
        self.italic_btn.clicked.connect(lambda: self.apply_formatting("italic"))
        toolbar_layout.addWidget(self.italic_btn)
        
        # Code button
        self.code_btn = QPushButton("< >")
        self.code_btn.setFont(QFont("Consolas", 8))
        self.code_btn.setFixedSize(30, 30)
        self.code_btn.setToolTip("Inline Code")
        self.code_btn.clicked.connect(lambda: self.apply_formatting("code"))
        toolbar_layout.addWidget(self.code_btn)
        
        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.VLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        toolbar_layout.addWidget(separator1)
        
        # Header buttons
        self.h1_btn = QPushButton("H1")
        self.h1_btn.setFixedSize(30, 30)
        self.h1_btn.setToolTip("Header 1 (Ctrl+1)")
        self.h1_btn.clicked.connect(lambda: self.apply_formatting("header1"))
        toolbar_layout.addWidget(self.h1_btn)
        
        self.h2_btn = QPushButton("H2")
        self.h2_btn.setFixedSize(30, 30)
        self.h2_btn.setToolTip("Header 2 (Ctrl+2)")
        self.h2_btn.clicked.connect(lambda: self.apply_formatting("header2"))
        toolbar_layout.addWidget(self.h2_btn)
        
        self.h3_btn = QPushButton("H3")
        self.h3_btn.setFixedSize(30, 30)
        self.h3_btn.setToolTip("Header 3 (Ctrl+3)")
        self.h3_btn.clicked.connect(lambda: self.apply_formatting("header3"))
        toolbar_layout.addWidget(self.h3_btn)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.VLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        toolbar_layout.addWidget(separator2)
        
        # List buttons
        self.ul_btn = QPushButton("• List")
        self.ul_btn.setFixedSize(50, 30)
        self.ul_btn.setToolTip("Unordered List")
        self.ul_btn.clicked.connect(lambda: self.apply_formatting("unordered_list"))
        toolbar_layout.addWidget(self.ul_btn)
        
        self.ol_btn = QPushButton("1. List")
        self.ol_btn.setFixedSize(50, 30)
        self.ol_btn.setToolTip("Ordered List")
        self.ol_btn.clicked.connect(lambda: self.apply_formatting("ordered_list"))
        toolbar_layout.addWidget(self.ol_btn)
        
        # Separator
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.Shape.VLine)
        separator3.setFrameShadow(QFrame.Shadow.Sunken)
        toolbar_layout.addWidget(separator3)
        
        # Quote button
        self.quote_btn = QPushButton("Quote")
        self.quote_btn.setFixedSize(50, 30)
        self.quote_btn.setToolTip("Blockquote")
        self.quote_btn.clicked.connect(lambda: self.apply_formatting("quote"))
        toolbar_layout.addWidget(self.quote_btn)
        
        # Link button
        self.link_btn = QPushButton("Link")
        self.link_btn.setFixedSize(40, 30)
        self.link_btn.setToolTip("Insert Link")
        self.link_btn.clicked.connect(self.insert_link)
        toolbar_layout.addWidget(self.link_btn)
        
        # Image button
        self.image_btn = QPushButton("Image")
        self.image_btn.setFixedSize(50, 30)
        self.image_btn.setToolTip("Insert Image")
        self.image_btn.clicked.connect(self.insert_image)
        toolbar_layout.addWidget(self.image_btn)
        
        # Table button
        self.table_btn = QPushButton("Table")
        self.table_btn.setFixedSize(50, 30)
        self.table_btn.setToolTip("Insert Table")
        self.table_btn.clicked.connect(self.insert_table)
        toolbar_layout.addWidget(self.table_btn)
        
        # Add stretch to push buttons to the left
        toolbar_layout.addStretch()
        
        # Insert toolbar at the beginning of the layout
        self.layout().insertLayout(0, toolbar_layout)
    
    def apply_formatting(self, format_type: str):
        """Apply markdown formatting to selected text."""
        self.markdown_processor.apply_formatting(self.text_editor, format_type)
        self.text_editor.setFocus()
    
    def insert_link(self):
        """Insert a markdown link."""
        from PyQt6.QtWidgets import QInputDialog
        
        # Get link text and URL
        link_text, ok1 = QInputDialog.getText(self, "Insert Link", "Link text:")
        if ok1 and link_text:
            url, ok2 = QInputDialog.getText(self, "Insert Link", "URL:")
            if ok2 and url:
                self.markdown_processor.insert_link(self.text_editor, url, link_text)
        
        self.text_editor.setFocus()
    
    def insert_image(self):
        """Insert a markdown image."""
        from PyQt6.QtWidgets import QInputDialog, QFileDialog
        
        # Get image file
        image_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", 
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp *.svg);;All Files (*)"
        )
        
        if image_path:
            alt_text, ok = QInputDialog.getText(self, "Insert Image", "Alt text:")
            if ok:
                self.markdown_processor.insert_image(self.text_editor, image_path, alt_text)
        
        self.text_editor.setFocus()
    
    def insert_table(self):
        """Insert a markdown table."""
        from PyQt6.QtWidgets import QInputDialog
        
        # Get table dimensions
        rows, ok1 = QInputDialog.getInt(self, "Insert Table", "Number of rows:", 3, 1, 20)
        if ok1:
            cols, ok2 = QInputDialog.getInt(self, "Insert Table", "Number of columns:", 3, 1, 10)
            if ok2:
                self.markdown_processor.insert_table(self.text_editor, rows, cols)
        
        self.text_editor.setFocus()
    
    def on_text_changed(self):
        """Handle text changes in the editor."""
        # Update chapter content
        self.chapter.content = self.text_editor.toPlainText()
        self.chapter.update_word_count(self.markdown_processor)
        
        # Update character count display
        self.word_count_label.setText(f"Characters: {self.chapter.word_count}")
        
        # Mark as having unsaved changes
        self._unsaved_changes = True
        
        # Emit content changed signal
        self.content_changed.emit()
        
        # Schedule preview update
        self.preview_timer.start(500)  # Update preview after 500ms of no typing
    
    def update_preview_delayed(self):
        """Update the preview with a delay."""
        content = self.text_editor.toPlainText()
        html = self.markdown_processor.render_markdown(content)
        
        # Add some basic styling
        styled_html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 20px;
                    color: #333;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    color: #2c3e50;
                    margin-top: 1.5em;
                    margin-bottom: 0.5em;
                }}
                h1 {{ border-bottom: 2px solid #3498db; padding-bottom: 0.3em; }}
                h2 {{ border-bottom: 1px solid #bdc3c7; padding-bottom: 0.2em; }}
                blockquote {{
                    border-left: 4px solid #3498db;
                    margin: 1em 0;
                    padding-left: 1em;
                    color: #7f8c8d;
                }}
                code {{
                    background-color: #f8f9fa;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: Consolas, monospace;
                }}
                pre {{
                    background-color: #f8f9fa;
                    padding: 1em;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 1em 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                    font-weight: bold;
                }}
                ul, ol {{
                    padding-left: 2em;
                }}
                li {{
                    margin-bottom: 0.5em;
                }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        self.preview_browser.setHtml(styled_html)
    
    def update_preview(self, html: str):
        """Update the preview browser with rendered HTML."""
        # This method is called by the markdown processor signal
        pass  # We use update_preview_delayed instead
    
    def has_unsaved_changes(self) -> bool:
        """Check if the editor has unsaved changes."""
        return self._unsaved_changes
    
    def mark_saved(self):
        """Mark the editor as saved."""
        self._unsaved_changes = False
    
    def undo(self):
        """Undo last action."""
        self.text_editor.undo()
    
    def redo(self):
        """Redo last action."""
        self.text_editor.redo()
    
    def cut(self):
        """Cut selected text."""
        self.text_editor.cut()
    
    def copy(self):
        """Copy selected text."""
        self.text_editor.copy()
    
    def paste(self):
        """Paste text."""
        self.text_editor.paste()
    
    def select_all(self):
        """Select all text."""
        self.text_editor.selectAll()
    
    def find_and_replace(self, find_text: str, replace_text: str, 
                        case_sensitive: bool = False, whole_words: bool = False):
        """Find and replace text in the editor."""
        content = self.text_editor.toPlainText()
        new_content = self.markdown_processor.find_and_replace(
            content, find_text, replace_text, case_sensitive, whole_words
        )
        
        if new_content != content:
            self.text_editor.setPlainText(new_content)
            return True
        return False
    
    def show_find_replace(self):
        """Show find and replace dialog."""
        from ui.dialogs.find_replace_dialog import FindReplaceDialog
        
        dialog = FindReplaceDialog(self)
        dialog.find_requested.connect(self.find_text)
        dialog.replace_requested.connect(self.replace_text)
        dialog.replace_all_requested.connect(self.replace_all_text)
        dialog.show()
    
    def find_text(self, text: str, case_sensitive: bool, whole_words: bool):
        """Find text in the editor."""
        # Implementation for finding text
        pass
    
    def replace_text(self, find_text: str, replace_text: str, 
                    case_sensitive: bool, whole_words: bool):
        """Replace current selection with new text."""
        # Implementation for replacing text
        pass
    
    def replace_all_text(self, find_text: str, replace_text: str, 
                        case_sensitive: bool, whole_words: bool):
        """Replace all occurrences of text."""
        if self.find_and_replace(find_text, replace_text, case_sensitive, whole_words):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Replace All", "Text replaced successfully.")
    
    def get_word_count_stats(self) -> dict:
        """Get detailed word count statistics."""
        content = self.text_editor.toPlainText()
        stats = self.markdown_processor.get_word_count(content)
        # Update chapter word count to match the accurate count
        self.chapter.word_count = stats['words']
        return stats
    
    def toggle_preview(self):
        """Toggle the preview panel visibility."""
        preview_widget = self.splitter.widget(1)
        if preview_widget.isVisible():
            preview_widget.hide()
        else:
            preview_widget.show()
    
    def set_font(self, font: QFont):
        """Set the editor font."""
        self.text_editor.setFont(font)
    
    def zoom_in(self):
        """Increase font size."""
        font = self.text_editor.font()
        font.setPointSize(font.pointSize() + 1)
        self.text_editor.setFont(font)
    
    def zoom_out(self):
        """Decrease font size."""
        font = self.text_editor.font()
        if font.pointSize() > 8:
            font.setPointSize(font.pointSize() - 1)
            self.text_editor.setFont(font)
    
    def export_to_html(self, file_path: str) -> bool:
        """Export the current content to HTML."""
        try:
            content = self.text_editor.toPlainText()
            html = self.markdown_processor.render_markdown(content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html)
            return True
        except Exception as e:
            print(f"Error exporting to HTML: {e}")
            return False