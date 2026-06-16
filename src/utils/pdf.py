"""
PDF text extraction using PyMuPDF.
"""
from pathlib import Path
from typing import List, Optional
import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text as a single string
    """
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n\n"
    return text


def split_text_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks for LLM processing.
    
    Args:
        text: Input text
        chunk_size: Maximum tokens per chunk (approximate by characters)
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunks.append(text[start:])
            break
        # Try to break at paragraph boundary
        para_break = text.rfind('\n\n', start, end)
        if para_break > start + chunk_size // 2:
            end = para_break + 2
        else:
            # Fallback to space
            space_break = text.rfind(' ', start, end)
            if space_break > start + chunk_size // 2:
                end = space_break + 1
        chunks.append(text[start:end])
        start = end - overlap
    
    return chunks
