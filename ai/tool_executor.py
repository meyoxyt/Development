"""Tool execution engine for AI assistant"""

import asyncio
import json
from typing import List, Dict, Any, Callable
from utils.logger import setup_logger

# Import all tool modules
from tools.file_ops import FileOperations
from tools.search import SearchTools
from tools.system import SystemTools
from tools.web import WebTools
from tools.code_tools import CodeTools
from tools.git_tools import GitTools
from tools.database import DatabaseTools

logger = setup_logger(__name__)

class ToolExecutor:
    """Executes tools requested by AI"""
    
    def __init__(self):
        # Initialize all tool handlers
        self.file_ops = FileOperations()
        self.search = SearchTools()
        self.system = SystemTools()
        self.web = WebTools()
        self.code = CodeTools()
        self.git = GitTools()
        self.database = DatabaseTools()
        
        # Map tool names to handlers
        self.tools: Dict[str, Callable] = {}
        self._register_tools()
    
    def _register_tools(self):
        """Register all available tools"""
        # File operations
        self.tools["read_file"] = self.file_ops.read_file
        self.tools["write_file"] = self.file_ops.write_file
        self.tools["append_file"] = self.file_ops.append_file
        self.tools["delete_file"] = self.file_ops.delete_file
        self.tools["list_directory"] = self.file_ops.list_directory
        self.tools["create_directory"] = self.file_ops.create_directory
        self.tools["remove_directory"] = self.file_ops.remove_directory
        self.tools["move_file"] = self.file_ops.move_file
        self.tools["copy_file"] = self.file_ops.copy_file
        
        # Search tools
        self.tools["grep_search"] = self.search.grep_search
        self.tools["fuzzy_search"] = self.search.fuzzy_search
        self.tools["find_files"] = self.search.find_files
        self.tools["search_content"] = self.search.search_content
        
        # System tools
        self.tools["execute_command"] = self.system.execute_command
        self.tools["get_system_info"] = self.system.get_system_info
        self.tools["list_processes"] = self.system.list_processes
        self.tools["kill_process"] = self.system.kill_process
        self.tools["get_environment_variables"] = self.system.get_environment_variables
        
        # Web tools
        self.tools["http_request"] = self.web.http_request
        self.tools["download_file"] = self.web.download_file
        self.tools["scrape_webpage"] = self.web.scrape_webpage
        
        # Code tools
        self.tools["parse_code"] = self.code.parse_code
        self.tools["format_code"] = self.code.format_code
        self.tools["lint_code"] = self.code.lint_code
        
        # Git tools
        self.tools["git_status"] = self.git.git_status
        self.tools["git_diff"] = self.git.git_diff
        self.tools["git_log"] = self.git.git_log
        self.tools["git_commit"] = self.git.git_commit
        self.tools["git_branch"] = self.git.git_branch
        
        # Database tools
        self.tools["db_query"] = self.database.db_query
        self.tools["db_create_table"] = self.database.db_create_table
        self.tools["db_insert"] = self.database.db_insert
        
        logger.info(f"Registered {len(self.tools)} tools")
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get OpenAI-style tool definitions for all tools"""
        return [
            # File Operations
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read the contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to the file"}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write content to a file (overwrites existing content)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to the file"},
                            "content": {"type": "string", "description": "Content to write"}
                        },
                        "required": ["path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "append_file",
                    "description": "Append content to an existing file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to the file"},
                            "content": {"type": "string", "description": "Content to append"}
                        },
                        "required": ["path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_file",
                    "description": "Delete a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to the file"}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_directory",
                    "description": "List contents of a directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to directory"},
                            "recursive": {"type": "boolean", "description": "List recursively", "default": False}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_directory",
                    "description": "Create a new directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path for new directory"}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "remove_directory",
                    "description": "Remove a directory and its contents",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to directory"}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "move_file",
                    "description": "Move or rename a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "src": {"type": "string", "description": "Source path"},
                            "dst": {"type": "string", "description": "Destination path"}
                        },
                        "required": ["src", "dst"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "copy_file",
                    "description": "Copy a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "src": {"type": "string", "description": "Source path"},
                            "dst": {"type": "string", "description": "Destination path"}
                        },
                        "required": ["src", "dst"]
                    }
                }
            },
            # Search Tools
            {
                "type": "function",
                "function": {
                    "name": "grep_search",
                    "description": "Search files using regex pattern",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pattern": {"type": "string", "description": "Regex pattern to search"},
                            "path": {"type": "string", "description": "Directory to search in"},
                            "file_pattern": {"type": "string", "description": "File pattern filter (e.g., '*.py')", "default": "*"}
                        },
                        "required": ["pattern", "path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "fuzzy_search",
                    "description": "Fuzzy search for files by name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "path": {"type": "string", "description": "Directory to search in"}
                        },
                        "required": ["query", "path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "find_files",
                    "description": "Find files matching a pattern",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pattern": {"type": "string", "description": "File pattern (e.g., '*.py')"},
                            "path": {"type": "string", "description": "Directory to search in"}
                        },
                        "required": ["pattern", "path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_content",
                    "description": "Search file contents for text",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Text to search for"},
                            "path": {"type": "string", "description": "Directory to search in"}
                        },
                        "required": ["text", "path"]
                    }
                }
            },
            # System Tools
            {
                "type": "function",
                "function": {
                    "name": "execute_command",
                    "description": "Execute a shell command (use with caution)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "Shell command to execute"}
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_system_info",
                    "description": "Get system information",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_processes",
                    "description": "List running processes",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "kill_process",
                    "description": "Terminate a process by PID",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pid": {"type": "integer", "description": "Process ID"}
                        },
                        "required": ["pid"]
                    }
                }
            },
            # Web Tools
            {
                "type": "function",
                "function": {
                    "name": "http_request",
                    "description": "Make HTTP request",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "URL to request"},
                            "method": {"type": "string", "description": "HTTP method", "enum": ["GET", "POST", "PUT", "DELETE"], "default": "GET"},
                            "data": {"type": "object", "description": "Request body data"}
                        },
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "download_file",
                    "description": "Download a file from URL",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "URL to download from"},
                            "path": {"type": "string", "description": "Local path to save file"}
                        },
                        "required": ["url", "path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "scrape_webpage",
                    "description": "Extract content from webpage",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "URL to scrape"}
                        },
                        "required": ["url"]
                    }
                }
            },
            # Code Tools  
            {
                "type": "function",
                "function": {
                    "name": "format_code",
                    "description": "Auto-format code file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to code file"},
                            "language": {"type": "string", "description": "Programming language", "default": "python"}
                        },
                        "required": ["path"]
                    }
                }
            },
            # Git Tools
            {
                "type": "function",
                "function": {
                    "name": "git_status",
                    "description": "Get git repository status",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "git_diff",
                    "description": "Show git diff for file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file": {"type": "string", "description": "File path"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "git_log",
                    "description": "Show git commit history",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "n": {"type": "integer", "description": "Number of commits", "default": 10}
                        }
                    }
                }
            },
            # Database Tools
            {
                "type": "function",
                "function": {
                    "name": "db_query",
                    "description": "Execute SQL query",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "SQL query to execute"}
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
    
    async def execute_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple tool calls"""
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("function", {}).get("name")
            tool_id = tool_call.get("id")
            arguments = json.loads(tool_call.get("function", {}).get("arguments", "{}"))
            
            logger.info(f"Executing tool: {tool_name} with args: {arguments}")
            
            if tool_name not in self.tools:
                result = {"error": f"Unknown tool: {tool_name}"}
            else:
                try:
                    tool_func = self.tools[tool_name]
                    output = await tool_func(**arguments)
                    result = {"success": True, "output": str(output)}
                except Exception as e:
                    logger.error(f"Tool execution error: {e}", exc_info=True)
                    result = {"error": str(e)}
            
            results.append({
                "tool_call_id": tool_id,
                "output": json.dumps(result)
            })
        
        return results
