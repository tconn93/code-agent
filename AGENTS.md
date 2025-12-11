# AGENTS.md

## Build/Lint/Test Commands

### Frontend (`cd frontend`)
- Lint: `npm run lint` (eslint . --ext .js,.jsx)
- Build: `npm run build`
- Dev: `npm run dev`
- Preview: `npm run preview`
- Tests: None configured (add vitest/jest)

### Backend (root)
- Deps: `pip install -r requirements.txt`
- Lint: None (add ruff/black/mypy)
- Test all: `pytest`
- Single test: `pytest path/to/test_file.py::test_name` or `pytest -k test_name`
- API dev: `uvicorn services.api.main:app --reload`
- No tests yet.

## Code Style Guidelines

### Python (FastAPI/SQLAlchemy/Pydantic)
- Snake_case vars/functions/classes (e.g. get_user, UserModel)
- Type hints everywhere
- Imports: absolute (from services.api.models import User)
- Group imports: stdlib, 3rd-party, local
- Error handling: raise HTTPException(status_code=404, detail=&quot;Not found&quot;)
- Docstrings: Google/numpy style

### Frontend (React 19/JSX/ Tailwind)
- PascalCase components (e.g. Agents.jsx)
- camelCase vars/functions/hooks
- ESLint: react-hooks recommended, no-unused-vars (ignore ^[A-Z_])
- Imports: explicit (import { useState } from 'react')
- Tailwind: utility classes, no custom CSS
- Axios for API calls (frontend/src/api.js)

### General
- No emojis/comments unless requested
- Mimic existing patterns (e.g. agents/base_agent.py)
- Security: No secrets in code/DB
- Commit: Descriptive msgs, no git push