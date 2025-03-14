# Contributing to FastAPI MCP Server

We welcome contributions to the FastAPI MCP Server project! Whether you're a seasoned developer or just starting out, your help is valuable. Here's how you can contribute:

## Development Setup 🛠️

1. **Fork the repository:** Create a fork of the FastAPI MCP Server repository on GitHub.
2. **Clone your fork:** Clone your fork to your local machine.
3. **Install Poetry:**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
4. **Install dependencies:**
   ```bash
   poetry install
   ```
5. **Set up pre-commit hooks:**
   ```bash
   poetry run pre-commit install
   ```

## Reporting Bugs 🐞

If you encounter a bug, please create a new issue on the GitHub issue tracker. Please include the following information:

- **Detailed description of the bug:** Explain what happened, what you expected to happen, and any relevant error messages.
- **Steps to reproduce:** Provide clear, concise steps to reproduce the bug.
- **Environment details:** Specify your operating system, Python version, and any relevant dependencies.
- **Screenshots or logs:** Include any relevant screenshots or logs to help us diagnose the problem.

## Suggesting Features ✨

If you have an idea for a new feature, please create a new issue on the GitHub issue tracker. Please include the following information:

- **Detailed description of the feature:** Explain what the feature should do and why it's needed.
- **Use cases:** Provide examples of how the feature would be used.
- **Technical details:** If possible, provide some technical details about how the feature could be implemented.

## Submitting Pull Requests ⬆️

1. **Create a branch:** Create a new branch for your changes. Use a descriptive branch name that reflects the changes you're making.
2. **Make your changes:** Make your changes and commit them with clear, concise commit messages.
3. **Ensure code quality:**
   ```bash
   # Format code
   poetry run just fmt
   
   # Run linters
   poetry run just lint
   
   # Run tests
   poetry run just test
   ```
4. **Push your branch:** Push your branch to your forked repository.
5. **Create a pull request:** Create a pull request on GitHub to merge your changes into the main branch. Please include a detailed description of your changes and any relevant testing information.

## Code Style 🎨

We follow these code standards:
- **Black:** For code formatting
- **isort:** For import sorting
- **Flake8:** For code linting
- **MyPy:** For type checking
- **Ruff:** Additional linter for performance and best practices

You can run all checks with:
```bash
poetry run just lint
```

## Testing 🧪

All new features and bug fixes should be accompanied by comprehensive tests. We use pytest for testing. Please ensure that your changes pass all existing tests and add new tests as needed.

Run tests with:
```bash
poetry run pytest
```

Or with coverage:
```bash
poetry run just test-cov
```

## Thank You 🙏

Thank you for your interest in contributing to the FastAPI MCP Server project! Your contributions are greatly appreciated.
