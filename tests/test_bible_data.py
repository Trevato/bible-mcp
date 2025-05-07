"""
Test suite for the Bible data module.
"""
import pytest
from typing import Dict, List, Optional, Tuple, Union, Any

import bible_data

def test_single_chapter_books():
    """Test single chapter books data."""
    # Verify all single-chapter books are correctly marked
    for book_id in bible_data.SINGLE_CHAPTER_BOOKS:
        assert book_id in bible_data.BIBLE_DATA
        assert bible_data.BIBLE_DATA[book_id]["chapters"] == 1
        
    # Verify all books marked as single-chapter actually have only one chapter
    for book_id, book_data in bible_data.BIBLE_DATA.items():
        if book_data["chapters"] == 1:
            assert book_id in bible_data.SINGLE_CHAPTER_BOOKS

def test_bible_data_structure():
    """Test the structure of the Bible data."""
    # Verify each book has required fields
    for book_id, book_data in bible_data.BIBLE_DATA.items():
        assert "name" in book_data
        assert "testament" in book_data
        assert "chapters" in book_data
        assert book_data["testament"] in (bible_data.OLD_TESTAMENT, bible_data.NEW_TESTAMENT)
        
        # Check chapters and verses
        assert isinstance(book_data["chapters"], int)
        assert book_data["chapters"] > 0
        
        # For single-chapter books
        if book_data["chapters"] == 1:
            assert isinstance(book_data["verses"], int)
            assert book_data["verses"] > 0
        else:
            # For multi-chapter books
            assert isinstance(book_data["verses"], list)
            assert len(book_data["verses"]) == book_data["chapters"]
            for verse_count in book_data["verses"]:
                assert isinstance(verse_count, int)
                assert verse_count > 0

def test_get_random_book():
    """Test getting random books."""
    # Test default (no testament filter)
    book_id = bible_data.get_random_book()
    assert book_id in bible_data.BIBLE_DATA
    
    # Test OT filter
    book_id = bible_data.get_random_book(testament=bible_data.OLD_TESTAMENT)
    assert book_id in bible_data.BIBLE_DATA
    assert bible_data.BIBLE_DATA[book_id]["testament"] == bible_data.OLD_TESTAMENT
    
    # Test NT filter
    book_id = bible_data.get_random_book(testament=bible_data.NEW_TESTAMENT)
    assert book_id in bible_data.BIBLE_DATA
    assert bible_data.BIBLE_DATA[book_id]["testament"] == bible_data.NEW_TESTAMENT
    
    # Test invalid testament
    with pytest.raises(ValueError):
        bible_data.get_random_book(testament="INVALID")

def test_get_random_chapter():
    """Test getting random chapters."""
    # Test valid book
    chapter = bible_data.get_random_chapter("JHN")
    assert 1 <= chapter <= bible_data.BIBLE_DATA["JHN"]["chapters"]
    
    # Test single-chapter book
    chapter = bible_data.get_random_chapter("OBAD")
    assert chapter == 1
    
    # Test invalid book
    with pytest.raises(ValueError):
        bible_data.get_random_chapter("INVALID")

def test_get_random_verse():
    """Test getting random verses."""
    # Test valid book and chapter
    verse = bible_data.get_random_verse("JHN", 3)
    assert 1 <= verse <= bible_data.BIBLE_DATA["JHN"]["verses"][2]  # 0-indexed list
    
    # Test single-chapter book
    verse = bible_data.get_random_verse("OBAD", 1)
    assert 1 <= verse <= bible_data.SINGLE_CHAPTER_BOOKS["OBAD"]
    
    # Test invalid book
    with pytest.raises(ValueError):
        bible_data.get_random_verse("INVALID", 1)
    
    # Test invalid chapter
    with pytest.raises(ValueError):
        bible_data.get_random_verse("JHN", 100)

def test_get_random_reference():
    """Test generating random references."""
    # Test default (no testament filter)
    reference = bible_data.get_random_reference()
    assert ":" in reference  # Should have book chapter:verse format
    
    # Test OT filter
    reference = bible_data.get_random_reference(testament=bible_data.OLD_TESTAMENT)
    assert ":" in reference
    
    # Test NT filter
    reference = bible_data.get_random_reference(testament=bible_data.NEW_TESTAMENT)
    assert ":" in reference

def test_is_valid_reference():
    """Test reference validation."""
    # Test valid references
    assert bible_data.is_valid_reference("JHN", 3, 16) is True
    assert bible_data.is_valid_reference("JHN", 3) is True
    assert bible_data.is_valid_reference("OBAD", 1, 1) is True
    
    # Test invalid book
    assert bible_data.is_valid_reference("INVALID", 1, 1) is False
    
    # Test invalid chapter
    assert bible_data.is_valid_reference("JHN", 100, 1) is False
    
    # Test invalid verse
    assert bible_data.is_valid_reference("JHN", 3, 1000) is False

def test_get_book_testament():
    """Test getting testament for books."""
    # Test OT book
    assert bible_data.get_book_testament("GEN") == bible_data.OLD_TESTAMENT
    
    # Test NT book
    assert bible_data.get_book_testament("JHN") == bible_data.NEW_TESTAMENT
    
    # Test invalid book
    with pytest.raises(ValueError):
        bible_data.get_book_testament("INVALID")

def test_parse_reference():
    """Test parsing reference strings."""
    # Test valid references
    book_id, chapter, verse = bible_data.parse_reference("John 3:16")
    assert book_id == "JHN"
    assert chapter == 3
    assert verse == 16
    
    book_id, chapter, verse = bible_data.parse_reference("Genesis 1")
    assert book_id == "GEN"
    assert chapter == 1
    assert verse is None
    
    # Test invalid reference format
    with pytest.raises(ValueError):
        bible_data.parse_reference("Invalid")
    
    # Test invalid book
    with pytest.raises(ValueError):
        bible_data.parse_reference("InvalidBook 1:1")
    
    # Test invalid chapter/verse
    with pytest.raises(ValueError):
        bible_data.parse_reference("John 999:1")
