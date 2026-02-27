"""Search and find tools"""

import re
import fnmatch
from pathlib import Path
from typing import List
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class SearchTools:
    """File and content search tools"""
    
    def __init__(self):
        self.workspace = Config.WORKSPACE_DIR
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve path relative to workspace"""
        p = Path(path)
        if not p.is_absolute():
            p = self.workspace / p
        return p.resolve()
    
    async def grep_search(self, pattern: str, path: str, file_pattern: str = "*") -> str:
        """Search files using regex pattern"""
        try:
            search_path = self._resolve_path(path)
            
            if not search_path.exists():
                return f"Error: Path not found: {path}"
            
            regex = re.compile(pattern)
            results = []
            
            # Search files
            for file_path in search_path.rglob(file_pattern):
                if not file_path.is_file():
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                rel_path = file_path.relative_to(search_path)
                                results.append(f"{rel_path}:{line_num}: {line.rstrip()}")
                except Exception as e:
                    logger.debug(f"Skipped {file_path}: {e}")
            
            output = "\n".join(results[:100])  # Limit results
            if len(results) > 100:
                output += f"\n... and {len(results) - 100} more matches"
            
            logger.info(f"Grep search found {len(results)} matches")
            return output if output else "No matches found"
            
        except Exception as e:
            logger.error(f"Grep search error: {e}")
            return f"Error: {str(e)}"
    
    async def fuzzy_search(self, query: str, path: str) -> str:
        """Fuzzy search for files by name"""
        try:
            search_path = self._resolve_path(path)
            
            if not search_path.exists():
                return f"Error: Path not found: {path}"
            
            query_lower = query.lower()
            results = []
            
            # Fuzzy match file names
            for file_path in search_path.rglob('*'):
                if file_path.is_file():
                    name_lower = file_path.name.lower()
                    if query_lower in name_lower:
                        rel_path = file_path.relative_to(search_path)
                        results.append(str(rel_path))
            
            results.sort()
            output = "\n".join(results[:50])  # Limit results
            if len(results) > 50:
                output += f"\n... and {len(results) - 50} more matches"
            
            logger.info(f"Fuzzy search found {len(results)} matches")
            return output if output else "No matches found"
            
        except Exception as e:
            logger.error(f"Fuzzy search error: {e}")
            return f"Error: {str(e)}"
    
    async def find_files(self, pattern: str, path: str) -> str:
        """Find files matching a pattern"""
        try:
            search_path = self._resolve_path(path)
            
            if not search_path.exists():
                return f"Error: Path not found: {path}"
            
            results = []
            
            for file_path in search_path.rglob(pattern):
                if file_path.is_file():
                    rel_path = file_path.relative_to(search_path)
                    size = file_path.stat().st_size
                    results.append(f"{size:>10} {rel_path}")
            
            results.sort()
            output = "\n".join(results[:100])
            if len(results) > 100:
                output += f"\n... and {len(results) - 100} more matches"
            
            logger.info(f"Find files found {len(results)} matches")
            return output if output else "No matches found"
            
        except Exception as e:
            logger.error(f"Find files error: {e}")
            return f"Error: {str(e)}"
    
    async def search_content(self, text: str, path: str) -> str:
        """Search file contents for text"""
        try:
            search_path = self._resolve_path(path)
            
            if not search_path.exists():
                return f"Error: Path not found: {path}"
            
            text_lower = text.lower()
            results = []
            
            for file_path in search_path.rglob('*'):
                if not file_path.is_file():
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        if text_lower in content:
                            rel_path = file_path.relative_to(search_path)
                            results.append(str(rel_path))
                except Exception as e:
                    logger.debug(f"Skipped {file_path}: {e}")
            
            results.sort()
            output = "\n".join(results[:50])
            if len(results) > 50:
                output += f"\n... and {len(results) - 50} more matches"
            
            logger.info(f"Content search found {len(results)} matches")
            return output if output else "No matches found"
            
        except Exception as e:
            logger.error(f"Content search error: {e}")
            return f"Error: {str(e)}"
