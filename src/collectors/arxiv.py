"""
arXiv collector - search and download papers from arXiv.
"""
import feedparser
import requests
import os
import hashlib
from typing import List

from src import ArticleMeta, DownloadResult
from src.collectors import BaseCollector


class ArxivCollector(BaseCollector):
    """arXiv article collector."""
    
    BASE_SEARCH_URL = "http://export.arxiv.org/api/query"
    BASE_PDF_URL = "https://arxiv.org/pdf/{id}.pdf"
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    def search(self, query: str, limit: int = 20) -> List[ArticleMeta]:
        """Search arXiv by query."""
        url = f"{self.BASE_SEARCH_URL}?search_query={query}&max_results={limit}&sortBy=relevance"
        response = requests.get(url, timeout=self.timeout)
        response.raise_for_status()
        
        feed = feedparser.parse(response.content)
        results = []
        
        for entry in feed.entries:
            # Extract arXiv ID from id
            arxiv_id = entry.id.split('/')[-1]
            title = entry.title
            authors = [author.name for author in entry.authors]
            year = int(entry.published[:4])
            pdf_url = self.BASE_PDF_URL.format(id=arxiv_id)
            
            results.append(ArticleMeta(
                id=arxiv_id,
                title=title,
                authors=authors,
                year=year,
                source="arxiv",
                url=entry.link,
                pdf_url=pdf_url,
                domain=query.replace(' ', '-').lower(),
                abstract=entry.summary
            ))
        
        return results
    
    def download(self, article: ArticleMeta, output_dir: str) -> DownloadResult:
        """Download PDF from arXiv."""
        if not article.pdf_url:
            return DownloadResult(
                success=False,
                error_message="No PDF URL available"
            )
        
        try:
            response = requests.get(article.pdf_url, timeout=self.timeout)
            response.raise_for_status()
            
            filename = f"{article.id}.pdf"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return DownloadResult(
                success=True,
                path=filepath
            )
        
        except Exception as e:
            return DownloadResult(
                success=False,
                error_message=str(e)
            )
