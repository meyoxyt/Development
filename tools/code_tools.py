"""Code analysis and formatting tools"""

import subprocess
from pathlib import Path
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class CodeTools:
    """Code parsing, formatting, and linting"""
    
    def __init__(self):
        self.workspace = Config.WORKSPACE_DIR
    
    def _resolve_path(self, path: str) -> Path:
        p = Path(path)
        if not p.is_absolute():
            p = self.workspace / p
        return p.resolve()
    
    async def parse_code(self, path: str, language: str = "python") -> str:
        """Parse code to AST (simplified)"""
        try:
            file_path = self._resolve_path(path)
            
            if not file_path.exists():
                return f"Error: File not found: {path}"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic code statistics
            lines = content.splitlines()
            total_lines = len(lines)
            code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
            comment_lines = len([l for l in lines if l.strip().startswith('#')])
            blank_lines = len([l for l in lines if not l.strip()])
            
            result = [
                f"File: {path}",
                f"Language: {language}",
                f"Total Lines: {total_lines}",
                f"Code Lines: {code_lines}",
                f"Comment Lines: {comment_lines}",
                f"Blank Lines: {blank_lines}"
            ]
            
            return "\n".join(result)
            
        except Exception as e:
            logger.error(f"Parse code error: {e}")
            return f"Error: {str(e)}"
    
    async def format_code(self, path: str, language: str = "python") -> str:
        """Auto-format code file"""
        try:
            file_path = self._resolve_path(path)
            
            if not file_path.exists():
                return f"Error: File not found: {path}"
            
            if language.lower() == "python":
                # Use Black formatter
                result = subprocess.run(
                    ['black', '--quiet', str(file_path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    logger.info(f"Formatted {path}")
                    return f"Successfully formatted {path} with Black"
                else:
                    return f"Error: Black formatter failed\n{result.stderr}"
            else:
                return f"Error: Formatting not supported for {language}"
                
        except FileNotFoundError:
            return "Error: Black formatter not installed (pip install black)"
        except Exception as e:
            logger.error(f"Format code error: {e}")
            return f"Error: {str(e)}"
    
    async def lint_code(self, path: str, language: str = "python") -> str:
        """Lint and check code"""
        try:
            file_path = self._resolve_path(path)
            
            if not file_path.exists():
                return f"Error: File not found: {path}"
            
            if language.lower() == "python":
                # Use flake8
                result = subprocess.run(
                    ['flake8', str(file_path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                output = result.stdout
                if not output:
                    output = "No issues found ✓"
                
                logger.info(f"Linted {path}")
                return output
            else:
                return f"Error: Linting not supported for {language}"
                
        except FileNotFoundError:
            return "Error: flake8 not installed (pip install flake8)"
        except Exception as e:
            logger.error(f"Lint code error: {e}")
            return f"Error: {str(e)}"
