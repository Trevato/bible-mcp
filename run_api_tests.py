"""
Simplified test script for the Bible API client.
"""
import asyncio
import json
from bible_api import BibleAPIClient

async def test_api():
    client = BibleAPIClient()
    
    # Test 1: Basic verse retrieval
    print("\nTest 1: Basic verse retrieval")
    try:
        result = await client.get_verse_by_reference("John 3:16")
        print(f"Result: {result.get('reference')}")
        print(f"Text: {result.get('text')[:50]}...")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test 2: Random verse
    print("\nTest 2: Random verse")
    try:
        result = await client.get_random_verse()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test 3: Chapter retrieval
    print("\nTest 3: Chapter retrieval")
    try:
        result = await client.get_by_book_chapter_verse("web", "GEN", 1)
        print(f"Result type: {type(result)}")
        print(f"Result: {json.dumps(result)[:100]}...")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test 4: Verse in single-chapter book
    print("\nTest 4: Verse in single-chapter book")
    try:
        result = await client.get_verse_by_reference("Jude 1", "web")
        print(f"Result: {result.get('reference')}")
        print(f"Text: {result.get('text')[:50]}...")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_api())
