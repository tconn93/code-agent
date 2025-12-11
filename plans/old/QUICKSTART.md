# Quick Start Guide

Get the AI Agent Platform up and running in 5 minutes!

## Prerequisites

Make sure you have:
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed
- At least one AI API key (Anthropic, OpenAI, Google, or Groq)
- Node.js 18+ (for frontend development)

## Step 1: Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd code-agent

# Create environment file
cp .env.example .env
```

## Step 2: Add Your API Key

Edit `.env` and add at least one API key:

```bash
# Example: Using Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# Or use OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxx

# Or use Google Gemini
GOOGLE_API_KEY=xxxxxxxxxxxxx
```

## Step 3: Start the Platform

```bash
# Make start script executable (first time only)
chmod +x start.sh

# Start all services
./start.sh
```

This starts:
- PostgreSQL database (port 5432)
- Redis queue (port 6379)
- API server (port 8000)
- Worker service

## Step 4: Start the Frontend

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: **http://localhost:5173**

## Step 5: Use the Platform

### Option A: Use the Web UI

1. Open http://localhost:5173 in your browser
2. Create a new project
3. Spawn an agent
4. Create a job and watch it execute!

### Option B: Use the API

```bash
# Create a project
curl -X POST http://localhost:8000/projects/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Project", "description": "My first project"}'

# Create a job
curl -X POST http://localhost:8000/jobs/ \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "type": "implement_feature",
    "payload": {
      "task": "Create a simple hello world FastAPI endpoint"
    }
  }'

# Check job status
curl http://localhost:8000/jobs/1
```

### Option C: Use the API Documentation

Visit **http://localhost:8000/docs** for interactive API documentation.

## Common Tasks

### View Logs

```bash
# API logs
docker-compose -f docker-compose.v2.yml logs -f api

# Worker logs
docker-compose -f docker-compose.v2.yml logs -f worker

# All logs
docker-compose -f docker-compose.v2.yml logs -f
```

### Stop Services

```bash
./stop.sh
```

### Restart Services

```bash
./stop.sh
./start.sh
```

### Access Database

```bash
docker-compose -f docker-compose.v2.yml exec db psql -U agent_user -d agent_platform
```

## Example Workflow

Here's a complete example of creating and running a coding task:

```bash
# 1. Create a project
PROJECT=$(curl -s -X POST http://localhost:8000/projects/ \
  -H "Content-Type: application/json" \
  -d '{"name": "My App", "description": "A web application"}' | jq -r '.id')

echo "Project ID: $PROJECT"

# 2. Create a coding job
JOB=$(curl -s -X POST http://localhost:8000/jobs/ \
  -H "Content-Type: application/json" \
  -d "{
    \"project_id\": $PROJECT,
    \"type\": \"implement_feature\",
    \"payload\": {
      \"task\": \"Create a FastAPI endpoint that returns the current time\"
    }
  }" | jq -r '.id')

echo "Job ID: $JOB"

# 3. Monitor job status
watch -n 2 "curl -s http://localhost:8000/jobs/$JOB | jq '.status'"

# 4. Get job results
curl -s http://localhost:8000/jobs/$JOB | jq '.result'
```

## Troubleshooting

### Services won't start

1. Make sure Docker is running
2. Check if ports are available:
   ```bash
   lsof -i :5432  # PostgreSQL
   lsof -i :6379  # Redis
   lsof -i :8000  # API
   ```
3. View logs: `docker-compose -f docker-compose.v2.yml logs`

### Jobs not processing

1. Check worker is running:
   ```bash
   docker-compose -f docker-compose.v2.yml ps worker
   ```
2. Check Redis queue:
   ```bash
   docker-compose -f docker-compose.v2.yml exec redis redis-cli LLEN job_queue
   ```
3. View worker logs:
   ```bash
   docker-compose -f docker-compose.v2.yml logs worker
   ```

### API key not working

1. Make sure the key is correctly set in `.env`
2. Restart services after changing `.env`:
   ```bash
   ./stop.sh
   ./start.sh
   ```
3. Check API logs for authentication errors

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Explore different agent types:
  - `architect` - System design
  - `coding` - Implementation
  - `testing` - QA and tests
  - `deployment` - CI/CD
  - `monitoring` - Observability

## Need Help?

- Check the main [README.md](README.md)
- Review [API Documentation](http://localhost:8000/docs)
- Open an issue on GitHub
- Check existing issues and discussions

Happy coding with AI agents!
