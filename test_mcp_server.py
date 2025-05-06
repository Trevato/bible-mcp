"""
Test the MCP server implementation using the mcp client libraries.
"""
import asyncio
import os
import sys
import subprocess
import time
from typing import Dict, Any, Optional, List, Tuple

from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# Start the MCP server process
def start_server_process():
    process = subprocess.Popen(
        [sys.executable, "bible_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    # Give it a moment to initialize
    time.sleep(1)
    return process

async def test_resources(session: ClientSession):
    """Test MCP resources."""
    print("\n=== Testing MCP Resources ===")
    
    # Test listing resources
    resources = await session.list_resources()
    print(f"Found {len(resources.resources)} resources")
    
    # Test common verse retrieval
    print("\nTesting standard verse resource")
    try:
        content, mime_type = await session.read_resource("bible://web/JHN/3/16")
        print(f"Content: {content[:100]}...")
        # Check for key parts of the verse rather than exact content
        if "John 3:16" in content and "Bible" in content:
            print("✅ Test passed - correct content")
        else:
            print("❌ Test failed - incorrect content")
            print(f"Full content: {content}")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    
    # Test single-chapter book
    print("\nTesting single-chapter book")
    try:
        content, mime_type = await session.read_resource("bible://web/JUD/1/1")
        print(f"Content: {content[:100]}...")
        if "Jude" in content:
            print("✅ Test passed - found Jude content")
        else:
            print("❌ Test failed - empty or incorrect content")
            print(f"Full content: {content}")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    
    # Test chapter retrieval
    print("\nTesting chapter resource")
    try:
        content, mime_type = await session.read_resource("bible://web/GEN/1")
        print(f"Content length: {len(content)} chars")
        # Check for content keywords rather than length
        if "Genesis 1" in content and "God" in content:
            print("✅ Test passed - chapter content received")
        else:
            print("❌ Test failed - chapter content insufficient")
            print(f"First 100 chars: {content[:100]}...")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    
    # Test random verse
    print("\nTesting random verse resource")
    try:
        content, mime_type = await session.read_resource("bible://random/web")
        print(f"Content: {content[:100]}...")
        if content and "📖" in content and "📝" in content:
            print("✅ Test passed - random verse format correct")
        else:
            print("❌ Test failed - incorrect or empty content")
            print(f"Full content: {content}")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

async def test_tools(session: ClientSession):
    """Test MCP tools."""
    print("\n=== Testing MCP Tools ===")
    
    # List available tools
    tools = await session.list_tools()
    print(f"Found {len(tools.tools)} tools")
    
    # Test verse by reference tool
    print("\nTesting get_verse_by_reference tool")
    try:
        result = await session.call_tool(
            "get_verse_by_reference", 
            {"reference": "John 3:16", "translation": "web"}
        )
        content = result.content[0].text if result.content else ""
        print(f"Content: {content[:100]}...")
        if "For God so loved the world" in content:
            print("✅ Test passed - correct content")
        else:
            print("❌ Test failed - incorrect content")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    
    # Test random verse tool
    print("\nTesting get_random_verse_tool")
    try:
        result = await session.call_tool(
            "get_random_verse_tool", 
            {"translation": "web", "testament": "NT"}
        )
        content = result.content[0].text if result.content else ""
        print(f"Content: {content[:100]}...")
        if content:
            print("✅ Test passed")
        else:
            print("❌ Test failed - empty content")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    
    # Test translations list tool
    print("\nTesting list_available_translations tool")
    try:
        result = await session.call_tool("list_available_translations", {})
        content = result.content[0].text if result.content else ""
        print(f"Found translations: {content.count('- ')}")
        if content and content.count("- ") > 5:
            print("✅ Test passed - found multiple translations")
        else:
            print("❌ Test failed - insufficient translations")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

async def test_prompts(session: ClientSession):
    """Test MCP prompts."""
    print("\n=== Testing MCP Prompts ===")
    
    # List available prompts
    prompts = await session.list_prompts()
    print(f"Found {len(prompts.prompts)} prompts")
    
    # Test analyze verse prompt
    print("\nTesting analyze_verse_prompt")
    try:
        result = await session.get_prompt(
            "analyze_verse_prompt", 
            {"reference": "John 3:16"}
        )
        prompt_text = result.messages[0].content.text if result.messages else ""
        print(f"Prompt: {prompt_text[:100]}...")
        if "John 3:16" in prompt_text:
            print("✅ Test passed - reference included in prompt")
        else:
            print("❌ Test failed - reference not in prompt")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    
    # Test find verses prompt
    print("\nTesting find_verses_on_topic_prompt")
    try:
        result = await session.get_prompt(
            "find_verses_on_topic_prompt", 
            {"topic": "love"}
        )
        prompt_text = result.messages[0].content.text if result.messages else ""
        print(f"Prompt: {prompt_text[:100]}...")
        if "love" in prompt_text:
            print("✅ Test passed - topic included in prompt")
        else:
            print("❌ Test failed - topic not in prompt")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

async def main():
    """Run all tests against the MCP server."""
    process = start_server_process()
    
    try:
        # Connect to the server
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["bible_server.py"],
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize session
                await session.initialize()
                
                # Run tests
                await test_resources(session)
                await test_tools(session)
                await test_prompts(session)
                
                print("\nAll tests completed.")
    except Exception as e:
        print(f"Error in main test routine: {str(e)}")
    finally:
        # Clean up the server process
        process.terminate()
        stdout, stderr = process.communicate()
        
        # Print any server output for debugging
        if stderr:
            print("\nServer stderr output:")
            print(stderr[:500])  # Limit output to first 500 chars

if __name__ == "__main__":
    asyncio.run(main())
