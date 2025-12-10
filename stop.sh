#!/bin/bash
# Stop script for AI Agent Platform

set -e

echo "========================================="
echo "  Stopping AI Agent Platform"
echo "========================================="
echo ""

docker-compose -f docker-compose.v2.yml down

echo ""
echo "Services stopped successfully!"
echo ""
echo "To remove all data (including database):"
echo "  docker-compose -f docker-compose.v2.yml down -v"
echo ""
