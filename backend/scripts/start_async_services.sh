#!/bin/bash
# Script to start all required services for async question generation
# Usage: ./scripts/start_async_services.sh

set -e

echo "🚀 Starting Async Interview System Services..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Redis is running
echo -n "Checking Redis connection... "
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${RED}✗ Redis is not running${NC}"
    echo ""
    echo "Please start Redis first:"
    echo "  Docker: docker run -d --name redis-datn -p 6379:6379 redis:7-alpine"
    echo "  Native: redis-server"
    exit 1
fi

# Get the backend directory
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BACKEND_DIR"

echo ""
echo "📂 Backend directory: $BACKEND_DIR"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        source .venv/bin/activate
    fi
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
fi

# Check if Celery is installed
if ! python -c "import celery" 2>/dev/null; then
    echo -e "${RED}✗ Celery is not installed${NC}"
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "Starting services in separate terminal windows..."
echo ""

# Function to start service in new terminal
start_in_terminal() {
    local title=$1
    local command=$2
    
    # Try gnome-terminal first (Ubuntu/Debian)
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal --title="$title" -- bash -c "cd '$BACKEND_DIR' && source venv/bin/activate 2>/dev/null || source .venv/bin/activate && $command; exec bash"
    # Try konsole (KDE)
    elif command -v konsole &> /dev/null; then
        konsole --title "$title" -e bash -c "cd '$BACKEND_DIR' && source venv/bin/activate 2>/dev/null || source .venv/bin/activate && $command; exec bash" &
    # Try xterm (fallback)
    elif command -v xterm &> /dev/null; then
        xterm -T "$title" -e bash -c "cd '$BACKEND_DIR' && source venv/bin/activate 2>/dev/null || source .venv/bin/activate && $command; exec bash" &
    # macOS Terminal
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        osascript -e "tell application \"Terminal\" to do script \"cd '$BACKEND_DIR' && source venv/bin/activate 2>/dev/null || source .venv/bin/activate && $command\""
    else
        echo -e "${YELLOW}⚠ Could not open new terminal. Please run manually:${NC}"
        echo "   $command"
    fi
}

# Start Celery Worker
echo "1️⃣  Starting Celery Worker..."
start_in_terminal "Celery Worker - Interview System" \
    "celery -A app.core.celery_app worker --loglevel=info --concurrency=2 --pool=solo"

sleep 2

# Start Celery Flower (monitoring)
echo "2️⃣  Starting Celery Flower (Monitoring)..."
start_in_terminal "Celery Flower - Monitoring" \
    "celery -A app.core.celery_app flower --port=5555"

sleep 2

# Start FastAPI
echo "3️⃣  Starting FastAPI Backend..."
start_in_terminal "FastAPI Backend - Interview API" \
    "uvicorn app.main:app --reload --port 8000 --host 0.0.0.0"

sleep 2

echo ""
echo -e "${GREEN}✅ All services started!${NC}"
echo ""
echo "📊 Service URLs:"
echo "   - FastAPI:        http://localhost:8000"
echo "   - API Docs:       http://localhost:8000/docs"
echo "   - Celery Flower:  http://localhost:5555"
echo "   - Redis:          localhost:6379"
echo ""
echo "📝 Logs:"
echo "   - Check the individual terminal windows for logs"
echo ""
echo "🧪 Test the system:"
echo "   curl -X POST http://localhost:8000/api/v1/interviews \\"
echo "     -H 'Authorization: Bearer YOUR_TOKEN' \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"job_description\": \"...\", \"cv_content\": \"...\", \"position_level\": \"middle\"}'"
echo ""
echo "🛑 To stop services:"
echo "   - Close the terminal windows or press Ctrl+C in each"
echo ""
