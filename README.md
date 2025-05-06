# Bible MCP Server

A Model Context Protocol server that exposes Bible content from bible-api.com.

## Features

- Access Bible verses and chapters as resources
- Tools for retrieving verses by reference and getting random verses
- Support for multiple translations
- Prompt templates for Bible study

## Installation

This project requires Python 3.9+ and dependencies installed with `uv`:

```bash
uv add "mcp[cli]" httpx
```

## Usage

### Running with MCP Development Tools

The fastest way to test the server is with the MCP Inspector:

```bash
mcp dev bible_server.py
```

### Installing in Claude Desktop

To use this server with Claude Desktop:

```bash
mcp install bible_server.py
```

### Direct Execution

You can also run the server directly:

```bash
python bible_server.py
```

## Available Resources

- `bible://{translation}/{book}/{chapter}` - Get a full chapter
- `bible://{translation}/{book}/{chapter}/{verse}` - Get a specific verse
- `bible://random/{translation}` - Get a random verse

## Available Tools

- `get_verse_by_reference` - Get verse(s) by reference string
- `get_random_verse_tool` - Get a random verse with optional filters
- `list_available_translations` - List all available Bible translations

## Prompts

- `analyze_verse_prompt` - Template for analyzing a verse
- `find_verses_on_topic_prompt` - Template for finding verses on a topic

## Credits

This project uses the Bible API service provided by [bible-api.com](https://bible-api.com/).

## License

MIT
