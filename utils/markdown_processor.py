"""
Markdown processor for BookWriter application.
Handles markdown rendering, syntax highlighting, and text formatting.
"""

import re
import markdown
from markdown.extensions import codehilite, tables, toc, fenced_code
from typing import Dict, List, Tuple, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QTextDocument, QTextCursor, QTextCharFormat, QFont, QColor
from PyQt6.QtWidgets import QTextEdit


class MarkdownProcessor(QObject):
    """Processes markdown text and provides formatting capabilities."""
    
    # Signal emitted when markdown is processed
    markdown_processed = pyqtSignal(str)
    
    def __init__(self):
        """Initialize the markdown processor."""
        super().__init__()
        
        # Configure markdown with extensions
        self.md = markdown.Markdown(
            extensions=[
                'codehilite',
                'tables',
                'toc',
                'fenced_code',
                'nl2br',
                'sane_lists'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': True
                },
                'toc': {
                    'permalink': True
                }
            }
        )
        
        # Markdown shortcuts mapping
        self.shortcuts = {
            'bold': ('**', '**'),
            'italic': ('*', '*'),
            'code': ('`', '`'),
            'strikethrough': ('~~', '~~'),
            'header1': ('# ', ''),
            'header2': ('## ', ''),
            'header3': ('### ', ''),
            'quote': ('> ', ''),
            'unordered_list': ('- ', ''),
            'ordered_list': ('1. ', ''),
            'link': ('[', '](url)'),
            'image': ('![', '](url)')
        }
    
    def render_markdown(self, text: str) -> str:
        """
        Render markdown text to HTML.
        
        Args:
            text: Markdown text to render
            
        Returns:
            Rendered HTML string
        """
        try:
            html = self.md.convert(text)
            self.markdown_processed.emit(html)
            return html
        except Exception as e:
            print(f"Error rendering markdown: {e}")
            return f"<p>Error rendering markdown: {e}</p>"
    
    def apply_formatting(self, text_edit: QTextEdit, format_type: str) -> bool:
        """
        Apply markdown formatting to selected text in a QTextEdit.
        
        Args:
            text_edit: The QTextEdit widget
            format_type: Type of formatting to apply
            
        Returns:
            True if formatting was applied successfully
        """
        if format_type not in self.shortcuts:
            return False
        
        cursor = text_edit.textCursor()
        
        # Get the formatting markers
        start_marker, end_marker = self.shortcuts[format_type]
        
        if cursor.hasSelection():
            # Apply formatting to selected text
            selected_text = cursor.selectedText()
            
            # Check if text is already formatted
            if self._is_formatted(selected_text, start_marker, end_marker):
                # Remove formatting
                new_text = self._remove_formatting(selected_text, start_marker, end_marker)
            else:
                # Add formatting
                new_text = start_marker + selected_text + end_marker
            
            cursor.insertText(new_text)
        else:
            # Insert formatting markers at cursor position
            if format_type.startswith('header') or format_type in ['quote', 'unordered_list', 'ordered_list']:
                # Line-based formatting
                cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
                cursor.insertText(start_marker)
            else:
                # Inline formatting
                cursor.insertText(start_marker + end_marker)
                # Move cursor between markers
                for _ in range(len(end_marker)):
                    cursor.movePosition(QTextCursor.MoveOperation.Left)
                text_edit.setTextCursor(cursor)
        
        return True
    
    def _is_formatted(self, text: str, start_marker: str, end_marker: str) -> bool:
        """Check if text already has the specified formatting."""
        return text.startswith(start_marker) and text.endswith(end_marker)
    
    def _remove_formatting(self, text: str, start_marker: str, end_marker: str) -> str:
        """Remove formatting markers from text."""
        if self._is_formatted(text, start_marker, end_marker):
            return text[len(start_marker):-len(end_marker) if end_marker else len(text)]
        return text
    
    def insert_link(self, text_edit: QTextEdit, url: str = "", link_text: str = "") -> bool:
        """
        Insert a markdown link at the cursor position.
        
        Args:
            text_edit: The QTextEdit widget
            url: The URL for the link
            link_text: The display text for the link
            
        Returns:
            True if link was inserted successfully
        """
        cursor = text_edit.textCursor()
        
        if not link_text and cursor.hasSelection():
            link_text = cursor.selectedText()
        
        if not link_text:
            link_text = "Link Text"
        
        if not url:
            url = "https://example.com"
        
        link_markdown = f"[{link_text}]({url})"
        cursor.insertText(link_markdown)
        
        return True
    
    def insert_image(self, text_edit: QTextEdit, image_path: str = "", alt_text: str = "") -> bool:
        """
        Insert a markdown image at the cursor position.
        
        Args:
            text_edit: The QTextEdit widget
            image_path: Path to the image file
            alt_text: Alternative text for the image
            
        Returns:
            True if image was inserted successfully
        """
        cursor = text_edit.textCursor()
        
        if not alt_text:
            alt_text = "Image"
        
        if not image_path:
            image_path = "path/to/image.png"
        
        image_markdown = f"![{alt_text}]({image_path})"
        cursor.insertText(image_markdown)
        
        return True
    
    def insert_table(self, text_edit: QTextEdit, rows: int = 3, cols: int = 3) -> bool:
        """
        Insert a markdown table at the cursor position.
        
        Args:
            text_edit: The QTextEdit widget
            rows: Number of rows in the table
            cols: Number of columns in the table
            
        Returns:
            True if table was inserted successfully
        """
        cursor = text_edit.textCursor()
        
        # Create table header
        header_cells = ["Header"] * cols
        header_row = "| " + " | ".join(header_cells) + " |"
        
        # Create separator row
        separator_cells = ["---"] * cols
        separator_row = "| " + " | ".join(separator_cells) + " |"
        
        # Create data rows
        data_rows = []
        for i in range(rows - 1):  # -1 because header is already one row
            data_cells = ["Cell"] * cols
            data_row = "| " + " | ".join(data_cells) + " |"
            data_rows.append(data_row)
        
        # Combine all rows
        table_lines = [header_row, separator_row] + data_rows
        table_markdown = "\n".join(table_lines) + "\n"
        
        cursor.insertText(table_markdown)
        
        return True
    
    def get_word_count(self, text: str) -> Dict[str, int]:
        """
        Get word count statistics for the given text.
        按字符计算字数（中英文都算1个），标点符号不算
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with word count statistics
        """
        # Remove markdown formatting for accurate word count
        plain_text = self._strip_markdown(text)
        
        # Count characters (excluding punctuation and spaces)
        # 统计字符数（排除标点符号和空格）
        import string
        import unicodedata
        
        char_count = 0
        for char in plain_text:
            # Skip spaces and common punctuation
            if char.isspace():
                continue
            # Skip ASCII punctuation
            if char in string.punctuation:
                continue
            # Skip Unicode punctuation (including Chinese punctuation)
            if unicodedata.category(char).startswith('P'):
                continue
            # Count valid characters (letters, numbers, Chinese characters, etc.)
            char_count += 1
        
        # Legacy word count for compatibility
        words = len([word for word in plain_text.split() if word.strip()])
        characters = len(plain_text)
        characters_no_spaces = len(plain_text.replace(' ', ''))
        paragraphs = len([p for p in plain_text.split('\n\n') if p.strip()])
        lines = len(plain_text.split('\n'))
        
        return {
            'words': char_count,  # 使用字符数作为字数
            'characters': characters,
            'characters_no_spaces': characters_no_spaces,
            'paragraphs': paragraphs,
            'lines': lines,
            'char_count': char_count  # 新增字符数字段
        }
    
    def _strip_markdown(self, text: str) -> str:
        """Remove markdown formatting from text to get plain text."""
        # Remove headers
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        
        # Remove bold and italic
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        
        # Remove strikethrough
        text = re.sub(r'~~([^~]+)~~', r'\1', text)
        
        # Remove code blocks and inline code
        text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Remove links
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        
        # Remove images
        text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text)
        
        # Remove blockquotes
        text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
        
        # Remove list markers
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # Remove horizontal rules
        text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
        
        return text.strip()
    
    def find_and_replace(self, text: str, find_text: str, replace_text: str, 
                        case_sensitive: bool = False, whole_words: bool = False) -> str:
        """
        Find and replace text with optional case sensitivity and whole word matching.
        
        Args:
            text: Text to search in
            find_text: Text to find
            replace_text: Text to replace with
            case_sensitive: Whether to match case
            whole_words: Whether to match whole words only
            
        Returns:
            Text with replacements made
        """
        if not find_text:
            return text
        
        flags = 0 if case_sensitive else re.IGNORECASE
        
        if whole_words:
            pattern = r'\b' + re.escape(find_text) + r'\b'
        else:
            pattern = re.escape(find_text)
        
        return re.sub(pattern, replace_text, text, flags=flags)
    
    def get_outline(self, text: str) -> List[Dict[str, any]]:
        """
        Extract document outline from markdown headers.
        
        Args:
            text: Markdown text to analyze
            
        Returns:
            List of header information with level, text, and line number
        """
        outline = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Match markdown headers
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if header_match:
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                outline.append({
                    'level': level,
                    'title': title,
                    'line': line_num
                })
        
        return outline