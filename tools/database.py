"""Database operation tools"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class DatabaseTools:
    """SQLite database operations"""
    
    def __init__(self):
        self.workspace = Config.WORKSPACE_DIR
        self.db_path = self.workspace / "assistant.db"
        self._init_db()
    
    def _init_db(self):
        """Initialize database"""
        try:
            self.workspace.mkdir(exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            conn.close()
            logger.info(f"Database initialized: {self.db_path}")
        except Exception as e:
            logger.error(f"Database init error: {e}")
    
    async def db_query(self, query: str) -> str:
        """Execute SQL query"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(query)
            
            # Check if it's a SELECT query
            if query.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                
                if not rows:
                    return "No results"
                
                # Format results as table
                headers = rows[0].keys()
                result = [" | ".join(headers)]
                result.append("-" * len(result[0]))
                
                for row in rows[:100]:  # Limit results
                    result.append(" | ".join(str(row[col]) for col in headers))
                
                if len(rows) > 100:
                    result.append(f"... and {len(rows) - 100} more rows")
                
                output = "\n".join(result)
            else:
                conn.commit()
                output = f"Query executed successfully. Rows affected: {cursor.rowcount}"
            
            conn.close()
            logger.info(f"Query executed: {query[:100]}")
            return output
            
        except Exception as e:
            logger.error(f"Database query error: {e}")
            return f"Error: {str(e)}"
    
    async def db_create_table(self, name: str, schema: str) -> str:
        """Create table"""
        try:
            query = f"CREATE TABLE IF NOT EXISTS {name} ({schema})"
            return await self.db_query(query)
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def db_insert(self, table: str, data: Dict[str, Any]) -> str:
        """Insert record"""
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, list(data.values()))
            conn.commit()
            conn.close()
            
            logger.info(f"Inserted record into {table}")
            return f"Successfully inserted record into {table}"
            
        except Exception as e:
            logger.error(f"Database insert error: {e}")
            return f"Error: {str(e)}"
