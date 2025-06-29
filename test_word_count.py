#!/usr/bin/env python3
"""
Test script to verify the new character counting functionality.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.markdown_processor import MarkdownProcessor

def test_character_counting():
    """Test the new character counting functionality."""
    processor = MarkdownProcessor()
    
    # Test cases
    test_cases = [
        {
            'text': 'Hello World',
            'expected_chars': 10,  # H-e-l-l-o-W-o-r-l-d (space doesn't count)
            'description': 'Simple English text'
        },
        {
            'text': '你好世界',
            'expected_chars': 4,  # 你-好-世-界
            'description': 'Chinese text'
        },
        {
            'text': 'Hello, 世界!',
            'expected_chars': 7,  # H-e-l-l-o-世-界 (comma and exclamation don't count)
            'description': 'Mixed English and Chinese with punctuation'
        },
        {
            'text': '**Bold** and *italic* text',
            'expected_chars': 15,  # Bold and italic text (markdown removed)
            'description': 'Markdown formatted text'
        },
        {
            'text': '# Header\n\nThis is a paragraph with 123 numbers.',
            'expected_chars': 30,  # Header This is a paragraph with 123 numbers
            'description': 'Text with header and numbers'
        }
    ]
    
    print("Testing new character counting functionality:")
    print("=" * 50)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        stats = processor.get_word_count(test_case['text'])
        actual_chars = stats['words']  # 'words' now contains character count
        expected_chars = test_case['expected_chars']
        
        passed = actual_chars == expected_chars
        all_passed = all_passed and passed
        
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"Test {i}: {test_case['description']}")
        print(f"  Text: '{test_case['text']}'")
        print(f"  Expected: {expected_chars} characters")
        print(f"  Actual: {actual_chars} characters")
        print(f"  Status: {status}")
        print()
    
    print("=" * 50)
    if all_passed:
        print("✓ All tests passed! Character counting is working correctly.")
    else:
        print("✗ Some tests failed. Please check the implementation.")
    
    return all_passed

if __name__ == "__main__":
    test_character_counting()