"""
Test suite for the Bible MCP server.
"""
import asyncio
import httpx
import json
from typing import Dict, Any, Optional, List, Tuple

# Test cases for different scenarios
TEST_CASES = [
    # Basic verses
    {"name": "Standard verse", "reference": "John 3:16", "translation": "web"},
    {"name": "Different translation", "reference": "John 3:16", "translation": "kjv"},
    
    # Edge cases
    {"name": "Single-chapter book", "reference": "Jude 1", "translation": "web"},
    {"name": "Last verse of chapter", "reference": "Genesis 1:31", "translation": "web"},
    {"name": "Verse range", "reference": "Matthew 5:3-10", "translation": "web"},
    {"name": "Verse with comma", "reference": "Matthew 5:3,5,7", "translation": "web"},
    
    # Error cases
    {"name": "Invalid book", "reference": "InvalidBook 1:1", "translation": "web", "expect_error": True},
    {"name": "Invalid chapter", "reference": "John 999:1", "translation": "web", "expect_error": True},
    {"name": "Invalid verse", "reference": "John 3:999", "translation": "web", "expect_error": True},
    {"name": "Invalid translation", "reference": "John 3:16", "translation": "invalid", "expect_error": True},
]

async def test_bible_api_client():
    """Test the Bible API client directly."""
    print("\n=== Testing Bible API Client ===")
    
    from bible_api import BibleAPIClient
    client = BibleAPIClient()
    
    # Test getting verse by reference
    for test_case in TEST_CASES:
        name = test_case["name"]
        reference = test_case["reference"]
        translation = test_case["translation"]
        expect_error = test_case.get("expect_error", False)
        
        print(f"\nTesting: {name}")
        print(f"Reference: {reference}, Translation: {translation}")
        
        try:
            result = await client.get_verse_by_reference(reference, translation)
            print(f"Success: {result.get('reference', 'No reference')}")
            
            if expect_error:
                print("❌ Expected error but got success")
            else:
                if 'reference' in result and 'text' in result and result['text'].strip():
                    print("✅ Test passed")
                else:
                    print("❌ Test failed - incomplete result")
                    print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {str(e)}")
            
            if expect_error:
                print("✅ Expected error received")
            else:
                print("❌ Test failed - unexpected error")
    
    # Test random verse
    print("\nTesting random verse")
    try:
        result = await client.get_random_verse()
        if 'reference' in result and 'text' in result and result['text'].strip():
            print("✅ Random verse test passed")
            print(f"Random verse: {result.get('reference', 'No reference')}")
        else:
            print("❌ Random verse test failed - incomplete result")
    except Exception as e:
        print(f"❌ Random verse test failed with error: {str(e)}")
    
    # Test NT filter
    print("\nTesting NT filter")
    try:
        result = await client.get_random_verse(book_ids="NT")
        if 'reference' in result and 'text' in result:
            print("✅ NT filter test passed")
            print(f"NT verse: {result.get('reference', 'No reference')}")
        else:
            print("❌ NT filter test failed - incomplete result")
    except Exception as e:
        print(f"❌ NT filter test failed with error: {str(e)}")
    
    # Test translations list
    print("\nTesting translations list")
    try:
        translations = await client.list_translations()
        if translations and isinstance(translations, list) and len(translations) > 0:
            print(f"✅ Found {len(translations)} translations")
        else:
            print("❌ Translations list test failed - no translations")
    except Exception as e:
        print(f"❌ Translations list test failed with error: {str(e)}")

async def main():
    """Run all tests."""
    await test_bible_api_client()
    print("\nAll tests completed.")

if __name__ == "__main__":
    asyncio.run(main())
