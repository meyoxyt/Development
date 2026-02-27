"""Unit tests for tool modules"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import shutil

from tools.file_ops import FileOperations
from tools.search import SearchTools
from tools.system import SystemTools
from config import Config

@pytest.fixture
def temp_workspace():
    """Create temporary workspace"""
    temp_dir = Path(tempfile.mkdtemp())
    original_workspace = Config.WORKSPACE_DIR
    Config.WORKSPACE_DIR = temp_dir
    
    yield temp_dir
    
    Config.WORKSPACE_DIR = original_workspace
    shutil.rmtree(temp_dir)

@pytest.mark.asyncio
class TestFileOperations:
    
    async def test_write_and_read_file(self, temp_workspace):
        file_ops = FileOperations()
        
        # Write file
        result = await file_ops.write_file("test.txt", "Hello World")
        assert "Successfully" in result
        
        # Read file
        content = await file_ops.read_file("test.txt")
        assert content == "Hello World"
    
    async def test_create_directory(self, temp_workspace):
        file_ops = FileOperations()
        
        result = await file_ops.create_directory("testdir")
        assert "Successfully" in result
        assert (temp_workspace / "testdir").exists()
    
    async def test_list_directory(self, temp_workspace):
        file_ops = FileOperations()
        
        # Create test files
        await file_ops.write_file("file1.txt", "test1")
        await file_ops.write_file("file2.txt", "test2")
        
        # List directory
        result = await file_ops.list_directory(".")
        assert "file1.txt" in result
        assert "file2.txt" in result
    
    async def test_delete_file(self, temp_workspace):
        file_ops = FileOperations()
        
        # Create and delete file
        await file_ops.write_file("temp.txt", "temporary")
        result = await file_ops.delete_file("temp.txt")
        
        assert "Successfully" in result
        assert not (temp_workspace / "temp.txt").exists()
    
    async def test_copy_file(self, temp_workspace):
        file_ops = FileOperations()
        
        # Create source file
        await file_ops.write_file("source.txt", "content")
        
        # Copy file
        result = await file_ops.copy_file("source.txt", "destination.txt")
        assert "Successfully" in result
        
        # Verify both exist
        assert (temp_workspace / "source.txt").exists()
        assert (temp_workspace / "destination.txt").exists()

@pytest.mark.asyncio
class TestSearchTools:
    
    async def test_find_files(self, temp_workspace):
        file_ops = FileOperations()
        search = SearchTools()
        
        # Create test files
        await file_ops.write_file("test.py", "print('hello')")
        await file_ops.write_file("test.txt", "hello")
        await file_ops.write_file("main.py", "print('main')")
        
        # Find Python files
        result = await search.find_files("*.py", ".")
        assert "test.py" in result
        assert "main.py" in result
        assert "test.txt" not in result
    
    async def test_grep_search(self, temp_workspace):
        file_ops = FileOperations()
        search = SearchTools()
        
        # Create test files with content
        await file_ops.write_file("file1.txt", "This contains hello\nAnother line")
        await file_ops.write_file("file2.txt", "No match here")
        
        # Search for pattern
        result = await search.grep_search("hello", ".")
        assert "file1.txt" in result
        assert "file2.txt" not in result
    
    async def test_fuzzy_search(self, temp_workspace):
        file_ops = FileOperations()
        search = SearchTools()
        
        # Create files
        await file_ops.write_file("my_test_file.txt", "content")
        await file_ops.write_file("other.txt", "content")
        
        # Fuzzy search
        result = await search.fuzzy_search("test", ".")
        assert "my_test_file.txt" in result

@pytest.mark.asyncio
class TestSystemTools:
    
    async def test_get_system_info(self):
        system = SystemTools()
        
        result = await system.get_system_info()
        assert "System:" in result
        assert "CPU" in result
        assert "Memory" in result
    
    async def test_execute_command(self):
        system = SystemTools()
        
        # Test safe command
        result = await system.execute_command("echo test")
        assert "test" in result
    
    async def test_restricted_command(self):
        system = SystemTools()
        
        # Test restricted command
        result = await system.execute_command("sudo rm -rf /")
        assert "Error" in result
        assert "restricted" in result.lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
