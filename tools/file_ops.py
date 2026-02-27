"""File operation tools"""

import os
import shutil
from pathlib import Path
from typing import Optional, List
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class FileOperations:
    """File and directory operations"""
    
    def __init__(self):
        self.workspace = Config.WORKSPACE_DIR
        self.workspace.mkdir(exist_ok=True)
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve path relative to workspace"""
        p = Path(path)
        if not p.is_absolute():
            p = self.workspace / p
        return p.resolve()
    
    def _validate_path(self, path: Path) -> bool:
        """Validate path is within workspace and not restricted"""
        try:
            path_str = str(path)
            for restricted in Config.RESTRICTED_PATHS:
                if path_str.startswith(restricted):
                    raise ValueError(f"Access to {restricted} is restricted")
            return True
        except Exception as e:
            logger.error(f"Path validation failed: {e}")
            raise
    
    async def read_file(self, path: str) -> str:
        """Read file contents"""
        try:
            file_path = self._resolve_path(path)
            self._validate_path(file_path)
            
            if not file_path.exists():
                return f"Error: File not found: {path}"
            
            if not file_path.is_file():
                return f"Error: Not a file: {path}"
            
            # Check file size
            size_mb = file_path.stat().st_size / (1024 * 1024)
            if size_mb > Config.MAX_FILE_SIZE_MB:
                return f"Error: File too large ({size_mb:.2f}MB > {Config.MAX_FILE_SIZE_MB}MB)"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Read file: {path} ({len(content)} bytes)")
            return content
            
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
            return f"Error: {str(e)}"
    
    async def write_file(self, path: str, content: str) -> str:
        """Write content to file"""
        try:
            file_path = self._resolve_path(path)
            self._validate_path(file_path)
            
            # Create parent directories
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Wrote file: {path} ({len(content)} bytes)")
            return f"Successfully wrote {len(content)} bytes to {path}"
            
        except Exception as e:
            logger.error(f"Error writing file {path}: {e}")
            return f"Error: {str(e)}"
    
    async def append_file(self, path: str, content: str) -> str:
        """Append content to file"""
        try:
            file_path = self._resolve_path(path)
            self._validate_path(file_path)
            
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Appended to file: {path} ({len(content)} bytes)")
            return f"Successfully appended {len(content)} bytes to {path}"
            
        except Exception as e:
            logger.error(f"Error appending to file {path}: {e}")
            return f"Error: {str(e)}"
    
    async def delete_file(self, path: str) -> str:
        """Delete a file"""
        try:
            file_path = self._resolve_path(path)
            self._validate_path(file_path)
            
            if not file_path.exists():
                return f"Error: File not found: {path}"
            
            if not file_path.is_file():
                return f"Error: Not a file: {path}"
            
            file_path.unlink()
            logger.info(f"Deleted file: {path}")
            return f"Successfully deleted {path}"
            
        except Exception as e:
            logger.error(f"Error deleting file {path}: {e}")
            return f"Error: {str(e)}"
    
    async def list_directory(self, path: str, recursive: bool = False) -> str:
        """List directory contents"""
        try:
            dir_path = self._resolve_path(path)
            self._validate_path(dir_path)
            
            if not dir_path.exists():
                return f"Error: Directory not found: {path}"
            
            if not dir_path.is_dir():
                return f"Error: Not a directory: {path}"
            
            results = []
            
            if recursive:
                for item in dir_path.rglob('*'):
                    rel_path = item.relative_to(dir_path)
                    item_type = 'dir' if item.is_dir() else 'file'
                    size = item.stat().st_size if item.is_file() else 0
                    results.append(f"{item_type:4} {size:>10} {rel_path}")
            else:
                for item in dir_path.iterdir():
                    item_type = 'dir' if item.is_dir() else 'file'
                    size = item.stat().st_size if item.is_file() else 0
                    results.append(f"{item_type:4} {size:>10} {item.name}")
            
            results.sort()
            output = "\n".join(results)
            logger.info(f"Listed directory: {path} ({len(results)} items)")
            return output if output else "Empty directory"
            
        except Exception as e:
            logger.error(f"Error listing directory {path}: {e}")
            return f"Error: {str(e)}"
    
    async def create_directory(self, path: str) -> str:
        """Create a new directory"""
        try:
            dir_path = self._resolve_path(path)
            self._validate_path(dir_path)
            
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {path}")
            return f"Successfully created directory: {path}"
            
        except Exception as e:
            logger.error(f"Error creating directory {path}: {e}")
            return f"Error: {str(e)}"
    
    async def remove_directory(self, path: str) -> str:
        """Remove a directory and its contents"""
        try:
            dir_path = self._resolve_path(path)
            self._validate_path(dir_path)
            
            if not dir_path.exists():
                return f"Error: Directory not found: {path}"
            
            if not dir_path.is_dir():
                return f"Error: Not a directory: {path}"
            
            shutil.rmtree(dir_path)
            logger.info(f"Removed directory: {path}")
            return f"Successfully removed directory: {path}"
            
        except Exception as e:
            logger.error(f"Error removing directory {path}: {e}")
            return f"Error: {str(e)}"
    
    async def move_file(self, src: str, dst: str) -> str:
        """Move or rename a file"""
        try:
            src_path = self._resolve_path(src)
            dst_path = self._resolve_path(dst)
            self._validate_path(src_path)
            self._validate_path(dst_path)
            
            if not src_path.exists():
                return f"Error: Source not found: {src}"
            
            shutil.move(str(src_path), str(dst_path))
            logger.info(f"Moved {src} to {dst}")
            return f"Successfully moved {src} to {dst}"
            
        except Exception as e:
            logger.error(f"Error moving {src} to {dst}: {e}")
            return f"Error: {str(e)}"
    
    async def copy_file(self, src: str, dst: str) -> str:
        """Copy a file"""
        try:
            src_path = self._resolve_path(src)
            dst_path = self._resolve_path(dst)
            self._validate_path(src_path)
            self._validate_path(dst_path)
            
            if not src_path.exists():
                return f"Error: Source not found: {src}"
            
            if src_path.is_dir():
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)
            
            logger.info(f"Copied {src} to {dst}")
            return f"Successfully copied {src} to {dst}"
            
        except Exception as e:
            logger.error(f"Error copying {src} to {dst}: {e}")
            return f"Error: {str(e)}"
