"""
Project navigator for BookWriter application.
Displays the book structure in a tree view with chapters, characters, and world building.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QMenu, 
    QInputDialog, QMessageBox, QPushButton, QHBoxLayout, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon

from core.book import Book, Chapter, Character, WorldBuilding, StoryNote


class ProjectNavigator(QWidget):
    """Project navigator widget showing book structure."""
    
    # Signals
    item_selected = pyqtSignal(str, str)  # item_type, item_id
    item_added = pyqtSignal(str, str)     # item_type, item_name
    item_removed = pyqtSignal(str, str)   # item_type, item_id
    
    def __init__(self):
        """Initialize the project navigator."""
        super().__init__()
        
        self.book: Book = None
        self.setup_ui()
        self.setup_context_menu()
    
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Project Structure")
        title_label.setStyleSheet("font-weight: bold; font-size: 12px; padding: 5px;")
        layout.addWidget(title_label)
        
        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self.on_item_clicked)
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.tree)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        self.add_chapter_btn = QPushButton("+ Chapter")
        self.add_chapter_btn.clicked.connect(self.add_chapter)
        self.add_chapter_btn.setEnabled(False)
        button_layout.addWidget(self.add_chapter_btn)
        
        self.add_character_btn = QPushButton("+ Character")
        self.add_character_btn.clicked.connect(self.add_character)
        self.add_character_btn.setEnabled(False)
        button_layout.addWidget(self.add_character_btn)
        
        layout.addLayout(button_layout)
        
        # Second row of buttons
        button_layout2 = QHBoxLayout()
        
        self.add_world_btn = QPushButton("+ World")
        self.add_world_btn.clicked.connect(self.add_world_building)
        self.add_world_btn.setEnabled(False)
        button_layout2.addWidget(self.add_world_btn)
        
        self.add_note_btn = QPushButton("+ Note")
        self.add_note_btn.clicked.connect(self.add_note)
        self.add_note_btn.setEnabled(False)
        button_layout2.addWidget(self.add_note_btn)
        
        layout.addLayout(button_layout2)
        
        # Third row of buttons for chapter ordering
        button_layout3 = QHBoxLayout()
        
        self.move_up_btn = QPushButton("↑ Up")
        self.move_up_btn.clicked.connect(self.move_chapter_up)
        self.move_up_btn.setEnabled(False)
        self.move_up_btn.setToolTip("Move selected chapter up")
        button_layout3.addWidget(self.move_up_btn)
        
        self.move_down_btn = QPushButton("↓ Down")
        self.move_down_btn.clicked.connect(self.move_chapter_down)
        self.move_down_btn.setEnabled(False)
        self.move_down_btn.setToolTip("Move selected chapter down")
        button_layout3.addWidget(self.move_down_btn)
        
        layout.addLayout(button_layout3)
    
    def setup_context_menu(self):
        """Setup context menu for tree items."""
        self.context_menu = QMenu(self)
        
        # Add actions
        self.add_chapter_action = QAction("Add Chapter", self)
        self.add_chapter_action.triggered.connect(self.add_chapter)
        self.context_menu.addAction(self.add_chapter_action)
        
        self.add_character_action = QAction("Add Character", self)
        self.add_character_action.triggered.connect(self.add_character)
        self.context_menu.addAction(self.add_character_action)
        
        self.add_world_action = QAction("Add World Building", self)
        self.add_world_action.triggered.connect(self.add_world_building)
        self.context_menu.addAction(self.add_world_action)
        
        self.context_menu.addSeparator()
        
        # Chapter order actions
        self.move_up_action = QAction("Move Up", self)
        self.move_up_action.triggered.connect(self.move_chapter_up)
        self.context_menu.addAction(self.move_up_action)
        
        self.move_down_action = QAction("Move Down", self)
        self.move_down_action.triggered.connect(self.move_chapter_down)
        self.context_menu.addAction(self.move_down_action)
        
        self.context_menu.addSeparator()
        
        # Edit actions
        self.rename_action = QAction("Rename", self)
        self.rename_action.triggered.connect(self.rename_item)
        self.context_menu.addAction(self.rename_action)
        
        self.delete_action = QAction("Delete", self)
        self.delete_action.triggered.connect(self.delete_item)
        self.context_menu.addAction(self.delete_action)
    
    def set_book(self, book: Book):
        """Set the book to display in the navigator."""
        self.book = book
        self.refresh_tree()
        
        # Enable buttons
        self.add_chapter_btn.setEnabled(True)
        self.add_character_btn.setEnabled(True)
        self.add_world_btn.setEnabled(True)
        self.add_note_btn.setEnabled(True)
    
    def refresh_tree(self):
        """Refresh the tree view with current book data."""
        self.tree.clear()
        
        if not self.book:
            return
        
        # Book root item
        book_item = QTreeWidgetItem([self.book.title or "Untitled Book"])
        book_item.setData(0, Qt.ItemDataRole.UserRole, ("book", self.book.id))
        self.tree.addTopLevelItem(book_item)
        book_item.setExpanded(True)
        
        # Chapters section
        chapters_item = QTreeWidgetItem(["Chapters"])
        chapters_item.setData(0, Qt.ItemDataRole.UserRole, ("section", "chapters"))
        book_item.addChild(chapters_item)
        chapters_item.setExpanded(True)
        
        # Add chapters
        for chapter in sorted(self.book.chapters, key=lambda x: x.order):
            chapter_item = QTreeWidgetItem([chapter.title or "Untitled Chapter"])
            chapter_item.setData(0, Qt.ItemDataRole.UserRole, ("chapter", chapter.id))
            chapter_item.setToolTip(0, f"Characters: {chapter.word_count}")
            chapters_item.addChild(chapter_item)
        
        # Characters section
        characters_item = QTreeWidgetItem(["Characters"])
        characters_item.setData(0, Qt.ItemDataRole.UserRole, ("section", "characters"))
        book_item.addChild(characters_item)
        characters_item.setExpanded(True)
        
        # Add characters
        for character in self.book.characters:
            character_item = QTreeWidgetItem([character.name or "Unnamed Character"])
            character_item.setData(0, Qt.ItemDataRole.UserRole, ("character", character.id))
            character_item.setToolTip(0, character.description[:100] + "..." if len(character.description) > 100 else character.description)
            characters_item.addChild(character_item)
        
        # World Building section
        world_item = QTreeWidgetItem(["World Building"])
        world_item.setData(0, Qt.ItemDataRole.UserRole, ("section", "world_building"))
        book_item.addChild(world_item)
        world_item.setExpanded(True)
        
        # Add world building elements
        for wb in self.book.world_building:
            wb_item = QTreeWidgetItem([wb.name or "Unnamed Element"])
            wb_item.setData(0, Qt.ItemDataRole.UserRole, ("world_building", wb.id))
            wb_item.setToolTip(0, wb.description[:100] + "..." if len(wb.description) > 100 else wb.description)
            world_item.addChild(wb_item)
        
        # Story Notes section
        story_item = QTreeWidgetItem(["Story Notes"])
        story_item.setData(0, Qt.ItemDataRole.UserRole, ("section", "story_notes"))
        book_item.addChild(story_item)
        story_item.setExpanded(True)
        
        # Add individual story notes
        for note in self.book.story_notes:
            note_item = QTreeWidgetItem([note.title or "Untitled Note"])
            note_item.setData(0, Qt.ItemDataRole.UserRole, ("story_note", note.id))
            note_item.setToolTip(0, note.content[:100] + "..." if len(note.content) > 100 else note.content)
            story_item.addChild(note_item)
        
        # Update button states after refreshing
        self.update_button_states()
    
    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            item_type, item_id = data
            if item_type in ["chapter", "character", "world_building", "story_note"]:
                self.item_selected.emit(item_type, item_id)
        
        # Update button states based on selection
        self.update_button_states()
    
    def on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item double click."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            item_type, item_id = data
            if item_type in ["chapter", "character", "world_building", "story_note"]:
                self.item_selected.emit(item_type, item_id)
    
    def show_context_menu(self, position):
        """Show context menu at the given position."""
        item = self.tree.itemAt(position)
        if item:
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data:
                item_type, item_id = data
                
                # Enable/disable actions based on item type
                is_chapter = item_type == "chapter"
                is_editable = item_type in ["chapter", "character", "world_building", "story_note"]
                
                self.rename_action.setEnabled(is_editable)
                self.delete_action.setEnabled(is_editable)
                
                # Chapter order actions only for chapters
                self.move_up_action.setEnabled(is_chapter)
                self.move_down_action.setEnabled(is_chapter)
                
                # Check if chapter can be moved up/down
                if is_chapter and self.book:
                    chapter_index = None
                    for i, chapter in enumerate(self.book.chapters):
                        if chapter.id == item_id:
                            chapter_index = i
                            break
                    
                    if chapter_index is not None:
                        self.move_up_action.setEnabled(chapter_index > 0)
                        self.move_down_action.setEnabled(chapter_index < len(self.book.chapters) - 1)
                
                self.context_menu.exec(self.tree.mapToGlobal(position))
    
    def add_chapter(self):
        """Add a new chapter."""
        if not self.book:
            return
        
        title, ok = QInputDialog.getText(self, "New Chapter", "Chapter title:")
        if ok and title:
            chapter = self.book.add_chapter(title)
            self.refresh_tree()
            self.item_added.emit("chapter", title)
            
            # Select the new chapter
            self.item_selected.emit("chapter", chapter.id)
    
    def add_character(self):
        """Add a new character."""
        if not self.book:
            return
        
        name, ok = QInputDialog.getText(self, "New Character", "Character name:")
        if ok and name:
            character = self.book.add_character(name)
            self.refresh_tree()
            self.item_added.emit("character", name)
            
            # Select the new character
            self.item_selected.emit("character", character.id)
    
    def add_world_building(self):
        """Add a new world building element."""
        if not self.book:
            return
        
        name, ok = QInputDialog.getText(self, "New World Building", "Element name:")
        if ok and name:
            wb = self.book.add_world_building(name)
            self.refresh_tree()
            self.item_added.emit("world_building", name)
            
            # Select the new world building element
            self.item_selected.emit("world_building", wb.id)
    
    def add_note(self):
        """Add a new story note."""
        if not self.book:
            return
        
        title, ok = QInputDialog.getText(self, "New Story Note", "Note title:")
        if ok and title:
            note = self.book.add_story_note(title)
            self.refresh_tree()
            self.item_added.emit("story_note", title)
            
            # Select the new story note
            self.item_selected.emit("story_note", note.id)
    
    def rename_item(self):
        """Rename the selected item."""
        current_item = self.tree.currentItem()
        if not current_item:
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        item_type, item_id = data
        current_name = current_item.text(0)
        
        new_name, ok = QInputDialog.getText(
            self, f"Rename {item_type.title()}", 
            f"New name:", text=current_name
        )
        
        if ok and new_name and new_name != current_name:
            # Update the item in the book
            if item_type == "chapter":
                for chapter in self.book.chapters:
                    if chapter.id == item_id:
                        chapter.title = new_name
                        chapter.modified = chapter.modified.__class__.now()
                        break
            elif item_type == "character":
                for character in self.book.characters:
                    if character.id == item_id:
                        character.name = new_name
                        character.modified = character.modified.__class__.now()
                        break
            elif item_type == "world_building":
                for wb in self.book.world_building:
                    if wb.id == item_id:
                        wb.name = new_name
                        wb.modified = wb.modified.__class__.now()
                        break
            elif item_type == "story_note":
                for note in self.book.story_notes:
                    if note.id == item_id:
                        note.title = new_name
                        note.modified = note.modified.__class__.now()
                        break
            
            # Update the book's modified time
            self.book.modified = self.book.modified.__class__.now()
            
            # Refresh the tree
            self.refresh_tree()
    
    def delete_item(self):
        """Delete the selected item."""
        current_item = self.tree.currentItem()
        if not current_item:
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        item_type, item_id = data
        item_name = current_item.text(0)
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, f"Delete {item_type.title()}", 
            f"Are you sure you want to delete '{item_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove the item from the book
            success = False
            if item_type == "chapter":
                success = self.book.remove_chapter(item_id)
            elif item_type == "character":
                success = self.book.remove_character(item_id)
            elif item_type == "world_building":
                success = self.book.remove_world_building(item_id)
            elif item_type == "story_note":
                success = self.book.remove_story_note(item_id)
            
            if success:
                self.refresh_tree()
                self.item_removed.emit(item_type, item_id)
    
    def move_chapter_up(self):
        """Move the selected chapter up in the order."""
        current_item = self.tree.currentItem()
        if not current_item:
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not data or data[0] != "chapter":
            return
        
        item_type, item_id = data
        
        # Find the chapter and move it up
        for i, chapter in enumerate(self.book.chapters):
            if chapter.id == item_id and i > 0:
                # Swap with previous chapter
                self.book.chapters[i], self.book.chapters[i-1] = self.book.chapters[i-1], self.book.chapters[i]
                
                # Update order numbers
                for j, ch in enumerate(self.book.chapters):
                    ch.order = j
                
                self.book.modified = self.book.modified.__class__.now()
                self.refresh_tree()
                break
    
    def move_chapter_down(self):
        """Move the selected chapter down in the order."""
        current_item = self.tree.currentItem()
        if not current_item:
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not data or data[0] != "chapter":
            return
        
        item_type, item_id = data
        
        # Find the chapter and move it down
        for i, chapter in enumerate(self.book.chapters):
            if chapter.id == item_id and i < len(self.book.chapters) - 1:
                # Swap with next chapter
                self.book.chapters[i], self.book.chapters[i+1] = self.book.chapters[i+1], self.book.chapters[i]
                
                # Update order numbers
                for j, ch in enumerate(self.book.chapters):
                    ch.order = j
                
                self.book.modified = self.book.modified.__class__.now()
                self.refresh_tree()
                break
    
    def get_selected_item(self):
        """Get the currently selected item."""
        current_item = self.tree.currentItem()
        if current_item:
            data = current_item.data(0, Qt.ItemDataRole.UserRole)
            if data:
                return data
        return None
    
    def select_item(self, item_type: str, item_id: str):
        """Select an item in the tree."""
        def find_item(parent_item, target_type, target_id):
            for i in range(parent_item.childCount()):
                child = parent_item.child(i)
                data = child.data(0, Qt.ItemDataRole.UserRole)
                if data and data[0] == target_type and data[1] == target_id:
                    return child
                
                # Recursively search children
                found = find_item(child, target_type, target_id)
                if found:
                    return found
            return None
        
        # Search through all top-level items
        for i in range(self.tree.topLevelItemCount()):
            top_item = self.tree.topLevelItem(i)
            found_item = find_item(top_item, item_type, item_id)
            if found_item:
                self.tree.setCurrentItem(found_item)
                self.tree.scrollToItem(found_item)
                break
    
    def update_button_states(self):
        """Update the state of move up/down buttons based on current selection."""
        current_item = self.tree.currentItem()
        if not current_item or not self.book:
            self.move_up_btn.setEnabled(False)
            self.move_down_btn.setEnabled(False)
            return
        
        data = current_item.data(0, Qt.ItemDataRole.UserRole)
        if not data or data[0] != "chapter":
            self.move_up_btn.setEnabled(False)
            self.move_down_btn.setEnabled(False)
            return
        
        item_type, item_id = data
        
        # Find chapter index
        chapter_index = None
        for i, chapter in enumerate(self.book.chapters):
            if chapter.id == item_id:
                chapter_index = i
                break
        
        if chapter_index is not None:
            self.move_up_btn.setEnabled(chapter_index > 0)
            self.move_down_btn.setEnabled(chapter_index < len(self.book.chapters) - 1)
        else:
            self.move_up_btn.setEnabled(False)
            self.move_down_btn.setEnabled(False)