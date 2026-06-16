"""
Data structures for the automated knowledge base.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict


@dataclass
class ArticleMeta:
    """Meta information for an article."""
    id: str                    # Article ID (arXiv ID or URL hash)
    title: str
    authors: List[str]
    year: Optional[int]
    source: str               # "arxiv", "github", "rss", "semantic_scholar"
    url: Optional[str]        # Original URL
    pdf_url: Optional[str]    # Direct PDF download URL
    domain: str               # Research domain/category
    abstract: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ExperimentalSetup:
    """Experimental setup information."""
    datasets: List[str] = field(default_factory=list)
    metrics: List[str] = field(default_factory=list)
    baselines: List[str] = field(default_factory=list)


@dataclass
class ExtractedInfo:
    """Extracted key information from an article."""
    id: str
    title: str
    authors: List[str]
    year: Optional[int]
    source: str
    url: Optional[str]
    original_path: str
    domain: List[str]
    core_approach: str
    experimental_setup: ExperimentalSetup = field(default_factory=ExperimentalSetup)
    key_findings: List[str] = field(default_factory=list)
    innovations: List[str] = field(default_factory=list)
    open_problems: List[str] = field(default_factory=list)
    references: List[Dict[str, str]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DownloadResult:
    """Result of a download operation."""
    success: bool
    path: Optional[str] = None
    error_message: Optional[str] = None
