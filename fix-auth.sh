#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Fixing Authentication Database${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if backend container is running
if ! docker ps | grep -q ipc-bns-backend; then
    echo -e "${YELLOW}Backend container is not running.${NC}"
    echo "Starting backend..."
    docker-compose up -d backend
    sleep 5
fi

echo "Running database repair script..."
echo ""

# Run repair script in container
docker exec -it ipc-bns-backend python /app/app/repair_database.py

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ Database repair complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Try registering a new user"
    echo "  2. Try logging in with existing user"
    echo ""
    echo "If you still have issues:"
    echo "  • Check backend logs: docker logs ipc-bns-backend"
    echo "  • Check frontend console (F12 in browser)"
    echo ""
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}✗ Database repair failed${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    echo "Check logs for details:"
    echo "  docker logs ipc-bns-backend"
    echo ""
fi
