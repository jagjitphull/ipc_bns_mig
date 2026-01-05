#!/bin/bash
# Frontend Rebuild Script - Ensures clean rebuild with no cache

echo "🔄 Rebuilding frontend with cache clearing..."
echo ""

# Stop the frontend container
echo "1. Stopping frontend container..."
docker-compose stop frontend

# Remove the frontend container
echo "2. Removing frontend container..."
docker-compose rm -f frontend

# Remove the frontend image to force full rebuild
echo "3. Removing frontend image..."
docker rmi ipc_bns_mig_frontend 2>/dev/null || echo "   (Image not found, skipping)"

# Rebuild frontend with no cache
echo "4. Rebuilding frontend with --no-cache..."
docker-compose build --no-cache frontend

# Start the frontend
echo "5. Starting frontend..."
docker-compose up -d frontend

# Wait for container to be healthy
echo "6. Waiting for frontend to start..."
sleep 5

# Show logs
echo "7. Frontend logs (last 20 lines):"
echo "================================"
docker-compose logs --tail=20 frontend

echo ""
echo "✅ Frontend rebuild complete!"
echo ""
echo "📋 Diagnostic Steps:"
echo "  1. Open browser to http://localhost:3000/cases (or your IP)"
echo "  2. Open Developer Tools (F12)"
echo "  3. Check Console tab for any errors"
echo "  4. Check Network tab to see if files are loading"
echo ""
echo "🔍 If page is still blank:"
echo "  - Clear browser cache (Ctrl+Shift+Delete)"
echo "  - Try incognito/private mode"
echo "  - Check browser console for error messages"
echo ""
