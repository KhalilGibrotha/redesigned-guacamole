# Comprehensive CI/CD Pipeline with Documentation Publishing

A **comprehensive reusable GitHub Actions CI/CD pipeline** that provides automated code quality checks, security scanning, and documentation publishing to Confluence for any repository. Supports enterprise GitHub, forks, and handles GitHub Advanced Security licensing constraints gracefully.

## Detailed Execution Flow

1. **📊 Change Detection**: Analyzes which file types changed (docs, ansible, Python, workflows)
2. **🔍 Super Linter**: Runs intelligent linting with auto-fix capabilities (includes Ansible validation)
3. **🛡️ Security Scan**: Performs vulnerability scanning and secret detection with GitHub Advanced Security detection
4. **🚀 Documentation Publishing**: Publishes docs to Confluence (main/release/hotfix branches only)
5. **📊 Comprehensive Report**: Generates detailed execution summary
6. **🚨 Failure Notifications**: Creates GitHub issues for any failures

## 📚 **Documentation**

📖 **[Complete Documentation](docs/INDEX.md)** - Start here for guides, setup, and usage instructions

🚀 **[Workflow Guide](docs/WORKFLOW_GUIDE.md)** - Main guide for using this CI/CD system

## 📁 Repository Dependencies

### What Your Repository Needs to Provide

The CI/CD pipeline is designed to work with **minimal dependencies** from your repository. Here's what you need:

#### For Basic CI/CD (Always Required)

```text
your-repo/
├── .github/
│   └── workflows/
│       └── ci-cd.yml        # Your workflow that calls our pipeline
└── [your code files]        # Python, YAML, Ansible, etc.
```text

#### For Documentation Publishing (Optional)
```text
your-repo/
└── docs/
    ├── vars.yaml            # Variables and Confluence hierarchy config
    ├── *.j2                 # Jinja2 template files with YAML headers
    ├── *.md                 # Markdown files with YAML headers
    └── images/              # Images referenced in your documentation
        ├── diagram.png
        └── screenshot.jpg
```text

### What We Automatically Provide

**No need to copy these to your repository** - our pipeline automatically handles:

```text
redesigned-guacamole/
├── scripts/
│   ├── confluence_publisher.py     # ✅ Documentation publishing script
│   └── generate_sarif_summary.py   # ✅ Embedded in workflow
├── docs/
│   ├── macros.j2                   # ✅ Jinja2 macros for templates
│   └── macros/                     # ✅ Additional macro files
├── .github/workflows/
│   ├── ci-optimized.yml            # ✅ Main CI/CD pipeline
│   ├── publish-docs.yml            # ✅ Documentation publishing
│   └── notifications.yml           # ✅ Failure notifications
└── requirements.txt                # ✅ Python dependencies
```text

### Documentation Template Example

Your `.j2` files should follow this structure:

```jinja2
---
# Metadata for Confluence Publishing
varsFile: "vars/aap.yml"
project_status: "In Review"

# Confluence Metadata
confluence:
  title: "My Document Title"
  space: "MYSPACE"
  category: "operations"  # Uses hierarchy from vars.yaml
  imageFolder: "docs/images"
---

{% import './docs/macros/macros.j2' as macros %}

# {{ organization_name }} Documentation

This document uses variables from vars.yaml like {{ organization_name }}
and macros provided by our pipeline.

{{ macros.info_box("This is an info box from our macro library") }}
```text

### Key Benefits

- ✅ **Zero Infrastructure Dependencies**: No need to copy our scripts or templates
- ✅ **Automatic Updates**: Pipeline improvements benefit all repositories immediately
- ✅ **Minimal Setup**: Only need your content and configuration
- ✅ **Centralized Maintenance**: All pipeline logic maintained in one place

[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/license/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Confluence](https://img.shields.io/badge/Confluence-172B4D?logo=atlassian&logoColor=white)](https://www.atlassian.com/software/confluence)

## 🎯 Purpose

This repository provides **reusable workflows** that any other repository can call to:
- 📊 **Intelligent Code Analysis**: Dynamic Super Linter with auto-fix capabilities
- 🛡️ **Enterprise Security Scanning**: DevSkim, Trivy vulnerability scanning, secret detection, and GitHub Advanced Security detection
- 🎭 **Ansible Validation**: Comprehensive Ansible syntax checking and linting (integrated with Super Linter)
- 📚 **Documentation Publishing**: Process and publish documentation to Confluence
- 🚨 **Failure Notifications**: Automatic GitHub issue creation for CI/CD failures
- 📊 **Comprehensive Reporting**: SARIF output and detailed execution summaries
- 🏢 **Enterprise Ready**: Supports GitHub Enterprise, licensing constraints, and fork management

## 🚀 Quick Start for Remote Repositories

### 1. Add CI/CD Pipeline to Your Repository

Create `.github/workflows/ci-cd.yml` in your repository:

```yaml
name: 🚀 CI/CD Pipeline

on:
  push:
    branches:
      - main
      - develop
      - 'feature/**'
      - 'release/**'
      - 'hotfix/**'
  pull_request:
    branches: [main, develop]
  workflow_dispatch:
    inputs:
      full_scan:
        description: 'Run full codebase scan'
        type: boolean
        default: true
      auto_fix:
        description: 'Enable automatic code fixing'
        type: boolean
        default: true

permissions:
  contents: write      # Required for auto-fix commits
  packages: read
  statuses: write
  security-events: write
  actions: read

jobs:
  ci-cd-pipeline:
    uses: YOUR_USERNAME/redesigned-guacamole/.github/workflows/ci-optimized.yml@main
    with:
      full_scan: ${{ inputs.full_scan || true }}
      auto_fix: ${{ inputs.auto_fix || true }}
      branch_name: ${{ github.ref_name }}
      # Optional: Specify custom repository name for forks
      # repository_name: 'my-forked-repo-name'
      # Optional: Specify branch/version of the source repository
      # source_branch: 'v2.0.0'  # Use a specific tag or branch
    secrets:
      CONFLUENCE_URL: ${{ secrets.CONFLUENCE_URL }}
      CONFLUENCE_USER: ${{ secrets.CONFLUENCE_USER }}
      CONFLUENCE_API_TOKEN: ${{ secrets.CONFLUENCE_API_TOKEN }}
```

#### For Forked Repositories

If you've forked this repository with a different name, specify your repository name:

```yaml
jobs:
  ci-cd-pipeline:
    uses: YOUR_USERNAME/your-forked-repo-name/.github/workflows/ci-optimized.yml@main
    with:
      full_scan: ${{ inputs.full_scan || true }}
      auto_fix: ${{ inputs.auto_fix || true }}
      branch_name: ${{ github.ref_name }}
      repository_name: 'your-forked-repo-name'  # Important for forks!
      source_branch: 'main'  # Or specify a version tag like 'v2.0.0'
    secrets:
      CONFLUENCE_URL: ${{ secrets.CONFLUENCE_URL }}
      CONFLUENCE_USER: ${{ secrets.CONFLUENCE_USER }}
      CONFLUENCE_API_TOKEN: ${{ secrets.CONFLUENCE_API_TOKEN }}
```

#### For Enterprise GitHub

No additional configuration needed! The workflow automatically handles enterprise GitHub authentication when you provide the secrets above.

#### Security Scanning with GitHub Advanced Security

The workflow automatically detects GitHub Advanced Security availability:

- ✅ **License Detection**: Checks if your organization has available GitHub Advanced Security licenses
- ✅ **Graceful Handling**: If you've reached the 40-seat limit, security scanning is skipped with informative messages
- ✅ **Alternative Guidance**: Provides manual security scanning options when automated scanning isn't available
- ✅ **No Workflow Failures**: Licensing constraints don't break your CI/CD pipeline

### 2. Set Up Repository Secrets

In your repository settings → Secrets and variables → Actions, add:

- `CONFLUENCE_URL`: Your Confluence base URL (e.g., `https://company.atlassian.net`)
- `CONFLUENCE_USER`: Your Confluence username/email
- `CONFLUENCE_API_TOKEN`: Your Confluence API token

### 3. Configure Your Repository Structure

The pipeline works with various project types and will automatically detect and validate:

```text
your-repo/
├── docs/                     # Documentation files (if any)
│   ├── *.md                 # Markdown files
│   ├── *.j2                 # Jinja2 templates
│   └── vars.yaml            # Template variables
├── playbooks/               # Ansible playbooks (if any)
├── roles/                   # Ansible roles (if any)
├── **/*.py                  # Python files
├── **/*.yml                 # YAML files
├── **/*.yaml                # YAML files
├── **/*.sh                  # Shell scripts
└── .github/
    └── workflows/
        └── ci-cd.yml        # Your CI/CD workflow
```text

## 🏢 Enterprise GitHub & Fork Support

### Enterprise GitHub Compatibility

This workflow is **fully compatible with GitHub Enterprise** environments:

✅ **Automatic Authentication**: Uses `GITHUB_TOKEN` for secure cross-repository access
✅ **Private Repository Support**: Handles private repositories within enterprise environments
✅ **Enterprise Security**: Follows enterprise GitHub security best practices
✅ **GitHub Advanced Security Integration**: Automatically detects and handles licensing constraints
✅ **No Additional Configuration**: Works out-of-the-box with standard enterprise setups

### GitHub Advanced Security Support

The workflow intelligently handles GitHub Advanced Security licensing:

- 🔍 **Automatic Detection**: Checks if Advanced Security is available for your repository
- 📊 **License Management**: Handles the 40-seat limit for organizations gracefully
- ⚠️ **Graceful Skipping**: Security scanning is skipped when licenses aren't available
- 📋 **Alternative Guidance**: Provides manual security scanning options
- ✅ **No Pipeline Failures**: Licensing constraints don't break your CI/CD

### Fork Support

If you've forked this repository with a different name, simply specify the `repository_name` parameter:

```yaml
jobs:
  ci-cd-pipeline:
    uses: your-org/your-forked-repo-name/.github/workflows/ci-optimized.yml@main
    with:
      repository_name: 'your-forked-repo-name'
      # ... other parameters
```

This ensures the workflow correctly locates scripts and configurations from your fork.

### Version/Branch Control

You can specify which version or branch of the source repository to use for scripts and configurations:

```yaml
with:
  source_branch: 'v2.0.0'    # Use a specific release tag
  # OR
  source_branch: 'develop'   # Use a specific branch
  # OR
  source_branch: 'main'      # Use main branch (default)
```

This is useful for:
- **Stable Releases**: Pin to a specific version tag for production
- **Testing**: Use develop branch for testing new features
- **Custom Forks**: Use your own branch with modifications

## � Troubleshooting

### Common Enterprise GitHub Issues

**Problem**: `fatal: could not read Username for 'https://github.com': terminal prompts not supported`
**Solution**: ✅ **Already Fixed!** This workflow includes proper authentication tokens for all enterprise GitHub environments.

**Problem**: `repository not found` when calling from forks
**Solution**: Add the `repository_name` parameter with your fork's name:

```yaml
with:
  repository_name: 'your-fork-name'
```

**Problem**: Secrets not being passed to the workflow
**Solution**: Ensure your calling workflow includes all required secrets:

```yaml
secrets:
  CONFLUENCE_URL: ${{ secrets.CONFLUENCE_URL }}
  CONFLUENCE_USER: ${{ secrets.CONFLUENCE_USER }}
  CONFLUENCE_API_TOKEN: ${{ secrets.CONFLUENCE_API_TOKEN }}
```

**Problem**: Security scanning fails due to GitHub Advanced Security licensing
**Solution**: ✅ **Already Fixed!** The workflow automatically detects licensing constraints and skips security scanning gracefully with informative messages.

**Problem**: Auto-fix commits not being created
**Solution**: Ensure your workflow has `contents: write` permission:

```yaml
permissions:
  contents: write  # Required for auto-fix commits
  packages: read
  statuses: write
  security-events: write
  actions: read
```

### Workflow Debugging

1. **Check GitHub Actions logs** for detailed error messages
2. **Verify repository permissions** (contents: write for auto-fix, security-events: write for security scanning)
3. **Confirm secret availability** in repository settings
4. **Test with dry-run mode** first: `dry_run: true`
5. **Check GitHub Advanced Security availability** if security scanning is being skipped

## �🔄 Workflow Execution Flow

Here's how the complete workflow executes:

```mermaid
graph TD
    A[Push/PR Event] --> B[test-workflow.yml]
    B --> C[ci-optimized.yml]
    C --> D[detect-changes]
    D --> E[super-linter]
    D --> F[security]
    E --> G[publish]
    F --> G
    G --> H[comprehensive-report]
    C --> I[notifications.yml]
    I --> J[GitHub Issue Creation]

    style A fill:#e1f5fe
    style C fill:#f3e5f5
    style G fill:#e8f5e8
    style I fill:#fff3e0
    style J fill:#ffebee
```text

## 📋 Available Workflows

### 1. Main CI/CD Pipeline (`ci-optimized.yml`)

**Purpose**: Complete CI/CD pipeline with code quality, security, and documentation publishing

**Triggers**: Called by remote repositories via `workflow_call`

**Inputs**:
- `full_scan` (boolean): Run full codebase scan vs. changed files only (default: true)
- `auto_fix` (boolean): Enable automatic code fixing and commits (default: true)
- `dry_run` (boolean): Run in dry-run mode for testing (default: false)
- `branch_name` (string): Branch name to checkout (default: current branch)
- `repository_name` (string): Name of the source repository for forks (default: 'redesigned-guacamole')
- `source_branch` (string): Branch or tag to use from the source repository (default: 'main')
- `target_repository` (string): Target repository for documentation publishing (optional)
- `target_environment` (string): Target environment for publishing (default: 'production')

**Secrets**:
- `CONFLUENCE_URL`: Confluence base URL (optional - enables dry-run if missing)
- `CONFLUENCE_USER`: Confluence username (optional - enables dry-run if missing)
- `CONFLUENCE_API_TOKEN`: Confluence API token (optional - enables dry-run if missing)

**Jobs**:
- `detect-changes`: Analyzes file changes for optimized execution
- `super-linter`: Intelligent linting with auto-fix capabilities (includes Ansible validation)
- `security`: DevSkim, Trivy, secret detection, and GitHub Advanced Security detection
- `publish`: Documentation publishing to Confluence (main/release/hotfix branches only)
- `execution-summary`: Detailed execution summary

### 2. Documentation Publishing (`publish-docs.yml`)

**Purpose**: Standalone documentation publishing workflow

**Inputs**:
- `dry_run` (boolean): Run without actual publishing (default: false)
- `target_environment` (string): Target environment (default: 'production')
- `repository_name` (string): Source repository name for configurations (default: 'redesigned-guacamole')
- `source_branch` (string): Branch or tag to use from source repository (default: 'main')

**Secrets**:
- `CONFLUENCE_URL`: Confluence base URL
- `CONFLUENCE_USER`: Confluence username
- `CONFLUENCE_API_TOKEN`: Confluence API token

### 3. Failure Notifications (`notifications.yml`)

**Purpose**: Automatically create GitHub issues when CI/CD pipeline fails

**Triggers**: Runs after "🚀 CI/CD Pipeline" workflow completion
- Only triggers on failure or non-success status
- Prevents duplicate issues for the same failure type
- Provides detailed troubleshooting information
```text

## 📝 File Format Examples

### Markdown File with Frontmatter

```markdown
---
confluence:
  space_key: "DOCS"
  title: "Getting Started Guide"
  parent_page_id: "789012"
---

# Getting Started

Welcome to our documentation...
```text

### Jinja2 Template

```jinja2
---
confluence:
  space_key: "DOCS"
  title: "{{ project_name }} Deployment Guide"
  parent_page_id: "345678"
---

# {{ project_name }} Deployment Guide

Environment: {{ environment }}
Version: {{ version }}

## Prerequisites

...
```text

## � Available Workflows

### 1. Main CI/CD Pipeline (`ci-optimized.yml`)

**Purpose**: Complete CI/CD pipeline with code quality, security, and documentation publishing

**Triggers**: Called by remote repositories via `workflow_call`

**Inputs**:
- `full_scan` (boolean): Run full codebase scan vs. changed files only (default: true)
- `auto_fix` (boolean): Enable automatic code fixing and commits (default: true)
- `dry_run` (boolean): Run in dry-run mode for testing (default: false)
- `branch_name` (string): Branch name to checkout (default: current branch)
- `repository_name` (string): Name of the source repository for forks (default: 'redesigned-guacamole')
- `source_branch` (string): Branch or tag to use from the source repository (default: 'main')
- `target_repository` (string): Target repository for documentation publishing (optional)
- `target_environment` (string): Target environment for publishing (default: 'production')

**Secrets**:
- `CONFLUENCE_URL`: Confluence base URL (optional - enables dry-run if missing)
- `CONFLUENCE_USER`: Confluence username (optional - enables dry-run if missing)
- `CONFLUENCE_API_TOKEN`: Confluence API token (optional - enables dry-run if missing)

**Jobs**:
- `detect-changes`: Analyzes file changes for optimized execution
- `super-linter`: Intelligent linting with auto-fix capabilities (includes Ansible validation)
- `security`: DevSkim, Trivy, secret detection, and GitHub Advanced Security detection
- `publish`: Documentation publishing to Confluence (main/release/hotfix branches only)
- `execution-summary`: Detailed execution summary

### 2. Documentation Publishing (`publish-docs.yml`)

**Purpose**: Standalone documentation publishing workflow

**Inputs**:
- `dry_run` (boolean): Run without actual publishing (default: false)
- `target_environment` (string): Target environment (default: 'production')
- `repository_name` (string): Source repository name for configurations (default: 'redesigned-guacamole')
- `source_branch` (string): Branch or tag to use from source repository (default: 'main')

**Secrets**:
- `CONFLUENCE_URL`: Confluence base URL
- `CONFLUENCE_USER`: Confluence username
- `CONFLUENCE_API_TOKEN`: Confluence API token

### 3. Failure Notifications (`notifications.yml`)

**Purpose**: Automatically create GitHub issues when CI/CD pipeline fails

**Triggers**: Runs after "🚀 CI/CD Pipeline" workflow completion
- Only triggers on failure or non-success status
- Prevents duplicate issues for the same failure type
- Provides detailed troubleshooting information

## 🛠️ Local Development

If you want to contribute to this repository or run components locally:

```bash
# Clone the repository
git clone https://github.com/KhalilGibrotha/redesigned-guacamole.git
cd redesigned-guacamole

# Install dependencies
pip install -r requirements.txt

# Test the documentation publisher locally
python scripts/confluence_publisher.py \
  --dry-run \
  --docs-dir docs \
  --vars-file docs/vars.yaml

# Run local linting
python -m py_compile scripts/*.py
yamllint .
# Note: ansible-lint is now handled by Super Linter in CI/CD
```text

## 📋 System Requirements

**Repository Requirements:**
- GitHub repository (public or private, including GitHub Enterprise)
- Standard file types: Python, YAML, Ansible, Markdown, Shell scripts, JSON

**For Documentation Publishing:**
- Confluence instance (Cloud or Server)
- API token with page creation permissions
- Documentation files with YAML frontmatter

**Permissions Required:**
- `contents: read` (minimum) / `contents: write` (for auto-fix)
- `security-events: write` (for security scanning)
- `actions: read` and `packages: read`

## 🎉 Key Features Summary

✅ **Zero Setup Overhead**: Works with any repository structure
✅ **Enterprise Ready**: GitHub Enterprise, forks, and licensing constraints supported
✅ **Intelligent Processing**: Only runs relevant checks based on changed files
✅ **Auto-Fix Capabilities**: Automatically fixes and commits code style issues
✅ **Security Aware**: Handles GitHub Advanced Security licensing gracefully
✅ **Documentation Pipeline**: Seamless Confluence integration
✅ **Comprehensive Reporting**: Detailed execution summaries and SARIF output
✅ **Failure Management**: Automatic GitHub issue creation for failures

## 📋 Support

- 📖 Check the [examples](docs/) in this repository
- 🐛 [Open an issue](https://github.com/KhalilGibrotha/redesigned-guacamole/issues) for bugs
- 💡 [Request features](https://github.com/KhalilGibrotha/redesigned-guacamole/discussions) via discussions
- 📚 Review workflow logs in GitHub Actions for detailed debugging

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Maintained by**: [Khalil Gibrotha](https://github.com/KhalilGibrotha)
**Created**: January 2025
**License**: MIT

**🚀 Ready to add comprehensive CI/CD to your repository? Start with the Quick Start guide above! 🎯**
