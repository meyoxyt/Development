# Development - Minimax 2.1 AI Assistant

A full-featured AI assistant powered by **Minimax 2.1 Cloud** via Ollama (FREE!) with comprehensive system and file management tools.

## Features

- **Minimax 2.1 Cloud via Ollama**: Free cloud-connected model through Ollama
- **30+ Tools**: File operations, search, system management, web tools, code analysis, Git, database
- **Autonomous Execution**: AI decides which tools to use and chains them together
- **Safety Built-in**: Command restrictions, path validation, sandboxing
- **Cross-platform**: Windows, Linux, macOS

## Prerequisites

1. **Python 3.9+**
2. **Ollama** installed and running
3. **Minimax 2.1 Cloud model** pulled in Ollama

## Quick Start

### 1. Install Ollama (if not installed)

**Windows:**
```powershell
winget install Ollama.Ollama
```

**Linux/Mac:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Pull Minimax 2.1 Cloud Model

```bash
ollama pull minimax-2.1:cloud
```

### 3. Setup This Project

**Windows:**
```powershell
git clone https://github.com/meyoxyt/Development.git
cd Development
.\setup.ps1
```

**Linux/Mac:**
```bash
git clone https://github.com/meyoxyt/Development.git
cd Development
chmod +x setup.sh
./setup.sh
```

### 4. Run It!

**Interactive mode:**
```bash
python main.py --interactive
```

**Single query:**
```bash
python main.py --query "Create a Python project with tests"
```

## Configuration

Edit `.env` file:

```bash
# Use Ollama with minimax-2.1:cloud (default)
USE_OLLAMA=true
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=minimax-2.1:cloud

# Or use Minimax Cloud API directly (requires paid API key)
USE_OLLAMA=false
MINIMAX_API_KEY=your_key
MINIMAX_GROUP_ID=your_group
```

## Available Tools (30+)

### File Operations
- `read_file(path)` - Read file contents
- `write_file(path, content)` - Write content to file
- `append_file(path, content)` - Append to file
- `delete_file(path)` - Remove file
- `list_directory(path)` - List directory contents
- `create_directory(path)` - Create directory
- `remove_directory(path)` - Remove directory recursively
- `move_file(src, dst)` - Move/rename file
- `copy_file(src, dst)` - Copy file

### Search Tools
- `grep_search(pattern, path)` - Regex search in files
- `fuzzy_search(query, path)` - Fuzzy file name search
- `find_files(pattern, path)` - Find files by pattern
- `search_content(text, path)` - Search file contents

### System Tools
- `execute_command(cmd)` - Run shell commands (with safety)
- `get_system_info()` - System information
- `list_processes()` - List running processes
- `kill_process(pid)` - Terminate process
- `get_environment_variables()` - List env vars

### Web Tools
- `http_request(url, method, data)` - Make HTTP requests
- `download_file(url, path)` - Download from URL
- `scrape_webpage(url)` - Extract webpage content

### Code Tools
- `format_code(path, language)` - Auto-format code (Black)
- `lint_code(path, language)` - Lint code (flake8)
- `parse_code(path, language)` - Parse code to AST

### Git Tools
- `git_status()` - Repository status
- `git_diff(file)` - Show differences
- `git_log(n)` - Commit history
- `git_commit(message)` - Commit changes
- `git_branch()` - List branches

### Database Tools
- `db_query(query)` - Execute SQL query
- `db_create_table(name, schema)` - Create table
- `db_insert(table, data)` - Insert records

## Usage Examples

### Basic File Operations
```bash
python main.py -q "Create a file hello.txt with 'Hello World'"
```

### Search Files
```bash
python main.py -q "Find all Python files in the current directory"
```

### Complex Tasks
```bash
python main.py -q "Create a web scraper project with main.py, requirements.txt, and README.md"
```

### Interactive Mode
```bash
python main.py --interactive

> You: Create a directory called 'projects' and list its contents
> AI: [uses tools autonomously]
```

## Docker Support

**With Ollama:**
```bash
docker-compose --profile ollama up
```

**Without Ollama (cloud API):**
```bash
docker-compose up
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_tools.py -v
```

## Architecture

```
Development/
├── main.py              # Entry point
├── config.py            # Configuration
├── ai/
│   ├── minimax_client.py    # Ollama/Minimax client
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
│   ├── logger.py            # Logging
│   └── validators.py        # Input validation
├── tests/
│   └── test_tools.py        # Unit tests
└── examples/
    ├── basic_usage.py       # Basic examples
    └── advanced_usage.py    # Advanced examples
```

## Safety Features

- **Command Restrictions**: Blocks dangerous commands (`rm -rf /`, `sudo`, etc.)
- **Path Validation**: Prevents access to system directories (`/etc`, `/sys`, etc.)
- **File Size Limits**: Default 100MB per file
- **Timeout Protection**: 30s command timeout, 300s total
- **Workspace Sandboxing**: All operations relative to workspace directory

## Troubleshooting

### "Ollama connection refused"
```bash
# Make sure Ollama is running
ollama serve

# Check if model is available
ollama list
```

### "Model not found"
```bash
# Pull the Minimax 2.1 Cloud model
ollama pull minimax-2.1:cloud
```

### "pip not recognized" (Windows)
```powershell
# Use python -m pip instead
python -m pip install -r requirements.txt
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - See [LICENSE](LICENSE) file.

## Support

- Issues: [GitHub Issues](https://github.com/meyoxyt/Development/issues)
- Docs: [GitHub Wiki](https://github.com/meyoxyt/Development/wiki)

## Acknowledgments

- Powered by [Minimax 2.1 Cloud](https://www.minimaxi.com/)
- Runs on [Ollama](https://ollama.ai/)
- Built by [ELITE Studios](https://plugincenter.store)
