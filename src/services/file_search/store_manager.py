"""
File Search Store Manager.

Manages File Search Stores using the Google Gemini API.
"""

import logging
from typing import Dict, Any, Optional
from google import genai
from src.config import Config

logger = logging.getLogger(__name__)


class FileSearchStoreManager:
    """Manages File Search Stores from Google Gemini API."""
    
    def __init__(self):
        """Initialize the File Search Store Manager."""
        if not Config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not configured in environment")
        
        self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)
    
    def create_store(self, display_name: str) -> Dict[str, Any]:
        """
        Create a new File Search Store.
        
        Args:
            display_name: User-friendly name for the store
            
        Returns:
            Dictionary with store information:
            - name: Full Google store name (projects/.../fileSearchStores/...)
            - display_name: User-friendly name
        """
        try:
            logger.info(f"Creating file search store: {display_name}")
            store = self.client.file_search_stores.create(
                config={'display_name': display_name}
            )
            
            logger.info(f"Successfully created file search store: {store.name}")
            return {
                'name': store.name,
                'display_name': display_name
            }
        except Exception as e:
            logger.error(f"Error creating file search store: {e}")
            raise RuntimeError(f"Failed to create file search store: {str(e)}")
    
    def get_store(self, store_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a File Search Store.
        
        Args:
            store_name: Full Google store name (projects/.../fileSearchStores/...)
            
        Returns:
            Dictionary with store information or None if not found
        """
        try:
            store = self.client.file_search_stores.get(store_name)
            return {
                'name': store.name,
                'display_name': getattr(store, 'display_name', None)
            }
        except Exception as e:
            logger.error(f"Error getting file search store {store_name}: {e}")
            return None
    
    def delete_store(self, store_name: str) -> bool:
        """
        Delete a File Search Store.
        
        Args:
            store_name: Full Google store name (projects/.../fileSearchStores/...)
            
        Returns:
            True if deleted successfully
        """
        try:
            logger.info(f"Deleting file search store: {store_name}")
            self.client.file_search_stores.delete(store_name)
            logger.info(f"Successfully deleted file search store: {store_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file search store {store_name}: {e}")
            raise RuntimeError(f"Failed to delete file search store: {str(e)}")

