#!/bin/bash
# list-jobs.sh - List recent jobs
API_URL=${API_URL:-http://localhost:8000}
curl "$API_URL/jobs/" | jq '.[] | {id, project_id, type, status, assigned_agent_id}'