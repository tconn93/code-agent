#!/bin/bash
# spawn-agent.sh - Spin up a new agent
# Usage: ./scripts/spawn-agent.sh <name> <type> [provider] [model] [--prompt "inline prompt" | --prompt-file path/to/file]
# Example: ./scripts/spawn-agent.sh codeB coding xai grok-4-fast-reasoning --prompt-file ../prompts/backendCoding.txt
# Types: architect, coding, testing, deployment, monitoring, scrum_master
# Providers: anthropic, openai, groq, grok, gemini, xai

set -e

PROMPT=""
PROMPT_FILE=""

# Parse flags for prompt/prompt-file (before positional args)
while [[ $# -gt 0 ]]; do
  case $1 in
    --prompt)
      PROMPT="$2"
      shift 2
      ;;
    --prompt-file)
      PROMPT_FILE="$2"
      shift 2
      ;;
    *)
      break
      ;;
  esac
done

if [ -n "$PROMPT_FILE" ]; then
  if [ ! -f "$PROMPT_FILE" ]; then
    echo "Error: Prompt file '$PROMPT_FILE' not found"
    exit 1
  fi
  PROMPT=$(cat "$PROMPT_FILE")
  echo "Loaded prompt from file: $PROMPT_FILE (length: ${#PROMPT} chars)"
fi

if [ $# -lt 2 ]; then
  echo "Usage: $0 <name> <type> [provider] [model] [--prompt \"inline prompt\" | --prompt-file path/to/file]"
  echo "Types: architect, coding, testing, deployment, monitoring, scrum_master"
  echo "Providers: anthropic, openai, groq, grok, gemini, xai"
  exit 1
fi

NAME=$1
TYPE=$2
PROVIDER=${3:-xai}
MODEL=${4:-grok-4-fast-reasoning}

API_URL=${API_URL:-http://localhost:8000}
echo "Using API URL: $API_URL"

echo "Spinning up agent: $NAME ($TYPE, $PROVIDER/$MODEL)"

# Build JSON payload safely with jq (auto-escapes prompt, handles newlines/quotes)
JSON_PAYLOAD=$(jq -n \
  --arg name "$NAME" \
  --arg type "$TYPE" \
  --arg provider "$PROVIDER" \
  --arg model "$MODEL" \
  --argjson has_prompt "$( [ -n "$PROMPT" ] && echo true || echo false )" \
  --arg prompt "$PROMPT" '
  {
    name: $name,
    type: $type,
    provider: $provider,
    model: $model
  } + (if $has_prompt then {custom_system_prompt: $prompt} else {} end)
')

# Debug: Uncomment to print payload (remove after testing)
# echo "Generated JSON payload: $JSON_PAYLOAD"

curl -X POST "$API_URL/agents/" \
  -H "Content-Type: application/json" \
  -d "$JSON_PAYLOAD" | jq '.'

echo "Agent created. Check status: curl $API_URL/agents/"