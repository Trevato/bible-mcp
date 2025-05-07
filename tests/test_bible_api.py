"""
Test suite for the Bible API client.
"""
import asyncio
import pytest
import httpx
from unittest.mock import patch, AsyncMock, MagicMock
from typing import Dict, Any, Optional, List, Tuple

from bible_api import BibleAPIClient
from bible_data import OLD_TESTAMENT, NEW_TESTAMENT

# Mock responses for different test cases
MOCK_RESPONSES = {
    "john_3_16": {
        "reference": "John 3:16",
        "verses": [{"book_id": "JHN", "book_name": "John", "chapter": 3, "verse": 16, "text": "For God so loved the world, that he gave his one and only Son, that whoever believes in him should not perish, but have eternal life."}],
        "text": "For God so loved the world, that he gave his one and only Son, that whoever believes in him should not perish, but have eternal life.",
        "translation_id": "web",
        "translation_name": "World English Bible"
    },
    "john_3_16_kjv": {
        "reference": "John 3:16",
        "verses": [{"book_id": "JHN", "book_name": "John", "chapter": 3, "verse": 16, "text": "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life."}],
        "text": "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.",
        "translation_id": "kjv",
        "translation_name": "King James Version"
    },
    "jude_1": {
        "reference": "Jude 1",
        "verses": [{"book_id": "JUD", "book_name": "Jude", "chapter": 1, "verse": 1, "text": "Jude, a servant of Jesus Christ, and brother of James, to those who are called, sanctified by God the Father, and kept for Jesus Christ:"}],
        "text": "Jude, a servant of Jesus Christ, and brother of James, to those who are called, sanctified by God the Father, and kept for Jesus Christ:",
        "translation_id": "web",
        "translation_name": "World English Bible"
    },
    "genesis_1_31": {
        "reference": "Genesis 1:31",
        "verses": [{"book_id": "GEN", "book_name": "Genesis", "chapter": 1, "verse": 31, "text": "God saw everything that he had made, and, behold, it was very good. There was evening and there was morning, a sixth day."}],
        "text": "God saw everything that he had made, and, behold, it was very good. There was evening and there was morning, a sixth day.",
        "translation_id": "web",
        "translation_name": "World English Bible"
    },
    "matthew_5_3_10": {
        "reference": "Matthew 5:3-10",
        "verses": [
            {"book_id": "MAT", "book_name": "Matthew", "chapter": 5, "verse": 3, "text": "Blessed are the poor in spirit, for theirs is the Kingdom of Heaven."},
            {"book_id": "MAT", "book_name": "Matthew", "chapter": 5, "verse": 4, "text": "Blessed are those who mourn, for they shall be comforted."},
            {"book_id": "MAT", "book_name": "Matthew", "chapter": 5, "verse": 5, "text": "Blessed are the gentle, for they shall inherit the earth."},
            {"book_id": "MAT", "book_name": "Matthew", "chapter": 5, "verse": 6, "text": "Blessed are those who hunger and thirst after righteousness, for they shall be filled."},
            {"book_id": "MAT", "book_name": "Matthew", "chapter": 5, "verse": 7, "text": "Blessed are the merciful, for they shall obtain mercy."},
            {"book_id": "MAT", "book_name": "Matthew", "chapter": 5, "verse": 8, "text": "Blessed are the pure in heart, for they shall see God."},
            {"book_id": "MAT", "book_name": "Matthew", "chapter": 5, "verse": 9, "text": "Blessed are the peacemakers, for they shall be called children of God."},
            {"book_id": "MAT", "book_name": "Matthew", "chapter": 5, "verse": 10, "text": "Blessed are those who have been persecuted for righteousness' sake, for theirs is the Kingdom of Heaven."}
        ],
        "text": "Blessed are the poor in spirit, for theirs is the Kingdom of Heaven. Blessed are those who mourn, for they shall be comforted. Blessed are the gentle, for they shall inherit the earth. Blessed are those who hunger and thirst after righteousness, for they shall be filled. Blessed are the merciful, for they shall obtain mercy. Blessed are the pure in heart, for they shall see God. Blessed are the peacemakers, for they shall be called children of God. Blessed are those who have been persecuted for righteousness' sake, for theirs is the Kingdom of Heaven.",
        "translation_id": "web",
        "translation_name": "World English Bible"
    },
    "matthew_5_3_5_7": {
        "reference": "Matthew 5:3,5,7",
        "verses": [
            {"book_id": "MAT", "book_name": "Matthew", "chapter": 5, "verse": 3, "text": "Blessed are the poor in spirit, for theirs is the Kingdom of Heaven."},
            {"book_id": "MAT", "book_name": "Matthew", "chapter": 5, "verse": 5, "text": "Blessed are the gentle, for they shall inherit the earth."},
            {"book_id": "MAT", "book_name": "Matthew", "chapter": 5, "verse": 7, "text": "Blessed are the merciful, for they shall obtain mercy."}
        ],
        "text": "Blessed are the poor in spirit, for theirs is the Kingdom of Heaven. Blessed are the gentle, for they shall inherit the earth. Blessed are the merciful, for they shall obtain mercy.",
        "translation_id": "web",
        "translation_name": "World English Bible"
    },
    "random_ot": {
        "reference": "1 Samuel 7:17",
        "verses": [{"book_id": "1SA", "book_name": "1 Samuel", "chapter": 7, "verse": 17, "text": "He returned to Ramah, for his house was there; and he judged Israel there: and he built an altar to Yahweh there."}],
        "text": "He returned to Ramah, for his house was there; and he judged Israel there: and he built an altar to Yahweh there.",
        "translation_id": "web",
        "translation_name": "World English Bible"
    },
    "random_nt": {
        "reference": "Matthew 12:21",
        "verses": [{"book_id": "MAT", "book_name": "Matthew", "chapter": 12, "verse": 21, "text": "In his name, the nations will hope."}],
        "text": "In his name, the nations will hope.",
        "translation_id": "web",
        "translation_name": "World English Bible"
    },
    "jhn_3": {
        "reference": "John 3",
        "verses": [
            {"book_id": "JHN", "book_name": "John", "chapter": 3, "verse": 1, "text": "Now there was a man of the Pharisees named Nicodemus, a ruler of the Jews."},
            {"book_id": "JHN", "book_name": "John", "chapter": 3, "verse": 2, "text": "The same came to him by night, and said to him, \"Rabbi, we know that you are a teacher come from God, for no one can do these signs that you do, unless God is with him.\""},
            # More verses would be here in a real response
            {"book_id": "JHN", "book_name": "John", "chapter": 3, "verse": 16, "text": "For God so loved the world, that he gave his one and only Son, that whoever believes in him should not perish, but have eternal life."}
        ],
        "text": "Now there was a man of the Pharisees named Nicodemus, a ruler of the Jews. The same came to him by night, and said to him, \"Rabbi, we know that you are a teacher come from God, for no one can do these signs that you do, unless God is with him.\" ... For God so loved the world, that he gave his one and only Son, that whoever believes in him should not perish, but have eternal life.",
        "translation_id": "web",
        "translation_name": "World English Bible"
    },
    "gen_1": {
        "reference": "Genesis 1",
        "verses": [
            {"book_id": "GEN", "book_name": "Genesis", "chapter": 1, "verse": 1, "text": "In the beginning, God created the heavens and the earth."},
            # More verses would be here in a real response
            {"book_id": "GEN", "book_name": "Genesis", "chapter": 1, "verse": 31, "text": "God saw everything that he had made, and, behold, it was very good. There was evening and there was morning, a sixth day."}
        ],
        "text": "In the beginning, God created the heavens and the earth. ... God saw everything that he had made, and, behold, it was very good. There was evening and there was morning, a sixth day.",
        "translation_id": "web",
        "translation_name": "World English Bible"
    }
}

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

# Helper to get mock response or raise appropriate exception
def get_mock_response(url):
    # Handle specific invalid references
    if "InvalidBook" in url:
        raise ValueError(f"Reference not found: Invalid reference in URL")
    elif "John+999" in url or "John%20999" in url:
        response = MagicMock()
        response.status_code = 404
        raise httpx.HTTPStatusError("Invalid chapter", request=MagicMock(), response=response)
    elif "John+3:999" in url or "John%203:999" in url:
        response = MagicMock()
        response.status_code = 404
        raise httpx.HTTPStatusError("Invalid verse", request=MagicMock(), response=response)
    elif "translation=invalid" in url:
        response = MagicMock()
        response.status_code = 404
        raise httpx.HTTPStatusError("Invalid translation", request=MagicMock(), response=response)
    
    # Handle valid references
    if "john+3:16" in url.lower() or "john%203:16" in url.lower():
        if "translation=kjv" in url:
            return MOCK_RESPONSES["john_3_16_kjv"]
        return MOCK_RESPONSES["john_3_16"]
    elif "jude+1" in url.lower() or "jude%201" in url.lower() or "jud%201" in url.lower():
        return MOCK_RESPONSES["jude_1"]
    elif "genesis+1:31" in url.lower() or "genesis%201:31" in url.lower() or "gen%201:31" in url.lower():
        return MOCK_RESPONSES["genesis_1_31"]
    elif "matthew+5:3-10" in url.lower() or "matthew%205:3-10" in url.lower():
        return MOCK_RESPONSES["matthew_5_3_10"]
    elif "matthew+5:3,5,7" in url.lower() or "matthew%205:3,5,7" in url.lower():
        return MOCK_RESPONSES["matthew_5_3_5_7"]
    elif "1+samuel+7:17" in url.lower() or "1%20samuel%207:17" in url.lower():
        return MOCK_RESPONSES["random_ot"]
    elif "matthew+12:21" in url.lower() or "matthew%2012:21" in url.lower():
        return MOCK_RESPONSES["random_nt"]
    elif "jhn+3" in url.lower() or "jhn%203" in url.lower():
        return MOCK_RESPONSES["jhn_3"]
    elif "gen+1" in url.lower() or "gen%201" in url.lower():
        return MOCK_RESPONSES["gen_1"]
    
    # For random verses
    return MOCK_RESPONSES["john_3_16"]

# Mock AsyncClient for httpx
class MockAsyncClient:
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
        
    async def get(self, url):
        # Check for invalid references explicitly
        lower_url = url.lower()
        
        # Handle specific error cases from TEST_CASES
        if "invalidbook" in lower_url:
            error_response = MagicMock()
            error_response.status_code = 404
            raise httpx.HTTPStatusError("Reference not found: InvalidBook", request=MagicMock(), response=error_response)
        
        if "john%20999" in lower_url or "john+999" in lower_url:
            error_response = MagicMock()
            error_response.status_code = 404
            raise httpx.HTTPStatusError("Client error '404 Not Found' for url", request=MagicMock(), response=error_response)
        
        if "john%203:999" in lower_url or "john+3:999" in lower_url:
            error_response = MagicMock()
            error_response.status_code = 404
            raise httpx.HTTPStatusError("Client error '404 Not Found' for url", request=MagicMock(), response=error_response)
        
        if "translation=invalid" in lower_url:
            error_response = MagicMock()
            error_response.status_code = 404
            raise httpx.HTTPStatusError("Client error '404 Not Found' for url", request=MagicMock(), response=error_response)
        
        # For valid URLs, return mock response
        response = MagicMock()
        
        # Handle KJV translation properly
        if "translation=kjv" in lower_url:
            # For John 3:16 with KJV, use the specific mock
            if "john+3:16" in lower_url or "john%203:16" in lower_url:
                response.json.return_value = MOCK_RESPONSES["john_3_16_kjv"]
            else:
                # For any other reference with KJV, duplicate and modify the response
                data = get_mock_response(url)
                # Create a deep copy to avoid modifying the original
                kjv_data = dict(data)
                kjv_data["translation_id"] = "kjv"
                kjv_data["translation_name"] = "King James Version"
                response.json.return_value = kjv_data
        else:
            # Handle regular cases
            response.json.return_value = get_mock_response(url)
            
        response.raise_for_status = MagicMock()
        return response

@pytest.mark.asyncio
@patch('httpx.AsyncClient', MockAsyncClient)
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
@patch('httpx.AsyncClient', MockAsyncClient)
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
@patch('httpx.AsyncClient', MockAsyncClient)
@patch('bible_data.get_random_reference')
async def test_get_random_verse(mock_random_reference):
    """Test getting random verses."""
    client = BibleAPIClient()
    
    # Test default random verse
    mock_random_reference.return_value = "John 3:16"
    result = await client.get_random_verse()
    assert 'reference' in result
    assert 'text' in result
    assert result['text'].strip()
    
    # Test with translation
    mock_random_reference.return_value = "John 3:16"
    result = await client.get_random_verse(translation_id="kjv")
    assert 'reference' in result
    assert 'text' in result
    assert result['translation_name'] == "King James Version"
    
    # Test with OT testament filter
    mock_random_reference.return_value = "1 Samuel 7:17"
    result = await client.get_random_verse(testament=OLD_TESTAMENT)
    assert 'reference' in result
    assert 'text' in result
    
    # Test with NT testament filter
    mock_random_reference.return_value = "Matthew 12:21"
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
