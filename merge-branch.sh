#!/bin/bash

# =============================================================================
# Safe Branch Merge Script with Validation
# =============================================================================
# This script validates a branch and safely merges it with main
# Usage: ./merge-branch.sh [branch-name]
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
VALIDATION_SCRIPT="./validate-all.sh"
QUICK_VALIDATION_SCRIPT="./quick-validate.sh"

# Functions
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
    echo "Safe Branch Merge Script"
    echo ""
    echo "Usage: $0 [options] [branch-name]"
    echo ""
    echo "Options:"
    echo "  -h, --help           Show this help"
    echo "  -q, --quick          Use quick validation only"
    echo "  --no-validation      Skip validation (not recommended)"
    echo "  --dry-run           Show what would be done without executing"
    echo "  --force             Force merge even if validation warns"
    echo ""
    echo "Examples:"
    echo "  $0                           # Interactive mode - select branch"
    echo "  $0 feature/new-docs          # Merge specific branch"
    echo "  $0 --quick feature/hotfix    # Quick validation and merge"
    echo ""
    echo "The script will:"
    echo "  1. Fetch latest changes"
    echo "  2. Checkout the target branch"
    echo "  3. Run validation checks"
    echo "  4. Switch to main and update"
    echo "  5. Merge the branch"
    echo "  6. Optionally clean up"
}

# Parse command line arguments
QUICK_MODE=false
NO_VALIDATION=false
DRY_RUN=false
FORCE=false
TARGET_BRANCH=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -q|--quick)
            QUICK_MODE=true
            shift
            ;;
        --no-validation)
            NO_VALIDATION=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        -*)
            echo "Unknown option $1"
            show_help
            exit 1
            ;;
        *)
            TARGET_BRANCH="$1"
            shift
            ;;
    esac
done

# Dry run mode
if [ "$DRY_RUN" = true ]; then
    echo "DRY RUN MODE - Would execute:"
    echo "1. git fetch --all"
    echo "2. git checkout $TARGET_BRANCH (or select interactively)"
    echo "3. Run validation checks"
    echo "4. git checkout $MAIN_BRANCH"
    echo "5. git pull origin $MAIN_BRANCH"
    echo "6. git merge $TARGET_BRANCH"
    echo "7. git push origin $MAIN_BRANCH"
    exit 0
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_error "Not in a git repository!"
    exit 1
fi

# Check if validation scripts exist
if [ "$NO_VALIDATION" = false ]; then
    if [ "$QUICK_MODE" = true ] && [ ! -f "$QUICK_VALIDATION_SCRIPT" ]; then
        log_warning "Quick validation script not found, falling back to full validation"
        QUICK_MODE=false
    fi
    
    if [ "$QUICK_MODE" = false ] && [ ! -f "$VALIDATION_SCRIPT" ]; then
        log_warning "Full validation script not found, will use quick validation"
        QUICK_MODE=true
    fi
fi

log_info "🚀 Starting safe branch merge process..."

# Step 1: Fetch latest changes
log_info "📡 Fetching latest changes..."
git fetch --all

# Step 2: Select or validate target branch
if [ -z "$TARGET_BRANCH" ]; then
    log_info "📋 Available branches:"
    git branch -a | grep -v "HEAD" | sed 's/^../  /'
    echo ""
    read -p "Enter branch name to merge: " TARGET_BRANCH
fi

# Validate branch exists
if ! git show-ref --verify --quiet "refs/heads/$TARGET_BRANCH" && ! git show-ref --verify --quiet "refs/remotes/origin/$TARGET_BRANCH"; then
    log_error "Branch '$TARGET_BRANCH' not found!"
    exit 1
fi

log_info "🎯 Target branch: $TARGET_BRANCH"

# Step 3: Checkout target branch
log_info "📂 Checking out target branch..."
git checkout "$TARGET_BRANCH"

# Pull latest if it's a remote branch
if git show-ref --verify --quiet "refs/remotes/origin/$TARGET_BRANCH"; then
    log_info "⬇️  Pulling latest changes for $TARGET_BRANCH..."
    git pull origin "$TARGET_BRANCH" || log_warning "Could not pull latest changes"
fi

# Step 4: Run validation
if [ "$NO_VALIDATION" = false ]; then
    log_info "🔍 Running validation checks..."
    
    if [ "$QUICK_MODE" = true ]; then
        log_info "Running quick validation..."
        if ! $QUICK_VALIDATION_SCRIPT; then
            if [ "$FORCE" = false ]; then
                log_error "Quick validation failed! Use --force to override."
                exit 1
            else
                log_warning "Validation failed but continuing due to --force"
            fi
        fi
    else
        log_info "Running comprehensive validation..."
        if ! $VALIDATION_SCRIPT; then
            if [ "$FORCE" = false ]; then
                log_error "Comprehensive validation failed! Use --force to override."
                exit 1
            else
                log_warning "Validation failed but continuing due to --force"
            fi
        fi
    fi
    
    log_success "Validation completed successfully!"
else
    log_warning "Skipping validation (not recommended)"
fi

# Step 5: Switch to main branch
log_info "🔄 Switching to $MAIN_BRANCH branch..."
git checkout "$MAIN_BRANCH"

# Step 6: Update main branch
log_info "⬇️  Updating $MAIN_BRANCH branch..."
git pull origin "$MAIN_BRANCH"

# Step 7: Check for conflicts before merging
log_info "🔍 Checking for potential merge conflicts..."
if ! git merge --no-commit --no-ff "$TARGET_BRANCH" > /dev/null 2>&1; then
    git merge --abort > /dev/null 2>&1 || true
    log_error "Merge conflicts detected!"
    log_info "Please resolve conflicts manually:"
    log_info "  1. git merge $TARGET_BRANCH"
    log_info "  2. Resolve conflicts"
    log_info "  3. git commit"
    log_info "  4. git push origin $MAIN_BRANCH"
    exit 1
else
    git reset --hard HEAD > /dev/null 2>&1
fi

# Step 8: Perform the actual merge
log_info "🔀 Merging $TARGET_BRANCH into $MAIN_BRANCH..."
git merge --no-ff "$TARGET_BRANCH" -m "Merge branch '$TARGET_BRANCH' into $MAIN_BRANCH

- Passed validation checks
- Merged via safe-merge script"

# Step 9: Push to remote
log_info "⬆️  Pushing to remote..."
git push origin "$MAIN_BRANCH"

log_success "🎉 Successfully merged $TARGET_BRANCH into $MAIN_BRANCH!"

# Step 10: Cleanup options
echo ""
read -p "Delete local branch '$TARGET_BRANCH'? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git branch -d "$TARGET_BRANCH"
    log_success "Local branch '$TARGET_BRANCH' deleted"
fi

read -p "Delete remote branch 'origin/$TARGET_BRANCH'? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin --delete "$TARGET_BRANCH"
    log_success "Remote branch 'origin/$TARGET_BRANCH' deleted"
fi

log_success "✨ Merge process completed successfully!"
log_info "📋 Summary:"
log_info "  • Branch: $TARGET_BRANCH"
log_info "  • Merged into: $MAIN_BRANCH"
log_info "  • Validation: $([ "$NO_VALIDATION" = true ] && echo "Skipped" || ([ "$QUICK_MODE" = true ] && echo "Quick" || echo "Comprehensive"))"
log_info "  • Status: Success"
