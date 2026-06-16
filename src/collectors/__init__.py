"""
Base collector interface for all data sources.
"""
from abc import ABC, abstractmethod
from typing import List

from src import ArticleMeta, DownloadResult


class BaseCollector(ABC):
    """Base class for all article collectors."""
    
    @abstractmethod
    def search(self, query: str, limit: int = 20) -> List[ArticleMeta]:
        """
        Search for articles by query.
        
        Args:
            query: Search keywords
            limit: Maximum number of results to return
            
        Returns:
            List of article metadata
        """
        pass
    
    @abstractmethod
    def download(self, article: ArticleMeta, output_dir: str) -> DownloadResult:
        """
        Download the article PDF to the output directory.
        
        Args:
            article: Article metadata
            output_dir: Output directory
            
        Returns:
            DownloadResult with success status and path
        """
        pass
