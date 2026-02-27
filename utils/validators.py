"""Input validation utilities"""

import re
from pathlib import Path
from typing import Any, List
from config import Config

class Validators:
    """Input validators for safety"""
    
    @staticmethod
    def validate_path(path: str) -> bool:
        """Validate file path"""
        try:
            p = Path(path).resolve()
            
            # Check if within workspace
            workspace = Config.WORKSPACE_DIR.resolve()
            if not str(p).startswith(str(workspace)):
                # Allow absolute paths if not in restricted areas
                for restricted in Config.RESTRICTED_PATHS:
                    if str(p).startswith(restricted):
                        return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_command(command: str) -> bool:
        """Validate shell command"""
        for restricted in Config.RESTRICTED_COMMANDS:
            if restricted in command:
                return False
        return True
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL"""
        pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return pattern.match(url) is not None
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 10000) -> str:
        """Sanitize user input"""
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Limit length
        if len(text) > max_length:
            text = text[:max_length]
        
        return text
