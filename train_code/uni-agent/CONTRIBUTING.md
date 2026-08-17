# Contributing to Uni-Agent

Thank you for your interest in contributing to **Uni-Agent**! We welcome contributions from everyone—whether it's fixing bugs, adding new features, improving documentation, or optimizing the asynchronous agent training loops.

## Getting Started

1. **Fork & Clone**: Fork the repository and clone it to your local machine.
2. **Install Dependencies**:
   It's recommended to install the project in an editable mode:
   ```bash
   pip install -e .
   ```
3. **Pre-commit Hooks**:
   We use `pre-commit` to enforce code formatting (via `ruff`) and type checking (via `mypy`). Please install it before submitting code:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Development Workflow

- Always create a new branch for your feature or bug fix.
- Ensure that your code complies with the project's formatting rules. You can manually run the linters using:
  ```bash
  pre-commit run --all-files
  ```
- If you are modifying the core async scheduling or rollout mechanisms, please provide clear reasoning and benchmark results if applicable.

## Submitting a Pull Request

- Keep PRs focused on a single issue or feature.
- Write a clear and descriptive PR title and description.
- If your PR addresses an open issue, link the issue in the description.
- Reviewers will check your code for readability, performance, and correctness.

We appreciate your contributions to Uni-Agent. Your efforts help make the project stronger and more user-friendly. Happy coding!
