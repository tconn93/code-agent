#!/bin/bash
# create-job.sh - Assign a job/task to agents
# Usage: ./scripts/create-job.sh &lt;project_id&gt; &lt;job_type&gt; &lt;task_description&gt; [agent_id]

set -e

if [ $# -lt 3 ]; then
  echo "Usage: $0 &lt;project_id&gt; &lt;job_type&gt; &lt;task_description&gt; [agent_id]"
  echo "Job types: implement_feature, design_system, create_tests, setup_deployment, setup_monitoring, review_code, run_qa_suite"
  exit 1
fi

PROJECT_ID=$1
JOB_TYPE=$2
TASK=$3
AGENT_ID=${4:-null}

API_URL=${API_URL:-http://localhost:8000}

echo "Creating job for project $PROJECT_ID (type: $JOB_TYPE)"

curl -X POST "$API_URL/jobs/" \\
  -H "Content-Type: application/json" \\
  -d "{
    \"project_id\": $PROJECT_ID,
    \"type\": \"$JOB_TYPE\",
    \"payload\": {
      \"task\": \"$TASK\"
    }$( [ \"$AGENT_ID\" != \"null\" ] && echo \", \"assigned_agent_id\": $AGENT_ID\" || echo \"\" )
  }" | jq '.'

echo "Job created. Monitor: curl $API_URL/jobs/&lt;job_id&gt;"