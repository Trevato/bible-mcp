# Contributing to Bible MCP

Thank you for considering contributing to the Bible MCP project! This document outlines the process and guidelines for contributing.

## Project Structure

The project is organized as follows:

- `bible_api.py`: Client for interacting with the bible-api.com service
- `bible_data.py`: Comprehensive Bible structure data and utilities
- `bible_server.py`: MCP server implementation with resources and tools
- `pyproject.toml`: Project configuration and dependencies
- `README.md`: Documentation and usage instructions
- `LICENSE`: MIT license information

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/trevato/bible-mcp.git
   cd bible-mcp
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install "mcp[cli]" httpx
   pip install -e ".[dev]"  # Install dev dependencies
   ```

## Running Tests

Run the tests with:

```bash
pytest
```

## Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, adhering to the project's coding style
3. Write tests for your changes
4. Run the tests to ensure they pass
5. Update documentation if necessary

## Submitting Changes

1. Push your changes to your fork
2. Submit a pull request to the main repository
3. Describe your changes and the problem they solve
4. Reference any related issues in your pull request

## Coding Guidelines

- Follow PEP 8 guidelines for Python code style
- Add docstrings to new functions and classes
- Include type annotations
- Write tests for new functionality
- Keep functions and methods focused and single-purpose

## Adding New Features

When adding new features to the Bible MCP server, consider:

1. **Resources**:
   - Are you adding a new URI pattern for accessing Bible content?
   - Is it consistent with the existing resource pattern?

2. **Tools**:
   - Does the tool serve a clear purpose in an LLM context?
   - Are parameters and return values well-defined and documented?

3. **Error Handling**:
   - Is your code handling errors gracefully?
   - Are error messages clear and helpful?

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License.
