# Contributing to AI Agent Platform

Thank you for your interest in contributing to the AI Agent Platform! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- Node.js 18 or higher
- Git
- A code editor (VS Code, PyCharm, etc.)

### Development Setup

1. **Fork and clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/code-agent.git
cd code-agent
```

2. **Create a development branch**
```bash
git checkout -b feature/your-feature-name
```

3. **Set up environment**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. **Start development environment**
```bash
./dev.sh
```

This will:
- Create a Python virtual environment
- Install dependencies
- Provide instructions for running services

## Development Workflow

### Running Services Locally

**Terminal 1 - API Server:**
```bash
source venv/bin/activate
uvicorn services.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Worker:**
```bash
source venv/bin/activate
python services/worker/main.py
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 4 - Database & Redis:**
```bash
docker run -d -p 5432:5432 -e POSTGRES_DB=agent_platform -e POSTGRES_USER=agent_user -e POSTGRES_PASSWORD=agent_password postgres:15-alpine
docker run -d -p 6379:6379 redis:7-alpine
```

### Project Structure

```
code-agent/
├── agents/              # Agent implementations
├── pipelines/           # Orchestration logic
├── services/
│   ├── api/            # FastAPI backend
│   └── worker/         # Job processor
├── frontend/           # React UI
├── config/             # Configuration
└── tests/              # Test suite
```

## Contribution Areas

### 1. Agent Development

Create new specialized agents by extending `BaseAgent`:

```python
from agents.base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    @property
    def agent_name(self) -> str:
        return "MyCustomAgent"

    def get_system_prompt(self) -> str:
        return "You are an expert in..."

    def get_tool_definitions(self) -> List[Dict]:
        # Define agent-specific tools
        pass
```

### 2. API Endpoints

Add new endpoints in `services/api/main.py`:

```python
@app.get("/my-endpoint")
def my_endpoint(db: Session = Depends(get_db)):
    # Implementation
    pass
```

### 3. Frontend Features

Add new pages or components in `frontend/src/`:

```jsx
// frontend/src/pages/MyPage.jsx
import React from 'react';

function MyPage() {
    return <div>My New Page</div>;
}

export default MyPage;
```

### 4. Database Models

Add new models in `services/api/models.py`:

```python
class MyModel(Base):
    __tablename__ = "my_table"
    id = Column(Integer, primary_key=True)
    # Add fields
```

## Coding Standards

### Python

- Follow PEP 8 style guide
- Use type hints where possible
- Write docstrings for classes and functions
- Keep functions focused and small

**Example:**
```python
def process_job(self, job_id: int) -> Dict[str, Any]:
    """
    Process a single job from the queue.

    Args:
        job_id: ID of the job to process

    Returns:
        Dictionary containing job results

    Raises:
        ValueError: If job_id is invalid
    """
    # Implementation
    pass
```

### JavaScript/React

- Use functional components with hooks
- Follow React best practices
- Use meaningful variable names
- Keep components small and reusable

**Example:**
```jsx
function JobCard({ job }) {
    const [status, setStatus] = useState(job.status);

    return (
        <div className="job-card">
            <h3>{job.type}</h3>
            <p>Status: {status}</p>
        </div>
    );
}
```

## Testing

### Python Tests

Write tests using pytest:

```python
# tests/test_worker.py
def test_worker_processes_job():
    worker = Worker()
    result = worker.process_job(job_id=1)
    assert result['status'] == 'completed'
```

Run tests:
```bash
pytest tests/
```

### Frontend Tests

(To be added - React Testing Library)

## Submitting Changes

### Commit Messages

Follow conventional commit format:

```
type(scope): subject

body

footer
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(agents): add code review agent

Implemented a new agent that can perform automated code reviews
with configurable rule sets.

Closes #123
```

```
fix(worker): handle redis connection errors

Added retry logic and better error handling for Redis connection
failures to prevent worker crashes.
```

### Pull Request Process

1. **Update documentation**
   - Update README.md if needed
   - Add docstrings to new code
   - Update API documentation

2. **Write tests**
   - Add tests for new features
   - Ensure existing tests pass

3. **Create pull request**
   - Provide clear description
   - Reference related issues
   - Add screenshots for UI changes

4. **Code review**
   - Address reviewer feedback
   - Keep PR focused and small
   - Rebase if needed

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Commit messages follow convention

## Screenshots (if applicable)
Add screenshots here

## Related Issues
Fixes #issue_number
```

## Areas for Contribution

### High Priority

- [ ] WebSocket support for real-time updates
- [ ] User authentication system
- [ ] Improved error handling and recovery
- [ ] Comprehensive test suite
- [ ] Performance optimization

### Medium Priority

- [ ] Agent capability plugins
- [ ] Workflow templates
- [ ] Metrics dashboard
- [ ] CI/CD pipeline improvements
- [ ] Documentation improvements

### Low Priority

- [ ] Multi-language support
- [ ] Dark mode for frontend
- [ ] Advanced filtering and search
- [ ] Export functionality
- [ ] Email notifications

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

Thank you for contributing!
