"""
Database management module for persistent storage
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import streamlit as st
from loguru import logger

class DatabaseManager:
    """Manager for SQLite database operations"""
    
    def __init__(self, db_path: str = "adk_writer.db"):
        """Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Documents table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS documents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        document_type TEXT NOT NULL,
                        provider TEXT NOT NULL,
                        model TEXT NOT NULL,
                        requirements TEXT,
                        recipient TEXT,
                        subject TEXT,
                        additional_context TEXT,
                        tone TEXT,
                        draft_document TEXT,
                        final_document TEXT,
                        quality_score REAL,
                        iterations INTEGER,
                        total_time REAL,
                        use_loop_agent BOOLEAN,
                        metadata TEXT
                    )
                """)
                
                # Statistics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS statistics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE DEFAULT (DATE('now')),
                        total_documents INTEGER DEFAULT 0,
                        avg_quality REAL DEFAULT 0,
                        avg_iterations REAL DEFAULT 0,
                        total_time REAL DEFAULT 0,
                        by_provider TEXT,
                        by_document_type TEXT,
                        UNIQUE(date)
                    )
                """)
                
                # Critique history table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS critique_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        document_id INTEGER,
                        iteration INTEGER,
                        critique_content TEXT,
                        quality_score REAL,
                        issues_found TEXT,
                        suggestions TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (document_id) REFERENCES documents (id)
                    )
                """)
                
                # User preferences table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_documents_created_at 
                    ON documents(created_at DESC)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_documents_provider 
                    ON documents(provider)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_critique_document_id 
                    ON critique_history(document_id)
                """)
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def save_document(self, document_data: Dict[str, Any]) -> int:
        """Save document to database
        
        Args:
            document_data: Document information to save
            
        Returns:
            Document ID
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Extract data
                input_data = document_data.get('input', {})
                result = document_data.get('result', {})
                
                cursor.execute("""
                    INSERT INTO documents (
                        document_type, provider, model, requirements, 
                        recipient, subject, additional_context, tone,
                        draft_document, final_document, quality_score,
                        iterations, total_time, use_loop_agent, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    input_data.get('document_type', ''),
                    result.get('provider', ''),
                    result.get('model_used', ''),
                    input_data.get('requirements', ''),
                    input_data.get('recipient', ''),
                    input_data.get('subject', ''),
                    input_data.get('additional_context', ''),
                    input_data.get('tone', ''),
                    result.get('draft_document', ''),
                    result.get('final_document', ''),
                    result.get('quality_score', 0),
                    result.get('iterations', 0),
                    result.get('total_time', 0),
                    result.get('use_loop_agent', False),
                    json.dumps(result.get('metadata', {}))
                ))
                
                document_id = cursor.lastrowid
                
                # Save critique history if available
                critique_history = result.get('critique_history', [])
                for idx, critique in enumerate(critique_history):
                    self.save_critique(document_id, idx + 1, critique)
                
                # Update daily statistics
                self.update_statistics(result)
                
                conn.commit()
                logger.info(f"Document saved with ID: {document_id}")
                return document_id
                
        except Exception as e:
            logger.error(f"Error saving document: {str(e)}")
            raise
    
    def save_critique(self, document_id: int, iteration: int, critique_data: Dict[str, Any]):
        """Save critique history
        
        Args:
            document_id: ID of the document
            iteration: Iteration number
            critique_data: Critique information
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO critique_history (
                        document_id, iteration, critique_content,
                        quality_score, issues_found, suggestions
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    document_id,
                    iteration,
                    critique_data.get('content', ''),
                    critique_data.get('quality_score', 0),
                    json.dumps(critique_data.get('issues_found', [])),
                    json.dumps(critique_data.get('suggestions', []))
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error saving critique: {str(e)}")
    
    def update_statistics(self, result: Dict[str, Any]):
        """Update daily statistics
        
        Args:
            result: Document result data
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                today = datetime.now().date()
                
                # Get current statistics
                cursor.execute("""
                    SELECT total_documents, avg_quality, avg_iterations, total_time,
                           by_provider, by_document_type
                    FROM statistics WHERE date = ?
                """, (today,))
                
                row = cursor.fetchone()
                
                if row:
                    # Update existing statistics
                    total_docs, avg_quality, avg_iterations, total_time, by_provider_str, by_type_str = row
                    
                    by_provider = json.loads(by_provider_str) if by_provider_str else {}
                    by_type = json.loads(by_type_str) if by_type_str else {}
                    
                    # Update counts
                    total_docs += 1
                    current_quality = result.get('quality_score', 0)
                    current_iterations = result.get('iterations', 0)
                    current_time = result.get('total_time', 0)
                    
                    # Update averages
                    avg_quality = (avg_quality * (total_docs - 1) + current_quality) / total_docs
                    avg_iterations = (avg_iterations * (total_docs - 1) + current_iterations) / total_docs
                    total_time += current_time
                    
                    # Update provider statistics
                    provider = result.get('provider', 'Unknown')
                    by_provider[provider] = by_provider.get(provider, 0) + 1
                    
                    # Update document type statistics
                    doc_type = result.get('document_type', 'Unknown')
                    by_type[doc_type] = by_type.get(doc_type, 0) + 1
                    
                    cursor.execute("""
                        UPDATE statistics SET
                            total_documents = ?,
                            avg_quality = ?,
                            avg_iterations = ?,
                            total_time = ?,
                            by_provider = ?,
                            by_document_type = ?
                        WHERE date = ?
                    """, (
                        total_docs, avg_quality, avg_iterations, total_time,
                        json.dumps(by_provider), json.dumps(by_type), today
                    ))
                else:
                    # Create new statistics entry
                    provider = result.get('provider', 'Unknown')
                    doc_type = result.get('document_type', 'Unknown')
                    
                    cursor.execute("""
                        INSERT INTO statistics (
                            date, total_documents, avg_quality, avg_iterations,
                            total_time, by_provider, by_document_type
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        today, 1,
                        result.get('quality_score', 0),
                        result.get('iterations', 0),
                        result.get('total_time', 0),
                        json.dumps({provider: 1}),
                        json.dumps({doc_type: 1})
                    ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error updating statistics: {str(e)}")
    
    def get_documents(self, limit: int = 100, offset: int = 0, 
                     provider: Optional[str] = None,
                     document_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get documents from database
        
        Args:
            limit: Maximum number of documents to retrieve
            offset: Offset for pagination
            provider: Filter by provider
            document_type: Filter by document type
            
        Returns:
            List of documents
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT id, created_at, document_type, provider, model,
                           requirements, recipient, subject, additional_context,
                           tone, draft_document, final_document, quality_score,
                           iterations, total_time, use_loop_agent, metadata
                    FROM documents
                    WHERE 1=1
                """
                params = []
                
                if provider:
                    query += " AND provider = ?"
                    params.append(provider)
                
                if document_type:
                    query += " AND document_type = ?"
                    params.append(document_type)
                
                query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                
                columns = [col[0] for col in cursor.description]
                documents = []
                
                for row in cursor.fetchall():
                    doc = dict(zip(columns, row))
                    if doc['metadata']:
                        doc['metadata'] = json.loads(doc['metadata'])
                    documents.append(doc)
                
                return documents
                
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return []
    
    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get statistics for the last N days
        
        Args:
            days: Number of days to include
            
        Returns:
            Statistics dictionary
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Overall statistics
                cursor.execute("""
                    SELECT 
                        SUM(total_documents) as total_docs,
                        AVG(avg_quality) as overall_quality,
                        AVG(avg_iterations) as overall_iterations,
                        SUM(total_time) as total_time
                    FROM statistics
                    WHERE date >= date('now', '-' || ? || ' days')
                """, (days,))
                
                overall = cursor.fetchone()
                
                # Daily statistics
                cursor.execute("""
                    SELECT date, total_documents, avg_quality, avg_iterations, total_time
                    FROM statistics
                    WHERE date >= date('now', '-' || ? || ' days')
                    ORDER BY date DESC
                """, (days,))
                
                daily_stats = []
                for row in cursor.fetchall():
                    daily_stats.append({
                        'date': row[0],
                        'total_documents': row[1],
                        'avg_quality': row[2],
                        'avg_iterations': row[3],
                        'total_time': row[4]
                    })
                
                # Provider statistics
                cursor.execute("""
                    SELECT by_provider
                    FROM statistics
                    WHERE date >= date('now', '-' || ? || ' days')
                """, (days,))
                
                provider_stats = {}
                for row in cursor.fetchall():
                    if row[0]:
                        stats = json.loads(row[0])
                        for provider, count in stats.items():
                            provider_stats[provider] = provider_stats.get(provider, 0) + count
                
                # Document type statistics
                cursor.execute("""
                    SELECT by_document_type
                    FROM statistics
                    WHERE date >= date('now', '-' || ? || ' days')
                """, (days,))
                
                type_stats = {}
                for row in cursor.fetchall():
                    if row[0]:
                        stats = json.loads(row[0])
                        for doc_type, count in stats.items():
                            type_stats[doc_type] = type_stats.get(doc_type, 0) + count
                
                return {
                    'total_documents': overall[0] or 0,
                    'avg_quality': overall[1] or 0,
                    'avg_iterations': overall[2] or 0,
                    'total_time': overall[3] or 0,
                    'daily_stats': daily_stats,
                    'by_provider': provider_stats,
                    'by_document_type': type_stats
                }
                
        except Exception as e:
            logger.error(f"Error retrieving statistics: {str(e)}")
            return {
                'total_documents': 0,
                'avg_quality': 0,
                'avg_iterations': 0,
                'total_time': 0,
                'daily_stats': [],
                'by_provider': {},
                'by_document_type': {}
            }
    
    def save_preference(self, key: str, value: Any):
        """Save user preference
        
        Args:
            key: Preference key
            value: Preference value
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                value_str = json.dumps(value) if not isinstance(value, str) else value
                
                cursor.execute("""
                    INSERT OR REPLACE INTO user_preferences (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (key, value_str))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error saving preference: {str(e)}")
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference
        
        Args:
            key: Preference key
            default: Default value if not found
            
        Returns:
            Preference value
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT value FROM user_preferences WHERE key = ?
                """, (key,))
                
                row = cursor.fetchone()
                if row:
                    try:
                        return json.loads(row[0])
                    except:
                        return row[0]
                
                return default
                
        except Exception as e:
            logger.error(f"Error getting preference: {str(e)}")
            return default
    
    def export_data(self, export_type: str = "json") -> str:
        """Export database data
        
        Args:
            export_type: Format to export (json or csv)
            
        Returns:
            Exported data as string
        """
        try:
            documents = self.get_documents(limit=10000)
            statistics = self.get_statistics(days=365)
            
            if export_type == "json":
                return json.dumps({
                    'documents': documents,
                    'statistics': statistics,
                    'export_date': datetime.now().isoformat()
                }, indent=2, default=str)
            
            elif export_type == "csv":
                import csv
                import io
                
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=[
                    'created_at', 'document_type', 'provider', 'model',
                    'quality_score', 'iterations', 'total_time'
                ])
                
                writer.writeheader()
                for doc in documents:
                    writer.writerow({
                        'created_at': doc['created_at'],
                        'document_type': doc['document_type'],
                        'provider': doc['provider'],
                        'model': doc['model'],
                        'quality_score': doc['quality_score'],
                        'iterations': doc['iterations'],
                        'total_time': doc['total_time']
                    })
                
                return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error exporting data: {str(e)}")
            return ""


# Singleton instance
@st.cache_resource
def get_db_manager():
    """Get database manager instance (cached)"""
    return DatabaseManager()