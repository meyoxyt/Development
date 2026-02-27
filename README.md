# Development - Minimax 2.1 AI Assistant

A full-featured AI assistant powered by [Minimax 2.1](https://platform.minimaxi.com/) through Ollama with comprehensive system and file management tools.

## Features

- **Minimax 2.1 Integration**: Cloud-based model via Ollama API
- **File Operations**: Create, read, edit, write, delete files and directories
- **Search Tools**: grep, regex search, fuzzy file search
- **System Management**: Execute shell commands, process management
- **Web Tools**: HTTP requests, web scraping, URL fetching
- **Code Analysis**: AST parsing, linting, formatting
- **Git Integration**: Repository operations, diff analysis
- **Database Tools**: SQLite operations, query execution

## Installation

```bash
git clone https://github.com/meyoxyt/Development.git
cd Development
pip install -r requirements.txt
```

## Configuration

1. Set up Minimax API credentials:
```bash
export MINIMAX_API_KEY="your_api_key_here"
export MINIMAX_GROUP_ID="your_group_id_here"
```

2. Configure Ollama endpoint (optional):
```bash
export OLLAMA_HOST="http://localhost:11434"
```

## Usage

```bash
python main.py
```

Or interactive mode:
```bash
python main.py --interactive
```

## Available Tools

### File Operations
- `read_file(path)` - Read file contents
- `write_file(path, content)` - Write content to file
- `append_file(path, content)` - Append to existing file
- `delete_file(path)` - Remove file
- `list_directory(path)` - List directory contents
- `create_directory(path)` - Create new directory
- `remove_directory(path)` - Remove directory (recursive)
- `move_file(src, dst)` - Move/rename file
- `copy_file(src, dst)` - Copy file

### Search Tools
- `grep_search(pattern, path)` - Search files using regex
- `fuzzy_search(query, path)` - Fuzzy file name search
- `find_files(pattern, path)` - Find files by pattern
- `search_content(text, path)` - Search file contents

### System Tools
- `execute_command(cmd)` - Run shell commands
- `get_system_info()` - System information
- `list_processes()` - List running processes
- `kill_process(pid)` - Terminate process

### Web Tools
- `http_request(url, method, data)` - Make HTTP requests
- `download_file(url, path)` - Download from URL
- `scrape_webpage(url)` - Extract webpage content

### Code Tools
- `parse_code(file, language)` - Parse code to AST
- `format_code(file, language)` - Auto-format code
- `lint_code(file, language)` - Lint and check code

### Git Tools
- `git_status()` - Repository status
- `git_diff(file)` - Show file differences
- `git_log(n)` - Show commit history
- `git_commit(message)` - Commit changes

### Database Tools
- `db_query(query)` - Execute SQL query
- `db_create_table(name, schema)` - Create table
- `db_insert(table, data)` - Insert records

## Architecture

```
Development/
├── main.py              # Entry point
├── config.py            # Configuration management
├── ai/
│   ├── minimax_client.py    # Minimax API wrapper
│   └── tool_executor.py     # Tool execution engine
├── tools/
│   ├── file_ops.py          # File operations
│   ├── search.py            # Search utilities
│   ├── system.py            # System management
│   ├── web.py               # Web tools
│   ├── code_tools.py        # Code analysis
│   ├── git_tools.py         # Git integration
│   └── database.py          # Database operations
├── utils/
│   ├── logger.py            # Logging utilities
│   └── validators.py        # Input validation
└── tests/
    └── test_tools.py        # Unit tests
```

## Example

```python
from ai.minimax_client import MinimaxClient
from ai.tool_executor import ToolExecutor

# Initialize
client = MinimaxClient()
executor = ToolExecutor()

# Ask AI to perform tasks
response = client.chat(
    "Create a directory called 'projects' and search all Python files in the current directory",
    tools=executor.get_available_tools()
)

# AI automatically calls tools
executor.execute(response.tool_calls)
```

## License

MIT License - See LICENSE file for details

## Contributing

Pull requests welcome! See CONTRIBUTING.md for guidelines.
