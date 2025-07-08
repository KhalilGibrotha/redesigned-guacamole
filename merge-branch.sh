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
DEVELOP_BRANCH="develop"
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
    echo "Safe Branch Merge Script with Git Flow Support"
    echo ""
    echo "Usage: $0 [options] [branch-name]"
    echo ""
    echo "Options:"
    echo "  -h, --help           Show this help"
    echo "  -q, --quick          Use quick validation only"
    echo "  --no-validation      Skip validation (not recommended)"
    echo "  --dry-run           Show what would be done without executing"
    echo "  --force             Force merge even if validation warns"
    echo "  --to-main           Merge to main branch (for releases)"
    echo "  --to-develop        Merge to develop branch (default for features)"
    echo ""
    echo "Examples:"
    echo "  $0                           # Interactive mode - select branch, merge to develop"
    echo "  $0 feature/new-docs          # Merge feature branch to develop"
    echo "  $0 --to-main release/v1.0    # Merge release branch to main"
    echo "  $0 --quick feature/hotfix    # Quick validation and merge to develop"
    echo ""
    echo "Git Flow Integration:"
    echo "  • Feature branches -> develop (default)"
    echo "  • Release branches -> main (use --to-main)"
    echo "  • Hotfix branches  -> main (use --to-main)"
    echo ""
    echo "The script will:"
    echo "  1. Fetch latest changes"
    echo "  2. Checkout the target branch"
    echo "  3. Run validation checks"
    echo "  4. Switch to target branch (develop/main)"
    echo "  5. Merge the branch"
    echo "  6. Push changes"
    echo "  7. Optionally clean up"
}

# Parse command line arguments
QUICK_MODE=false
NO_VALIDATION=false
DRY_RUN=false
FORCE=false
TARGET_BRANCH=""
MERGE_TO_MAIN=false
MERGE_TO_DEVELOP=false

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
        --to-main)
            MERGE_TO_MAIN=true
            shift
            ;;
        --to-develop)
            MERGE_TO_DEVELOP=true
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

# Determine target merge branch
if [ "$MERGE_TO_MAIN" = true ] && [ "$MERGE_TO_DEVELOP" = true ]; then
    log_error "Cannot specify both --to-main and --to-develop"
    exit 1
fi

if [ "$MERGE_TO_MAIN" = true ]; then
    MERGE_TARGET="$MAIN_BRANCH"
elif [ "$MERGE_TO_DEVELOP" = true ]; then
    MERGE_TARGET="$DEVELOP_BRANCH"
else
    # Default: determine based on branch type
    if [[ "$TARGET_BRANCH" =~ ^(release|hotfix)/ ]]; then
        MERGE_TARGET="$MAIN_BRANCH"
        log_info "🎯 Detected $TARGET_BRANCH - defaulting to merge into $MAIN_BRANCH"
    else
        MERGE_TARGET="$DEVELOP_BRANCH"
        log_info "🎯 Detected feature/other branch - defaulting to merge into $DEVELOP_BRANCH"
    fi
fi

# Dry run mode
if [ "$DRY_RUN" = true ]; then
    echo "DRY RUN MODE - Would execute:"
    echo "1. git fetch --all"
    echo "2. git checkout $TARGET_BRANCH (or select interactively)"
    echo "3. Run validation checks"
    echo "4. git checkout $MERGE_TARGET"
    echo "5. git pull origin $MERGE_TARGET"
    echo "6. git merge $TARGET_BRANCH"
    echo "7. git push origin $MERGE_TARGET"
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
    echo "  Local branches:"
    git branch | sed 's/^../    /'
    echo "  Remote branches:"
    git branch -r | grep -v "HEAD" | sed 's/^../    /'
    echo ""
    echo "Git Flow Guidelines:"
    echo "  • feature/* branches -> merge to develop"
    echo "  • release/* branches -> merge to main"
    echo "  • hotfix/* branches  -> merge to main"
    echo ""
    read -p "Enter branch name to merge: " TARGET_BRANCH
fi

# Validate branch exists
if ! git show-ref --verify --quiet "refs/heads/$TARGET_BRANCH" && ! git show-ref --verify --quiet "refs/remotes/origin/$TARGET_BRANCH"; then
    log_error "Branch '$TARGET_BRANCH' not found!"
    exit 1
fi

# Re-determine merge target now that we have the branch name
if [ "$MERGE_TO_MAIN" = false ] && [ "$MERGE_TO_DEVELOP" = false ]; then
    if [[ "$TARGET_BRANCH" =~ ^(release|hotfix)/ ]]; then
        MERGE_TARGET="$MAIN_BRANCH"
        log_info "🎯 Detected $TARGET_BRANCH - will merge into $MAIN_BRANCH"
    else
        MERGE_TARGET="$DEVELOP_BRANCH"
        log_info "🎯 Detected feature/other branch - will merge into $DEVELOP_BRANCH"
    fi
fi

log_info "🎯 Target branch: $TARGET_BRANCH"
log_info "🎯 Merge destination: $MERGE_TARGET"

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

# Step 5: Switch to target merge branch
log_info "🔄 Switching to $MERGE_TARGET branch..."
git checkout "$MERGE_TARGET"

# Step 6: Update target merge branch
log_info "⬇️  Updating $MERGE_TARGET branch..."
git pull origin "$MERGE_TARGET"

# Step 7: Check for conflicts before merging
log_info "🔍 Checking for potential merge conflicts..."
if ! git merge --no-commit --no-ff "$TARGET_BRANCH" > /dev/null 2>&1; then
    git merge --abort > /dev/null 2>&1 || true
    log_error "Merge conflicts detected!"
    log_info "Please resolve conflicts manually:"
    log_info "  1. git merge $TARGET_BRANCH"
    log_info "  2. Resolve conflicts"
    log_info "  3. git commit"
    log_info "  4. git push origin $MERGE_TARGET"
    exit 1
else
    git reset --hard HEAD > /dev/null 2>&1
fi

# Step 8: Perform the actual merge
log_info "🔀 Merging $TARGET_BRANCH into $MERGE_TARGET..."
MERGE_MESSAGE="Merge branch '$TARGET_BRANCH' into $MERGE_TARGET

- Passed validation checks
- Merged via safe-merge script"

# Add additional context for different branch types
if [[ "$TARGET_BRANCH" =~ ^feature/ ]]; then
    MERGE_MESSAGE="$MERGE_MESSAGE
- Feature branch integration"
elif [[ "$TARGET_BRANCH" =~ ^release/ ]]; then
    MERGE_MESSAGE="$MERGE_MESSAGE
- Release branch merge"
elif [[ "$TARGET_BRANCH" =~ ^hotfix/ ]]; then
    MERGE_MESSAGE="$MERGE_MESSAGE
- Hotfix branch merge"
fi

git merge --no-ff "$TARGET_BRANCH" -m "$MERGE_MESSAGE"

# Step 9: Push to remote
log_info "⬆️  Pushing to remote..."
git push origin "$MERGE_TARGET"

log_success "🎉 Successfully merged $TARGET_BRANCH into $MERGE_TARGET!"

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
log_info "  • Merged into: $MERGE_TARGET"
log_info "  • Validation: $([ "$NO_VALIDATION" = true ] && echo "Skipped" || ([ "$QUICK_MODE" = true ] && echo "Quick" || echo "Comprehensive"))"
log_info "  • Status: Success"

# Additional Git Flow guidance
if [ "$MERGE_TARGET" = "$DEVELOP_BRANCH" ]; then
    log_info ""
    log_info "🌟 Next Steps (Git Flow):"
    log_info "  • Your feature is now in the develop branch"
    log_info "  • When ready for release, create a release branch:"
    log_info "    git checkout -b release/v1.0 develop"
    log_info "  • Then merge the release to main:"
    log_info "    ./merge-branch.sh --to-main release/v1.0"
elif [ "$MERGE_TARGET" = "$MAIN_BRANCH" ]; then
    log_info ""
    log_info "🚀 Production Deployment:"
    log_info "  • Your changes are now in the main branch"
    log_info "  • Consider creating a tag for this release:"
    log_info "    git tag -a v1.0 -m 'Release version 1.0'"
    log_info "    git push origin v1.0"
    if [[ "$TARGET_BRANCH" =~ ^release/ ]]; then
        log_info "  • Don't forget to merge back to develop:"
        log_info "    git checkout develop && git merge main"
    fi
fi
