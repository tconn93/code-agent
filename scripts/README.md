# Scripts README

## spawn-agent.sh
Spins up a new agent via API.
- **Usage:** `./spawn-agent.sh <name> <type> [provider] [model] [--prompt "inline prompt" | --prompt-file path/to/file]`
- **Params:**
  - `<name>`: Unique agent name (e.g., "coder1").
  - `<type>`: Agent type (architect, coding, testing, deployment, monitoring, scrum_master).
  - `[provider]`: LLM provider (default: xai; options: anthropic, openai, groq, grok, gemini, xai).
  - `[model]`: Model name (default: grok-4-fast-reasoning).
  - `--prompt`: Inline custom system prompt (overrides default).
  - `--prompt-file`: Path to file with custom prompt (content loaded and escaped).
- **Behavior:** POST to /agents/ with JSON payload (jq for escaping). Sets AGENT_CUSTOM_PROMPT env for Docker worker. Returns agent ID/status.
- **Example:** `./spawn-agent.sh coder1 coding xai grok-4-fast-reasoning --prompt-file prompts/coding.txt`

## create-project.sh
Creates a new project via API.
- **Usage:** `./create-project.sh <name> [description] [repo_url]`
- **Params:**
  - `<name>`: Project name.
  - `[description]`: Optional description.
  - `[repo_url]`: Optional Git repo URL.
- **Behavior:** POST to /projects/. Returns project ID for use in jobs.
- **Example:** `./create-project.sh my-app "Backend API" "https://github.com/user/my-app"`

## create-job.sh
Assigns a job/task to agents via API.
- **Usage:** `./create-job.sh <project_id> <job_type> "<task_description>" [agent_id]`
- **Params:**
  - `<project_id>`: ID from create-project.
  - `<job_type>`: Type (implement_feature, design_system, create_tests, setup_deployment, setup_monitoring, review_code, run_qa_suite).
  - `"<task_description>"`: Task details (quoted for multi-word).
  - `[agent_id]`: Optional agent ID to assign (auto-assigns otherwise).
- **Behavior:** POST to /jobs/ with payload {"task": description}. Routes to orchestrator via Redis. Returns job ID.
- **Example:** `./create-job.sh 1 implement_feature "Add user authentication" 2`

## list-agents.sh
Lists all agents and status.
- **Usage:** `./list-agents.sh`
- **Behavior:** GET /agents/, jq filters {name, type, provider, model, status, total_jobs_completed}.
- **Output:** JSON array of agents.

## list-jobs.sh
Lists recent jobs.
- **Usage:** `./list-jobs.sh`
- **Behavior:** GET /jobs/, jq filters {id, project_id, type, status, assigned_agent_id}.
- **Output:** JSON array of jobs.

**Notes:**
- Set `API_URL` env for custom endpoint (default: http://localhost:8000).
- Requires jq for JSON handling.
- Run API first (`uvicorn services.api.main:app --reload`).
- Custom prompts override agent defaults in base_agent.py.