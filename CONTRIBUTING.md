# Contributor Guidelines

The development team welcomes contributions to the SmartGovAI repository. We invite improvements, defect reports, and documentation enhancements that align with the project's accessibility and performance objectives.

## Project Mission

SmartGovAI is an open-source academic prototype designed to mitigate the digital divide by helping citizens with limited digital literacy discover and understand government health and welfare schemes. We prioritize offline resilience, Telugu-first localization, and client-side privacy.

## Development Setup

1. Fork the repository and clone it locally.
2. Ensure you have Python 3.10+ installed.
3. Establish a virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate    # Windows
   source .venv/bin/activate  # macOS / Linux
   ```
4. Install dependencies: `pip install -r requirements.txt`
5. Run tests to confirm your setup: `pytest`

## Repository Structure
- `data/` - JSON scheme definitions and facility data
- `docs/` - Technical documentation and academic materials
- `services/` - Core backend logic (audio, chat, Gemini, PDF, QR)
- `static/` & `templates/` - Frontend assets and Jinja2 templates
- `tests/` - Pytest suite

## Branching & Commit Conventions

- Initialize a feature branch utilizing standard nomenclature: `feat/your-feature-name` or `fix/defect-description`.
- Isolate modifications; ensure each Pull Request addresses a single logical change.
- Employ descriptive, conventional commit messages. Example: `fix(pdf): validate header and remove temp file on invalid upload`.

## Pull Request Requirements

- **Testing**: Author automated tests for all novel features or defect resolutions. `pytest` must pass.
- **Documentation**: Append relevant contextual updates to `docs/CHANGELOG.md` and update `README.md` if necessary.
- **Accessibility**: Ensure UI changes are navigable by screen readers and maintain high contrast.
- **Telugu Localization**: Any new text presented to the user MUST include bilingual support (Telugu and English). Do not rely on machine translation without verification.

## Government Data Provenance Rules

When adding or modifying government schemes in `data/`, you must adhere to strict data provenance rules. Where possible, include:

- `source_name`: The official government department or portal.
- `source_url`: The exact URL where the information was verified.
- `retrieved_at`: The date the data was retrieved (ISO format).
- `last_verified_at`: The date the data was last verified.
- `verification_status`: Status of the verification (e.g., "verified", "unverified").
- `state` / `district`: Geographic applicability.

*(Note: If the current data schema does not fully support these fields, they are highly recommended future improvements. Please document any provenance gaps.)*

## AI Safety & Privacy Rules

- **Zero-Trust**: Do not introduce code that sends PII to the server.
- **Hallucination Mitigation**: Any prompts added to Gemini services must be strictly grounded.
- **Offline Fallbacks**: Do not break the offline capabilities. Ensure fallbacks are implemented if AI services fail.

## Security Vulnerability Reporting

If you identify a security vulnerability, please do not submit a public issue report. Instead, open a private security report under the repository's Security tab on GitHub or contact the project maintainers directly.

## Code Style

Adhere to the established code style (PEP8). Utilize formatting utilities such as `black` and `flake8` when available.

We appreciate your cooperation and technical contributions.
