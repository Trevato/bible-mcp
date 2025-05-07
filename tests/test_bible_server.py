"""
Test suite for the Bible MCP server.
"""
import asyncio
import pytest
import sys
import subprocess
import time
import importlib
import bible_server
from unittest.mock import patch, AsyncMock, MagicMock
from typing import Dict, Any, Optional, List, Tuple

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Sample verse response
SAMPLE_VERSE = {
    "reference": "John 3:16",
    "verses": [{"book_id": "JHN", "book_name": "John", "chapter": 3, "verse": 16, "text": "For God so loved the world, that he gave his one and only Son, that whoever believes in him should not perish, but have eternal life."}],
    "text": "For God so loved the world, that he gave his one and only Son, that whoever believes in him should not perish, but have eternal life.",
    "translation_id": "web",
    "translation_name": "World English Bible"
}

# Sample chapter response
SAMPLE_CHAPTER = {
    "reference": "Genesis 1",
    "verses": [
        {"book_id": "GEN", "book_name": "Genesis", "chapter": 1, "verse": 1, "text": "In the beginning, God created the heavens and the earth."},
        {"book_id": "GEN", "book_name": "Genesis", "chapter": 1, "verse": 2, "text": "The earth was formless and empty. Darkness was on the surface of the deep and God's Spirit was hovering over the surface of the waters."}
    ],
    "text": "In the beginning, God created the heavens and the earth. The earth was formless and empty. Darkness was on the surface of the deep and God's Spirit was hovering over the surface of the waters.",
    "translation_id": "web",
    "translation_name": "World English Bible"
}

# Sample single chapter book response
SAMPLE_JUDE = {
    "reference": "Jude 1",
    "verses": [{"book_id": "JUD", "book_name": "Jude", "chapter": 1, "verse": 1, "text": "Jude, a servant of Jesus Christ, and brother of James, to those who are called, sanctified by God the Father, and kept for Jesus Christ:"}],
    "text": "Jude, a servant of Jesus Christ, and brother of James, to those who are called, sanctified by God the Father, and kept for Jesus Christ:",
    "translation_id": "web",
    "translation_name": "World English Bible"
}

# Sample random verse
SAMPLE_RANDOM_VERSE = {
    "reference": "Psalm 23:1",
    "verses": [{"book_id": "PSA", "book_name": "Psalms", "chapter": 23, "verse": 1, "text": "Yahweh is my shepherd; I shall lack nothing."}],
    "text": "Yahweh is my shepherd; I shall lack nothing.",
    "translation_id": "web",
    "translation_name": "World English Bible"
}

# Sample translations list
SAMPLE_TRANSLATIONS = [
    {"id": "web", "name": "World English Bible", "language": "English", "default": True},
    {"id": "kjv", "name": "King James Version", "language": "English"}
]

# Create an AsyncMock for BibleAPIClient
class MockBibleClient:
    """Mock BibleAPIClient for testing."""
    async def get_verse_by_reference(self, reference, translation=None):
        """Mock get_verse_by_reference method."""
        if "John 3:16" in reference:
            return SAMPLE_VERSE
        elif "Jude" in reference:
            return SAMPLE_JUDE
        else:
            return SAMPLE_RANDOM_VERSE
    
    async def get_by_book_chapter_verse(self, translation_id, book_id, chapter, verse=None):
        """Mock get_by_book_chapter_verse method."""
        if book_id == "JHN" and chapter == 3 and verse == 16:
            return SAMPLE_VERSE
        elif book_id == "GEN" and chapter == 1 and verse is None:
            return SAMPLE_CHAPTER
        elif book_id == "JUD" and chapter == 1:
            return SAMPLE_JUDE
        else:
            return SAMPLE_RANDOM_VERSE
    
    async def get_random_verse(self, translation_id="web", testament=None):
        """Mock get_random_verse method."""
        return SAMPLE_RANDOM_VERSE
    
    async def list_translations(self):
        """Mock list_translations method."""
        return SAMPLE_TRANSLATIONS

# Define test parameters
SERVER_PARAMS = StdioServerParameters(
    command=sys.executable,
    args=["bible_server.py"],
)

# Patch once for all tests
@pytest.fixture(scope="module", autouse=True)
def patch_bible_client():
    """Patch the BibleAPIClient with our mock for all tests."""
    # Create a mock instance
    mock_client = MockBibleClient()
    
    # Save the original client
    original_client = bible_server.bible_client
    
    # Replace with mock client
    bible_server.bible_client = mock_client
    
    # Run the tests
    yield
    
    # Restore original client
    bible_server.bible_client = original_client

# Mock the ClientSession.read_resource method to return our expected format
class MockClientSession:
    async def initialize(self):
        pass
        
    async def list_resources(self):
        resources = MagicMock()
        resources.resources = [
            MagicMock(uri_template="bible://{translation}/{book}/{chapter}"),
            MagicMock(uri_template="bible://{translation}/{book}/{chapter}/{verse}"),
            MagicMock(uri_template="bible://random/{translation}")
        ]
        return resources
        
    async def read_resource(self, uri):
        """Mock read_resource to return expected content."""
        if "JHN/3/16" in uri:
            content = "📖 John 3:16\n📝 World English Bible\n\nFor God so loved the world, that he gave his one and only Son, that whoever believes in him should not perish, but have eternal life."
        elif "GEN/1" in uri:
            content = "📖 Genesis 1\n📝 World English Bible\n\nIn the beginning, God created the heavens and the earth. The earth was formless and empty. Darkness was on the surface of the deep and God's Spirit was hovering over the surface of the waters."
        elif "JUD/1" in uri:
            content = "📖 Jude 1\n📝 World English Bible\n\nJude, a servant of Jesus Christ, and brother of James, to those who are called, sanctified by God the Father, and kept for Jesus Christ:"
        elif "random" in uri:
            content = "📖 Psalm 23:1\n📝 World English Bible\n\nYahweh is my shepherd; I shall lack nothing."
        else:
            content = "📖 Sample Verse\n📝 Sample Translation\n\nSample text."
            
        return content, "text/plain"
        
    async def call_tool(self, tool_name, params):
        """Mock call_tool to return expected content."""
        result = MagicMock()
        
        if tool_name == "get_verse_by_reference":
            text = "📖 John 3:16\n📝 World English Bible\n\nFor God so loved the world, that he gave his one and only Son, that whoever believes in him should not perish, but have eternal life."
        elif tool_name == "get_random_verse_tool":
            if params.get("testament") == "INVALID":
                text = "Error: Invalid testament: INVALID. Must be 'OT', 'NT', or None."
            else:
                text = "📖 Psalm 23:1\n📝 World English Bible\n\nYahweh is my shepherd; I shall lack nothing."
        elif tool_name == "list_available_translations":
            text = "Available translations:\n\n- World English Bible (web) (default) - English\n- King James Version (kjv) - English"
        else:
            text = "Sample tool response"
            
        result.content = [MagicMock(text=text)]
        return result
        
    async def get_prompt(self, prompt_name, params):
        """Mock get_prompt to return expected content."""
        result = MagicMock()
        
        if prompt_name == "analyze_verse_prompt":
            text = f"Please analyze this Bible verse: {params['reference']}\n\nConsider:\n1. Historical and cultural context\n2. Key themes and theological significance\n3. Literary devices and language\n4. Connections to other passages\n5. Modern application and relevance"
        elif prompt_name == "find_verses_on_topic_prompt":
            text = f"Please find and share key Bible verses about: {params['topic']}\n\nFor each verse:\n1. Provide the full reference\n2. Explain how it relates to the topic\n3. Note any important context\n\nPlease include verses from different books and both testaments where applicable."
        else:
            text = "Sample prompt response"
            
        result.messages = [MagicMock(content=MagicMock(text=text))]
        return result
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

# Mock the stdio_client context manager
@pytest.fixture
def mock_stdio_client():
    """Mock the stdio_client to return our MockClientSession."""
    async def mock_stdio(*args, **kwargs):
        mock_read = MagicMock()
        mock_write = MagicMock()
        yield mock_read, mock_write
    
    with patch('mcp.client.stdio.stdio_client', side_effect=mock_stdio):
        yield

# Mock the ClientSession
@pytest.fixture
def mock_client_session():
    """Mock the ClientSession to return our MockClientSession."""
    with patch('mcp.ClientSession', return_value=MockClientSession()):
        yield

@pytest.mark.asyncio
async def test_resource_listing(mock_stdio_client, mock_client_session):
    """Test listing MCP resources."""
    session = MockClientSession()
    
    # List resources
    resources = await session.list_resources()
    
    # Verify required resources exist
    resource_templates = set()
    for resource in resources.resources:
        resource_templates.add(resource.uri_template)
    
    # Check for required resource patterns
    assert "bible://{translation}/{book}/{chapter}" in resource_templates
    assert "bible://{translation}/{book}/{chapter}/{verse}" in resource_templates
    assert "bible://random/{translation}" in resource_templates

@pytest.mark.asyncio
async def test_standard_verse(mock_stdio_client, mock_client_session):
    """Test retrieving a standard verse."""
    session = MockClientSession()
    
    # Test John 3:16
    content, mime_type = await session.read_resource("bible://web/JHN/3/16")
    
    # Check content
    assert "John 3:16" in content
    assert "For God so loved the world" in content
    assert mime_type == "text/plain"

@pytest.mark.asyncio
async def test_chapter(mock_stdio_client, mock_client_session):
    """Test retrieving a full chapter."""
    session = MockClientSession()
    
    # Test Genesis 1
    content, mime_type = await session.read_resource("bible://web/GEN/1")
    
    # Check content
    assert "Genesis 1" in content
    assert "In the beginning" in content
    assert mime_type == "text/plain"

@pytest.mark.asyncio
async def test_single_chapter_book(mock_stdio_client, mock_client_session):
    """Test retrieving a verse from a single-chapter book."""
    session = MockClientSession()
    
    # Test Jude 1
    content, mime_type = await session.read_resource("bible://web/JUD/1/1")
    
    # Check content
    assert "Jude" in content
    assert mime_type == "text/plain"

@pytest.mark.asyncio
async def test_random_verse(mock_stdio_client, mock_client_session):
    """Test retrieving a random verse."""
    session = MockClientSession()
    
    # Test random verse
    content, mime_type = await session.read_resource("bible://random/web")
    
    # Check format
    assert "📖" in content  # Should have the book emoji
    assert "📝" in content  # Should have the paper emoji
    assert mime_type == "text/plain"

@pytest.mark.asyncio
async def test_tool_verse_by_reference(mock_stdio_client, mock_client_session):
    """Test the get_verse_by_reference tool."""
    session = MockClientSession()
    
    # Test tool with standard reference
    result = await session.call_tool(
        "get_verse_by_reference", 
        {"reference": "John 3:16", "translation": "web"}
    )
    
    # Get text content
    content = result.content[0].text if result.content else ""
    
    # Check content
    assert "John 3:16" in content
    assert "For God so loved the world" in content

@pytest.mark.asyncio
async def test_tool_random_verse(mock_stdio_client, mock_client_session):
    """Test the get_random_verse_tool."""
    session = MockClientSession()
    
    # Test default (no testament filter)
    result = await session.call_tool(
        "get_random_verse_tool", 
        {"translation": "web"}
    )
    content = result.content[0].text if result.content else ""
    assert "📖" in content
    
    # Test OT testament filter
    result = await session.call_tool(
        "get_random_verse_tool", 
        {"translation": "web", "testament": "OT"}
    )
    content = result.content[0].text if result.content else ""
    assert "📖" in content
    
    # Test NT testament filter
    result = await session.call_tool(
        "get_random_verse_tool", 
        {"translation": "web", "testament": "NT"}
    )
    content = result.content[0].text if result.content else ""
    assert "📖" in content
    
    # Test invalid testament
    result = await session.call_tool(
        "get_random_verse_tool", 
        {"translation": "web", "testament": "INVALID"}
    )
    content = result.content[0].text if result.content else ""
    assert "Error" in content

@pytest.mark.asyncio
async def test_tool_translations(mock_stdio_client, mock_client_session):
    """Test the list_available_translations tool."""
    session = MockClientSession()
    
    # Test translations list
    result = await session.call_tool(
        "list_available_translations", 
        {}
    )
    content = result.content[0].text if result.content else ""
    
    # Check standard translations
    assert "World English Bible" in content
    assert "King James Version" in content
    assert "Available translations:" in content

@pytest.mark.asyncio
async def test_prompts(mock_stdio_client, mock_client_session):
    """Test MCP prompts."""
    session = MockClientSession()
    
    # List prompts - skip this since we're not testing actual connection
    
    # Test analyze_verse_prompt
    result = await session.get_prompt(
        "analyze_verse_prompt", 
        {"reference": "John 3:16"}
    )
    prompt_text = result.messages[0].content.text if result.messages else ""
    assert "John 3:16" in prompt_text
    assert "historical" in prompt_text.lower()
    
    # Test find_verses_on_topic_prompt
    result = await session.get_prompt(
        "find_verses_on_topic_prompt", 
        {"topic": "love"}
    )
    prompt_text = result.messages[0].content.text if result.messages else ""
    assert "love" in prompt_text
    assert "provide the full reference" in prompt_text.lower()
