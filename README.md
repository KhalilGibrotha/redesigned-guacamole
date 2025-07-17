# � Comprehensive CI/CD Pipeline with Documentation Publishing

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Confluence](https://img.shields.io/badge/Confluence-172B4D?logo=atlassian&logoColor=white)](https://www.atlassian.com/software/confluence)

A **comprehensive reusable GitHub Actions CI/CD pipeline** that provides automated code quality checks, security scanning, and documentation publishing to Confluence for any repository.

## 🎯 Purpose

This repository provides **reusable workflows** that any other repository can call to:
- � **Intelligent Code Analysis**: Dynamic Super Linter with auto-fix capabilities
- 🛡️ **Security Scanning**: DevSkim, Trivy vulnerability scanning, and secret detection
- 🎭 **Ansible Validation**: Comprehensive Ansible syntax checking and linting
- � **Documentation Publishing**: Process and publish documentation to Confluence
- 🚨 **Failure Notifications**: Automatic GitHub issue creation for CI/CD failures
- 📊 **Comprehensive Reporting**: SARIF output and detailed execution summaries

## 🚀 Quick Start for Remote Repositories

### 1. Add CI/CD Pipeline to Your Repository

Create `.github/workflows/ci-cd.yml` in your repository:

```yaml
name: � CI/CD Pipeline

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

permissions:
  contents: read
  packages: read
  statuses: write
  security-events: write
  actions: read

jobs:
  ci-cd-pipeline:
    uses: KhalilGibrotha/redesigned-guacamole/.github/workflows/ci-optimized.yml@main
    with:
      full_scan: ${{ inputs.full_scan || true }}
      branch_name: ${{ github.ref_name }}
    secrets:
      CONFLUENCE_URL: ${{ secrets.CONFLUENCE_URL }}
      CONFLUENCE_USER: ${{ secrets.CONFLUENCE_USER }}
      CONFLUENCE_API_TOKEN: ${{ secrets.CONFLUENCE_API_TOKEN }}
```

### 2. Set Up Repository Secrets

In your repository settings → Secrets and variables → Actions, add:
- `CONFLUENCE_URL`: Your Confluence base URL (e.g., `https://company.atlassian.net`)
- `CONFLUENCE_USER`: Your Confluence username/email
- `CONFLUENCE_API_TOKEN`: Your Confluence API token

### 3. Configure Your Repository Structure

The pipeline works with various project types and will automatically detect and validate:

```
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
```

## 🔄 Workflow Execution Flow

Here's how the complete workflow executes:

```mermaid
graph TD
    A[Push/PR Event] --> B[test-workflow.yml]
    B --> C[ci-optimized.yml]
    C --> D[detect-changes]
    D --> E[super-linter]
    D --> F[security]
    D --> G[ansible-syntax-check]
    E --> H[publish]
    F --> H
    G --> H
    H --> I[comprehensive-report]
    C --> J[notifications.yml]
    J --> K[GitHub Issue Creation]
    
    style A fill:#e1f5fe
    style C fill:#f3e5f5
    style H fill:#e8f5e8
    style J fill:#fff3e0
    style K fill:#ffebee
```

### Detailed Execution Flow:

1. **� Change Detection**: Analyzes which file types changed (docs, ansible, python, workflows)
2. **🔍 Super Linter**: Runs intelligent linting with auto-fix capabilities
3. **🛡️ Security Scan**: Performs vulnerability scanning and secret detection
4. **🎭 Ansible Syntax Check**: Validates Ansible playbooks and roles (if present)
5. **🚀 Documentation Publishing**: Publishes docs to Confluence (main/release/hotfix branches only)
6. **📊 Comprehensive Report**: Generates detailed execution summary
7. **🚨 Failure Notifications**: Creates GitHub issues for any failures

## 📋 Available Workflows

### 1. Main CI/CD Pipeline (`ci-optimized.yml`)

**Purpose**: Complete CI/CD pipeline with code quality, security, and documentation publishing

**Triggers**: Called by remote repositories via `workflow_call`

**Inputs**:
- `full_scan` (boolean): Run full codebase scan vs. changed files only (default: true)
- `branch_name` (string): Branch name to checkout (default: '')

**Secrets**:
- `CONFLUENCE_URL`: Confluence base URL (optional)
- `CONFLUENCE_USER`: Confluence username (optional)
- `CONFLUENCE_API_TOKEN`: Confluence API token (optional)

**Jobs**:
- `detect-changes`: Analyzes file changes for optimized execution
- `super-linter`: Intelligent linting with auto-fix capabilities
- `security`: DevSkim, Trivy, and secret detection
- `ansible-syntax-check`: Ansible validation (if applicable)
- `publish`: Documentation publishing to Confluence
- `comprehensive-report`: Detailed execution summary

### 2. Documentation Publishing (`publish-docs.yml`)

**Purpose**: Standalone documentation publishing workflow

**Inputs**:
- `dry_run` (boolean): Run without actual publishing (default: false)
- `target_environment` (string): Target environment (default: 'production')

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
```

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
```

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
```

## 🔧 Available Workflows

### 1. Documentation Publishing (`publish-docs.yml`)

**Purpose**: Process and publish documentation to Confluence

**Inputs**:
- `dry_run` (boolean): Run without actual publishing (default: false)
- `target_environment` (string): Target environment (default: 'production')

**Secrets**:
- `CONFLUENCE_URL`: Confluence base URL
- `CONFLUENCE_USER`: Confluence username
- `CONFLUENCE_API_TOKEN`: Confluence API token

### 2. CI/CD Pipeline (`ci-optimized.yml`)

**Purpose**: Comprehensive CI/CD pipeline with linting, security, and documentation publishing

**Inputs**:
- `full_scan` (boolean): Run full codebase scan (default: true)
- `branch_name` (string): Branch to checkout

## 🛠️ Local Development

If you want to contribute to this repository or run components locally:

```bash
# Clone the repository
git clone https://github.com/KhalilGibrotha/redesigned-guacamole.git
cd redesigned-guacamole

# Install dependencies
pip install -r requirements.txt

# Test the documentation publisher locally
python scripts/confluence_publisher.py 
  --dry-run 
  --docs-dir docs 
  --vars-file docs/vars.yaml

# Run local linting
ansible-lint
yamllint .
```

## 📋 Requirements

## �� Support

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
