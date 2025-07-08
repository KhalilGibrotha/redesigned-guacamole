#!/bin/bash

# =============================================================================
# Git Flow Helper Script
# =============================================================================
# This script helps manage Git Flow workflow with feature, release, and hotfix branches
# Usage: ./git-flow.sh [command] [options]
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
MAIN_BRANCH="main"
DEVELOP_BRANCH="develop"

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

show_help() {
    echo "Git Flow Helper Script"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  feature start <name>     Create and checkout a new feature branch"
    echo "  feature finish <name>    Merge feature branch to develop (with validation)"
    echo "  feature list             List all feature branches"
    echo ""
    echo "  release start <version>  Create a release branch from develop"
    echo "  release finish <version> Merge release to main and back to develop"
    echo "  release list             List all release branches"
    echo ""
    echo "  hotfix start <name>      Create a hotfix branch from main"
    echo "  hotfix finish <name>     Merge hotfix to main and develop"
    echo "  hotfix list              List all hotfix branches"
    echo ""
    echo "  init                     Initialize Git Flow (create develop branch)"
    echo "  status                   Show current Git Flow status"
    echo "  cleanup                  Clean up merged branches"
    echo ""
    echo "Examples:"
    echo "  $0 feature start user-auth       # Create feature/user-auth branch"
    echo "  $0 feature finish user-auth      # Merge feature to develop"
    echo "  $0 release start v1.0            # Create release/v1.0 branch"
    echo "  $0 release finish v1.0           # Merge release to main"
    echo "  $0 hotfix start critical-bug     # Create hotfix/critical-bug branch"
    echo ""
    echo "Git Flow Structure:"
    echo "  • main: Production-ready code"
    echo "  • develop: Integration branch for features"
    echo "  • feature/*: Feature development branches"
    echo "  • release/*: Release preparation branches"
    echo "  • hotfix/*: Emergency fixes for production"
}

# Check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not in a git repository!"
        exit 1
    fi
}

# Check if branch exists
branch_exists() {
    git show-ref --verify --quiet "refs/heads/$1" 2>/dev/null
}

# Check if remote branch exists
remote_branch_exists() {
    git show-ref --verify --quiet "refs/remotes/origin/$1" 2>/dev/null
}

# Feature branch operations
feature_start() {
    local feature_name="$1"
    if [ -z "$feature_name" ]; then
        log_error "Feature name required: $0 feature start <name>"
        exit 1
    fi
    
    local branch_name="feature/$feature_name"
    
    if branch_exists "$branch_name"; then
        log_error "Feature branch '$branch_name' already exists"
        exit 1
    fi
    
    log_info "🌟 Creating feature branch: $branch_name"
    git checkout "$DEVELOP_BRANCH"
    git pull origin "$DEVELOP_BRANCH"
    git checkout -b "$branch_name"
    git push -u origin "$branch_name"
    
    log_success "Feature branch '$branch_name' created and checked out"
    log_info "💡 When ready, use: $0 feature finish $feature_name"
}

feature_finish() {
    local feature_name="$1"
    if [ -z "$feature_name" ]; then
        log_error "Feature name required: $0 feature finish <name>"
        exit 1
    fi
    
    local branch_name="feature/$feature_name"
    
    if ! branch_exists "$branch_name"; then
        log_error "Feature branch '$branch_name' does not exist"
        exit 1
    fi
    
    log_info "🔀 Finishing feature: $branch_name"
    
    # Use the merge script with validation
    if [ -f "./merge-branch.sh" ]; then
        ./merge-branch.sh --to-develop "$branch_name"
    else
        log_warning "merge-branch.sh not found, using basic merge"
        git checkout "$DEVELOP_BRANCH"
        git pull origin "$DEVELOP_BRANCH"
        git merge --no-ff "$branch_name"
        git push origin "$DEVELOP_BRANCH"
    fi
    
    log_success "Feature '$feature_name' merged to develop"
}

feature_list() {
    log_info "📋 Feature branches:"
    git branch -a | grep "feature/" | sed 's/^../  /' || echo "  No feature branches found"
}

# Release branch operations
release_start() {
    local version="$1"
    if [ -z "$version" ]; then
        log_error "Version required: $0 release start <version>"
        exit 1
    fi
    
    local branch_name="release/$version"
    
    if branch_exists "$branch_name"; then
        log_error "Release branch '$branch_name' already exists"
        exit 1
    fi
    
    log_info "🚀 Creating release branch: $branch_name"
    git checkout "$DEVELOP_BRANCH"
    git pull origin "$DEVELOP_BRANCH"
    git checkout -b "$branch_name"
    git push -u origin "$branch_name"
    
    log_success "Release branch '$branch_name' created and checked out"
    log_info "💡 When ready, use: $0 release finish $version"
}

release_finish() {
    local version="$1"
    if [ -z "$version" ]; then
        log_error "Version required: $0 release finish <version>"
        exit 1
    fi
    
    local branch_name="release/$version"
    
    if ! branch_exists "$branch_name"; then
        log_error "Release branch '$branch_name' does not exist"
        exit 1
    fi
    
    log_info "🎯 Finishing release: $branch_name"
    
    # Merge to main
    if [ -f "./merge-branch.sh" ]; then
        ./merge-branch.sh --to-main "$branch_name"
    else
        log_warning "merge-branch.sh not found, using basic merge"
        git checkout "$MAIN_BRANCH"
        git pull origin "$MAIN_BRANCH"
        git merge --no-ff "$branch_name"
        git push origin "$MAIN_BRANCH"
    fi
    
    # Create tag
    git tag -a "$version" -m "Release $version"
    git push origin "$version"
    
    # Merge back to develop
    git checkout "$DEVELOP_BRANCH"
    git merge "$MAIN_BRANCH"
    git push origin "$DEVELOP_BRANCH"
    
    log_success "Release '$version' completed and tagged"
}

release_list() {
    log_info "📋 Release branches:"
    git branch -a | grep "release/" | sed 's/^../  /' || echo "  No release branches found"
}

# Hotfix branch operations
hotfix_start() {
    local hotfix_name="$1"
    if [ -z "$hotfix_name" ]; then
        log_error "Hotfix name required: $0 hotfix start <name>"
        exit 1
    fi
    
    local branch_name="hotfix/$hotfix_name"
    
    if branch_exists "$branch_name"; then
        log_error "Hotfix branch '$branch_name' already exists"
        exit 1
    fi
    
    log_info "🚨 Creating hotfix branch: $branch_name"
    git checkout "$MAIN_BRANCH"
    git pull origin "$MAIN_BRANCH"
    git checkout -b "$branch_name"
    git push -u origin "$branch_name"
    
    log_success "Hotfix branch '$branch_name' created and checked out"
    log_info "💡 When ready, use: $0 hotfix finish $hotfix_name"
}

hotfix_finish() {
    local hotfix_name="$1"
    if [ -z "$hotfix_name" ]; then
        log_error "Hotfix name required: $0 hotfix finish <name>"
        exit 1
    fi
    
    local branch_name="hotfix/$hotfix_name"
    
    if ! branch_exists "$branch_name"; then
        log_error "Hotfix branch '$branch_name' does not exist"
        exit 1
    fi
    
    log_info "🔧 Finishing hotfix: $branch_name"
    
    # Merge to main
    if [ -f "./merge-branch.sh" ]; then
        ./merge-branch.sh --to-main "$branch_name"
    else
        log_warning "merge-branch.sh not found, using basic merge"
        git checkout "$MAIN_BRANCH"
        git pull origin "$MAIN_BRANCH"
        git merge --no-ff "$branch_name"
        git push origin "$MAIN_BRANCH"
    fi
    
    # Merge to develop
    git checkout "$DEVELOP_BRANCH"
    git merge "$MAIN_BRANCH"
    git push origin "$DEVELOP_BRANCH"
    
    log_success "Hotfix '$hotfix_name' merged to main and develop"
}

hotfix_list() {
    log_info "📋 Hotfix branches:"
    git branch -a | grep "hotfix/" | sed 's/^../  /' || echo "  No hotfix branches found"
}

# Utility functions
git_flow_init() {
    log_info "🚀 Initializing Git Flow..."
    
    # Check if develop branch exists
    if ! branch_exists "$DEVELOP_BRANCH"; then
        log_info "Creating develop branch..."
        git checkout "$MAIN_BRANCH"
        git pull origin "$MAIN_BRANCH"
        git checkout -b "$DEVELOP_BRANCH"
        git push -u origin "$DEVELOP_BRANCH"
        log_success "Develop branch created"
    else
        log_info "Develop branch already exists"
    fi
    
    log_success "Git Flow initialized!"
}

git_flow_status() {
    log_info "📊 Git Flow Status:"
    echo ""
    
    echo "Current branch: $(git branch --show-current)"
    echo ""
    
    echo "Main branches:"
    if branch_exists "$MAIN_BRANCH"; then
        echo "  ✅ $MAIN_BRANCH"
    else
        echo "  ❌ $MAIN_BRANCH (missing)"
    fi
    
    if branch_exists "$DEVELOP_BRANCH"; then
        echo "  ✅ $DEVELOP_BRANCH"
    else
        echo "  ❌ $DEVELOP_BRANCH (missing)"
    fi
    
    echo ""
    feature_list
    echo ""
    release_list
    echo ""
    hotfix_list
}

cleanup_branches() {
    log_info "🧹 Cleaning up merged branches..."
    
    # Clean up local branches that have been merged to develop
    git checkout "$DEVELOP_BRANCH"
    git branch --merged | grep -E "feature/" | xargs -n 1 git branch -d 2>/dev/null || true
    
    # Clean up local branches that have been merged to main
    git checkout "$MAIN_BRANCH"
    git branch --merged | grep -E "(release|hotfix)/" | xargs -n 1 git branch -d 2>/dev/null || true
    
    log_success "Cleanup completed"
}

# Main script logic
check_git_repo

case "${1:-}" in
    feature)
        case "${2:-}" in
            start)
                feature_start "$3"
                ;;
            finish)
                feature_finish "$3"
                ;;
            list)
                feature_list
                ;;
            *)
                echo "Usage: $0 feature {start|finish|list} [name]"
                exit 1
                ;;
        esac
        ;;
    release)
        case "${2:-}" in
            start)
                release_start "$3"
                ;;
            finish)
                release_finish "$3"
                ;;
            list)
                release_list
                ;;
            *)
                echo "Usage: $0 release {start|finish|list} [version]"
                exit 1
                ;;
        esac
        ;;
    hotfix)
        case "${2:-}" in
            start)
                hotfix_start "$3"
                ;;
            finish)
                hotfix_finish "$3"
                ;;
            list)
                hotfix_list
                ;;
            *)
                echo "Usage: $0 hotfix {start|finish|list} [name]"
                exit 1
                ;;
        esac
        ;;
    init)
        git_flow_init
        ;;
    status)
        git_flow_status
        ;;
    cleanup)
        cleanup_branches
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: ${1:-}"
        echo ""
        show_help
        exit 1
        ;;
esac
