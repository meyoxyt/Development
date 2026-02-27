# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-27

### Added
- Initial release of Minimax 2.1 AI Assistant
- Minimax API integration with cloud model support
- Ollama local model support
- Comprehensive tool suite (30+ tools):
  - File operations (read, write, delete, copy, move)
  - Directory management (create, remove, list)
  - Search tools (grep, fuzzy search, content search)
  - System tools (command execution, process management, system info)
  - Web tools (HTTP requests, downloads, scraping)
  - Code tools (formatting, linting, parsing)
  - Git tools (status, diff, log, commit)
  - Database tools (SQLite queries, table management)
- Interactive CLI mode
- Single query mode
- Configuration management with .env support
- Comprehensive logging system
- Safety features:
  - Command restriction
  - Path validation
  - File size limits
  - Timeout protection
- Unit tests with pytest
- Usage examples (basic and advanced)
- Documentation (README, CONTRIBUTING)
- MIT License

### Security
- Implemented restricted command/path blocking
- Added input validation and sanitization
- Workspace sandboxing for file operations
- Sensitive environment variable redaction

## [Unreleased]

### Planned
- Docker support tools
- Kubernetes integration
- AWS CLI tools
- Web UI interface
- Voice input/output
- Multi-model switching
- Plugin system
- Conversation history persistence
- Performance optimizations
- Enhanced error recovery
