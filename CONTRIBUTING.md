
# Contributing to SEO Audit Toolkit

First off, thank you for considering contributing to SEO Audit Toolkit! It's people like you that make this toolkit such a great resource for the SEO community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
- [Style Guidelines](#style-guidelines)
  - [Python Style Guide](#python-style-guide)
  - [JavaScript Style Guide](#javascript-style-guide)
  - [Git Commit Messages](#git-commit-messages)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to youssef@mindflowmarketing.com.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

**Bug Report Template:**

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Import module '...'
2. Call function '....'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots/Output**
If applicable, add screenshots or error output.

**Environment:**
 - OS: [e.g. Ubuntu 20.04]
 - Python version: [e.g. 3.8.5]
 - Node.js version: [e.g. 14.17.0]
 - Toolkit version: [e.g. 1.0.0]

**Additional context**
Add any other context about the problem here.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description** of the suggested enhancement
- **Provide specific examples** to demonstrate the steps
- **Describe the current behavior** and explain which behavior you expected to see instead
- **Include screenshots and animated GIFs** if helpful
- **Explain why this enhancement would be useful** to most users

### Pull Requests

Please follow these steps for sending us a pull request:

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code follows our style guidelines
6. Issue that pull request!

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- Git

### Setting Up Your Development Environment

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/seo-audit-toolkit.git
   cd seo-audit-toolkit
   ```

2. **Set up Python environment:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Set up Node.js environment:**
   ```bash
   # Install dependencies
   npm install
   ```

4. **Run tests to ensure everything is working:**
   ```bash
   # Python tests
   pytest
   
   # JavaScript tests
   npm test
   ```

## Style Guidelines

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code. Key points:

- Use 4 spaces for indentation (no tabs)
- Maximum line length is 100 characters
- Use descriptive variable names
- Add docstrings to all functions and classes
- Use type hints where appropriate

**Example:**
```python
def analyze_website(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Analyze a website for SEO issues.
    
    Args:
        url: The URL to analyze
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing analysis results
    """
    # Implementation here
    pass
```

### JavaScript Style Guide

We follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript). Key points:

- Use 2 spaces for indentation
- Use semicolons
- Use single quotes for strings
- Use `const` for all references; avoid using `var`
- Add JSDoc comments to all functions

**Example:**
```javascript
/**
 * Analyze a website for SEO issues
 * @param {string} url - The URL to analyze
 * @param {number} timeout - Request timeout in milliseconds
 * @returns {Promise<Object>} Analysis results
 */
async function analyzeWebsite(url, timeout = 10000) {
  // Implementation here
}
```

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

**Good commit messages:**
```
Add Core Web Vitals analysis for mobile devices

- Implement LCP, FID, and CLS metrics extraction
- Add PageSpeed Insights API integration
- Include recommendations based on metric values

Fixes #123
```

## Testing

### Python Tests

We use pytest for Python testing. Tests should be placed in the `tests/` directory.

**Running tests:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=python --cov-report=html

# Run specific test file
pytest tests/test_technical_audit.py
```

**Writing tests:**
```python
import pytest
from seo_audit_toolkit import TechnicalAuditor

def test_audit_website():
    auditor = TechnicalAuditor()
    results = auditor.audit_website("https://example.com")
    
    assert results['status'] == 'completed'
    assert 'score' in results
    assert 0 <= results['score'] <= 100
```

### JavaScript Tests

We use Jest for JavaScript testing.

**Running tests:**
```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

**Writing tests:**
```javascript
const { TechnicalAuditor } = require('../javascript/index');

describe('TechnicalAuditor', () => {
  test('should analyze website successfully', async () => {
    const auditor = new TechnicalAuditor();
    const results = await auditor.analyze('https://example.com');
    
    expect(results.status).toBe('completed');
    expect(results.score).toBeGreaterThanOrEqual(0);
    expect(results.score).toBeLessThanOrEqual(100);
  });
});
```

## Documentation

- Update the README.md if you change functionality
- Update the API documentation in `/docs/api-reference.md` for any API changes
- Add code examples for new features
- Keep documentation concise and clear
- Use proper markdown formatting

### Documentation Structure

```
docs/
├── installation.md      # Installation instructions
├── usage-guide.md       # How to use the toolkit
└── api-reference.md     # API documentation
```

## Adding New Features

When adding a new feature:

1. **Discuss first**: Open an issue to discuss the feature before implementing
2. **Design**: Consider how it fits with existing architecture
3. **Implement**: Follow the coding standards
4. **Test**: Add comprehensive tests
5. **Document**: Update all relevant documentation
6. **Example**: Add an example showing how to use the feature

## Module Structure

When creating new modules, follow this structure:

### Python Module Template
```python
"""
Module Name
Brief description of what this module does

Author: Your Name
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class YourClass:
    """Class description."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the class."""
        self.config = config or {}
    
    def your_method(self, param: str) -> Dict:
        """
        Method description.
        
        Args:
            param: Parameter description
            
        Returns:
            Description of return value
        """
        # Implementation
        pass
```

### JavaScript Module Template
```javascript
/**
 * Module Name
 * Brief description of what this module does
 * 
 * Author: Your Name
 */

class YourClass {
  /**
   * Initialize the class
   * @param {Object} config - Configuration options
   */
  constructor(config = {}) {
    this.config = config;
  }

  /**
   * Method description
   * @param {string} param - Parameter description
   * @returns {Promise<Object>} Description of return value
   */
  async yourMethod(param) {
    // Implementation
  }
}

module.exports = YourClass;
```

## Release Process

1. Update version numbers in:
   - `python/__init__.py`
   - `package.json`
   - `README.md`

2. Update CHANGELOG.md with release notes

3. Create a pull request with version updates

4. After merge, create a GitHub release with tag

## Questions?

Feel free to open an issue with your question or contact:
- Email: youssef@mindflowmarketing.com
- Website: https://youssefhodaigui.com
- Company: https://mindflowmarketing.com

Thank you for contributing to SEO Audit Toolkit! 🚀
