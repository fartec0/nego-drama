# Contributing to Quantum UI

Thank you for your interest in contributing to Quantum UI! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to uphold our Code of Conduct (be respectful, inclusive, and collaborative).

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with the following information:
- A clear, descriptive title
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Screenshots if applicable
- Environment information (OS, Python version, etc.)

### Suggesting Features

We welcome feature suggestions! Please create an issue with:
- A clear, descriptive title
- A detailed description of the proposed feature
- Any relevant examples or mock-ups
- Explanation of why this feature would be valuable

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Run tests to ensure they pass
5. Commit your changes (`git commit -m 'Add some feature'`)
6. Push to the branch (`git push origin feature/your-feature-name`)
7. Create a Pull Request

## Development Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run tests:
   ```bash
   pytest
   ```

## Code Style

We follow these coding conventions:
- Use [Black](https://github.com/psf/black) for code formatting
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Write docstrings following [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Use type hints where appropriate

## Testing

- Write unit tests for all new functionality
- Ensure all tests pass before submitting a PR
- Aim for high test coverage

## Documentation

- Update documentation to reflect any changes
- Document all public functions, classes, and methods
- Include examples where appropriate

## License

By contributing to Quantum UI, you agree that your contributions will be licensed under the project's MIT license.