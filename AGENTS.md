# Guidelines for contributing via Codex

## Style
- Code must target Python 3.10 or later.
- Follow PEP8 formatting (4‑space indents, docstrings for all functions).
- Type hints should be used for new or modified functions.
- Place scripts and modules logically in the current structure (`DB/`, `new_api/`, etc.).

## Testing
1. Install dependencies (only needed once per environment):

   ```bash
   python -m pip install -r requirements.txt
