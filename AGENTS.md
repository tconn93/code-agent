# Agent Development Guidelines

## Build/Lint/Test Commands

**Frontend:**
- Build: `cd frontend && npm run build`
- Lint: `cd frontend && npm run lint`
- Dev: `cd frontend && npm run dev`

**Python:**
- Test all: `pytest`
- Test single file: `pytest path/to/test_file.py`
- Test single test: `pytest path/to/test_file.py::test_function_name`
- Coverage: `pytest --cov=.`

**Development:**
- Full dev setup: `./dev.sh`

## Code Style Guidelines

**Python:**
- Follow PEP 8 with type hints and docstrings
- Naming: snake_case for variables/functions, PascalCase for classes
- Imports: stdlib → third-party → local (alphabetized within groups)
- Error handling: Use specific exceptions, log errors appropriately
- Functions: Keep focused and small (<50 lines)

**JavaScript/React:**
- Use functional components with hooks
- Naming: camelCase for variables/functions, PascalCase for components
- Imports: Group by type (React, third-party, local)
- JSX: One component per file, meaningful prop names
- State: Use useState/useEffect appropriately

**General:**
- No unused variables (ESLint enforces)
- Meaningful names over abbreviations
- Add docstrings/comments for complex logic
- Follow existing patterns in codebase