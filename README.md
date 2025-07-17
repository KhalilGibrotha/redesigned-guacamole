# 📚 Confluence Documentation Publisher

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Confluence](https://img.shields.io/badge/Confluence-172B4D?logo=atlassian&logoColor=white)](https://www.atlassian.com/software/confluence)

A **reusable GitHub Actions workflow** for automatically publishing documentation from any repository to Atlassian Confluence. Supports Markdown files and Jinja2 templates with YAML frontmatter configuration.

## 🎯 Purpose

This repository provides **reusable workflows** that any other repository can call to:
- 📝 Process documentation files (`.md` and `.j2`) with YAML frontmatter
- 🚀 Publish content to Confluence with proper page hierarchy
- 🔄 Support both dry-run testing and live publishing
- 🎨 Render Jinja2 templates with custom variables
- 📊 Generate comprehensive publishing reports

## 🚀 Quick Start for Calling Repositories

### 1. Add Workflow to Your Repository

Create `.github/workflows/publish-docs.yml` in your repository:

```yaml
name: 📚 Publish Documentation

on:
  push:
    branches: [main]
    paths: ['docs/**']
  workflow_dispatch:
    inputs:
      dry_run:
        description: 'Dry run (no actual publishing)'
        type: boolean
        default: true

jobs:
  publish:
    uses: KhalilGibrotha/redesigned-guacamole/.github/workflows/publish-docs.yml@main
    with:
      dry_run: ${{ inputs.dry_run || false }}
      target_environment: 'production'
    secrets:
      CONFLUENCE_URL: ${{ secrets.CONFLUENCE_URL }}
      CONFLUENCE_USER: ${{ secrets.CONFLUENCE_USER }}
      CONFLUENCE_API_TOKEN: ${{ secrets.CONFLUENCE_API_TOKEN }}
```

### 2. Configure Your Documentation

Create your documentation files in the `docs/` directory with YAML frontmatter:

```markdown
---
confluence:
  space_key: "DOCS"
  title: "My Documentation Page"
  parent_page_id: "123456"
---

# My Documentation

Your content here...
```

### 3. Set Up Repository Secrets

In your repository settings, add these secrets:
- `CONFLUENCE_URL`: Your Confluence base URL (e.g., `https://company.atlassian.net`)
- `CONFLUENCE_USER`: Your Confluence username/email
- `CONFLUENCE_API_TOKEN`: Your Confluence API token

### 4. Optional: Add Variables File

Create `docs/vars.yaml` for Jinja2 template substitution:

```yaml
---
project_name: "My Project"
environment: "Production"
version: "1.0.0"
```

## 📁 Documentation Structure

Your calling repository should structure documentation like this:

```
your-repo/
├── docs/
│   ├── vars.yaml                 # Variables for Jinja2 templates
│   ├── getting-started.md        # Simple Markdown file
│   ├── api-reference.j2          # Jinja2 template
│   └── admin/
│       └── deployment-guide.md   # Nested documentation
└── .github/
    └── workflows/
        └── publish-docs.yml       # Your workflow file
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

### 2. CI/CD Pipeline (`ci.yml`)

**Purpose**: Lint and validate your repository

**Inputs**:
- `full_scan` (boolean): Run full codebase scan (default: true)
- `branch_name` (string): Branch to checkout

## 🧪 Testing Your Setup

1. **Dry Run Test**: Use manual workflow dispatch with `dry_run: true`
2. **Check Logs**: Review the workflow output for processing details
3. **Validate**: Confirm your YAML frontmatter is correctly formatted

Example dry run output:
```
📤 Publishing 3 files to Confluence
🔍 Processing: docs/getting-started.md
  ✅ Title: Getting Started Guide
  ✅ Space: DOCS
  ✅ Content: 1,234 characters
🧪 DRY RUN: Would create/update page in Confluence
```

## 🔍 Features

### ✅ Supported File Types
- **Markdown (`.md`)**: Direct processing with frontmatter
- **Jinja2 Templates (`.j2`)**: Variable substitution + frontmatter

### ✅ Frontmatter Configuration
```yaml
confluence:
  space_key: "YOUR_SPACE"      # Required: Confluence space key
  title: "Page Title"          # Required: Page title
  parent_page_id: "123456"     # Optional: Parent page ID
```

### ✅ Template Variables
- Use `docs/vars.yaml` to define variables
- Reference in templates: `{{ variable_name }}`
- Supports complex data structures (lists, dictionaries)

### ✅ Publishing Modes
- **Dry Run**: Preview changes without publishing
- **Live Publishing**: Create/update pages in Confluence

## 🛠️ Local Development

If you want to contribute to this repository:

```bash
# Clone the repository
git clone https://github.com/KhalilGibrotha/redesigned-guacamole.git
cd redesigned-guacamole

# Install dependencies
pip install -r requirements.txt

# Test the Python script locally
python scripts/confluence_publisher.py \
  --dry-run \
  --docs-dir docs \
  --vars-file docs/vars.yaml
```

## 📋 Requirements

### For Calling Repositories:
- GitHub repository with documentation in `docs/` directory
- Confluence Cloud or Server instance
- Valid Confluence API credentials

### For This Repository:
- Python 3.11+
- Dependencies: `jinja2`, `pyyaml`, `requests`, `markdown`, `beautifulsoup4`

## 🤝 Contributing

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Test with the provided documentation examples
5. Submit a pull request

## 📚 Advanced Configuration

### Multiple Confluence Spaces

You can publish to different spaces by setting different `space_key` values in your frontmatter:

```yaml
---
confluence:
  space_key: "DEV"     # Development space
  title: "Dev Guide"
---
```

### Page Hierarchies

Create nested page structures using `parent_page_id`:

```yaml
---
confluence:
  space_key: "DOCS"
  title: "Child Page"
  parent_page_id: "123456"  # ID of parent page
---
```

### Template Variables

Use complex variables in your `docs/vars.yaml`:

```yaml
---
environments:
  - name: "Development"
    url: "https://dev.example.com"
  - name: "Production"
    url: "https://prod.example.com"

features:
  authentication: true
  monitoring: true
```

Reference in templates:

```jinja2
## Environments

{% for env in environments %}
- **{{ env.name }}**: {{ env.url }}
{% endfor %}

## Available Features

{% if features.authentication %}
- ✅ Authentication enabled
{% endif %}
```

## 📞 Support

- 📖 Check the [examples](docs/) in this repository
- 🐛 [Open an issue](https://github.com/KhalilGibrotha/redesigned-guacamole/issues) for bugs
- 💡 [Request features](https://github.com/KhalilGibrotha/redesigned-guacamole/discussions) via discussions

## � License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
docs/
├── automation_hub/              # 🎯 Primary documentation (auto-discovered)
│   ├── automation_hub.j2        # Main parent page
│   ├── platform_governance.j2   # Child pages (automatically discovered)
│   ├── platform_runbook.j2      # Add any .j2 file here and it's
│   ├── operator_runbook.j2       # automatically included! 
│   └── ...                      # No manual configuration needed!
scripts/
├── discover_docs_enhanced.py    # 🔍 Dynamic discovery engine
playbooks/
├── automation_hub_publishing.yml # 📤 Primary publishing workflow
vars/
├── vars.yml                     # 🔧 Your variables
└── aap.yml                      # 🤖 AAP-specific variables
```

## 🎯 Core Workflows

### **Primary Workflow**
```bash
make run-full                    # Complete automation ✅
```

### **Individual Steps**
```bash
make convert-templates-dynamic   # Discover and process templates
make convert-markdown           # Convert to HTML
make run-publish               # Publish to Confluence
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
- YAML and Ansible linting (yamllint, ansible-lint)
- Security scanning and credential protection
- Cross-platform installation (RHEL, Ubuntu, macOS)
- Template processing and Confluence publishing
- Local development workflow

### ⚠️ **Work in Progress (Experimental)**
- **Molecule Testing**: Configuration exists but requires additional validation
- **CI/CD Templates**: Provided as examples, need platform-specific testing
- **Advanced Quality Gates**: May require customization for your environment

### 🎯 **Recommended Usage**
For production use, rely on the ✅ tested features. The ⚠️ experimental features can be used as starting points but should be thoroughly tested in your environment before production deployment.

## Project Structure

```
confluence-automation/
├── ci-cd-templates/         # Multi-platform CI/CD configurations
│   ├── github-actions.yml  # GitHub Actions basic workflow ⚠️
│   ├── github-actions-confluence.yml # GitHub Actions Confluence publisher ✅
│   ├── gitlab-ci.yml       # GitLab CI/CD pipeline ⚠️
│   ├── azure-pipelines.yml # Azure DevOps pipeline ⚠️
│   ├── Jenkinsfile         # Jenkins pipeline ⚠️
│   ├── bitbucket-pipelines.yml # Bitbucket Pipelines ⚠️
│   └── teamcity-config.txt # TeamCity configuration ⚠️
├── .yamllint               # YAML linting configuration ✅
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
│   └── GITHUB_ACTIONS_SETUP.md ✅      # Complete GitHub Actions setup guide
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
make help                      # See all available commands
make check-deps               # Verify dependencies
make discover-enhanced        # View discovery results
make debug-conversion         # Troubleshoot issues
```

## 🎯 Adding New Documentation

### **Zero-Maintenance Approach**
1. Create new `.j2` file in `docs/automation_hub/`
2. Run `make run-full`
3. **That's it!** New template is automatically discovered and published

### **Template Example**
```jinja2
{% from 'macros.j2' import page_header, auto_generated_notice %}
{{ page_header(title="My New Section") }}
{{ auto_generated_notice() }}

# My New Section

## Overview
This documentation for {{ project_name }} is automatically discovered and published.

## Environment Details
- Environment: {{ env }}
- Database: {{ database_url }}
- Monitoring: {{ monitoring_tool }}
```

## 📋 Available Commands

### **🔧 Development & Validation**
- `make lint` - Run all linting checks
- `make test` - Ansible syntax validation
- `make security-check` - Security validation
- `make validate-templates` - Template structure check

### **🛠️ Installation & Setup**
- `make install-tools` - Install required dependencies
- `make check-deps` - Check what's installed
- `make check-os` - Display OS compatibility

### **📚 Documentation Workflow (Primary)**
- `make run-full` - **Complete dynamic workflow** ✅
- `make convert-templates-dynamic` - **Dynamic template conversion** ✅
- `make convert-markdown` - Convert markdown to HTML
- `make discover-enhanced` - Show discovery results

### **🧹 Maintenance**
- `make clean` - Remove temporary files
- `make verify-html` - Verify HTML generation
- `make debug-conversion` - Debug conversion issues

## 🔧 Prerequisites

### **System Requirements**
- **Ansible**: 2.9+ (for template processing)
- **Python**: 3.8+ (for scripts and Ansible)
- **Pandoc**: Latest (for HTML conversion)
- **jq**: Latest (for JSON processing)

### **Automatic Installation**
```bash
make install-tools              # Detects OS and installs everything
```

### **Manual Installation**
```bash
# RHEL/CentOS/Fedora
make install-rhel-dnf-only

# Ubuntu/Debian
make install-ubuntu-apt-only

# Verify installation
make check-deps
```

## ⚙️ Configuration

### **Required Variables** (`vars/vars.yml`)
```yaml
project_name: "Your Project"
env: "Production"
confluence_url: "https://your-domain.atlassian.net"
confluence_space: "YOUR_SPACE"
confluence_auth: "base64_encoded_credentials"
database_url: "https://your-database.com"
monitoring_tool: "Your Monitor"
```

### **Confluence Setup**
1. Create Confluence space
2. Generate API token
3. Encode credentials: `echo "user@domain.com:api_token" | base64`
4. Add to `vars/vars.yml`

## 🔍 How It Works

### **Dynamic Discovery Process**
1. **Scan**: `discover_docs_enhanced.py` scans `docs/automation_hub/`
2. **Analyze**: Determines file types and relationships
3. **Structure**: Creates JSON structure for processing
4. **Process**: Templates rendered with variable substitution
5. **Convert**: Markdown converted to Confluence-ready HTML
6. **Publish**: Pages created/updated with proper hierarchy

### **Template Processing**
- **Engine**: Ansible template module
- **Variables**: Full access to `vars/vars.yml` and `vars/aap.yml`
- **Features**: Conditionals, loops, includes, macros
- **Output**: Clean, formatted markdown

### **Publishing**
- **Hierarchy**: Parent-child relationships preserved
- **Updates**: Intelligent page update detection
- **Versioning**: Confluence version management
- **Validation**: Success verification

## 🚨 Troubleshooting

### **Common Issues**

**"No templates found"**
```bash
ls -la docs/automation_hub/*.j2  # Verify templates exist
make validate-templates         # Check structure
```

**"Rendering failed"**
```bash
make debug-conversion          # Comprehensive debugging
ansible-playbook --syntax-check playbook.yml  # Check syntax
```

**"Publishing failed"**
```bash
# Check Confluence credentials
grep confluence vars/vars.yml
# Verify connectivity
curl -H "Authorization: Basic $CONFLUENCE_AUTH" $CONFLUENCE_URL/rest/api/space
```

### **Debug Commands**
```bash
make debug-conversion          # Complete debugging workflow
make test-pandoc              # Test HTML conversion
make discover-enhanced        # Show what was discovered
make verify-html             # Verify generated files
```

## 📚 Documentation

### **Comprehensive Guides**
- [`DOCUMENTATION_WORKFLOW.md`](./DOCUMENTATION_WORKFLOW.md) - Complete workflow guide
- [`RELEASE_NOTES.md`](./RELEASE_NOTES.md) - Version 2.0 features and improvements
- [`MAKEFILE_CLEANUP_SUMMARY.md`](./MAKEFILE_CLEANUP_SUMMARY.md) - Technical implementation details

### **Quick Reference**
```bash
make help                     # All available commands
make run-full                # Primary workflow
make debug-conversion        # When things go wrong
```

## 🎯 Migration from Legacy

### **From Manual to Dynamic**
**Old Way:**
```bash
# Manual template list maintenance
vim Makefile                 # Update template lists
make convert-templates       # Static processing
make convert-markdown
ansible-playbook playbooks/04-publish-confluence.yml
```

**New Way:**
```bash
# Zero maintenance
make run-full               # Everything automated!
```

### **Backward Compatibility**
- ✅ All existing templates work unchanged
- ✅ Legacy workflows still available
- ✅ Gradual migration supported
- ✅ No breaking changes

## 💡 Best Practices

### **Template Development**
- Use shared macros from `macros.j2`
- Include auto-generated notices
- Test with `make convert-templates-dynamic`
- Use descriptive filenames

### **Variable Management**
- Keep secrets in encrypted `vars/vars.yml`
- Use environment-specific files
- Document new variables in templates

### **Workflow Integration**
- Use `make run-full` for complete automation
- Verify with `make verify-html` before publishing
- Test changes in development environment first

## 🏆 Success Metrics

### **Before Dynamic Discovery**
- ❌ Manual template list maintenance
- ❌ Multi-step error-prone process
- ❌ New templates required Makefile updates

### **After Dynamic Discovery**
- ✅ Zero-maintenance automation
- ✅ One-command complete workflow
- ✅ Automatic new template integration
- ✅ 80% reduction in setup time

## 🔮 Roadmap

### **Planned Enhancements**
- 📁 Nested folder hierarchy support
- 🔄 Multi-repository documentation aggregation
- 📊 Publishing analytics and metrics
- 🎨 Custom styling and themes

### **Integration Opportunities**
- CI/CD pipeline integration
- Git hook automation
- Notification systems
- Change tracking

## 📞 Support

### **Self-Service**
1. Run `make help` for available commands
2. Use `make debug-conversion` for troubleshooting
3. Check documentation in this repository
4. Review generated files in `~/tmp/`

### **Getting Help**
- Check comprehensive guides in [`DOCUMENTATION_WORKFLOW.md`](./DOCUMENTATION_WORKFLOW.md)
- Review troubleshooting section above
- Examine playbook logs for detailed errors

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<<<<<<< HEAD
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
=======
**🎉 Ready to automate your documentation? Start with `make run-full`! 🚀**

> **💡 Pro Tip**: The entire workflow is now just one command: `make run-full`. Everything else is automatic! 🎯
>>>>>>> ac5ebea51ca19bef2af1c03cbe2fec0d779e8cab
>>>>>>> main
