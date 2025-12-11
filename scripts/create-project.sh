#!/bin/bash
# create-project.sh - Create a new project
# Usage: ./scripts/create-project.sh &lt;name&gt; [description] [repo_url]

set -e

if [ $# -lt 1 ]; then
  echo "Usage: $0 &lt;name&gt; [description] [repo_url]"
  exit 1
fi

NAME=$1
DESCRIPTION=${2:-"Project created via script"}
REPO_URL=${3:-""}

API_URL=${API_URL:-http://localhost:8000}

echo "Creating project: $NAME"

curl -s -X POST "$API_URL/projects/" \\
  -H "Content-Type: application/json" \\
  -d "{
    \"name\": \"$NAME\",
    \"description\": \"$DESCRIPTION\",
    \"repo_url\": $REPO_URL
  }"

#echo $RESPONSE | jq '.'
#echo "Project ID: $(echo $RESPONSE | jq -r '.id')"
#echo "Use this ID for jobs: ./scripts/create-job.sh &lt;project_id&gt; &lt;job_type&gt; \"&lt;task&gt;\""
