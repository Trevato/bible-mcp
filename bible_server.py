"""
MCP Server for Bible content using bible-api.com.

This server provides Bible verses and chapters as resources and tools
for searching and retrieving Bible content.
"""
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import asyncio
from typing import Dict, List, Optional, Any

from mcp.server.fastmcp import FastMCP, Context, Image
from bible_api import BibleAPIClient

# Create a global instance of the Bible API client
bible_client = BibleAPIClient()


# Create the MCP server
mcp = FastMCP(
    "Bible MCP",
    dependencies=["httpx"],
)


# === RESOURCES ===

@mcp.resource("bible://{translation}/{book}/{chapter}")
async def get_chapter(translation: str, book: str, chapter: str) -> str:
    """
    Get a full chapter from the Bible.
    
    Args:
        translation: Translation ID (e.g., "web", "kjv")
        book: Book ID (e.g., "JHN", "GEN")
        chapter: Chapter number
        
    Returns:
        String containing the chapter text
    """
    try:
        data = await bible_client.get_by_book_chapter_verse(
            translation_id=translation, 
            book_id=book, 
            chapter=int(chapter)
        )
        
        # Format the chapter text
        return format_chapter(data)
    except Exception as e:
        return f"Error retrieving chapter: {str(e)}"


@mcp.resource("bible://{translation}/{book}/{chapter}/{verse}")
async def get_verse(translation: str, book: str, chapter: str, verse: str) -> str:
    """
    Get a specific verse from the Bible.
    
    Args:
        translation: Translation ID (e.g., "web", "kjv")
        book: Book ID (e.g., "JHN", "GEN")
        chapter: Chapter number
        verse: Verse number
        
    Returns:
        String containing the verse text
    """
    try:
        data = await bible_client.get_by_book_chapter_verse(
            translation_id=translation, 
            book_id=book, 
            chapter=int(chapter),
            verse=int(verse)
        )
        
        # Format the verse text
        return format_verse(data)
    except Exception as e:
        return f"Error retrieving verse: {str(e)}"


@mcp.resource("bible://random/{translation}")
async def get_random_verse(translation: str) -> str:
    """
    Get a random verse from the Bible.
    
    Args:
        translation: Translation ID (e.g., "web", "kjv")
        
    Returns:
        String containing a random verse
    """
    try:
        data = await bible_client.get_random_verse(translation_id=translation)
        
        # Format the verse text
        return format_verse(data)
    except Exception as e:
        return f"Error retrieving random verse: {str(e)}"


# === TOOLS ===

@mcp.tool()
async def get_verse_by_reference(ctx: Context, reference: str, translation: Optional[str] = "web") -> str:
    """
    Get verse(s) by reference string.
    
    Args:
        ctx: MCP context
        reference: Bible reference (e.g., "John 3:16", "Matthew 5:1-10")
        translation: Translation ID (default: "web")
        
    Returns:
        Formatted string containing the verse(s)
    """
    try:
        data = await bible_client.get_verse_by_reference(reference, translation)
        return format_verse(data)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def get_random_verse_tool(
    ctx: Context,
    translation: str = "web", 
    testament: Optional[str] = None
) -> str:
    """
    Get a random verse from the Bible.
    
    Args:
        ctx: MCP context
        translation: Translation ID (default: "web")
        testament: Optional filter for "OT" (Old Testament) or "NT" (New Testament)
        
    Returns:
        Formatted string containing a random verse
    """
    try:
        data = await bible_client.get_random_verse(
            translation_id=translation,
            book_ids=testament
        )
        return format_verse(data)
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
async def list_available_translations(ctx: Context) -> str:
    """
    List all available Bible translations.
    
    Args:
        ctx: MCP context
        
    Returns:
        Formatted string containing translation information
    """
    try:
        translations = await bible_client.list_translations()
        result = "Available translations:\n\n"
        
        for t in translations:
            default_marker = " (default)" if t.get("default") else ""
            result += f"- {t['name']} ({t['id']}){default_marker} - {t['language']}\n"
            
        return result
    except Exception as e:
        return f"Error listing translations: {str(e)}"


# === PROMPTS ===

@mcp.prompt()
def analyze_verse_prompt(reference: str) -> str:
    """
    Create a prompt to analyze a Bible verse.
    
    Args:
        reference: Bible verse reference (e.g., "John 3:16")
        
    Returns:
        A prompt string for analyzing the verse
    """
    return f"""Please analyze this Bible verse: {reference}

Consider:
1. Historical and cultural context
2. Key themes and theological significance
3. Literary devices and language
4. Connections to other passages
5. Modern application and relevance"""


@mcp.prompt()
def find_verses_on_topic_prompt(topic: str) -> str:
    """
    Create a prompt to find Bible verses on a specific topic.
    
    Args:
        topic: The topic to search for
        
    Returns:
        A prompt string for finding relevant verses
    """
    return f"""Please find and share key Bible verses about: {topic}

For each verse:
1. Provide the full reference
2. Explain how it relates to the topic
3. Note any important context

Please include verses from different books and both testaments where applicable."""


# === HELPER FUNCTIONS ===

def format_verse(data: Dict) -> str:
    """
    Format verse data into a readable string.
    
    Args:
        data: Verse data from the Bible API
        
    Returns:
        Formatted string with verse information
    """
    result = f"📖 {data.get('reference', 'Unknown reference')}\n"
    result += f"📝 {data.get('translation_name', 'Unknown translation')}\n\n"
    
    # Add text, cleaning up any extra newlines
    text = data.get('text', '').strip()
    result += text
    
    return result


def format_chapter(data: Dict) -> str:
    """
    Format chapter data into a readable string.
    
    Args:
        data: Chapter data from the Bible API
        
    Returns:
        Formatted string with chapter information
    """
    # For chapters, the format is similar but may contain multiple verses
    if "reference" in data:
        # Extract book and chapter from reference
        ref_parts = data.get('reference', '').split(':')[0]
        result = f"📖 {ref_parts}\n"
        result += f"📝 {data.get('translation_name', 'Unknown translation')}\n\n"
        
        # Add text, cleaning up any extra newlines
        text = data.get('text', '').strip()
        result += text
    else:
        # Handle parameterized API response which may have a different structure
        result = "Chapter content:\n\n"
        result += str(data)  # Simplified for now, may need adjustment based on actual API response
    
    return result


if __name__ == "__main__":
    # Run the server directly when executed
    mcp.run()
