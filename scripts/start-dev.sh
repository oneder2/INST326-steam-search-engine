#!/bin/bash
# Development Startup Script
# Starts both frontend and backend services for local development

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Steam Game Search Engine - Dev Startup${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if we're in the project root
if [ ! -d "frontend-INST326-steam-search" ] || [ ! -d "backend-INST326-steam-search" ]; then
    echo -e "${YELLOW}Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Check for .env files
echo -e "${BLUE}Checking environment configuration...${NC}"

if [ ! -f "backend-INST326-steam-search/.env" ]; then
    echo -e "${YELLOW}Warning: backend-INST326-steam-search/.env not found${NC}"
    echo -e "${YELLOW}Creating from .env.example...${NC}"
    if [ -f "backend-INST326-steam-search/.env.example" ]; then
        cp backend-INST326-steam-search/.env.example backend-INST326-steam-search/.env
        echo -e "${YELLOW}Please update backend-INST326-steam-search/.env with your configuration${NC}"
    fi
fi

if [ ! -f "frontend-INST326-steam-search/.env.local" ]; then
    echo -e "${YELLOW}Warning: frontend-INST326-steam-search/.env.local not found${NC}"
    echo -e "${YELLOW}Creating from .env.local.example...${NC}"
    if [ -f "frontend-INST326-steam-search/.env.local.example" ]; then
        cp frontend-INST326-steam-search/.env.local.example frontend-INST326-steam-search/.env.local
    fi
fi

# Start backend
echo -e "${GREEN}Starting backend server...${NC}"
cd backend-INST326-steam-search

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.deps_installed" ]; then
    echo -e "${BLUE}Installing backend dependencies...${NC}"
    pip install -r requirements.txt
    touch venv/.deps_installed
fi

# Start backend in background
echo -e "${GREEN}Backend starting on http://localhost:8000${NC}"
python main.py &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend
echo -e "${GREEN}Starting frontend server...${NC}"
cd ../frontend-INST326-steam-search

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}Installing frontend dependencies...${NC}"
    npm install
fi

# Start frontend
echo -e "${GREEN}Frontend starting on http://localhost:3000${NC}"
npm run dev &
FRONTEND_PID=$!

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup INT TERM

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Services started successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${BLUE}Backend:  http://localhost:8000${NC}"
echo -e "${BLUE}Frontend: http://localhost:3000${NC}"
echo -e "${BLUE}API Docs: http://localhost:8000/docs${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Wait for processes
wait

