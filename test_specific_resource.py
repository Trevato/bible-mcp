"""
Test a specific resource in the Bible MCP server.
"""
import asyncio
import subprocess
import sys
import time
from typing import Dict, Any, Optional, List, Tuple

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_specific_resource():
    """Test a specific resource in the Bible MCP server."""
    # Start the server process
    print("Starting the Bible MCP server...")
    
    # Set up client parameters
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["bible_server.py"],
    )
    
    print("Connecting to server...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            print("Initializing session...")
            await session.initialize()
            
            print("\nListing resources...")
            resources = await session.list_resources()
            print(f"Found {len(resources.resources)} resources:")
            
            # Print details of each resource
            for idx, resource in enumerate(resources.resources, 1):
                print(f"{idx}. Name: {resource.name}")
                if hasattr(resource, 'uri') and resource.uri:
                    print(f"   URI: {resource.uri}")
                if hasattr(resource, 'uri_template') and resource.uri_template:
                    print(f"   URI Template: {resource.uri_template}")
                if resource.description:
                    print(f"   Description: {resource.description}")
                print()
            
            # Test reading John 3:16
            print("\nTesting reading John 3:16...")
            try:
                content, mime_type = await session.read_resource("bible://web/JHN/3/16")
                print(f"Content from John 3:16:")
                print(content)
                print(f"MIME Type: {mime_type}")
            except Exception as e:
                print(f"Error reading resource: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_specific_resource())
