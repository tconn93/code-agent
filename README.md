# AI Agent Platform

A scalable multi-agent platform for automating software development tasks. The system uses specialized AI agents (architect, coding, testing, deployment, monitoring) orchestrated through a central API with a web-based UI.

## Architecture

```
┌─────────────┐
│   Frontend  │ (React + Vite)
│  Dashboard  │
└──────┬──────┘
       │ HTTP
┌──────▼──────┐
│  API Server │ (FastAPI)
│ Orchestrator│
└──────┬──────┘
       │
   ┌───┴────┐
   │        │
   ▼        ▼
┌──────┐ ┌──────────┐
│Redis │ │PostgreSQL│
│Queue │ │ Database │
└───┬──┘ └──────────┘
    │
    ▼
┌──────────┐
│  Worker  │ (Agent Processor)
│  Pools   │
└──────────┘
    │
    ▼
┌──────────┐
│  Agents  │
│ ┌──────┐ │
│ │Coding│ │
│ │Test  │ │
│ │Deploy│ │
│ └──────┘ │
└──────────┘
```

## Core Components

### 1. API Server (`services/api/`)
- **Technology**: FastAPI with SQLAlchemy ORM
- **Responsibilities**:
  - Enterprise project management with governance and compliance
  - User and team management with role-based access control
  - Agent registry and lifecycle management with performance tracking
  - Job creation and dispatch with SLA management
  - Comprehensive audit logging and compliance reporting
  - RESTful API endpoints for enterprise frontend

### 2. Database (PostgreSQL)
- **Entities**:
  - `Project`: Software projects with repo URLs
  - `Agent`: Worker instances (type, status, provider, model)
  - `Job`: Tasks assigned to agents (type, payload, status, results)
  - `Artifact`: Generated files and outputs
  - `SystemConfig`: Platform configuration

### 3. Worker Service (`services/worker/`)
- **Function**: Processes jobs from Redis queue
- **Workflow**:
  1. Poll Redis for pending jobs
  2. Fetch job details from database
  3. Instantiate appropriate agent (coding, testing, etc.)
  4. Execute agent with job payload
  5. Update job status and results in database

### 4. Agent Classes (`agents/`)
Specialized agents for different development tasks:
- **ArchitectAgent**: System design, architecture reviews
- **CodingAgent**: Feature implementation, code reviews
- **TestingAgent**: Test creation, QA automation
- **DeploymentAgent**: CI/CD setup, containerization
- **MonitoringAgent**: Observability, health checks

### 5. Frontend (`frontend/`)
- **Technology**: React 19 + React Router + Tailwind CSS
- **Pages**:
  - Projects: Create and manage projects
  - Agents: View and spawn agent workers
  - Jobs: Monitor task execution
  - Settings: Configure API keys and system settings

### 6. Pipeline Orchestrator (`pipelines/orchestrator.py`)
- Coordinates multi-stage workflows
- Manages agent lifecycle and task handoff
- Supports full pipeline or partial stage execution

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js 18+ (for frontend development)
- PostgreSQL 15+
- Redis 7+

### Environment Setup

1. **Clone the repository**
```bash
git clone <repo-url>
cd code-agent
```

2. **Create `.env` file**
```bash
cat > .env << EOF
# API Keys
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here  # Optional
GOOGLE_API_KEY=your_google_key_here  # Optional
GROQ_API_KEY=your_groq_key_here      # Optional

# Database
DATABASE_URL=postgresql://agent_user:agent_password@db:5432/agent_platform

# Redis
REDIS_URL=redis://redis:6379/0
EOF
```

3. **Start the platform**
```bash
docker-compose -f docker-compose.v2.yml up --build
```

This will start:
- PostgreSQL on port 5432
- Redis on port 6379
- API Server on port 8000
- Worker service (background)

4. **Start the frontend** (in a separate terminal)
```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at http://localhost:5173

### Manual Setup (Without Docker)

1. **Install Python dependencies**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Start PostgreSQL and Redis**
```bash
# Using system services or Docker
docker run -d -p 5432:5432 -e POSTGRES_DB=agent_platform -e POSTGRES_USER=agent_user -e POSTGRES_PASSWORD=agent_password postgres:15-alpine
docker run -d -p 6379:6379 redis:7-alpine
```

3. **Run database migrations**
```bash
# The API will create tables automatically on first run
```

4. **Start the API server**
```bash
export DATABASE_URL="postgresql://agent_user:agent_password@localhost:5432/agent_platform"
export REDIS_URL="redis://localhost:6379/0"
export ANTHROPIC_API_KEY="your_key_here"
uvicorn services.api.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Start the worker**
```bash
python services/worker/main.py
```

6. **Start the frontend**
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Projects
- `POST /projects/` - Create a new project
- `GET /projects/` - List all projects
- `GET /projects/{id}` - Get project details
- `GET /projects/{id}/jobs` - Get project jobs

### Agents
- `POST /agents/` - Spawn a new agent worker
- `GET /agents/` - List all agents

### Jobs
- `POST /jobs/` - Create and dispatch a job
- `GET /jobs/` - List all jobs
- `GET /jobs/{id}` - Get job details and status

### Settings
- `POST /settings/` - Save configuration
- `GET /settings/` - Retrieve settings

## Usage Examples

### 1. Create a Project
```bash
curl -X POST http://localhost:8000/projects/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Web App",
    "description": "E-commerce platform",
    "repo_url": "https://github.com/user/repo"
  }'
```

### 2. Spawn an Agent
```bash
curl -X POST http://localhost:8000/agents/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "coding-agent-1",
    "type": "coding",
    "provider": "anthropic",
    "model": "claude-3-5-sonnet-20241022"
  }'
```

### 3. Create a Job
```bash
curl -X POST http://localhost:8000/jobs/ \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "type": "implement_feature",
    "payload": {
      "task": "Add user authentication with JWT",
      "requirements": "Use FastAPI dependencies for auth"
    }
  }'
```

## Agent Types and Job Types

### Agent Types
- `architect` - System design and architecture
- `coding` - Feature implementation
- `testing` - Test creation and QA
- `deployment` - CI/CD and infrastructure
- `monitoring` - Observability and health checks

### Job Types
- `design_system` - Architecture design
- `implement_feature` - Code implementation
- `create_tests` - Test generation
- `setup_deployment` - Deployment configuration
- `setup_monitoring` - Monitoring setup
- `review_code` - Code review
- `run_qa_suite` - Quality assurance

## Development

### Project Structure
```
code-agent/
├── agents/                 # Agent implementations
│   ├── base_agent.py      # Base agent class
│   ├── architect_agent.py
│   ├── coding_agent.py
│   ├── testing_agent.py
│   ├── deployment_agent.py
│   └── monitoring_agent.py
├── pipelines/             # Orchestration logic
│   └── orchestrator.py
├── services/
│   ├── api/               # FastAPI backend
│   │   ├── main.py       # API endpoints
│   │   ├── models.py     # SQLAlchemy models
│   │   └── database.py   # DB configuration
│   └── worker/            # Job processor
│       └── main.py       # Worker loop
├── frontend/              # React UI
│   ├── src/
│   │   ├── pages/        # Page components
│   │   ├── App.jsx
│   │   └── api.js        # API client
│   └── package.json
├── config/                # Configuration
├── docker-compose.v2.yml  # Docker setup
├── requirements.txt       # Python dependencies
└── README.md
```

### Adding a New Agent Type

1. Create agent class in `agents/`:
```python
from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    @property
    def agent_name(self) -> str:
        return "MyAgent"

    def get_system_prompt(self) -> str:
        return "You are an expert in..."

    # Implement agent-specific methods
```

2. Register in orchestrator
3. Update API to support new agent type
4. Add UI components for the new agent

## Configuration

### AI Provider Configuration
The platform supports multiple AI providers:
- **Anthropic** (Claude): `ANTHROPIC_API_KEY`
- **OpenAI** (GPT): `OPENAI_API_KEY`
- **Google** (Gemini): `GOOGLE_API_KEY`
- **Groq**: `GROQ_API_KEY`

Configure per-agent via the `provider` and `model` fields when creating agents.

### Worker Configuration
Workers can be scaled horizontally by running multiple instances:
```bash
docker-compose -f docker-compose.v2.yml up --scale worker=5
```

## Monitoring and Logs

### API Logs
```bash
docker-compose -f docker-compose.v2.yml logs -f api
```

### Worker Logs
```bash
docker-compose -f docker-compose.v2.yml logs -f worker
```

### Database Access
```bash
docker-compose -f docker-compose.v2.yml exec db psql -U agent_user -d agent_platform
```

### Redis CLI
```bash
docker-compose -f docker-compose.v2.yml exec redis redis-cli
```

## Troubleshooting

### Worker not processing jobs
1. Check Redis connection: `redis-cli -u $REDIS_URL ping`
2. Verify jobs in queue: `redis-cli LLEN job_queue`
3. Check worker logs for errors

### Agent execution fails
1. Verify API keys are set correctly
2. Check agent has Docker access (for sandbox)
3. Review job logs in database

### Database connection issues
1. Ensure PostgreSQL is running
2. Verify `DATABASE_URL` is correct
3. Check database credentials

## Security Considerations

- API keys are stored in environment variables, not in database
- Agent sandboxes use Docker isolation
- Database credentials should be rotated regularly
- Use HTTPS in production
- Implement authentication for API endpoints (future)

## Roadmap

- [ ] Worker service implementation
- [ ] WebSocket support for real-time updates
- [ ] User authentication and authorization
- [ ] Multi-tenancy support
- [ ] Kubernetes deployment manifests
- [ ] Metrics and observability dashboard
- [ ] Agent capability plugins
- [ ] Workflow templates

## License

[Your License Here]

## Contributing

[Contributing Guidelines]
