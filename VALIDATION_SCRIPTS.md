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

## Workflow Examples

### Quick Development Check
```bash
# Before committing changes
./quick-validate.sh
```

### Before Merging a Branch
```bash
# Full validation and merge
./merge-branch.sh feature/my-feature

# Or step by step
git checkout feature/my-feature
./validate-all.sh
./merge-branch.sh feature/my-feature
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

## Integration with Makefile

These scripts complement the existing Makefile targets:

```bash
# Manual validation using Make
make validate          # Full validation
make dev               # Development checks
make ci                # CI/CD checks

# Or use the scripts
./validate-all.sh      # Equivalent to make validate
./quick-validate.sh    # Quick essential checks
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

4. **Integrate with git hooks** (optional):
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
