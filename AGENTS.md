# Contributor Guide

The repository contains multiple packages, most of which are depracted. The focus of our work
is exclusively on the `datacommons_client` package, which is a Python client for the
Data Commons API. The other packages are not actively maintained and should not be used for new development.

## Dev Environment Tips
- We use `uv` to manage the Python environment, dependencies, and development tools.
- To set up the Python environment for development, run:
  ```bash
  uv sync
  ```
- To run tests, use:
  ```bash
  uv run pytest
  ```

# Linting and Formatting
- We use `isort` and `yapf` for code formatting.
- To check formatting, run:
  ```bash
  uv run ./run_test.sh -l
  ```
- To automatically fix formatting, run:
  ```bash
    uv run ./run_test.sh -f
    ```
  
- This repository adheres strictly to the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).
- Always add comprehensive docstrings to your functions and classes (Google style).
- Use type hints for all function signatures to ensure clarity and maintainability.

## Testing Instructions
- Test should follow best practice and focus on testing any logic introduced in code. We're not
    testing the Data Commons API itself. We are not testing the functionality of libraries we depend on, 
    we are not testing the python standard library.
- Fix any test or type errors until the whole suite is green.
- Add or update tests for the code you change, even if nobody asked.
