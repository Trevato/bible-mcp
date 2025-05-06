"""
Simple test script to run the Bible MCP server and test resource listing
"""
import asyncio
import subprocess
import sys
import time
import signal
from typing import Dict, Any, Optional, List, Tuple

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_resource_listing():
    # Start the server process
    server_process = subprocess.Popen(
        [sys.executable, "bible_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give the server a moment to start
    time.sleep(2)
    
    try:
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
                    print(f"   URI: {resource.uri}")
                    if resource.description:
                        print(f"   Description: {resource.description}")
                    print()
                
                if not resources.resources:
                    print("No resources found!")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Clean up the server process
        server_process.terminate()
        stdout, stderr = server_process.communicate(timeout=5)
        
        if stderr:
            print("\nServer stderr:")
            print(stderr)

if __name__ == "__main__":
    asyncio.run(test_resource_listing())
