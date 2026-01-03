#!/bin/bash

# IPC/BNS Legal Reasoning Agent - Startup Script

set -e

echo "=========================================="
echo "IPC/BNS Legal Reasoning Agent"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed."
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed."
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker and Docker Compose found"
echo ""

# Check if containers are already running
if [ "$(docker-compose ps -q)" ]; then
    echo "Containers are already running."
    echo ""
    read -p "Do you want to restart them? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Stopping existing containers..."
        docker-compose down
    else
        echo "Keeping existing containers running."
        echo ""
        echo "Access the application at:"
        echo "  Frontend: http://localhost:3000"
        echo "  Backend:  http://localhost:8000"
        echo "  API Docs: http://localhost:8000/docs"
        exit 0
    fi
fi

echo "Starting IPC/BNS Legal Reasoning Agent..."
echo ""

# Build and start containers
echo "Building Docker images (this may take a few minutes on first run)..."
docker-compose up --build -d

echo ""
echo "Waiting for services to be ready..."
sleep 5

# Check backend health
echo "Checking backend health..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Backend is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠ Backend health check timeout. Check logs with: docker-compose logs backend"
    fi
    sleep 2
done

echo ""
echo "=========================================="
echo "✓ Application started successfully!"
echo "=========================================="
echo ""
echo "Access the application at:"
echo ""
echo "  Frontend:    http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs:    http://localhost:8000/docs"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop the application:"
echo "  docker-compose down"
echo ""
echo "=========================================="
