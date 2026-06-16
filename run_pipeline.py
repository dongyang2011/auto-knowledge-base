#!/usr/bin/env python3
"""
Example: End-to-end pipeline for a single domain.
- Search articles from arXiv
- Download PDFs
- Extract information using LLM
"""

import os
import argparse
from pathlib import Path
from dotenv import load_dotenv

from src.collectors import BaseCollector
from src.collectors.arxiv import ArxivCollector
from src.extractors import LLMInformationExtractor
from src.storage.metadata_db import MetadataDB
from src.utils.pdf import extract_text_from_pdf, split_text_into_chunks

load_dotenv()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--limit", type=int, default=10, help="Number of papers")
    args = parser.parse_args()
    
    # Initialize components
    db = MetadataDB("data/articles.db")
    collector = ArxivCollector()
    extractor = LLMInformationExtractor(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("OPENAI_MODEL", "gpt-4o")
    )
    
    # Search
    print(f"Searching arXiv for: {args.query}")
    articles = collector.search(args.query, limit=args.limit)
    print(f"Found {len(articles)} articles")
    
    # Download
    domain_dir = args.query.replace(' ', '-').lower()
    output_original = Path("originals") / domain_dir
    output_original.mkdir(parents=True, exist_ok=True)
    
    for article in articles:
        # Check if already downloaded
        existing = db.get_article(article.id)
        if existing and existing["status"] in ["downloaded", "extracted"]:
            print(f"Already downloaded: {article.title}")
            continue
        
        print(f"Downloading: {article.title}")
        result = collector.download(article, str(output_original))
        if result.success:
            db.add_article(article, result.path)
            db.add_log(article.id, "download", "success")
            print(f"  ✓ Downloaded to {result.path}")
        else:
            db.add_article(article, None)
            db.add_log(article.id, "download", "failed", result.error_message)
            print(f"  ✗ Failed: {result.error_message}")
    
    # Extract
    to_extract = db.list_articles_by_status("downloaded")
    print(f"\nExtracting information for {len(to_extract)} downloaded articles...")
    
    domain_extracted = Path("extracted") / domain_dir
    domain_extracted.mkdir(parents=True, exist_ok=True)
    
    for article_meta in to_extract:
        article_id = article_meta["id"]
        original_path = article_meta["original_path"]
        print(f"Extracting: {article_meta['title']}")
        
        try:
            # Extract text from PDF
            text = extract_text_from_pdf(original_path)
            
            # For now, take first 4000 characters (fits in context)
            # TODO: split into sections and extract incrementally
            text_for_llm = text[:6000]
            
            extracted = extractor.extract(text_for_llm)
            if not extracted:
                db.add_log(article_id, "extraction", "failed", "LLLM extraction returned None")
                continue
            
            # Fill metadata from article_meta
            extracted.id = article_id
            extracted.title = article_meta["title"]
            extracted.year = article_meta["year"]
            extracted.source = article_meta["source"]
            extracted.url = article_meta["url"]
            extracted.original_path = original_path
            extracted.domain = [article_meta["domain"]]
            
            # Save
            md_path = domain_extracted / f"{article_id}.md"
            json_path = domain_extracted / f"{article_id}.json"
            extractor.save_extracted(extracted, md_path, json_path)
            
            # Update database
            db.update_extracted_paths(article_id, str(md_path), str(json_path))
            db.add_log(article_id, "extraction", "success")
            print(f"  ✓ Saved to {md_path}, {json_path}")
        
        except Exception as e:
            db.add_log(article_id, "extraction", "failed", str(e))
            print(f"  ✗ Failed: {e}")
    
    db.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
