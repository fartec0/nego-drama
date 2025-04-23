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

## Quantum-Specific Guidelines

### Quantum Circuit Construction

- All quantum circuits should be built using the micro-module architecture
- Ensure all gates are properly documented with their mathematical representations
- Include references to published papers for non-trivial quantum algorithms
- Clearly document the expected input and output quantum states
- For parameterized circuits, document the valid parameter ranges

### Genesis States

- When adding new genesis states to the catalog, include:
  - Mathematical definition
  - Expected entanglement properties
  - Use cases and applications
  - Verification methods
- All genesis states must implement the verification protocol

### Entanglement Handling

- Any operation that could affect entanglement must use the entanglement tracking system
- Document the entanglement preservation strategy for all quantum operations
- Include explicit tests for entanglement preservation

### Quantum Backends

- Backend implementations must conform to the `backend_interface.py` specification
- Include both simulator and real hardware test cases where applicable
- Document any hardware-specific limitations or considerations
- Include error mitigation strategies where appropriate

### Performance Considerations

- Document the computational complexity of quantum algorithms (in terms of gates and qubits)
- Include benchmarks for non-trivial quantum operations
- Consider the trade-offs between simulation accuracy and performance

## Testing Quantum Components

- All quantum components must include:
  - Unit tests for basic functionality
  - Integration tests with other quantum components
  - Test cases that verify expected quantum behavior
  - Edge cases (e.g., maximum entanglement, zero entanglement)
- Use the provided test fixtures in `tests/unit/quantum/`
- Verify results against known analytical solutions where possible

## Documentation

- Update documentation to reflect any changes
- Document all public functions, classes, and methods
- Include examples where appropriate
- For quantum algorithms, include:
  - Circuit diagrams
  - Mathematical explanation
  - Expected output for sample inputs
  - References to relevant literature

## Gradio UI Components

- Follow the established component structure for all UI elements
- Ensure all quantum visualizations correctly represent the quantum state
- Test UI components with both small and large quantum systems
- Document any performance limitations for visualization components

## License

By contributing to Quantum UI, you agree that your contributions will be licensed under the project's MIT license.