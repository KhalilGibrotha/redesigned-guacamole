# GitHub Actions Super Linter Setup Guide

This guide explains how to use the centralized GitHub Actions Super Linter workflows across multiple repositories for consistent code quality enforcement.

## 🎯 Overview

The Super Linter implementation provides:

- **🔄 Reusable Workflows**: Single source of truth for linting configuration
- **🛡️ Comprehensive Coverage**: 15+ linters including Ansible, YAML, Markdown, Python, Bash, JSON, and security scanning
- **⚡ Performance Optimized**: Parallel execution, smart filtering, and change detection
- **🏢 Enterprise Ready**: SARIF reporting, security scanning, and audit trails
- **📊 Rich Reporting**: Detailed summaries, PR comments, and artifact uploads

## 🚀 Quick Setup for New Repositories

### Option 1: Use as Reusable Workflow (Recommended)

Create `.github/workflows/lint.yml` in your repository:

```yaml
---
name: 🔍 Code Quality & Linting

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  super-linter:
    uses: your-org/confluence-automation/.github/workflows/reusable-super-linter.yml@main
    with:
      validate_ansible: true
      validate_yaml: true
      validate_markdown: true
      validate_python: true
      validate_bash: true
      validate_json: true
      validate_secrets: true
```

### Option 2: Copy Full Workflow

```bash
# Copy the complete workflow
curl -O https://raw.githubusercontent.com/your-org/confluence-automation/main/.github/workflows/lint.yml

# Copy configuration files
curl -O https://raw.githubusercontent.com/your-org/confluence-automation/main/.markdownlint.json
curl -O https://raw.githubusercontent.com/your-org/confluence-automation/main/.github/super-linter.env
```

## 📋 Supported Linters

### Core DevOps & Infrastructure
- **Ansible**: Best practices, syntax, and security
- **YAML**: Syntax, formatting, and consistency
- **JSON**: Syntax validation and formatting
- **Dockerfile**: Security and best practices (Hadolint)
- **Shell Scripts**: Bash syntax and best practices (ShellCheck)

### Documentation & Content
- **Markdown**: Formatting, links, and structure (markdownlint)

### Programming Languages
- **Python**: Code formatting (Black), style (Flake8), imports (isort), and quality (Pylint)

### Security & Compliance
- **Secrets Detection**: Gitleaks for credential scanning
- **Security Patterns**: Custom security anti-pattern detection
- **File Permissions**: World-writable file detection

## ⚙️ Configuration Options

### Linter Toggles

```yaml
# In your workflow file
with:
  validate_ansible: true      # Enable/disable Ansible linting
  validate_yaml: true         # Enable/disable YAML linting
  validate_markdown: true     # Enable/disable Markdown linting
  validate_python: true       # Enable/disable Python linting
  validate_bash: true         # Enable/disable Bash linting
  validate_json: true         # Enable/disable JSON linting
  validate_secrets: true      # Enable/disable secrets detection
```

### Execution Options

```yaml
with:
  validate_all_codebase: false  # true = scan all files, false = only changed files
  default_branch: main           # Branch to compare changes against
  create_log_file: true          # Generate detailed log files
  output_format: tap             # Output format: tap, json, sarif
```

### Custom Configuration Files

Create these files in your repository root to customize linting behavior:

#### `.markdownlint.json` - Markdown Rules
```json
{
  "default": true,
  "MD013": {
    "line_length": 180,
    "code_blocks": false
  },
  "MD033": false,
  "MD041": false
}
```

#### `.yamllint` - YAML Rules
```yaml
extends: default
rules:
  line-length:
    max: 180
  truthy:
    allowed-values: ['true', 'false']
```

#### `.ansible-lint` - Ansible Rules
```yaml
skip_list:
  - yaml[line-length]
  - name[casing]
```

## 🔧 Advanced Usage

### Environment-Specific Configuration

```yaml
# Production repositories
with:
  validate_secrets: true
  validate_all_codebase: true
  output_format: sarif

# Development repositories  
with:
  validate_secrets: false
  validate_all_codebase: false
  output_format: tap
```

### Custom File Filtering

Add to `.github/super-linter.env`:

```bash
# Include only specific file types
FILTER_REGEX_INCLUDE: .*\.(yml|yaml|md|py|sh)$

# Exclude specific patterns
FILTER_REGEX_EXCLUDE: |
  .*node_modules.*
  .*\.git.*
  .*__pycache__.*
  build/.*
  dist/.*
```

### Performance Tuning

```yaml
# For large repositories
with:
  validate_all_codebase: false  # Only scan changed files
  
# In .github/super-linter.env
PARALLEL: true                  # Enable parallel execution
FAIL_FAST: false               # Continue on first failure
SLIM_IMAGE: true               # Use smaller Docker image
```

## 📊 Outputs and Reporting

### Workflow Outputs

The reusable workflow provides:

- **Summary Output**: Overall pass/fail status
- **Detailed Logs**: Per-linter results and error details
- **Artifacts**: Downloadable reports and logs
- **SARIF Files**: Security findings for GitHub Security tab

### PR Comments

Automatic comments on pull requests include:

- ✅/❌ Overall status
- 📊 Linter execution summary  
- 🔗 Links to detailed reports
- 📁 Artifact download links

### GitHub Security Integration

When `output_format: sarif` is used:

- Security findings appear in the Security tab
- Code scanning alerts are created
- Integration with GitHub Advanced Security features

## 🐛 Troubleshooting

### Common Issues

#### 1. "No files to lint" Error
**Cause**: File filtering is too restrictive
**Solution**: Check `FILTER_REGEX_INCLUDE` and `FILTER_REGEX_EXCLUDE` settings

#### 2. Ansible Lint Failures
**Cause**: Strict Ansible rules
**Solution**: Create `.ansible-lint` with appropriate skip rules:
```yaml
skip_list:
  - yaml[line-length]
  - name[casing]
  - risky-file-permissions
```

#### 3. Markdown Lint Failures
**Cause**: Strict markdown formatting rules
**Solution**: Adjust `.markdownlint.json`:
```json
{
  "MD013": false,
  "MD033": false
}
```

#### 4. Python Lint Conflicts
**Cause**: Conflicting Python linters (Black vs Flake8)
**Solution**: Configure in `pyproject.toml` or `setup.cfg`:
```toml
[tool.black]
line-length = 88
extend-ignore = ["E203", "W503"]
```

### Debug Mode

Enable verbose logging:

```yaml
# In .github/super-linter.env
LOG_LEVEL: DEBUG
OUTPUT_DETAILS: detailed
CREATE_LOG_FILE: true
```

### Local Testing

Test linting locally before pushing:

```bash
# Test specific linters
docker run --rm -v $(pwd):/tmp/lint ghcr.io/github/super-linter:slim-latest

# Test with custom config
docker run --rm -v $(pwd):/tmp/lint \
  -e VALIDATE_YAML=true \
  -e YAML_CONFIG_FILE=.yamllint \
  ghcr.io/github/super-linter:slim-latest
```

## 🔄 Migration from Makefile Linting

### Before (Makefile)
```bash
make lint-yaml
make lint-ansible
make security-check
```

### After (GitHub Actions)
```yaml
# Automatic on every push/PR
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

### Benefits of Migration

| Feature | Makefile | GitHub Actions | Improvement |
|---------|----------|----------------|-------------|
| **Automation** | Manual execution | Automatic on push/PR | No manual intervention |
| **Consistency** | Environment dependent | Consistent Docker environment | Reproducible results |
| **Reporting** | Terminal output only | Rich reports + PR comments | Better visibility |
| **Security** | Basic pattern matching | Advanced secret detection | Better security |
| **Performance** | Sequential execution | Parallel linting | Faster execution |
| **Maintenance** | Per-repo configuration | Centralized reusable workflow | Easier updates |

## 📈 Best Practices

### Repository Setup
1. **Start Gradually**: Enable core linters first (YAML, Markdown)
2. **Configure Incrementally**: Add language-specific linters as needed
3. **Document Exceptions**: Use `.markdownlint.json` and `.ansible-lint` for justified exceptions

### Team Adoption
1. **Train on Basics**: Ensure team understands linting concepts
2. **Provide Quick Fixes**: Document common fixes for frequent issues
3. **Iterate Configuration**: Adjust rules based on team feedback

### Maintenance
1. **Regular Updates**: Keep Super Linter version current
2. **Monitor Performance**: Track workflow execution times
3. **Review Rules**: Periodically review and update linting rules

## 🎯 Next Steps

1. **Implement in Current Repository**: Use the provided workflows
2. **Roll Out to Other Repositories**: Use reusable workflow pattern  
3. **Customize as Needed**: Adjust linting rules for specific projects
4. **Monitor and Iterate**: Track effectiveness and adjust configuration

---

**💡 Pro Tip**: Start with permissive settings and gradually tighten rules as your team adapts to the new linting standards!
