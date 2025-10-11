#!/bin/bash

# Steam Game Search Engine - Render Deployment Script
# This script automates the deployment process to Render.com

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="steam-game-search-engine"
FRONTEND_SERVICE="steam-search-frontend"
BACKEND_SERVICE="steam-search-backend"
RENDER_API_URL="https://api.render.com/v1"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check if curl is installed
    if ! command -v curl &> /dev/null; then
        log_error "curl is required but not installed"
        exit 1
    fi
    
    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        log_warning "jq is not installed. JSON parsing will be limited"
    fi
    
    # Check if git is installed
    if ! command -v git &> /dev/null; then
        log_error "git is required but not installed"
        exit 1
    fi
    
    log_success "Dependencies check passed"
}

check_render_api_key() {
    if [ -z "$RENDER_API_KEY" ]; then
        log_error "RENDER_API_KEY environment variable is not set"
        log_info "Please set your Render API key: export RENDER_API_KEY=your_api_key"
        exit 1
    fi
    log_success "Render API key found"
}

validate_git_status() {
    log_info "Validating git status..."
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not in a git repository"
        exit 1
    fi
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        log_warning "You have uncommitted changes"
        read -p "Do you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Deployment cancelled"
            exit 0
        fi
    fi
    
    log_success "Git status validated"
}

build_frontend() {
    log_info "Building frontend..."
    
    # Install dependencies
    if [ -f "package.json" ]; then
        npm ci
        log_success "Frontend dependencies installed"
    else
        log_error "package.json not found"
        exit 1
    fi
    
    # Run type checking
    npm run type-check
    log_success "TypeScript type checking passed"
    
    # Run linting
    npm run lint
    log_success "ESLint checks passed"
    
    # Build the application
    npm run build
    log_success "Frontend build completed"
}

prepare_backend() {
    log_info "Preparing backend..."
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        log_error "requirements.txt not found"
        exit 1
    fi
    
    # Validate Python syntax (if Python is available)
    if command -v python3 &> /dev/null; then
        log_info "Validating Python syntax..."
        find . -name "*.py" -exec python3 -m py_compile {} \; 2>/dev/null || {
            log_warning "Python syntax validation failed or Python not available"
        }
    fi
    
    log_success "Backend preparation completed"
}

deploy_to_render() {
    log_info "Deploying to Render..."
    
    # Get current git commit
    COMMIT_SHA=$(git rev-parse HEAD)
    COMMIT_MESSAGE=$(git log -1 --pretty=%B)
    
    log_info "Deploying commit: $COMMIT_SHA"
    log_info "Commit message: $COMMIT_MESSAGE"
    
    # Trigger deployment via Render API
    if [ ! -z "$RENDER_API_KEY" ]; then
        log_info "Triggering deployment via Render API..."
        
        # Deploy frontend
        FRONTEND_RESPONSE=$(curl -s -X POST \
            -H "Authorization: Bearer $RENDER_API_KEY" \
            -H "Content-Type: application/json" \
            -d "{\"clearCache\": true}" \
            "$RENDER_API_URL/services/$FRONTEND_SERVICE/deploys")
        
        if echo "$FRONTEND_RESPONSE" | grep -q "error"; then
            log_error "Frontend deployment failed"
            echo "$FRONTEND_RESPONSE"
        else
            log_success "Frontend deployment triggered"
        fi
        
        # Deploy backend
        BACKEND_RESPONSE=$(curl -s -X POST \
            -H "Authorization: Bearer $RENDER_API_KEY" \
            -H "Content-Type: application/json" \
            -d "{\"clearCache\": true}" \
            "$RENDER_API_URL/services/$BACKEND_SERVICE/deploys")
        
        if echo "$BACKEND_RESPONSE" | grep -q "error"; then
            log_error "Backend deployment failed"
            echo "$BACKEND_RESPONSE"
        else
            log_success "Backend deployment triggered"
        fi
    else
        log_info "Manual deployment required - push to main branch"
    fi
}

check_deployment_status() {
    log_info "Checking deployment status..."
    
    if [ ! -z "$RENDER_API_KEY" ]; then
        # Check frontend status
        FRONTEND_STATUS=$(curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
            "$RENDER_API_URL/services/$FRONTEND_SERVICE")
        
        # Check backend status
        BACKEND_STATUS=$(curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
            "$RENDER_API_URL/services/$BACKEND_SERVICE")
        
        log_info "Frontend status: $(echo $FRONTEND_STATUS | jq -r '.status' 2>/dev/null || echo 'Unknown')"
        log_info "Backend status: $(echo $BACKEND_STATUS | jq -r '.status' 2>/dev/null || echo 'Unknown')"
    else
        log_info "Check deployment status manually in Render dashboard"
    fi
}

run_health_checks() {
    log_info "Running health checks..."
    
    # Wait a bit for deployment to complete
    sleep 30
    
    # Check frontend health
    FRONTEND_URL="https://$FRONTEND_SERVICE.onrender.com"
    if curl -s -f "$FRONTEND_URL" > /dev/null; then
        log_success "Frontend health check passed: $FRONTEND_URL"
    else
        log_warning "Frontend health check failed: $FRONTEND_URL"
    fi
    
    # Check backend health
    BACKEND_URL="https://$BACKEND_SERVICE.onrender.com/api/v1/health"
    if curl -s -f "$BACKEND_URL" > /dev/null; then
        log_success "Backend health check passed: $BACKEND_URL"
    else
        log_warning "Backend health check failed: $BACKEND_URL"
    fi
}

cleanup() {
    log_info "Cleaning up temporary files..."
    # Add any cleanup tasks here
    log_success "Cleanup completed"
}

show_deployment_info() {
    log_success "Deployment completed!"
    echo
    echo "🌐 Frontend URL: https://$FRONTEND_SERVICE.onrender.com"
    echo "🔧 Backend API: https://$BACKEND_SERVICE.onrender.com"
    echo "📊 Health Check: https://$BACKEND_SERVICE.onrender.com/api/v1/health"
    echo "📚 Function Library: https://$FRONTEND_SERVICE.onrender.com/function-library"
    echo
    echo "📋 Render Dashboard: https://dashboard.render.com/"
    echo
}

# Main deployment process
main() {
    log_info "Starting deployment process for $PROJECT_NAME"
    
    # Pre-deployment checks
    check_dependencies
    check_render_api_key
    validate_git_status
    
    # Build and prepare
    build_frontend
    prepare_backend
    
    # Deploy
    deploy_to_render
    
    # Post-deployment
    check_deployment_status
    run_health_checks
    cleanup
    show_deployment_info
    
    log_success "Deployment process completed!"
}

# Handle script arguments
case "${1:-}" in
    "check")
        check_dependencies
        check_render_api_key
        validate_git_status
        ;;
    "build")
        build_frontend
        prepare_backend
        ;;
    "deploy")
        deploy_to_render
        ;;
    "status")
        check_deployment_status
        ;;
    "health")
        run_health_checks
        ;;
    *)
        main
        ;;
esac
