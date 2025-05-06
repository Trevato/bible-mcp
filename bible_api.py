"""
Bible API client for interacting with bible-api.com.
"""
import httpx
from typing import Dict, List, Optional, Any, Tuple, Union


class BibleAPIClient:
    """
    Client for interacting with the bible-api.com service.
    
    This client provides methods for retrieving Bible verses and passages
    using both the User Input API and the Parameterized API.
    """
    BASE_URL = "https://bible-api.com"
    PARAMETRIZED_URL = "https://bible-api.com/data"
    
    async def get_verse_by_reference(self, reference: str, translation: Optional[str] = None) -> Dict:
        """
        Get verse(s) by reference using the User Input API.
        
        Args:
            reference: Bible reference (e.g., "john 3:16", "matt 25:31-33,46")
            translation: Optional translation ID (e.g., "kjv", "web")
            
        Returns:
            Dictionary containing the verse data
        """
        url = f"{self.BASE_URL}/{reference}"
        if translation:
            url += f"?translation={translation}"
            
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            return response.json()
    
    async def get_by_book_chapter_verse(
        self, 
        translation_id: str, 
        book_id: str, 
        chapter: int, 
        verse: Optional[int] = None
    ) -> Dict:
        """
        Get verse(s) using the Parameterized API with specific identifiers.
        
        Args:
            translation_id: Translation identifier (e.g., "web", "kjv")
            book_id: Book identifier (e.g., "JHN", "GEN")
            chapter: Chapter number
            verse: Optional verse number
            
        Returns:
            Dictionary containing the verse data
        """
        # Build URL based on whether a specific verse is requested
        if verse is not None:
            reference = f"{book_id} {chapter}:{verse}"
            url = f"{self.BASE_URL}/{reference}?translation={translation_id}"
        else:
            url = f"{self.PARAMETRIZED_URL}/{translation_id}/{book_id}/{chapter}"
            
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    
    async def get_random_verse(
        self, 
        translation_id: str = "web", 
        book_ids: Optional[Union[List[str], str]] = None
    ) -> Dict:
        """
        Get a random verse from the Bible.
        
        Args:
            translation_id: Translation identifier (default: "web")
            book_ids: Optional list of book IDs or special string "OT" or "NT"
            
        Returns:
            Dictionary containing the random verse data
        """
        url = f"{self.PARAMETRIZED_URL}/{translation_id}/random"
        
        # Add book filters if specified
        if book_ids:
            if isinstance(book_ids, list):
                book_ids_str = ",".join(book_ids)
            else:
                book_ids_str = book_ids  # Assume it's "OT" or "NT"
            url += f"/{book_ids_str}"
            
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
            
    async def list_translations(self) -> List[Dict]:
        """
        Get a list of available translations.
        
        Returns:
            List of translation dictionaries with id, name, and language
        """
        # bible-api.com doesn't have a direct endpoint for this,
        # so we're providing the list based on their documentation
        return [
            {"id": "web", "name": "World English Bible", "language": "English", "default": True},
            {"id": "kjv", "name": "King James Version", "language": "English"},
            {"id": "asv", "name": "American Standard Version (1901)", "language": "English"},
            {"id": "bbe", "name": "Bible in Basic English", "language": "English"},
            {"id": "darby", "name": "Darby Bible", "language": "English"},
            {"id": "dra", "name": "Douay-Rheims 1899 American Edition", "language": "English"},
            {"id": "ylt", "name": "Young's Literal Translation (NT only)", "language": "English"},
            {"id": "oeb-cw", "name": "Open English Bible, Commonwealth Edition", "language": "English (UK)"},
            {"id": "webbe", "name": "World English Bible, British Edition", "language": "English (UK)"},
            {"id": "oeb-us", "name": "Open English Bible, US Edition", "language": "English (US)"},
            {"id": "cherokee", "name": "Cherokee New Testament", "language": "Cherokee"},
            {"id": "cuv", "name": "Chinese Union Version", "language": "Chinese"},
            {"id": "bkr", "name": "Bible kralická", "language": "Czech"},
            {"id": "clementine", "name": "Clementine Latin Vulgate", "language": "Latin"},
            {"id": "almeida", "name": "João Ferreira de Almeida", "language": "Portuguese"},
            {"id": "rccv", "name": "Protestant Romanian Corrected Cornilescu Version", "language": "Romanian"},
        ]
