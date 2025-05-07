"""
Test suite for the Bible API client.
"""
import asyncio
import pytest
import httpx
from typing import Dict, Any, Optional, List, Tuple

from bible_api import BibleAPIClient
from bible_data import OLD_TESTAMENT, NEW_TESTAMENT

# Test cases for different scenarios
TEST_CASES = [
    # Basic verses
    {"name": "Standard verse", "reference": "John 3:16", "translation": "web"},
    {"name": "Different translation", "reference": "John 3:16", "translation": "kjv"},
    
    # Edge cases
    {"name": "Single-chapter book", "reference": "Jude 1", "translation": "web"},
    {"name": "Last verse of chapter", "reference": "Genesis 1:31", "translation": "web"},
    {"name": "Verse range", "reference": "Matthew 5:3-10", "translation": "web"},
    {"name": "Verse with comma", "reference": "Matthew 5:3,5,7", "translation": "web"},
    
    # Error cases
    {"name": "Invalid book", "reference": "InvalidBook 1:1", "translation": "web", "expect_error": True},
    {"name": "Invalid chapter", "reference": "John 999:1", "translation": "web", "expect_error": True},
    {"name": "Invalid verse", "reference": "John 3:999", "translation": "web", "expect_error": True},
    {"name": "Invalid translation", "reference": "John 3:16", "translation": "invalid", "expect_error": True},
]

@pytest.mark.asyncio
async def test_get_verse_by_reference():
    """Test getting verses by reference."""
    client = BibleAPIClient()
    
    for test_case in TEST_CASES:
        name = test_case["name"]
        reference = test_case["reference"]
        translation = test_case["translation"]
        expect_error = test_case.get("expect_error", False)
        
        if expect_error:
            with pytest.raises((ValueError, httpx.HTTPStatusError)):
                await client.get_verse_by_reference(reference, translation)
        else:
            result = await client.get_verse_by_reference(reference, translation)
            assert 'reference' in result
            assert 'text' in result
            assert result['text'].strip()

@pytest.mark.asyncio
async def test_get_by_book_chapter_verse():
    """Test getting verses using book, chapter, verse format."""
    client = BibleAPIClient()
    
    # Test valid reference
    result = await client.get_by_book_chapter_verse("web", "JHN", 3, 16)
    assert 'reference' in result
    assert 'text' in result
    assert 'John 3:16' in result['reference']
    
    # Test chapter only
    result = await client.get_by_book_chapter_verse("web", "JHN", 3)
    assert 'reference' in result
    assert 'text' in result
    assert 'John 3' in result['reference']
    
    # Test invalid reference
    with pytest.raises(ValueError):
        await client.get_by_book_chapter_verse("web", "INVALID", 3, 16)

@pytest.mark.asyncio
async def test_get_random_verse():
    """Test getting random verses."""
    client = BibleAPIClient()
    
    # Test default random verse
    result = await client.get_random_verse()
    assert 'reference' in result
    assert 'text' in result
    assert result['text'].strip()
    
    # Test with translation
    result = await client.get_random_verse(translation_id="kjv")
    assert 'reference' in result
    assert 'text' in result
    assert result['translation_name'] == "King James Version"
    
    # Test with OT testament filter
    result = await client.get_random_verse(testament=OLD_TESTAMENT)
    assert 'reference' in result
    assert 'text' in result
    
    # Test with NT testament filter
    result = await client.get_random_verse(testament=NEW_TESTAMENT)
    assert 'reference' in result
    assert 'text' in result
    
    # Test with invalid testament
    with pytest.raises(ValueError):
        await client.get_random_verse(testament="INVALID")

@pytest.mark.asyncio
async def test_list_translations():
    """Test listing available translations."""
    client = BibleAPIClient()
    
    translations = await client.list_translations()
    assert isinstance(translations, list)
    assert len(translations) > 0
    
    # Check translation structure
    for translation in translations:
        assert 'id' in translation
        assert 'name' in translation
        assert 'language' in translation
        
    # Check if default translation exists
    default_translations = [t for t in translations if t.get('default')]
    assert len(default_translations) > 0
