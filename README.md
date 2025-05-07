# Bible MCP Server

A Model Context Protocol server that exposes Bible content from bible-api.com for Large Language Models like Claude.

## Features

- Access Bible verses and chapters as resources
- Tools for retrieving verses by reference and getting random verses
- Support for multiple translations
- Prompt templates for Bible study
- True random verse generation from any book in the Bible
- Testament filtering (OT/NT) for random verses
- Comprehensive error handling

## Installation

### From PyPI (recommended)

The simplest way to install Bible MCP is via pip:

```bash
pip install bible-mcp
```

### From Source

Clone the repository and install dependencies:

```bash
git clone https://github.com/trevato/bible-mcp.git
cd bible-mcp
pip install -e .
```

Requirements:
- Python 3.10+
- Dependencies are managed via `pyproject.toml`

## Usage

### Running with MCP Development Tools

The fastest way to test the server is with the MCP Inspector:

```bash
mcp dev bible_server.py
```

This will run the server and open a web interface for testing.

### Installing in Claude Desktop

To use this server with Claude Desktop:

```bash
mcp install bible_server.py
```

After installation, you can access Bible content in your Claude conversations.

### Direct Execution

You can also run the server directly:

```bash
python -m bible_server
```

## Available Resources

Bible MCP provides the following resources:

### Chapter Resource

```
bible://{translation}/{book}/{chapter}
```

Example: `bible://web/JHN/3` (John chapter 3 from the World English Bible)

### Verse Resource

```
bible://{translation}/{book}/{chapter}/{verse}
```

Example: `bible://kjv/JHN/3/16` (John 3:16 from the King James Version)

### Random Verse Resource

```
bible://random/{translation}
```

Example: `bible://random/web` (Random verse from the World English Bible)

## Available Tools

### Get Verse by Reference

```python
get_verse_by_reference(reference: str, translation: str = "web") -> str
```

Parameters:
- `reference`: Bible reference (e.g., "John 3:16", "Matthew 5:1-10")
- `translation`: Translation ID (default: "web")

Example:
```
get_verse_by_reference("Psalm 23:1", "kjv")
```

### Get Random Verse

```python
get_random_verse_tool(translation: str = "web", testament: Optional[str] = None) -> str
```

Parameters:
- `translation`: Translation ID (default: "web")
- `testament`: Optional filter for "OT" (Old Testament) or "NT" (New Testament)

Example:
```
get_random_verse_tool(translation="web", testament="NT")
```

### List Available Translations

```python
list_available_translations() -> str
```

Returns a formatted list of all available Bible translations.

## Prompts

### Analyze Verse Prompt

```python
analyze_verse_prompt(reference: str) -> str
```

Creates a prompt for analyzing a specific Bible verse.

Example:
```
analyze_verse_prompt("John 3:16")
```

### Find Verses on Topic Prompt

```python
find_verses_on_topic_prompt(topic: str) -> str
```

Creates a prompt for finding verses on a specific topic.

Example:
```
find_verses_on_topic_prompt("love")
```

## Supported Translations

Bible MCP supports multiple translations through the bible-api.com service:

- World English Bible (web) - Default
- King James Version (kjv)
- American Standard Version (asv)
- Bible in Basic English (bbe)
- And many more...

Run the `list_available_translations` tool to see all available translations.

## Examples

### Example: Getting John 3:16 from the Web UI

When running `mcp dev bible_server.py`, you can navigate to the Web UI and:

1. Select the "Resources" tab
2. Enter `bible://web/JHN/3/16` in the URI field
3. Click "Read Resource"

### Example: Using Bible MCP in an LLM Tool

```python
from mcp import ClientSession, StdioServerParameters
import asyncio

async def use_bible_mcp():
    server_params = StdioServerParameters(
        command="python",
        args=["bible_server.py"],
    )
    
    async with ClientSession.from_stdio_server(server_params) as session:
        # Initialize session
        await session.initialize()
        
        # Get a verse
        content, _ = await session.read_resource("bible://web/JHN/3/16")
        print(content)
        
        # Use a tool
        result = await session.call_tool(
            "get_random_verse_tool", 
            {"testament": "NT"}
        )
        print(result.content[0].text)

if __name__ == "__main__":
    asyncio.run(use_bible_mcp())
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## Credits

This project uses the Bible API service provided by [bible-api.com](https://bible-api.com/).

## License

MIT
