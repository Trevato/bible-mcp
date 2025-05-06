"""
Simple test for the Bible MCP server
"""
import asyncio
import subprocess
import sys
import time

async def main():
    # Start the server in a subprocess
    print("Starting the Bible MCP server...")
    server_process = subprocess.Popen(
        [sys.executable, "/Users/trevato/projects/bible-mcp/bible_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give the server a moment to start
    await asyncio.sleep(2)
    
    # Run mcp dev command to check
    print("\nRunning 'mcp dev' to test the server...")
    dev_process = subprocess.Popen(
        ["uv", "run", "mcp", "dev", "/Users/trevato/projects/bible-mcp/bible_server.py", "--no-ui"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for a few seconds
    await asyncio.sleep(3)
    
    # Clean up
    server_process.terminate()
    dev_process.terminate()
    
    # Print server output
    stdout, stderr = server_process.communicate(timeout=5)
    if stdout:
        print("\nServer stdout:")
        print(stdout.decode('utf-8'))
    if stderr:
        print("\nServer stderr:")
        print(stderr.decode('utf-8'))
    
    print("\nTest complete!")

if __name__ == "__main__":
    asyncio.run(main())
