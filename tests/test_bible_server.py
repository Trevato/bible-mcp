"""
Test suite for the Bible MCP server.
"""
import asyncio
import pytest
import sys
import subprocess
import time
from typing import Dict, Any, Optional, List, Tuple

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

@pytest.mark.asyncio
async def test_resource_listing():
    """Test listing MCP resources."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["bible_server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List resources
            resources = await session.list_resources()
            
            # Verify required resources exist
            resource_templates = set()
            for resource in resources.resources:
                if hasattr(resource, 'uri_template'):
                    resource_templates.add(resource.uri_template)
            
            # Check for required resource patterns
            assert "bible://{translation}/{book}/{chapter}" in resource_templates
            assert "bible://{translation}/{book}/{chapter}/{verse}" in resource_templates
            assert "bible://random/{translation}" in resource_templates

@pytest.mark.asyncio
async def test_standard_verse():
    """Test retrieving a standard verse."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["bible_server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Test John 3:16
            content, mime_type = await session.read_resource("bible://web/JHN/3/16")
            
            # Check content
            assert "John 3:16" in content
            assert "For God so loved the world" in content
            assert mime_type == "text/plain"

@pytest.mark.asyncio
async def test_chapter():
    """Test retrieving a full chapter."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["bible_server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Test Genesis 1
            content, mime_type = await session.read_resource("bible://web/GEN/1")
            
            # Check content
            assert "Genesis 1" in content
            assert "In the beginning" in content
            assert mime_type == "text/plain"

@pytest.mark.asyncio
async def test_single_chapter_book():
    """Test retrieving a verse from a single-chapter book."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["bible_server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Test Jude 1
            content, mime_type = await session.read_resource("bible://web/JUD/1/1")
            
            # Check content
            assert "Jude" in content
            assert mime_type == "text/plain"

@pytest.mark.asyncio
async def test_random_verse():
    """Test retrieving a random verse."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["bible_server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Test random verse
            content, mime_type = await session.read_resource("bible://random/web")
            
            # Check format
            assert "📖" in content  # Should have the book emoji
            assert "📝" in content  # Should have the paper emoji
            assert mime_type == "text/plain"

@pytest.mark.asyncio
async def test_tool_verse_by_reference():
    """Test the get_verse_by_reference tool."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["bible_server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
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
async def test_tool_random_verse():
    """Test the get_random_verse_tool."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["bible_server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
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
async def test_tool_translations():
    """Test the list_available_translations tool."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["bible_server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
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
async def test_prompts():
    """Test MCP prompts."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["bible_server.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List prompts
            prompts = await session.list_prompts()
            prompt_names = set()
            for prompt in prompts.prompts:
                prompt_names.add(prompt.name)
            
            # Verify expected prompts exist
            assert "analyze_verse_prompt" in prompt_names
            assert "find_verses_on_topic_prompt" in prompt_names
            
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
