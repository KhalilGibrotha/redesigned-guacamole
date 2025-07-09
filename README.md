# Confluence Documentation Automation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ansible Lint](https://img.shields.io/badge/ansible--lint-passing-brightgreen)](https://ansible-lint.readthedocs.io/)
[![YAML Lint](https://img.shields.io/badge/yamllint-passing-brightgreen)](https://yamllint.readthedocs.io/)
[![Multi-Platform CI/CD](https://img.shields.io/badge/CI%2FCD-Multi--Platform-blue)](./ci-cd-templates/)

An enterprise-grade Ansible automation solution for generating and publishing documentation to Atlassian Confluence. This project includes comprehensive testing, linting, and quality assurance tools designed for Ansible Automation Platform (AAP) environments.

## Features

- 🚀 **Automated Documentation**: Convert Markdown templates to HTML and publish to Confluence
- 🤖 **GitHub Actions Ready**: Advanced CI/CD workflow for automatic publishing ✅
- 🔍 **Enterprise Linting**: Super Linter with 15+ languages, security scanning, and quality gates ✅
- 🔄 **Reusable Workflows**: Centralized linting that can be used across multiple repositories ✅
- 🛡️ **Security First**: Built-in security scanning and credential protection ✅
- 📝 **Template System**: Jinja2-based markdown templates with variable substitution ✅
- 🔧 **Multi-Platform CI/CD**: Ready-to-use configurations for GitLab, GitHub, Azure DevOps, Jenkins, Bitbucket, and TeamCity ⚠️ *Work in Progress*
- 📊 **Quality Gates**: Production-ready linting standards and validation ✅

> **Note**: Features marked with ⚠️ are work-in-progress and may require additional testing and customization.

## Quick Start

### Prerequisites

- Ansible 2.9+
- Python 3.8+
- Pandoc (for markdown conversion)
- Docker (optional, for Molecule testing - ⚠️ *experimental*)

### Installation

**Option 1: Quick Setup (Recommended)**
```bash
# Clone the repository
git clone https://github.com/KhalilGibrotha/confluence-automation.git
cd confluence-automation

# Run the interactive setup script
./setup.sh
```

**Option 2: Manual Setup**
```bash
# Clone the repository
git clone https://github.com/KhalilGibrotha/confluence-automation.git
cd confluence-automation

# Install dependencies
make install-tools

# Copy configuration template
cp vars/vars.yml.example vars/vars.yml

# Run validation
make validate
```

### Restricted Environment Installation

For environments with limited internet access or where PyPI is blocked:

**RHEL/CentOS/Fedora (DNF only):**
```bash
# Install only via system packages, no pip required
make install-rhel-dnf-only
```

**Ubuntu/Debian (APT only):**
```bash
# Install only via system packages, no pip required
make install-ubuntu-apt-only
```

These options install available tools through system package managers and provide guidance on what functionality is available without PyPI access.

### Basic Usage

1. **Configure your environment**:
   ```bash
   # Copy the example configuration
   cp vars/vars.yml.example vars/vars.yml
   
   # Edit with your actual Confluence details
   # SECURITY: Never commit real credentials!
   # Consider using ansible-vault: ansible-vault encrypt vars/vars.yml
   nano vars/vars.yml
   ```

2. **Create your documentation templates**:
   ```bash
   # Templates are in docs/ directory
   # Edit docs/main.md.j2 and other templates
   ```

3. **Run the automation**:
   ```bash
   # Test run (no actual publishing)
   ansible-playbook playbook.yml --check

   # Publish to Confluence
   ansible-playbook playbook.yml
   ```

## 📊 Project Status

### ✅ **Fully Tested & Production Ready**
- Core Ansible automation (playbook.yml)
- GitHub Actions workflows for Confluence publishing and code quality ✅
- Super Linter with 8+ languages (YAML, Ansible, Shell, Python, Markdown, JSON, Dockerfile, GitHub Actions) ✅
- Security scanning (Trivy, TruffleHog) and credential protection
- Cross-platform installation (RHEL, Ubuntu, macOS)
- Template processing and Confluence publishing
- Local development workflow with Makefile automation

### ⚠️ **Work in Progress (Experimental)**
- **Molecule Testing**: Configuration exists but requires additional validation
- **CI/CD Templates**: Provided as examples, need platform-specific testing
- **Advanced Quality Gates**: May require customization for your environment

### 🎯 **Recommended Usage**
For production use, rely on the ✅ tested features. The ⚠️ experimental features can be used as starting points but should be thoroughly tested in your environment before production deployment.

## Project Structure

```
confluence-automation/
├── .github/               # GitHub Actions workflows ✅
│   ├── workflows/        
│   │   ├── lint.yml     # Main linting workflow ✅
│   │   ├── reusable-super-linter.yml # Reusable linter workflow ✅
│   │   └── confluence-publish.yml    # Confluence publishing workflow ✅
│   └── super-linter.env # Super Linter configuration ✅
├── ci-cd-templates/         # Multi-platform CI/CD configurations
│   ├── github-actions.yml  # GitHub Actions basic workflow ⚠️
│   ├── github-actions-confluence.yml # GitHub Actions Confluence publisher ✅
│   ├── gitlab-ci.yml       # GitLab CI/CD pipeline ⚠️
│   ├── azure-pipelines.yml # Azure DevOps pipeline ⚠️
│   ├── Jenkinsfile         # Jenkins pipeline ⚠️
│   ├── bitbucket-pipelines.yml # Bitbucket Pipelines ⚠️
│   └── teamcity-config.txt # TeamCity configuration ⚠️
├── .yamllint               # YAML linting configuration ✅
├── .markdownlint.json      # Markdown linting configuration ✅
├── .pre-commit-config.yaml # Pre-commit hooks ✅
├── molecule/               # Molecule test scenarios ⚠️ WIP
│   ├── default/           # Basic functionality tests ⚠️
│   ├── playbook-test/     # Full playbook testing ⚠️
│   └── syntax-check/      # Syntax validation ⚠️
├── docs/                  # Documentation and guides
│   ├── main.md.j2        # Main page template
│   ├── platform_governance.md.j2
│   ├── platform_runbook.md.j2
│   ├── operator_runbook.md.j2
│   ├── training_enablement.md.j2
│   ├── GITHUB_ACTIONS_ASSESSMENT.md ✅ # GitHub Actions vs Ansible analysis
│   ├── GITHUB_ACTIONS_SETUP.md ✅      # Complete GitHub Actions setup guide
│   └── GITHUB_ACTIONS_LINTING.md ✅    # Super Linter implementation guide
├── playbooks/             # Modular Ansible playbooks ✅
│   ├── main.yml          # Main orchestrator playbook
│   ├── 01-validate-environment.yml
│   ├── 02-convert-templates.yml  
│   ├── 03-convert-html.yml
│   ├── 04-publish-confluence.yml
│   ├── cleanup.yml
│   └── README.md         # Playbook usage guide
├── vars/                  # Variable definitions
│   ├── vars.yml          # Main variables (encrypted)
│   └── vars.yml.example  # Template for configuration
├── playbook.yml           # Legacy/wrapper playbook ✅
├── Makefile              # Automation commands ✅
└── README.md             # This file
```

## Development Workflow

### Daily Development
```bash
# Quick validation during development
make sanity-check

# Complete development validation
make dev

# Before committing
make validate
```

### Available Commands

| Command | Description |
|---------|-------------|
| `make install-tools` | Install all required tools via package managers and pip |
| `make install-rhel-dnf-only` | Install tools via DNF only (RHEL restricted environments) |
| `make install-ubuntu-apt-only` | Install tools via APT only (Ubuntu restricted environments) |
| `make sanity-check` | Quick development validation |
| `make security-check` | Security compliance verification |
| `make validate-templates` | Template structure validation |
| `make lint` | Run all linting checks |
| `make test` | Syntax check playbook |
| `make dev` | Complete development workflow |
| `make validate` | Full validation suite |
| `make ci` | CI/CD pipeline validation |

## Configuration

### Environment Variables
```yaml
# vars/vars.yml
project_name: "Your Project"
env: "Production"
confluence_url: "https://your-domain.atlassian.net/wiki"
confluence_space: "YOUR_SPACE"
confluence_auth: "base64_encoded_credentials"
```

### 🔐 Security Best Practices

⚠️ **CRITICAL: Never commit real credentials to version control!**

**Quick Secure Setup:**
```bash
# Use the secure setup script (recommended)
./secure-setup.sh
```

**Manual approaches:**

1. **Ansible Vault** (Recommended for local development):
   ```bash
   # Encrypt the entire vars file
   ansible-vault encrypt vars/vars.yml
   
   # Run playbook with vault password
   ansible-playbook playbook.yml --ask-vault-pass
   ```

2. **Environment Variables** (Ideal for CI/CD):
   ```yaml
   confluence_auth: "{{ lookup('env', 'CONFLUENCE_AUTH_TOKEN') }}"
   ```

3. **External Secret Management**:
   ```yaml
   # HashiCorp Vault, AWS Secrets Manager, etc.
   confluence_auth: "{{ lookup('vault', 'secret/confluence/auth') }}"
   ```

**The project includes:**
- 🔒 `secure-setup.sh` - Automated secure credential setup
- 🚫 `.gitignore` protection for `vars/vars.yml`
- 🔍 Automated secret detection in `make security-check`
- 📝 Example configuration in `vars/vars.yml.example`

## Testing

### Linting and Validation
```bash
# YAML syntax and formatting
make lint-yaml

# Ansible best practices
make lint-ansible

# Security scanning
make security-check
```

### Molecule Testing (Optional)
```bash
# Install with Docker support
pipx install molecule[docker]

# Run tests
molecule test
```

## CI/CD Integration

### 🔧 **Flexible Platform Support**

This project supports **all major CI/CD platforms** with ready-to-use configurations:

| Platform | Configuration File | Enterprise Ready |
|----------|-------------------|------------------|
| **GitLab CI/CD** | `ci-cd-templates/gitlab-ci.yml` | ✅ |
| **GitHub Actions** | `ci-cd-templates/github-actions.yml` | ✅ |
| **Azure DevOps** | `ci-cd-templates/azure-pipelines.yml` | ✅ |
| **Jenkins** | `ci-cd-templates/Jenkinsfile` | ✅ |
| **Bitbucket Pipelines** | `ci-cd-templates/bitbucket-pipelines.yml` | ✅ |
| **TeamCity** | `ci-cd-templates/teamcity-config.txt` | ✅ |

### 🚀 **Quick Setup**

```bash
# Choose your platform and copy the configuration
cp ci-cd-templates/gitlab-ci.yml .gitlab-ci.yml        # GitLab
cp ci-cd-templates/github-actions.yml .github/workflows/ci.yml  # GitHub
cp ci-cd-templates/azure-pipelines.yml azure-pipelines.yml     # Azure DevOps
cp ci-cd-templates/Jenkinsfile Jenkinsfile              # Jenkins
cp ci-cd-templates/bitbucket-pipelines.yml bitbucket-pipelines.yml  # Bitbucket
```

### 📋 **Standardized Pipeline Stages**

All configurations include these enterprise-grade stages:

1. **Validation** 🔍 - `make sanity-check`, `make lint`, `make validate-templates`
2. **Security** 🔒 - `make security-check` with secret detection
3. **Testing** 🧪 - `make validate`, `make test-render`
4. **Advanced Testing** 🔬 - `molecule test` (optional)

See [CI_CD_INTEGRATION_GUIDE.md](CI_CD_INTEGRATION_GUIDE.md) for detailed platform-specific setup instructions.

## Quality Standards

This project follows enterprise-grade quality standards:

- **Line Length**: 120 characters maximum
- **Indentation**: 2 spaces consistently
- **Boolean Values**: `true`/`false` only
- **Security**: Automated secret detection
- **Documentation**: Comprehensive inline comments

See [YAML_LINTING_STANDARDS.md](YAML_LINTING_STANDARDS.md) for complete guidelines.

## Documentation

- [Testing Setup Guide](TESTING_SETUP_GUIDE.md) - Complete testing documentation
- [YAML Linting Standards](YAML_LINTING_STANDARDS.md) - Enterprise linting guidelines
- [Molecule Testing Guide](MOLECULE_TESTING_GUIDE.md) - Advanced testing with Molecule
- [Current Testing Status](CURRENT_TESTING_STATUS.md) - Implementation status

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run validation (`make validate`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Pre-commit Setup
```bash
pip install pre-commit
pre-commit install
```

## Use Cases

- **Platform Documentation**: Automated runbooks and governance docs
- **API Documentation**: Service and integration documentation
- **Team Knowledge Base**: Centralized documentation management
- **Compliance Reporting**: Automated compliance documentation
- **Change Management**: Documentation updates with code changes

## Examples

### Template Variables
```yaml
# Available in all templates
{{ project_name }}        # Project name
{{ env }}                 # Environment (Dev/Test/Prod)
{{ database_url }}        # Database connection
{{ monitoring_tool }}     # Monitoring solution
{{ child_pages }}         # List of child pages
```

### Custom Templates
```markdown
# {{ project_name }} - {{ item.title }}

Environment: {{ env }}
Last Updated: {{ ansible_date_time.iso8601 }}

## Overview
This document covers {{ item.title | lower }} procedures.
```

## Troubleshooting

### Common Issues

**Linting Failures**
```bash
make fix  # Auto-fix common issues
yamllint -c .yamllint playbook.yml  # Check specific file
```

**Template Rendering**
```bash
make validate-templates  # Validate template syntax
ansible-playbook playbook.yml --check  # Test run
```

**Confluence Connection**
```bash
# Test API connectivity
curl -H "Authorization: Basic YOUR_AUTH" \
     "https://your-domain.atlassian.net/wiki/rest/api/content"
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 **Issues**: [GitHub Issues](https://github.com/KhalilGibrotha/confluence-automation/issues)
- 📖 **Documentation**: See docs/ directory
- 💬 **Discussions**: [GitHub Discussions](https://github.com/KhalilGibrotha/confluence-automation/discussions)

## Roadmap

- [ ] Advanced Molecule testing scenarios
- [ ] Multi-space Confluence support
- [ ] Template library expansion
- [ ] Integration with external CMDBs
- [ ] Advanced security scanning
- [ ] Performance optimization

## Acknowledgments

- Built for enterprise Ansible Automation Platform environments
- Follows Red Hat Ansible best practices
- Implements industry-standard quality gates
- Designed for scalable team collaboration

---

**Maintained by**: [Khalil Gibrotha](https://github.com/KhalilGibrotha)  
**Created**: January 2025  
**License**: MIT

## 🚀 Deployment Options

### Option 1: GitHub Actions (Recommended for Production)

The project includes a comprehensive GitHub Actions workflow that automates the entire publishing process with enterprise-grade features:

**✅ Advantages:**
- 🤖 **Automatic Publishing**: Triggers on every commit to main
- 🔐 **Enterprise Security**: GitHub secrets management, no credential exposure  
- 📊 **Full Audit Trail**: Complete history of all publishing activities
- 🚀 **Zero Infrastructure**: No Ansible control nodes required
- 🔄 **Advanced Features**: Change detection, dry runs, environment-specific deployments
- 📈 **Better Performance**: Parallel processing, smart caching, faster execution

**Quick Setup:**
```bash
# 1. Copy the workflow
mkdir -p .github/workflows
cp ci-cd-templates/github-actions-confluence.yml .github/workflows/confluence-publish.yml

# 2. Configure secrets in GitHub repository settings:
#    - CONFLUENCE_URL
#    - CONFLUENCE_USERNAME  
#    - CONFLUENCE_API_TOKEN
#    - CONFLUENCE_SPACE

# 3. Commit and push - automatic publishing begins!
git add .github/workflows/confluence-publish.yml
git commit -m "Add GitHub Actions Confluence publishing"
git push origin main
```

📚 **Complete Setup Guide**: [docs/GITHUB_ACTIONS_SETUP.md](docs/GITHUB_ACTIONS_SETUP.md)

### Option 2: Local Ansible (Recommended for Development)

Perfect for local development, testing, and environments where GitHub Actions cannot be used:

**✅ Advantages:**
- 🛠️ **Local Testing**: Test changes before committing
- 🔧 **Full Control**: Complete control over execution environment
- 🏢 **Corporate Networks**: Works in air-gapped or restricted environments
- 📦 **No Dependencies**: Just Ansible and standard tools

**Usage:**
```bash
# Development workflow
make run-validate    # Validate environment and templates
make run-templates   # Convert templates to markdown  
make run-html        # Convert markdown to HTML
make run-publish     # Publish to Confluence
make run-cleanup     # Clean up temporary files

# Or run everything at once
make run-full        # Complete end-to-end workflow
```

### Hybrid Approach (Best of Both Worlds)

Use both methods for maximum flexibility:

- **Development**: Local Ansible for testing and iteration
- **Production**: GitHub Actions for reliable, automatic publishing
- **Fallback**: Ansible available if GitHub Actions has issues

```bash
# Local development and testing
make run-full

# Commit changes - GitHub Actions handles production publishing automatically
git add . && git commit -m "Update documentation" && git push
```

**🎯 Assessment**: [GitHub Actions can handle ~90% of the workflow](docs/GITHUB_ACTIONS_ASSESSMENT.md) with significant improvements in reliability, security, and automation.

## 🔍 Code Quality & Linting

The project includes a comprehensive GitHub Actions-based linting solution using Super Linter that can be reused across multiple repositories.

### 🎯 Enterprise Linting Features

- **15+ Linters**: Ansible, YAML, Markdown, Python, Bash, JSON, Dockerfile, and more
- **Security Scanning**: Gitleaks secret detection and security pattern analysis
- **Reusable Workflows**: Single source of truth for linting across repositories
- **Smart Execution**: Only lints changed files for faster feedback
- **Rich Reporting**: PR comments, artifacts, SARIF integration, and detailed summaries

### 🚀 Quick Setup for Other Repositories

**Option 1: Reusable Workflow (Recommended)**
```yaml
# .github/workflows/lint.yml
name: 🔍 Code Quality & Linting
on: [push, pull_request]

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

**Option 2: Copy Complete Workflow**
```bash
# Copy to any repository
cp .github/workflows/lint.yml /path/to/other/repo/.github/workflows/
cp .markdownlint.json /path/to/other/repo/
cp .github/super-linter.env /path/to/other/repo/.github/
```

### 📊 Supported Linters

| Category | Linters | Purpose |
|----------|---------|---------|
| **DevOps** | Ansible, YAML, JSON, Dockerfile | Infrastructure as Code |
| **Documentation** | Markdown | Content quality |
| **Scripts** | Bash, ShellCheck | Shell script quality |
| **Python** | Black, Flake8, isort, Pylint | Code formatting & quality |
| **Security** | Gitleaks, Custom patterns | Secret detection |

### 🔧 Local vs GitHub Actions Linting

| Feature | Local (Makefile) | GitHub Actions | Recommendation |
|---------|------------------|----------------|----------------|
| **Development** | `make lint` | Automatic on PR | Use both |
| **Consistency** | Environment dependent | Consistent Docker | GitHub Actions |
| **Speed** | Faster (local) | Parallel processing | Context dependent |
| **Reporting** | Terminal only | Rich PR comments | GitHub Actions |
| **Security** | Basic | Advanced scanning | GitHub Actions |

📚 **Complete Guide**: [docs/GITHUB_ACTIONS_LINTING.md](docs/GITHUB_ACTIONS_LINTING.md)
