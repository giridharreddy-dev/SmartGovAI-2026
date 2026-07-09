# Contributing

Thanks for your interest in contributing to SmartGovAI! We welcome improvements, bug reports, and documentation fixes.

Guidelines

- Fork the repository and create a feature branch named `feat/your-feature` or `fix/brief-description`.
- Run tests locally and ensure they pass before opening a PR:

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate  # macOS / Linux
pip install -r requirements.txt
pytest
```

- Keep changes small and focused; one logical change per PR.
- Write tests for new features or bug fixes and update CHANGELOG.md appropriately.
- Follow the existing code style (PEP8). Use `black` and `flake8` if available.
- Use descriptive commit messages. Example: `fix(pdf): validate header and remove temp file on invalid upload`.

Code review process

- Open a Pull Request against `main` and provide a summary of the change and testing steps.
- At least one approving review is required before merging.
- Squash or rebase commits as requested by maintainers.

Reporting security issues

If you discover a security vulnerability, please do not open a public issue. Instead send a private email to the maintainers at security@smartgov.health with details and reproduction steps.

Thanks — maintainers.
