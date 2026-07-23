# Contributor Guidelines

The development team welcomes contributions to the SmartGovAI repository. We invite improvements, defect reports, and documentation enhancements that align with the project's accessibility and performance objectives.

## Submission Guidelines

- Fork the repository and initialize a feature branch utilizing standard nomenclature, such as `feat/your-feature-name` or `fix/defect-description`.
- Execute the local test suite and ensure all validations pass prior to initiating a Pull Request:

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows execution
source .venv/bin/activate  # macOS / Linux execution
pip install -r requirements.txt
pytest
```

- Isolate modifications; ensure that each Pull Request addresses a single logical change or feature addition.
- Author automated tests for all novel features or defect resolutions, and append the relevant contextual updates to the `CHANGELOG.md` file.
- Adhere to the established code style (PEP8). Utilize formatting utilities such as `black` and `flake8` when available.
- Employ descriptive, conventional commit messages. Example: `fix(pdf): validate header and remove temp file on invalid upload`.

## Code Review Process

- Initialize a Pull Request targeting the `main` branch, accompanied by a comprehensive summary of the modification and the associated validation steps.
- At least one approving review from a core maintainer is required prior to branch integration.
- Contributors may be requested to squash or rebase commits to preserve linear version history prior to merging.

## Security Vulnerability Reporting

If you identify a security vulnerability, do not submit a public issue report. Instead, securely transmit the vulnerability details and reproduction methodology to the maintainers via private email at security@smartgov.health.

We appreciate your cooperation and technical contributions.
