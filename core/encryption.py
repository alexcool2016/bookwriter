"""
Encryption module for BookWriter application.
Handles AES-256-GCM encryption and decryption of book files.
"""

import os
import json
import zlib
from typing import Dict, Any, Tuple
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag


class EncryptionEngine:
    """Handles encryption and decryption of book data using AES-256-GCM."""
    
    # File format constants
    MAGIC_NUMBER = b"BOOK"
    VERSION = 1
    SALT_SIZE = 16
    IV_SIZE = 12
    KEY_SIZE = 32
    ITERATIONS = 100000
    
    def __init__(self):
        """Initialize the encryption engine."""
        pass
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derive encryption key from password using PBKDF2.
        
        Args:
            password: User password
            salt: Random salt bytes
            
        Returns:
            Derived key bytes
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=salt,
            iterations=self.ITERATIONS,
        )
        return kdf.derive(password.encode('utf-8'))
    
    def encrypt_book_data(self, book_data: Dict[str, Any], password: str) -> bytes:
        """
        Encrypt book data with password protection.
        
        Args:
            book_data: Dictionary containing all book information
            password: User password for encryption
            
        Returns:
            Encrypted file bytes
            
        Raises:
            ValueError: If password is empty or data is invalid
        """
        if not password:
            raise ValueError("Password cannot be empty")
        
        if not book_data:
            raise ValueError("Book data cannot be empty")
        
        # Generate random salt and IV
        salt = os.urandom(self.SALT_SIZE)
        iv = os.urandom(self.IV_SIZE)
        
        # Derive encryption key
        key = self._derive_key(password, salt)
        
        # Serialize and compress data
        json_data = json.dumps(book_data, ensure_ascii=False, indent=2)
        compressed_data = zlib.compress(json_data.encode('utf-8'))
        
        # Encrypt data
        aesgcm = AESGCM(key)
        encrypted_data = aesgcm.encrypt(iv, compressed_data, None)
        
        # Build file header
        header = (
            self.MAGIC_NUMBER +
            self.VERSION.to_bytes(4, 'little') +
            salt +
            iv
        )
        
        return header + encrypted_data
    
    def decrypt_book_data(self, file_data: bytes, password: str) -> Dict[str, Any]:
        """
        Decrypt book data from encrypted file.
        
        Args:
            file_data: Encrypted file bytes
            password: User password for decryption
            
        Returns:
            Decrypted book data dictionary
            
        Raises:
            ValueError: If file format is invalid or password is wrong
        """
        if len(file_data) < 32:
            raise ValueError("Invalid file format: file too small")
        
        # Parse header
        magic = file_data[:4]
        if magic != self.MAGIC_NUMBER:
            raise ValueError("Invalid file format: wrong magic number")
        
        version = int.from_bytes(file_data[4:8], 'little')
        if version != self.VERSION:
            raise ValueError(f"Unsupported file version: {version}")
        
        salt = file_data[8:24]
        iv = file_data[24:36]
        encrypted_data = file_data[36:]
        
        # Derive decryption key
        key = self._derive_key(password, salt)
        
        try:
            # Decrypt data
            aesgcm = AESGCM(key)
            compressed_data = aesgcm.decrypt(iv, encrypted_data, None)
            
            # Decompress and deserialize
            json_data = zlib.decompress(compressed_data).decode('utf-8')
            book_data = json.loads(json_data)
            
            return book_data
            
        except InvalidTag:
            raise ValueError("Invalid password or corrupted file")
        except (zlib.error, json.JSONDecodeError) as e:
            raise ValueError(f"File corruption detected: {e}")
    
    def change_password(self, file_data: bytes, old_password: str, new_password: str) -> bytes:
        """
        Change the password of an encrypted book file.
        
        Args:
            file_data: Current encrypted file bytes
            old_password: Current password
            new_password: New password
            
        Returns:
            Re-encrypted file bytes with new password
            
        Raises:
            ValueError: If old password is incorrect or new password is empty
        """
        if not new_password:
            raise ValueError("New password cannot be empty")
        
        # Decrypt with old password
        book_data = self.decrypt_book_data(file_data, old_password)
        
        # Re-encrypt with new password
        return self.encrypt_book_data(book_data, new_password)
    
    def verify_password(self, file_data: bytes, password: str) -> bool:
        """
        Verify if a password is correct for a book file.
        
        Args:
            file_data: Encrypted file bytes
            password: Password to verify
            
        Returns:
            True if password is correct, False otherwise
        """
        try:
            self.decrypt_book_data(file_data, password)
            return True
        except ValueError:
            return False