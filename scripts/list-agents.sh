#!/bin/bash
# list-agents.sh - List all agents and their status
API_URL=${API_URL:-http://localhost:8000}
curl "$API_URL/agents/" | jq '.[] | {name, type, provider, model, status, total_jobs_completed}'