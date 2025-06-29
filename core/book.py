"""
Book data model for BookWriter application.
Defines the core Book class and related data structures.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from .encryption import EncryptionEngine


@dataclass
class StoryNote:
    """Represents a story note in the book."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    content: str = ""
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert story note to dictionary."""
        data = asdict(self)
        data['created'] = self.created.isoformat()
        data['modified'] = self.modified.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoryNote':
        """Create story note from dictionary."""
        if 'created' in data and isinstance(data['created'], str):
            data['created'] = datetime.fromisoformat(data['created'])
        if 'modified' in data and isinstance(data['modified'], str):
            data['modified'] = datetime.fromisoformat(data['modified'])
        return cls(**data)


@dataclass
class Character:
    """Represents a character in the book."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    background: str = ""
    attributes: Dict[str, str] = field(default_factory=dict)
    image_path: str = ""
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert character to dictionary."""
        data = asdict(self)
        data['created'] = self.created.isoformat()
        data['modified'] = self.modified.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        """Create character from dictionary."""
        if 'created' in data and isinstance(data['created'], str):
            data['created'] = datetime.fromisoformat(data['created'])
        if 'modified' in data and isinstance(data['modified'], str):
            data['modified'] = datetime.fromisoformat(data['modified'])
        return cls(**data)


@dataclass
class WorldBuilding:
    """Represents world building elements."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    locations: Dict[str, str] = field(default_factory=dict)
    rules: Dict[str, str] = field(default_factory=dict)
    history: str = ""
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert world building to dictionary."""
        data = asdict(self)
        data['created'] = self.created.isoformat()
        data['modified'] = self.modified.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorldBuilding':
        """Create world building from dictionary."""
        if 'created' in data and isinstance(data['created'], str):
            data['created'] = datetime.fromisoformat(data['created'])
        if 'modified' in data and isinstance(data['modified'], str):
            data['modified'] = datetime.fromisoformat(data['modified'])
        return cls(**data)


@dataclass
class Chapter:
    """Represents a chapter in the book."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    content: str = ""
    order: int = 0
    word_count: int = 0
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)
    
    def update_word_count(self, markdown_processor=None):
        """Update the word count based on content."""
        if markdown_processor:
            # Use markdown processor for accurate word count
            stats = markdown_processor.get_word_count(self.content)
            self.word_count = stats['words']
        else:
            # Fallback to character count with basic markdown stripping
            import re
            import string
            import unicodedata
            
            # Remove common markdown formatting
            text = self.content
            # Remove headers
            text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
            # Remove bold and italic
            text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
            text = re.sub(r'\*([^*]+)\*', r'\1', text)
            text = re.sub(r'__([^_]+)__', r'\1', text)
            text = re.sub(r'_([^_]+)_', r'\1', text)
            # Remove strikethrough
            text = re.sub(r'~~([^~]+)~~', r'\1', text)
            # Remove inline code
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
            
            # Count characters (excluding punctuation and spaces)
            char_count = 0
            for char in text:
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
            
            self.word_count = char_count
        
        self.modified = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chapter to dictionary."""
        data = asdict(self)
        data['created'] = self.created.isoformat()
        data['modified'] = self.modified.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Chapter':
        """Create chapter from dictionary."""
        if 'created' in data and isinstance(data['created'], str):
            data['created'] = datetime.fromisoformat(data['created'])
        if 'modified' in data and isinstance(data['modified'], str):
            data['modified'] = datetime.fromisoformat(data['modified'])
        return cls(**data)


class Book:
    """Main book class that contains all book data and manages encryption."""
    
    def __init__(self, title: str = "", author: str = "", genre: str = ""):
        """Initialize a new book."""
        self.id = str(uuid.uuid4())
        self.title = title
        self.author = author
        self.genre = genre
        self.created = datetime.now()
        self.modified = datetime.now()
        
        # Book content
        self.chapters: List[Chapter] = []
        self.characters: List[Character] = []
        self.world_building: List[WorldBuilding] = []
        self.story_notes: List[StoryNote] = []
        
        # Additional writing elements (kept for backward compatibility)
        self.story_background = ""
        self.plot_outline = ""
        self.research_notes = ""
        self.timeline = ""
        
        # Metadata
        self.metadata: Dict[str, Any] = {
            "language": "en",
            "target_audience": "",
            "estimated_pages": 0,
            "status": "draft",
            "tags": []
        }
        
        # File management
        self.file_path: Optional[str] = None
        self.is_encrypted = False
        self._encryption_engine = EncryptionEngine()
    
    def add_chapter(self, title: str = "", content: str = "") -> Chapter:
        """Add a new chapter to the book."""
        chapter = Chapter(
            title=title,
            content=content,
            order=len(self.chapters)
        )
        chapter.update_word_count()
        self.chapters.append(chapter)
        self.modified = datetime.now()
        return chapter
    
    def remove_chapter(self, chapter_id: str) -> bool:
        """Remove a chapter by ID."""
        for i, chapter in enumerate(self.chapters):
            if chapter.id == chapter_id:
                del self.chapters[i]
                # Reorder remaining chapters
                for j, remaining_chapter in enumerate(self.chapters[i:], i):
                    remaining_chapter.order = j
                self.modified = datetime.now()
                return True
        return False
    
    def add_character(self, name: str = "") -> Character:
        """Add a new character to the book."""
        character = Character(name=name)
        self.characters.append(character)
        self.modified = datetime.now()
        return character
    
    def remove_character(self, character_id: str) -> bool:
        """Remove a character by ID."""
        for i, character in enumerate(self.characters):
            if character.id == character_id:
                del self.characters[i]
                self.modified = datetime.now()
                return True
        return False
    
    def add_world_building(self, name: str = "") -> WorldBuilding:
        """Add a new world building element."""
        world_element = WorldBuilding(name=name)
        self.world_building.append(world_element)
        self.modified = datetime.now()
        return world_element
    
    def remove_world_building(self, world_id: str) -> bool:
        """Remove a world building element by ID."""
        for i, world_element in enumerate(self.world_building):
            if world_element.id == world_id:
                del self.world_building[i]
                self.modified = datetime.now()
                return True
        return False
    
    def add_story_note(self, title: str = "", content: str = "") -> StoryNote:
        """Add a new story note to the book."""
        story_note = StoryNote(title=title, content=content)
        self.story_notes.append(story_note)
        self.modified = datetime.now()
        return story_note
    
    def remove_story_note(self, note_id: str) -> bool:
        """Remove a story note by ID."""
        for i, note in enumerate(self.story_notes):
            if note.id == note_id:
                del self.story_notes[i]
                self.modified = datetime.now()
                return True
        return False
    
    def get_total_word_count(self) -> int:
        """Get the total word count of all chapters."""
        return sum(chapter.word_count for chapter in self.chapters)
    
    def refresh_word_counts(self, markdown_processor=None):
        """Refresh word counts for all chapters."""
        for chapter in self.chapters:
            chapter.update_word_count(markdown_processor)
        self.modified = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert book to dictionary for serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'genre': self.genre,
            'created': self.created.isoformat(),
            'modified': self.modified.isoformat(),
            'chapters': [chapter.to_dict() for chapter in self.chapters],
            'characters': [character.to_dict() for character in self.characters],
            'world_building': [wb.to_dict() for wb in self.world_building],
            'story_notes': [note.to_dict() for note in self.story_notes],
            'story_background': self.story_background,
            'plot_outline': self.plot_outline,
            'research_notes': self.research_notes,
            'timeline': self.timeline,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Book':
        """Create book from dictionary."""
        book = cls()
        book.id = data.get('id', str(uuid.uuid4()))
        book.title = data.get('title', '')
        book.author = data.get('author', '')
        book.genre = data.get('genre', '')
        
        # Parse dates
        if 'created' in data:
            book.created = datetime.fromisoformat(data['created'])
        if 'modified' in data:
            book.modified = datetime.fromisoformat(data['modified'])
        
        # Load chapters
        book.chapters = [Chapter.from_dict(ch) for ch in data.get('chapters', [])]
        
        # Load characters
        book.characters = [Character.from_dict(char) for char in data.get('characters', [])]
        
        # Load world building
        book.world_building = [WorldBuilding.from_dict(wb) for wb in data.get('world_building', [])]
        
        # Load story notes
        book.story_notes = [StoryNote.from_dict(note) for note in data.get('story_notes', [])]
        
        # Load additional content
        book.story_background = data.get('story_background', '')
        book.plot_outline = data.get('plot_outline', '')
        book.research_notes = data.get('research_notes', '')
        book.timeline = data.get('timeline', '')
        book.metadata = data.get('metadata', {})
        
        return book
    
    def save_to_file(self, file_path: str, password: str = None):
        """Save book to encrypted file."""
        book_data = self.to_dict()
        
        if password:
            # Encrypt the data
            encrypted_data = self._encryption_engine.encrypt_book_data(book_data, password)
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)
            self.is_encrypted = True
        else:
            # Save as plain JSON (for debugging or unencrypted books)
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(book_data, f, ensure_ascii=False, indent=2)
            self.is_encrypted = False
        
        self.file_path = file_path
    
    @classmethod
    def load_from_file(cls, file_path: str, password: str = None) -> 'Book':
        """Load book from encrypted file."""
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        encryption_engine = EncryptionEngine()
        
        # Try to decrypt if password provided
        if password:
            book_data = encryption_engine.decrypt_book_data(file_data, password)
        else:
            # Try to load as plain JSON
            try:
                import json
                book_data = json.loads(file_data.decode('utf-8'))
            except (UnicodeDecodeError, json.JSONDecodeError):
                raise ValueError("File appears to be encrypted but no password provided")
        
        book = cls.from_dict(book_data)
        book.file_path = file_path
        book.is_encrypted = password is not None
        return book
    
    def change_password(self, old_password: str, new_password: str):
        """Change the password of an encrypted book."""
        if not self.file_path:
            raise ValueError("Book must be saved to file before changing password")
        
        with open(self.file_path, 'rb') as f:
            file_data = f.read()
        
        # Change password using encryption engine
        new_file_data = self._encryption_engine.change_password(file_data, old_password, new_password)
        
        # Write back to file
        with open(self.file_path, 'wb') as f:
            f.write(new_file_data)