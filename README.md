# CI/CD Pipeline for Ansible Documentation

This repository hosts reusable GitHub Actions workflows and helper scripts for linting, security scanning and publishing documentation to Confluence. It is designed to be dropped into any Ansible project with minimal configuration.

## Key Features

- **Change detection** to run only the jobs affected by your commit
- **Super Linter** integration with Ansible and Python checks
- **Security scanning** for secrets and vulnerabilities
- **Documentation publishing** to Confluence
- **Failure notifications** that open a GitHub issue when the workflow fails

## Quick Start

1. Create `.github/workflows/ci-cd.yml` in your repository:

```yaml
name: CI/CD Pipeline
on:
  push:
    branches: [main, develop, 'feature/**', 'release/**', 'hotfix/**']
  pull_request:
    branches: [main, develop]
jobs:
  ci:
    uses: your-org/redesigned-guacamole/.github/workflows/ci-optimized.yml@main
    secrets:
      CONFLUENCE_URL: ${{ secrets.CONFLUENCE_URL }}
      CONFLUENCE_USER: ${{ secrets.CONFLUENCE_USER }}
      CONFLUENCE_API_TOKEN: ${{ secrets.CONFLUENCE_API_TOKEN }}
```

2. Add your Confluence credentials as repository secrets.
3. Place Markdown or Jinja2 documentation under `docs/` when you want to publish to Confluence.

## Workflows Overview

- **`ci-optimized.yml`** – main pipeline with linting, security checks and optional publishing
- **`publish-docs.yml`** – publish documentation without running tests
- **`notifications.yml`** – create an issue when another workflow fails

## Local Development

Install dependencies and run the publisher in dry-run mode:

```bash
pip install -r requirements.txt
python scripts/confluence_publisher.py --dry-run --docs-dir docs --vars-file docs/vars.yaml
```

## License

MIT © 2024 Khalil Gibrotha
