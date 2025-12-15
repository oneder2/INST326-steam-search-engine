#!/bin/bash
# Setup Verification Script
# Verifies that the project is properly configured for local development

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Steam Game Search Engine - Setup Check${NC}"
echo -e "${BLUE}========================================${NC}"

ERRORS=0

# Check Node.js
echo -e "\n${BLUE}Checking Node.js...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js installed: $NODE_VERSION${NC}"
else
    echo -e "${RED}✗ Node.js not found. Please install Node.js 18+${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check Python
echo -e "\n${BLUE}Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python installed: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python3 not found. Please install Python 3.12+${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check npm
echo -e "\n${BLUE}Checking npm...${NC}"
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓ npm installed: $NPM_VERSION${NC}"
else
    echo -e "${RED}✗ npm not found. Please install npm${NC}"
    ERRORS=$((ERRORS + 1))
fi

# Check frontend dependencies
echo -e "\n${BLUE}Checking frontend dependencies...${NC}"
if [ -d "frontend-INST326-steam-search/node_modules" ]; then
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠ Frontend dependencies not installed${NC}"
    echo -e "${YELLOW}  Run: cd frontend-INST326-steam-search && npm install${NC}"
fi

# Check backend virtual environment
echo -e "\n${BLUE}Checking backend virtual environment...${NC}"
if [ -d "backend-INST326-steam-search/venv" ]; then
    echo -e "${GREEN}✓ Backend virtual environment exists${NC}"
else
    echo -e "${YELLOW}⚠ Backend virtual environment not found${NC}"
    echo -e "${YELLOW}  Run: cd backend-INST326-steam-search && python3 -m venv venv${NC}"
fi

# Check environment files
echo -e "\n${BLUE}Checking environment files...${NC}"

if [ -f "backend-INST326-steam-search/.env" ]; then
    echo -e "${GREEN}✓ Backend .env file exists${NC}"
else
    echo -e "${YELLOW}⚠ Backend .env file not found${NC}"
    if [ -f "backend-INST326-steam-search/.env.example" ]; then
        echo -e "${YELLOW}  Copy from .env.example: cp backend-INST326-steam-search/.env.example backend-INST326-steam-search/.env${NC}"
    fi
fi

if [ -f "frontend-INST326-steam-search/.env.local" ]; then
    echo -e "${GREEN}✓ Frontend .env.local file exists${NC}"
else
    echo -e "${YELLOW}⚠ Frontend .env.local not found (optional, defaults work)${NC}"
fi

# Check ports availability
echo -e "\n${BLUE}Checking port availability...${NC}"

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠ Port 3000 is in use${NC}"
else
    echo -e "${GREEN}✓ Port 3000 is available${NC}"
fi

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}⚠ Port 8000 is in use${NC}"
else
    echo -e "${GREEN}✓ Port 8000 is available${NC}"
fi

# Summary
echo -e "\n${BLUE}========================================${NC}"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}Setup check completed!${NC}"
    echo -e "${GREEN}You can start development with:${NC}"
    echo -e "${BLUE}  ./scripts/start-dev.sh${NC}"
    echo -e "${BLUE}  Or manually start frontend and backend${NC}"
else
    echo -e "${RED}Setup check found $ERRORS critical issue(s)${NC}"
    echo -e "${YELLOW}Please fix the issues above before starting development${NC}"
    exit 1
fi
echo -e "${BLUE}========================================${NC}"

