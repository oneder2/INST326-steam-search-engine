#!/bin/bash

# Steam Game Search Engine - Monorepo Deployment Script
# This script helps deploy both frontend and backend services to Render.com

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_DIR="frontend-INST326-steam-search"
BACKEND_DIR="backend-INST326-steam-search"
FRONTEND_URL="https://steam-search-frontend.onrender.com"
BACKEND_URL="https://steam-search-backend.onrender.com"

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Steam Game Search Engine${NC}"
    echo -e "${BLUE}  Monorepo Deployment Script${NC}"
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
    
    # Check if we're in the right directory
    if [[ ! -d "$FRONTEND_DIR" ]] || [[ ! -d "$BACKEND_DIR" ]]; then
        print_error "Not in monorepo root directory. Please run from project root."
        exit 1
    fi
    
    # Check git status
    if [[ -n $(git status --porcelain) ]]; then
        print_error "Working directory is not clean. Please commit or stash changes."
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

test_frontend_build() {
    print_step "Testing frontend build..."
    
    cd "$FRONTEND_DIR"
    
    # Install dependencies
    npm ci
    
    # Run type check
    npm run type-check
    
    # Run tests
    npm test -- --passWithNoTests
    
    # Build
    npm run build
    
    cd ..
    print_success "Frontend build test passed"
}

test_backend() {
    print_step "Testing backend..."
    
    cd "$BACKEND_DIR"
    
    # Check if Python is available
    if ! command -v python &> /dev/null; then
        print_error "Python not found. Please install Python 3.8+"
        exit 1
    fi
    
    # Install dependencies
    pip install -r requirements-core.txt
    
    # Basic import test
    python -c "import main; print('Backend imports successful')"
    
    cd ..
    print_success "Backend test passed"
}

deploy_services() {
    print_step "Deploying to Render.com..."
    
    # Push to GitHub (triggers auto-deployment)
    git push origin main
    
    print_success "Code pushed to GitHub. Render.com will auto-deploy."
    print_info "Monitor deployment at:"
    print_info "  Frontend: https://dashboard.render.com"
    print_info "  Backend: https://dashboard.render.com"
}

check_health() {
    print_step "Checking service health..."
    
    # Wait a bit for deployment
    sleep 10
    
    # Check backend health
    print_info "Checking backend health..."
    if curl -f -s "$BACKEND_URL/api/v1/health" > /dev/null; then
        print_success "Backend is healthy"
    else
        print_error "Backend health check failed"
    fi
    
    # Check frontend
    print_info "Checking frontend..."
    if curl -f -s "$FRONTEND_URL" > /dev/null; then
        print_success "Frontend is accessible"
    else
        print_error "Frontend health check failed"
    fi
}

show_status() {
    print_step "Service Status"
    echo
    echo "Frontend:"
    echo "  URL: $FRONTEND_URL"
    echo "  Status: $(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")"
    echo
    echo "Backend:"
    echo "  URL: $BACKEND_URL"
    echo "  Health: $BACKEND_URL/api/v1/health"
    echo "  Status: $(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/v1/health")"
    echo
}

show_help() {
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  deploy    - Full deployment (test + deploy + health check)"
    echo "  test      - Run tests only"
    echo "  push      - Push to GitHub (triggers deployment)"
    echo "  health    - Check service health"
    echo "  status    - Show service status"
    echo "  help      - Show this help"
    echo
    echo "Examples:"
    echo "  $0 deploy   # Full deployment"
    echo "  $0 test     # Test only"
    echo "  $0 health   # Health check only"
}

# Main script
main() {
    print_header
    
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            test_frontend_build
            test_backend
            deploy_services
            check_health
            show_status
            ;;
        "test")
            check_prerequisites
            test_frontend_build
            test_backend
            ;;
        "push")
            check_prerequisites
            deploy_services
            ;;
        "health")
            check_health
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

# Run main function with all arguments
main "$@"
