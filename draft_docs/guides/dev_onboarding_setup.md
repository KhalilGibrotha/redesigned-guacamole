---
title: Developer Onboarding and Environment Setup Guide
version: 1.0-draft
date: 2025-10-22
audience: Engineers, Developers
classification: Internal
status: Draft
---

# Developer Onboarding and Environment Setup Guide

## Document Information

- **Document Type**: Technical Guide
- **Audience**: Engineers, Developers, QA Engineers
- **Effective Date**: TBD
- **Review Cycle**: Quarterly
- **Owner**: Platform Engineering Team

## Overview

This guide provides step-by-step instructions for onboarding into the Ansible Automation Platform development environment using Dev Spaces and Execution Environments.

## Prerequisites

### Required Access

Before beginning setup, ensure you have:

- Active Directory account with appropriate group memberships
- OpenShift Dev Spaces access
- Git repository access (GitHub/GitLab)
- AAP instance access for testing
- VPN access (if required)

### Required Software Knowledge

Basic familiarity with:
- Git version control
- YAML syntax
- Ansible fundamentals
- Container concepts
- Linux command line

## Access and Environment Setup

### Step 1: Dev Spaces Access

#### Accessing Dev Spaces

1. Navigate to the OpenShift Dev Spaces URL: `https://devspaces.example.com`
2. Authenticate using your Active Directory credentials
3. Accept any required terms of service
4. Verify your workspace quota and limits

#### Creating Your First Workspace

1. Click "Create Workspace"
2. Select the appropriate devfile:
   - `ansible-automation-devfile` for Ansible development
   - `molecule-testing-devfile` for testing-focused work
3. Configure workspace settings:
   - Name: `your-username-ansible-dev`
   - Description: Brief description of your work
   - Storage: Select appropriate storage class

### Step 2: Development Environment Configuration

#### Workspace Structure

Your Dev Spaces workspace will include:

```
/projects/
├── ansible-project-1/
├── ansible-project-2/
├── shared-collections/
└── documentation/
```

#### Environment Variables

The following environment variables are pre-configured:

- `ANSIBLE_CONFIG`: Points to workspace ansible.cfg
- `ANSIBLE_COLLECTIONS_PATH`: Collections installation path
- `EXECUTION_ENVIRONMENT_IMAGE`: Default EE image
- `REGISTRY_URL`: Container registry location

### Step 3: Repository Access and Cloning

#### Cloning Repositories

Use the integrated Git functionality or terminal:

```bash
# Navigate to projects directory
cd /projects

# Clone your assigned repositories
git clone https://github.com/organization/ansible-project-1.git
git clone https://github.com/organization/shared-collections.git

# Set up git configuration
git config --global user.name "Your Name"
git config --global user.email "your.email@company.com"
```

#### Repository Structure Validation

Verify each repository contains:
- `.pre-commit-config.yaml`
- `ansible.cfg`
- `execution-environment.yml`
- `molecule/` directory
- `requirements.yml`

## Execution Environment Configuration

### Understanding EE Images

#### Available Images

| Image Name | Purpose | Python Version | Key Collections |
|------------|---------|----------------|-----------------|
| `ee-base:2025.10` | General automation | 3.11 | ansible.posix, community.general |
| `ee-windows:2025.10` | Windows management | 3.11 | ansible.windows, community.windows |
| `ee-network:2025.10` | Network automation | 3.11 | cisco.ios, arista.eos |
| `ee-cloud:2025.10` | Cloud platforms | 3.11 | amazon.aws, azure.azcollection |

#### Image Selection Guidelines

Choose the appropriate image based on your automation targets:
- Use `ee-base` for Linux system management
- Use `ee-windows` for Windows environments
- Use `ee-network` for network device automation
- Use `ee-cloud` for cloud platform automation

### EE Configuration in Projects

#### ansible.cfg Configuration

Ensure your `ansible.cfg` includes:

```ini
[defaults]
host_key_checking = False
stdout_callback = yaml
fact_caching = memory
gathering = smart

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
```

#### Execution Environment Specification

Your `execution-environment.yml` should specify:

```yaml
---
version: 3
images:
  base_image:
    name: registry.example.com/ee-base:2025.10

dependencies:
  galaxy: requirements.yml
  python: requirements.txt
  system: bindep.txt

additional_build_steps:
  prepend_base:
    - RUN whoami
  append_final:
    - RUN ansible-galaxy collection list
```

## Secrets Management

### OpenShift Secrets

#### Viewing Available Secrets

Use the OpenShift UI to view available secrets:
1. Navigate to Workloads → Secrets
2. Filter by your namespace
3. Identify automation-related secrets

#### Secret Mounting in Dev Spaces

Secrets are automatically mounted to:
- `/etc/secrets/ssh-keys/` - SSH private keys
- `/etc/secrets/certificates/` - SSL certificates
- `/etc/secrets/credentials/` - Service account credentials

#### Using Secrets in Ansible

Access mounted secrets in your playbooks:

```yaml
---
- name: Use mounted SSH key
  ansible.builtin.ssh_key:
    name: automation_key
    private_key_file: /etc/secrets/ssh-keys/automation_key
```

### Credential Security Best Practices

- Never commit credentials to version control
- Use AAP credential types for production
- Rotate development credentials regularly
- Report suspected credential compromise immediately

## Running Ansible Navigator

### Basic Navigation Commands

#### Project Execution

```bash
# Navigate to your project
cd /projects/ansible-project-1

# Run a playbook with ansible-navigator
ansible-navigator run playbooks/site.yml

# Run with specific inventory
ansible-navigator run playbooks/site.yml -i inventory/development

# Run with custom EE image
ansible-navigator run playbooks/site.yml --execution-environment-image ee-windows:2025.10
```

#### Interactive Mode

```bash
# Start interactive session
ansible-navigator

# Available commands in interactive mode:
# :collections - View installed collections
# :config - Display configuration
# :images - List available EE images
# :inventory - Browse inventory
# :run - Execute playbooks
# :settings - View navigator settings
```

### Configuration and Settings

#### Navigator Configuration

Create `ansible-navigator.yml` in your project root:

```yaml
---
ansible-navigator:
  execution-environment:
    image: registry.example.com/ee-base:2025.10
    enabled: true
    pull:
      policy: missing
  
  logging:
    level: info
    append: true
    file: /tmp/ansible-navigator.log
  
  playbook-artifact:
    enable: true
    save-as: /tmp/playbook-artifacts/{playbook_name}-{ts_utc}.json
```

## Testing with Molecule

### Molecule Scenarios

#### Understanding Scenarios

Each project includes molecule scenarios in `molecule/` directory:

```
molecule/
├── default/
│   ├── molecule.yml
│   ├── converge.yml
│   ├── verify.yml
│   └── destroy.yml
├── integration/
└── production-like/
```

#### Running Tests

```bash
# Run default scenario
molecule test

# Run specific scenario
molecule test -s integration

# Run test steps individually
molecule create
molecule converge
molecule verify
molecule destroy
```

### Test Development

#### Creating New Scenarios

```bash
# Create new scenario
molecule init scenario production-test

# Configure scenario for your environment
# Edit molecule/production-test/molecule.yml
```

#### Writing Verification Tests

Create verification tests in `molecule/*/verify.yml`:

```yaml
---
- name: Verify deployment
  hosts: all
  gather_facts: false
  tasks:
    - name: Check service status
      ansible.builtin.service_facts:
      
    - name: Verify service is running
      ansible.builtin.assert:
        that:
          - ansible_facts.services['myservice.service'].state == 'running'
```

## Linting and Code Quality

### Pre-commit Hooks

#### Installation and Setup

Pre-commit hooks are automatically configured in Dev Spaces:

```bash
# Verify pre-commit installation
pre-commit --version

# Install hooks for current repository
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

#### Available Hooks

Standard hooks include:
- `yamllint` - YAML syntax and style
- `ansible-lint` - Ansible best practices
- `trailing-whitespace` - Remove trailing spaces
- `end-of-file-fixer` - Ensure files end with newline
- `check-yaml` - YAML syntax validation

### Manual Linting

#### YAML Linting

```bash
# Lint specific files
yamllint playbooks/site.yml

# Lint entire directory
yamllint .

# Show configuration
yamllint --print-filename config-file
```

#### Ansible Linting

```bash
# Lint playbooks
ansible-lint playbooks/

# Lint specific playbook
ansible-lint playbooks/site.yml

# Show rule documentation
ansible-lint -L

# Exclude specific rules
ansible-lint -x ANSIBLE0010,ANSIBLE0011 playbooks/
```

## Pull Request Workflow

### Creating Pull Requests

#### Branch Creation

```bash
# Create feature branch
git checkout -b feature/JIRA-123-new-automation

# Make your changes
# ... edit files ...

# Stage and commit changes
git add .
git commit -m "feat: add new automation for JIRA-123"

# Push branch
git push origin feature/JIRA-123-new-automation
```

#### PR Requirements

Before creating a PR, ensure:
- All tests pass locally
- Pre-commit hooks pass
- Documentation is updated
- Commit messages follow conventions

### Review Process

#### Automated Checks

Your PR will trigger:
- Linting validation (yamllint, ansible-lint)
- Molecule testing
- Security scanning
- Policy compliance checks

#### Manual Review

Reviews will check for:
- Code quality and standards compliance
- Security best practices
- Documentation completeness
- Test coverage adequacy

## Troubleshooting Common Issues

### Dev Spaces Issues

#### Workspace Won't Start

1. Check resource quotas in OpenShift console
2. Verify devfile syntax
3. Check for conflicting workspaces
4. Contact platform team if issues persist

#### EE Image Pull Failures

1. Verify image name and tag
2. Check registry authentication
3. Ensure network connectivity
4. Try alternative image versions

### Ansible Navigator Issues

#### Command Not Found

```bash
# Verify installation
which ansible-navigator

# Check PATH
echo $PATH

# Reinstall if necessary
pip install ansible-navigator
```

#### EE Container Issues

```bash
# Check container runtime
podman ps -a

# View container logs
podman logs <container-id>

# Clean up containers
podman system prune
```

### Git and Repository Issues

#### Authentication Failures

1. Verify SSH key configuration
2. Check repository permissions
3. Validate network access
4. Contact repository administrators

#### Merge Conflicts

```bash
# Update local branch
git fetch origin main
git rebase origin/main

# Resolve conflicts manually
# Edit conflicted files

# Continue rebase
git rebase --continue
```

## Getting Help

### Self-Service Resources

- Platform documentation portal
- Ansible community documentation
- Internal knowledge base
- Video tutorials and recordings

### Support Channels

#### Platform Team Support

- **Slack**: #platform-automation-support
- **Email**: platform-team@company.com
- **Ticket System**: ServiceNow (Category: Platform/Automation)

#### Escalation Process

1. **Level 1**: Peer support and documentation
2. **Level 2**: Platform team support
3. **Level 3**: Vendor support (if applicable)

### Training Resources

#### Required Training

- Ansible Fundamentals (internal course)
- Container Security Basics
- Git Workflow Training
- Platform Governance Overview

#### Optional Training

- Advanced Ansible Development
- Molecule Testing Deep Dive
- OpenShift Developer Training
- Security Best Practices

## Next Steps

After completing setup:

1. Complete assigned training modules
2. Join relevant communication channels
3. Identify your first automation project
4. Schedule pairing session with experienced team member
5. Begin contributing to existing projects

### First Week Checklist

- [ ] Dev Spaces access verified
- [ ] First repository cloned and configured
- [ ] EE image tested successfully
- [ ] Molecule test executed
- [ ] Pre-commit hooks working
- [ ] First PR created (even if just documentation update)
- [ ] Team introductions completed
- [ ] Training schedule established

## Document Control

### Revision History

| Version | Date | Changes | Approved By |
|---------|------|---------|-------------|
| 1.0-draft | 2025-10-22 | Initial draft | TBD |

### Document Maintenance

- **Owner**: Platform Engineering Team
- **Review Frequency**: Quarterly
- **Next Review**: 2025-01-22