# Contributing to Minimax AI Assistant

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/Development.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit: `git commit -am 'Add new feature'`
7. Push: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio black flake8 mypy

# Set up environment
cp .env.example .env
# Edit .env with your API keys
```

## Code Style

- Follow PEP 8 guidelines
- Use Black for formatting: `black .`
- Use flake8 for linting: `flake8 .`
- Use type hints where possible
- Add docstrings to all functions and classes

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_tools.py

# Run with coverage
pytest --cov=. --cov-report=html
```

## Adding New Tools

1. Create tool implementation in `tools/` directory
2. Add tool class with async methods
3. Register tool in `ai/tool_executor.py`:
   - Add to `_register_tools()` method
   - Add OpenAI-style definition to `get_tool_definitions()`
4. Add tests in `tests/test_tools.py`
5. Update README.md with new tool documentation

### Tool Template

```python
# tools/my_new_tool.py
from utils.logger import setup_logger

logger = setup_logger(__name__)

class MyNewTool:
    """Description of what this tool does"""
    
    async def my_function(self, param: str) -> str:
        """Function description
        
        Args:
            param: Parameter description
            
        Returns:
            Result description
        """
        try:
            # Implementation
            result = f"Processed: {param}"
            logger.info(f"My function executed: {param}")
            return result
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {str(e)}"
```

## Commit Message Guidelines

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- First line should be 50 characters or less
- Reference issues and pull requests when applicable

Examples:
```
Add web scraping tool
Fix file path validation bug
Update documentation for search tools
Refactor database connection handling
```

## Pull Request Process

1. Update README.md with details of changes if applicable
2. Update documentation in docstrings
3. Add tests for new features
4. Ensure all tests pass
5. Update CHANGELOG.md
6. Request review from maintainers

## Areas for Contribution

### High Priority
- Additional tool implementations (Docker, Kubernetes, AWS CLI)
- Improved error handling and validation
- Performance optimizations
- Better test coverage
- Documentation improvements

### Medium Priority
- Web UI interface
- Voice input/output support
- Multi-model support (GPT-4, Claude, Gemini)
- Plugin system for custom tools
- Conversation persistence

### Nice to Have
- IDE integrations (VSCode, PyCharm)
- Mobile app
- Multi-language support
- Advanced visualization tools
- Workflow automation templates

## Code Review Guidelines

Reviewers should check for:
- Code quality and readability
- Test coverage
- Documentation completeness
- Security considerations
- Performance implications
- Compatibility with existing code

## Security

If you discover a security vulnerability:
1. **DO NOT** open a public issue
2. Email security concerns to: [your-email@example.com]
3. Include detailed description and steps to reproduce

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Documentation clarifications
- General questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes for significant contributions
- GitHub contributor graph

Thank you for contributing! 🎉
