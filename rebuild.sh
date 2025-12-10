#!/bin/bash
# Script to rebuild Docker images with updated dependencies

echo "Stopping containers..."
docker-compose -f docker-compose.v2.yml down

echo ""
echo "Removing old images..."
docker-compose -f docker-compose.v2.yml rm -f

echo ""
echo "Rebuilding with no cache to ensure fresh install..."
docker-compose -f docker-compose.v2.yml build --no-cache

echo ""
echo "Starting services..."
docker-compose -f docker-compose.v2.yml up -d

echo ""
echo "Done! Check logs with:"
echo "  docker-compose -f docker-compose.v2.yml logs -f"
