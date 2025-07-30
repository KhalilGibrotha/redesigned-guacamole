# 🚀 Redesigned Guacamole: CI/CD Workflow Guide

## 📚 Overview

This repository provides a comprehensive, reusable CI/CD workflow system for code quality, linting, auto-fixing, and documentation publishing. The workflow can be used locally within this repository or called remotely from other repositories.

## 🎯 Key Features

- **🔍 Multi-Language Linting**: Supports Python, Shell, YAML, Markdown, JSON, and more
- **🤖 Auto-Fix Capabilities**: Automatically fixes common code quality issues
- **📄 Documentation Publishing**: Automated Confluence publishing with Jinja2 templates
- **🌐 Remote Usage**: Can be called from external repositories with full functionality
- **🛡️ Security Scanning**: Integrated security analysis and secret detection
- **📊 Comprehensive Reporting**: Detailed analysis and health scoring

## 📖 Quick Start Guides

### For Users of This Repository

If you're working directly in this repository:

```yaml
# Workflow runs automatically on push/PR
# Manual trigger also available in Actions tab
```

### For Remote Repository Usage

To use this workflow from another repository:

```yaml
# .github/workflows/ci.yml in your repository
name: CI/CD with Auto-fix
on: [push, pull_request]

permissions:
  contents: write  # Required for auto-fix commits
  packages: read
  statuses: write

jobs:
  ci-cd:
    uses: your-org/redesigned-guacamole/.github/workflows/ci-optimized.yml@develop
    with:
      auto_fix: true
      full_scan: false
    secrets:
      CONFLUENCE_URL: ${{ secrets.CONFLUENCE_URL }}
      CONFLUENCE_USER: ${{ secrets.CONFLUENCE_USER }}
      CONFLUENCE_API_TOKEN: ${{ secrets.CONFLUENCE_API_TOKEN }}
```

## 🔧 Workflow Configuration

### Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `auto_fix` | boolean | `true` | Enable automatic code fixes |
| `full_scan` | boolean | `false` | Run full scan regardless of changes |
| `dry_run` | boolean | `false` | Test mode (no actual publishing) |
| `branch_name` | string | `github.ref` | Override branch for checkout |

### Branch Triggers

The workflow automatically runs on:
- **Main branches**: `main`, `develop`
- **Feature branches**: `feature/*`, `ft/*`, `feature/**`, `ft/**`
- **Release branches**: `release/*`, `rel/*`, `release/**`, `rel/**`
- **Hotfix branches**: `hotfix/*`, `hf/*`, `hotfix/**`, `hf/**`

See [BRANCH_NAMING_GUIDE.md](BRANCH_NAMING_GUIDE.md) for complete details.

## 🛠️ Linting & Code Quality

### Supported Linters

| Tool | Purpose | Config File |
|------|---------|-------------|
| **Super Linter v5** | Multi-language linting | `.github/super-linter.env` |
| **Ansible Lint** | Ansible best practices | `.ansible-lint` |
| **ShellCheck** | Shell script analysis | `.shellcheckrc` |
| **EditorConfig Checker** | File formatting consistency | `.editorconfig-checker.json` |
| **GitLeaks** | Secret detection | `.gitleaks.toml` |
| **yamllint** | YAML formatting | `.yamllint` |
| **markdownlint** | Markdown consistency | `.markdownlint.json` |
| **flake8** | Python code analysis | `.flake8` |
| **pylint** | Python code quality | `.pylintrc` |

### Auto-Fix Capabilities

The workflow can automatically fix:

- **Python**: Code formatting (Black), import sorting (isort)
- **Shell**: Script formatting (shfmt)  
- **YAML**: Basic structure and whitespace
- **JSON**: Formatting and validation
- **Markdown**: Basic formatting and structure

### Configuration Files

All linter configuration files are automatically copied to remote repositories:

```bash
# Core configurations copied to calling repositories
.ansible-lint           # Ansible linting rules
.yamllint              # YAML formatting rules  
.markdownlint.json     # Markdown linting rules
.flake8                # Python linting rules
.pylintrc              # Python code analysis
.editorconfig-checker.json  # File formatting rules
.shellcheckrc          # Shell script rules
# ... and more
```

## 📄 Documentation System

### Template-Based Documentation

This repository uses a Jinja2-based documentation system:

- **Templates**: `.j2` files in `docs/` directory
- **Variables**: Defined in `vars/` directory  
- **Macros**: Reusable components in `docs/macros/`
- **Publishing**: Automated Confluence publishing

### Quick Template Example

```jinja2
---
varsFile: "vars/aap.yml"
project_status: "Active"
confluence:
  title: "{{ organization_name }} Operations Guide"
  space: "AH"
  category: "operations"
---

{% import 'docs/macros/macros.j2' as macros %}

# {{ organization_name }} Operations Guide

Our technologies: {{ macros.oxford_comma_list(aap_network_tech) }}
```

For complete documentation details, see [README.md](README.md).

## 🌐 Remote Usage Guide

### Setup for Remote Repositories

1. **Basic Setup** (Analysis only):
```yaml
jobs:
  lint:
    uses: your-org/redesigned-guacamole/.github/workflows/ci-optimized.yml@develop
```

2. **With Auto-fix Commits**:
```yaml
permissions:
  contents: write
jobs:
  lint:
    uses: your-org/redesigned-guacamole/.github/workflows/ci-optimized.yml@develop
    with:
      auto_fix: true
```

3. **With Confluence Publishing**:
```yaml
jobs:
  lint:
    uses: your-org/redesigned-guacamole/.github/workflows/ci-optimized.yml@develop
    secrets:
      CONFLUENCE_URL: ${{ secrets.CONFLUENCE_URL }}
      CONFLUENCE_USER: ${{ secrets.CONFLUENCE_USER }}
      CONFLUENCE_API_TOKEN: ${{ secrets.CONFLUENCE_API_TOKEN }}
```

### Troubleshooting Remote Usage

**Common Issues & Solutions:**

1. **Auto-fixes not committed**:
   - Add `contents: write` permission to calling workflow
   
2. **Confluence publishing fails**:
   - Ensure secrets are configured in calling repository
   - Or use `dry_run: true` for testing

3. **Missing dependencies**:
   - Workflow automatically installs required tools
   - No action needed from calling repository

For detailed troubleshooting, see [REMOTE_WORKFLOW_USAGE.md](REMOTE_WORKFLOW_USAGE.md).

## 🔍 Security & Compliance

### Security Features

- **Secret Detection**: GitLeaks scans for hardcoded secrets
- **Vulnerability Scanning**: Trivy security analysis
- **DevSkim Analysis**: Microsoft security patterns
- **Permission Validation**: File permission checks

### Compliance

- **Code Quality Standards**: Enforced via multiple linters
- **Documentation Standards**: Template-based consistency
- **Security Standards**: Automated security scanning
- **Audit Trail**: Complete workflow logging and reporting

## 📊 Monitoring & Reporting

### Workflow Outputs

The workflow provides:
- **Health Score**: Overall code quality rating (0-100)
- **Fix Count**: Number of issues automatically resolved
- **Issue Summary**: Detailed breakdown by tool/language
- **Security Report**: Security findings and recommendations

### GitHub Actions Integration

- **Status Checks**: Required checks for branch protection
- **Artifacts**: Downloadable reports and logs
- **Annotations**: Inline code comments for issues
- **Summary**: Rich markdown summaries in workflow results

## 🔄 Development Workflow

### Recommended Development Process

1. **Create Feature Branch**: 
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Develop & Test**: 
   - Workflow runs automatically on push
   - Auto-fixes applied automatically

3. **Review Results**:
   - Check workflow status in GitHub Actions
   - Review any remaining issues in workflow summary

4. **Merge**:
   - All checks pass automatically
   - Documentation publishes on main branches

### Local Development

For local testing:
```bash
# Run specific linters locally
yamllint docs/
markdownlint docs/
black --check scripts/
```

## 📚 Additional Documentation

- **[Branch Naming Guide](BRANCH_NAMING_GUIDE.md)**: Supported branch patterns
- **[Template Documentation](README.md)**: Complete Jinja2 template guide  
- **[Remote Usage Guide](REMOTE_WORKFLOW_USAGE.md)**: Detailed remote usage instructions
- **[Linter Reference](SUPER_LINTER_CONFIGURATION_REFERENCE.md)**: Complete linter documentation

## 🤝 Contributing

### Adding New Linters

1. Add configuration file to repository root
2. Update `.github/workflows/ci-optimized.yml` lint config copying section
3. Test with both local and remote usage
4. Update documentation

### Modifying Templates

1. Edit template files in `docs/`
2. Update variables in `vars/`
3. Test rendering locally
4. Commit changes - publishing happens automatically

### Reporting Issues

- **Workflow Issues**: Check Actions tab for detailed logs
- **Template Issues**: Test locally with Jinja2
- **Remote Usage Issues**: Verify permissions and secrets

## 📞 Support

For questions or issues:
1. Check the troubleshooting sections in this guide
2. Review workflow logs in GitHub Actions
3. Consult the specific documentation files linked above
4. Open an issue in this repository for workflow problems

---

**🚀 Ready to get started?** Check out the [Quick Start](#-quick-start-guides) section above for your use case!
