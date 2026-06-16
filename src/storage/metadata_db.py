"""
Metadata database - SQLite for tracking article processing status.
"""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path

from src import ArticleMeta, ExtractedInfo


class MetadataDB:
    """SQLite metadata database for tracking articles."""
    
    CREATE_TABLES = [
        """
        CREATE TABLE IF NOT EXISTS articles (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            year INTEGER,
            source TEXT NOT NULL,
            url TEXT,
            original_path TEXT,
            extracted_path_md TEXT,
            extracted_path_json TEXT,
            domain TEXT,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS domains (
            domain_id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain_name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS article_domain (
            article_id TEXT REFERENCES articles(id),
            domain_id INTEGER REFERENCES domains(domain_id),
            PRIMARY KEY (article_id, domain_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS processing_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id TEXT REFERENCES articles(id),
            step TEXT NOT NULL,
            status TEXT NOT NULL,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    ]
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database and create tables."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        cursor = self._conn.cursor()
        for create_sql in self.CREATE_TABLES:
            cursor.execute(create_sql)
        self._conn.commit()
    
    def add_article(self, article: ArticleMeta, original_path: Optional[str]) -> str:
        """Add a new article to the database."""
        cursor = self._conn.cursor()
        domain = article.domain
        status = "downloaded" if original_path else "pending"
        
        cursor.execute("""
            INSERT OR REPLACE INTO articles
            (id, title, year, source, url, original_path, domain, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article.id,
            article.title,
            article.year,
            article.source,
            article.url,
            original_path,
            domain,
            status
        ))
        self._conn.commit()
        return article.id
    
    def get_article(self, article_id: str) -> Optional[Dict]:
        """Get article by ID."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
        row = cursor.fetchone()
        if not row:
            return None
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))
    
    def list_articles_by_status(self, status: str) -> List[Dict]:
        """List articles with given status."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM articles WHERE status = ?", (status,))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def update_status(self, article_id: str, status: str):
        """Update article processing status."""
        cursor = self._conn.cursor()
        cursor.execute("""
            UPDATE articles
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, article_id))
        self._conn.commit()
    
    def update_extracted_paths(self, article_id: str, md_path: str, json_path: str):
        """Update paths after extraction."""
        cursor = self._conn.cursor()
        cursor.execute("""
            UPDATE articles
            SET extracted_path_md = ?, extracted_path_json = ?,
                status = 'extracted', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (md_path, json_path, article_id))
        self._conn.commit()
    
    def add_log(self, article_id: str, step: str, status: str, error_message: Optional[str] = None):
        """Add processing log entry."""
        cursor = self._conn.cursor()
        cursor.execute("""
            INSERT INTO processing_log (article_id, step, status, error_message)
            VALUES (?, ?, ?, ?)
        """, (article_id, step, status, error_message))
        self._conn.commit()
    
    def close(self):
        """Close database connection."""
        if self._conn:
            self._conn.close()
