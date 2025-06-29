"""
File manager for BookWriter application.
Handles file operations, recent files, and backup management.
"""

import os
import json
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class FileManager:
    """Manages file operations for BookWriter application."""
    
    def __init__(self):
        """Initialize file manager."""
        self.app_data_dir = self._get_app_data_dir()
        self.recent_files_path = os.path.join(self.app_data_dir, "recent_files.json")
        self.preferences_path = os.path.join(self.app_data_dir, "preferences.json")
        self.backup_dir = os.path.join(self.app_data_dir, "backups")
        
        # Ensure directories exist
        os.makedirs(self.app_data_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def _get_app_data_dir(self) -> str:
        """Get the application data directory."""
        if os.name == 'nt':  # Windows
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
            return os.path.join(app_data, 'BookWriter')
        else:  # Unix-like systems
            return os.path.expanduser('~/.bookwriter')
    
    def add_recent_file(self, file_path: str, title: str = ""):
        """Add a file to the recent files list."""
        recent_files = self.get_recent_files()
        
        # Remove if already exists
        recent_files = [f for f in recent_files if f['path'] != file_path]
        
        # Add to beginning
        recent_files.insert(0, {
            'path': file_path,
            'title': title or os.path.basename(file_path),
            'last_opened': datetime.now().isoformat()
        })
        
        # Keep only last 10 files
        recent_files = recent_files[:10]
        
        # Save to file
        try:
            with open(self.recent_files_path, 'w', encoding='utf-8') as f:
                json.dump(recent_files, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving recent files: {e}")
    
    def get_recent_files(self) -> List[Dict[str, str]]:
        """Get the list of recent files."""
        try:
            if os.path.exists(self.recent_files_path):
                with open(self.recent_files_path, 'r', encoding='utf-8') as f:
                    recent_files = json.load(f)
                
                # Filter out files that no longer exist
                existing_files = []
                for file_info in recent_files:
                    if os.path.exists(file_info['path']):
                        existing_files.append(file_info)
                
                # Update the file if any were removed
                if len(existing_files) != len(recent_files):
                    with open(self.recent_files_path, 'w', encoding='utf-8') as f:
                        json.dump(existing_files, f, ensure_ascii=False, indent=2)
                
                return existing_files
        except Exception as e:
            print(f"Error loading recent files: {e}")
        
        return []
    
    def remove_recent_file(self, file_path: str):
        """Remove a file from the recent files list."""
        recent_files = self.get_recent_files()
        recent_files = [f for f in recent_files if f['path'] != file_path]
        
        try:
            with open(self.recent_files_path, 'w', encoding='utf-8') as f:
                json.dump(recent_files, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error updating recent files: {e}")
    
    def save_preferences(self, preferences: Dict[str, Any]):
        """Save application preferences."""
        try:
            with open(self.preferences_path, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def load_preferences(self) -> Dict[str, Any]:
        """Load application preferences."""
        default_preferences = {
            'window_geometry': None,
            'window_state': None,
            'font_family': 'Arial',
            'font_size': 12,
            'theme': 'light',
            'auto_save_interval': 30,  # seconds
            'backup_enabled': True,
            'backup_interval': 300,  # seconds (5 minutes)
            'recent_files_count': 10,
            'spell_check_enabled': True,
            'word_wrap': True,
            'show_line_numbers': False,
            'highlight_current_line': True
        }
        
        try:
            if os.path.exists(self.preferences_path):
                with open(self.preferences_path, 'r', encoding='utf-8') as f:
                    saved_preferences = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    default_preferences.update(saved_preferences)
        except Exception as e:
            print(f"Error loading preferences: {e}")
        
        return default_preferences
    
    def create_backup(self, file_path: str) -> Optional[str]:
        """Create a backup of a book file."""
        if not os.path.exists(file_path):
            return None
        
        try:
            # Generate backup filename with timestamp
            file_name = os.path.basename(file_path)
            name, ext = os.path.splitext(file_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{name}_backup_{timestamp}{ext}"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Copy file to backup directory
            shutil.copy2(file_path, backup_path)
            
            # Clean old backups (keep only last 20)
            self._cleanup_old_backups(name)
            
            return backup_path
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None
    
    def _cleanup_old_backups(self, base_name: str):
        """Clean up old backup files, keeping only the most recent ones."""
        try:
            # Find all backup files for this base name
            backup_files = []
            for file_name in os.listdir(self.backup_dir):
                if file_name.startswith(f"{base_name}_backup_"):
                    file_path = os.path.join(self.backup_dir, file_name)
                    backup_files.append((file_path, os.path.getmtime(file_path)))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old backups (keep only 20 most recent)
            for file_path, _ in backup_files[20:]:
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error removing old backup {file_path}: {e}")
        except Exception as e:
            print(f"Error cleaning up backups: {e}")
    
    def get_backup_files(self, base_name: str) -> List[Dict[str, Any]]:
        """Get list of backup files for a given base name."""
        backup_files = []
        
        try:
            for file_name in os.listdir(self.backup_dir):
                if file_name.startswith(f"{base_name}_backup_"):
                    file_path = os.path.join(self.backup_dir, file_name)
                    stat = os.stat(file_path)
                    backup_files.append({
                        'path': file_path,
                        'name': file_name,
                        'created': datetime.fromtimestamp(stat.st_ctime),
                        'size': stat.st_size
                    })
            
            # Sort by creation time (newest first)
            backup_files.sort(key=lambda x: x['created'], reverse=True)
        except Exception as e:
            print(f"Error getting backup files: {e}")
        
        return backup_files
    
    def restore_backup(self, backup_path: str, target_path: str) -> bool:
        """Restore a backup file to the target location."""
        try:
            shutil.copy2(backup_path, target_path)
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
    
    def validate_file_path(self, file_path: str) -> bool:
        """Validate if a file path is valid for saving."""
        try:
            # Check if directory exists or can be created
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Check if we can write to the location
            test_path = file_path + ".tmp"
            with open(test_path, 'w') as f:
                f.write("test")
            os.remove(test_path)
            
            return True
        except Exception:
            return False
    
    def get_safe_filename(self, title: str) -> str:
        """Generate a safe filename from a book title."""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        safe_title = ''.join(c for c in title if c not in invalid_chars)
        
        # Replace spaces with underscores and limit length
        safe_title = safe_title.replace(' ', '_')[:50]
        
        # Ensure it's not empty
        if not safe_title:
            safe_title = "untitled_book"
        
        return safe_title + ".book"
    
    def export_to_markdown(self, book_data: Dict[str, Any], export_path: str) -> bool:
        """Export book data to markdown format."""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                # Write book metadata
                f.write(f"# {book_data.get('title', 'Untitled Book')}\n\n")
                f.write(f"**Author:** {book_data.get('author', 'Unknown')}\n")
                f.write(f"**Genre:** {book_data.get('genre', 'Unknown')}\n")
                f.write(f"**Created:** {book_data.get('created', '')}\n\n")
                
                # Write story background if exists
                if book_data.get('story_background'):
                    f.write("## Story Background\n\n")
                    f.write(book_data['story_background'])
                    f.write("\n\n")
                
                # Write plot outline if exists
                if book_data.get('plot_outline'):
                    f.write("## Plot Outline\n\n")
                    f.write(book_data['plot_outline'])
                    f.write("\n\n")
                
                # Write chapters
                chapters = book_data.get('chapters', [])
                if chapters:
                    f.write("## Chapters\n\n")
                    for chapter in sorted(chapters, key=lambda x: x.get('order', 0)):
                        f.write(f"### {chapter.get('title', 'Untitled Chapter')}\n\n")
                        f.write(chapter.get('content', ''))
                        f.write("\n\n")
                
                # Write characters
                characters = book_data.get('characters', [])
                if characters:
                    f.write("## Characters\n\n")
                    for character in characters:
                        f.write(f"### {character.get('name', 'Unnamed Character')}\n\n")
                        if character.get('description'):
                            f.write(f"**Description:** {character['description']}\n\n")
                        if character.get('background'):
                            f.write(f"**Background:** {character['background']}\n\n")
                
                # Write world building
                world_building = book_data.get('world_building', [])
                if world_building:
                    f.write("## World Building\n\n")
                    for wb in world_building:
                        f.write(f"### {wb.get('name', 'Unnamed Element')}\n\n")
                        if wb.get('description'):
                            f.write(wb['description'])
                            f.write("\n\n")
            
            return True
        except Exception as e:
            print(f"Error exporting to markdown: {e}")
            return False