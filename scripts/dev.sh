#!/bin/bash

# Steam Game Search Engine - Development Script
# This script helps start development servers for the monorepo

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_DIR="frontend-INST326-steam-search"
BACKEND_DIR="backend-INST326-steam-search"

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Steam Game Search Engine${NC}"
    echo -e "${BLUE}  Development Environment${NC}"
    echo -e "${BLUE}================================${NC}"
    echo
}

print_step() {
    echo -e "${YELLOW}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check directories
    if [[ ! -d "$FRONTEND_DIR" ]] || [[ ! -d "$BACKEND_DIR" ]]; then
        print_error "Not in monorepo root directory"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js not found. Please install Node.js 18+"
        exit 1
    fi
    
    # Check Python
    if ! command -v python &> /dev/null; then
        print_error "Python not found. Please install Python 3.8+"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

install_dependencies() {
    print_step "Installing dependencies..."
    
    # Frontend dependencies
    print_info "Installing frontend dependencies..."
    cd "$FRONTEND_DIR"
    npm install
    cd ..
    
    # Backend dependencies
    print_info "Installing backend dependencies..."
    cd "$BACKEND_DIR"
    pip install -r requirements-core.txt
    cd ..
    
    print_success "Dependencies installed"
}

start_frontend() {
    print_step "Starting frontend development server..."
    cd "$FRONTEND_DIR"
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    print_success "Frontend started (PID: $FRONTEND_PID)"
}

start_backend() {
    print_step "Starting backend development server..."
    cd "$BACKEND_DIR"
    python main.py &
    BACKEND_PID=$!
    cd ..
    print_success "Backend started (PID: $BACKEND_PID)"
}

start_both() {
    print_step "Starting both services..."
    
    # Use concurrently if available, otherwise start separately
    if command -v npx &> /dev/null; then
        cd "$FRONTEND_DIR"
        npx concurrently \
            --names "FRONTEND,BACKEND" \
            --prefix-colors "blue,green" \
            "npm run dev" \
            "cd ../$BACKEND_DIR && python main.py"
    else
        start_backend
        sleep 2
        start_frontend
        
        print_info "Services started:"
        print_info "  Frontend: http://localhost:3000"
        print_info "  Backend: http://localhost:8000"
        print_info "  Backend API Docs: http://localhost:8000/docs"
        print_info ""
        print_info "Press Ctrl+C to stop all services"
        
        # Wait for user interrupt
        trap 'kill $FRONTEND_PID $BACKEND_PID 2>/dev/null; exit' INT
        wait
    fi
}

test_services() {
    print_step "Testing services..."
    
    # Frontend tests
    print_info "Running frontend tests..."
    cd "$FRONTEND_DIR"
    npm run type-check
    npm test -- --passWithNoTests
    cd ..
    
    # Backend tests
    print_info "Testing backend imports..."
    cd "$BACKEND_DIR"
    python -c "import main; print('Backend imports successful')"
    cd ..
    
    print_success "All tests passed"
}

show_status() {
    print_step "Service Status"
    echo
    
    # Check frontend
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend: Running (http://localhost:3000)"
    else
        print_error "Frontend: Not running"
    fi
    
    # Check backend
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        print_success "Backend: Running (http://localhost:8000)"
    else
        print_error "Backend: Not running"
    fi
    
    echo
    print_info "Available URLs:"
    print_info "  Frontend: http://localhost:3000"
    print_info "  Backend API: http://localhost:8000"
    print_info "  API Documentation: http://localhost:8000/docs"
    print_info "  Health Check: http://localhost:8000/api/v1/health"
}

show_help() {
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  start     - Start both frontend and backend (default)"
    echo "  frontend  - Start frontend only"
    echo "  backend   - Start backend only"
    echo "  install   - Install dependencies"
    echo "  test      - Run tests"
    echo "  status    - Show service status"
    echo "  help      - Show this help"
    echo
    echo "Examples:"
    echo "  $0 start     # Start both services"
    echo "  $0 frontend  # Start frontend only"
    echo "  $0 install   # Install dependencies"
}

main() {
    print_header
    
    case "${1:-start}" in
        "start")
            check_prerequisites
            start_both
            ;;
        "frontend")
            check_prerequisites
            start_frontend
            wait
            ;;
        "backend")
            check_prerequisites
            start_backend
            wait
            ;;
        "install")
            check_prerequisites
            install_dependencies
            ;;
        "test")
            check_prerequisites
            test_services
            ;;
        "status")
            show_status
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
