# BookWriter

A professional book writing application with markdown support and AES-256 encryption, built with Python and PyQt6.

## Features

- **Rich Text Editing**: Professional markdown editor with live preview
- **Book Organization**: Organize your work by chapters, characters, world building, and story notes
- **Strong Encryption**: AES-256 encryption to protect your work with password
- **Auto-save**: Automatic saving to prevent data loss
- **Export Options**: Export to markdown format
- **Cross-platform**: Works on Windows, macOS, and Linux

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)

### Install Dependencies

1. Clone or download this repository
2. Navigate to the project directory
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Required Packages

- PyQt6 >= 6.4.0
- cryptography >= 3.4.8
- markdown >= 3.4.1
- Pygments >= 2.12.0
- python-markdown-math >= 0.8

## Usage

### Starting the Application

Run the main application file:

```bash
python main.py
```

### Creating a New Book

1. Click "New Book" or use File → New Book
2. Enter book title, author, and genre
3. Click OK to create the book

### Opening an Existing Book

1. Click "Open Book" or use File → Open Book
2. Select a .book file
3. Enter the password if the book is encrypted

### Writing and Editing

- Use the project navigator on the left to organize your book structure
- Add chapters, characters, world building elements, and story notes
- Create multiple story notes using the "+ Note" button for ideas, plot points, and research
- Use the rich text editor with markdown formatting tools
- Preview your work in real-time on the right panel

### Saving Your Work

- Use Ctrl+S or File → Save to save your book
- Choose whether to encrypt with a password when saving
- The application auto-saves every 30 seconds by default

### Security Features

- **Password Protection**: Encrypt your entire book with a password
- **AES-256 Encryption**: Military-grade encryption for your data
- **Change Password**: Update your book's password anytime
- **Secure Storage**: All data is encrypted at rest

## File Format

BookWriter uses a custom `.book` file format:

- **Encrypted**: Files are encrypted with AES-256-GCM
- **Compressed**: Content is compressed using zlib
- **Structured**: JSON-based internal structure for flexibility

## Keyboard Shortcuts

### File Operations
- `Ctrl+N` - New Book
- `Ctrl+O` - Open Book
- `Ctrl+S` - Save Book
- `Ctrl+Shift+S` - Save As

### Editing
- `Ctrl+Z` - Undo
- `Ctrl+Y` - Redo
- `Ctrl+X` - Cut
- `Ctrl+C` - Copy
- `Ctrl+V` - Paste
- `Ctrl+F` - Find and Replace

### Formatting
- `Ctrl+B` - Bold
- `Ctrl+I` - Italic
- `Ctrl+1` - Header 1
- `Ctrl+2` - Header 2
- `Ctrl+3` - Header 3

## Project Structure

```
bookwriter/
├── main.py                 # Application entry point
├── core/                   # Core business logic
│   ├── book.py            # Book data models
│   ├── encryption.py      # AES encryption engine
│   └── file_manager.py    # File operations
├── ui/                     # User interface
│   ├── main_window.py     # Main application window
│   ├── editor_widget.py   # Rich text editor
│   ├── navigator.py       # Project navigation
│   └── dialogs/           # Dialog windows
├── utils/                  # Utilities
│   └── markdown_processor.py  # Markdown processing
├── resources/              # Application resources
│   └── icons/             # Application icons
└── requirements.txt        # Python dependencies
```

## Data Security

BookWriter takes your data security seriously:

- **Local Storage**: All data is stored locally on your computer
- **No Cloud Sync**: Your work never leaves your device
- **Strong Encryption**: AES-256 encryption with PBKDF2 key derivation
- **Secure Deletion**: Overwrite sensitive data in memory
- **Backup Support**: Automatic local backups

## Troubleshooting

### Common Issues

**Application won't start:**
- Ensure Python 3.9+ is installed
- Install all required dependencies: `pip install -r requirements.txt`
- Check for error messages in the console

**Can't open encrypted book:**
- Verify you're entering the correct password
- Check if the file is corrupted
- Try restoring from a backup

**Performance issues:**
- Close unused tabs in the editor
- Reduce auto-save frequency in preferences
- Check available system memory

### Getting Help

If you encounter issues:

1. Check the console output for error messages
2. Verify all dependencies are installed correctly
3. Ensure you have sufficient disk space
4. Try creating a new book to test basic functionality

## Development

### Contributing

This is a complete implementation of a book writing application. To extend or modify:

1. Follow the existing code structure
2. Add new features in appropriate modules
3. Update documentation and tests
4. Maintain backward compatibility with existing .book files

### Architecture

The application follows a modular architecture:

- **Core**: Business logic and data models
- **UI**: User interface components
- **Utils**: Helper functions and utilities
- **Resources**: Static assets and resources

## License

This project is provided as-is for educational and personal use.

## Version History

- **v1.1.0** - Story Notes Enhancement
  - Changed "Story Elements" to "Story Notes"
  - Added ability to create multiple individual story notes
  - Enhanced "+ Note" button functionality
  - Improved note management with title and content editing
  - Auto-save for story notes

- **v1.0.0** - Initial release with core functionality
  - Rich text editing with markdown support
  - AES-256 encryption
  - Book organization features
  - Auto-save and backup
  - Export capabilities