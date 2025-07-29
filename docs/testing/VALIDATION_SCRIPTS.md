# Validation and Merge Scripts

This directory contains automated scripts for validating and merging branches safely.

## Available Scripts

### 1. `validate-all.sh` - Comprehensive Validation
Runs all validation checks including:
- System compatibility checks
- Security validation
- File structure validation
- Code quality (YAML/Ansible linting)
- Syntax validation
- Template rendering tests
- Git status checks

```bash
# Run full validation
./validate-all.sh

# Show help
./validate-all.sh --help

# Dry run (show what would be checked)
./validate-all.sh --dry-run

# Quiet mode
./validate-all.sh --quiet
```

### 2. `quick-validate.sh` - Essential Checks Only
Runs only the most critical validation checks for quick feedback:
- Essential file existence
- YAML syntax validation
- Ansible syntax validation
- Template structure check
- Basic security check
- Git status

```bash
# Run quick validation
./quick-validate.sh
```

### 3. `merge-branch.sh` - Safe Branch Merge
Validates a branch and safely merges it with main:

```bash
# Interactive mode - select branch
./merge-branch.sh

# Merge specific branch
./merge-branch.sh feature/new-docs

# Quick validation and merge
./merge-branch.sh --quick feature/hotfix

# Force merge even with warnings
./merge-branch.sh --force problematic-branch

# Dry run mode
./merge-branch.sh --dry-run feature/test
```

### 4. `git-flow.sh` - Git Flow Helper
Manages Git Flow workflow with feature, release, and hotfix branches:

```bash
# Initialize Git Flow (creates develop branch)
./git-flow.sh init

# Feature development
./git-flow.sh feature start user-auth       # Create feature/user-auth
./git-flow.sh feature finish user-auth      # Merge to develop with validation

# Release management
./git-flow.sh release start v1.0            # Create release/v1.0
./git-flow.sh release finish v1.0           # Merge to main, tag, merge back to develop

# Hotfix management
./git-flow.sh hotfix start critical-bug     # Create hotfix/critical-bug
./git-flow.sh hotfix finish critical-bug    # Merge to main and develop

# Status and cleanup
./git-flow.sh status                         # Show Git Flow status
./git-flow.sh cleanup                        # Clean up merged branches
```

## Workflow Examples

### Git Flow Development Workflow
```bash
# 1. Start a new feature
./git-flow.sh feature start user-dashboard

# 2. Develop your feature (make commits)
# ... work on feature ...

# 3. Quick validation during development
./quick-validate.sh

# 4. Finish the feature (validates and merges to develop)
./git-flow.sh feature finish user-dashboard

# 5. When ready for release
./git-flow.sh release start v1.2.0

# 6. Finalize release and deploy to production
./git-flow.sh release finish v1.2.0
```

### Traditional Workflow (Manual Branch Management)
```bash
# Before committing changes
./quick-validate.sh

# Before merging a feature branch to develop
./merge-branch.sh feature/my-feature

# Before merging a release to main
./merge-branch.sh --to-main release/v1.0
```

### CI/CD Integration
```bash
# In your CI/CD pipeline
./validate-all.sh --quiet
if [ $? -eq 0 ]; then
    echo "Validation passed, ready for deployment"
else
    echo "Validation failed, blocking deployment"
    exit 1
fi
```

## Git Flow Integration

The project now follows Git Flow with two main branches:
- **`main`**: Production-ready code
- **`develop`**: Integration branch for features

### Branch Types and Merge Destinations

| Branch Type | Merge To | Use Case |
|-------------|----------|----------|
| `feature/*` | `develop` | New features and improvements |
| `release/*` | `main` | Release preparation |
| `hotfix/*`  | `main` | Emergency production fixes |

### Updated Merge Script Behavior

The `merge-branch.sh` script now automatically detects branch types:

```bash
# Feature branches automatically merge to develop
./merge-branch.sh feature/new-docs          # → merges to develop

# Release/hotfix branches automatically merge to main  
./merge-branch.sh release/v1.0              # → merges to main
./merge-branch.sh hotfix/critical-fix       # → merges to main

# Override automatic detection
./merge-branch.sh --to-main feature/special # → force merge to main
./merge-branch.sh --to-develop hotfix/test  # → force merge to develop
```

## Exit Codes

All scripts follow standard exit codes:
- `0`: Success
- `1`: Validation/merge failed
- `2`: Invalid arguments or missing dependencies

## Requirements

### For Full Validation (`validate-all.sh`)
- `make` (uses Makefile targets)
- `yamllint`
- `ansible-playbook`
- `ansible-lint` (optional)
- `pandoc` (optional, for template rendering)

### For Quick Validation (`quick-validate.sh`)
- `yamllint` (optional)
- `ansible-playbook` (optional)
- Basic shell tools (`find`, `grep`, `git`)

### For Branch Merge (`merge-branch.sh`)
- `git`
- One of the validation scripts
- Write access to the repository

### For Git Flow (`git-flow.sh`)
- `git`
- `git-flow` (installed and initialized)

## Troubleshooting

### Missing Tools
```bash
# Install tools using Makefile
make install-tools

# Or platform-specific
make install-ubuntu-apt-only    # Ubuntu/Debian
make install-rhel-dnf-only      # RHEL/CentOS/Fedora
```

### Validation Failures
1. Run with verbose output to see details
2. Check individual Makefile targets
3. Use `--force` flag to override warnings (not recommended)

### Merge Conflicts
The merge script will detect conflicts and provide instructions:
```bash
git merge feature/branch-name
# Resolve conflicts manually
git commit
git push origin main
```

## Best Practices

1. **Always validate before merging**:
   ```bash
   ./validate-all.sh && ./merge-branch.sh my-branch
   ```

2. **Use quick validation during development**:
   ```bash
   # Make changes
   ./quick-validate.sh
   # If OK, commit
   ```

3. **Use comprehensive validation before releases**:
   ```bash
   ./validate-all.sh
   ```

4. **Integrate with Git hooks** (optional):
   ```bash
   # In .git/hooks/pre-commit
   #!/bin/bash
   ./quick-validate.sh
   ```

## Customization

### Adding Custom Checks
Edit the scripts to add project-specific validations:

```bash
# In validate-all.sh, add to main() function
run_check "Custom check" "your-custom-command"
```

### Environment Variables
Set environment variables to customize behavior:

```bash
export VALIDATION_STRICT=true    # Fail on warnings
export SKIP_TEMPLATE_TESTS=true  # Skip template rendering
```

## Support

For issues or questions:
1. Check the script help: `./script-name.sh --help`
2. Run in dry-run mode to understand actions: `./script-name.sh --dry-run`
3. Check individual Makefile targets: `make help`
