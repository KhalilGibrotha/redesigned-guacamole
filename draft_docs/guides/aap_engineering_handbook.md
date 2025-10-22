---
title: AAP Engineering Handbook - Developer Standards
version: 1.0-draft
date: 2025-10-22
audience: Developers, QA, SREs
classification: Internal
status: Draft
---

# AAP Engineering Handbook - Developer Standards

## Document Information

- **Document Type**: Technical Standards
- **Audience**: Developers, QA Engineers, SREs, Automation SMEs
- **Effective Date**: TBD
- **Review Cycle**: Quarterly
- **Owner**: Engineering Standards Committee

## Overview

This handbook codifies technical conventions and expectations for code quality, repository hygiene, and development practices within the Ansible Automation Platform ecosystem.

## Coding Standards

### Ansible Role Development

#### Directory Structure

All roles must follow the standard Ansible role structure:

```
roles/my_role/
├── defaults/
│   └── main.yml
├── files/
├── handlers/
│   └── main.yml
├── meta/
│   └── main.yml
├── tasks/
│   └── main.yml
├── templates/
├── tests/
│   ├── inventory
│   └── test.yml
├── vars/
│   └── main.yml
└── README.md
```

#### Role Naming Conventions

- Use lowercase with underscores: `web_server`, `database_backup`
- Prefix with organization namespace: `company_web_server`
- Avoid generic names: use `nginx_proxy` instead of `proxy`
- Keep names descriptive but concise

#### Task Organization

##### Main Tasks File Structure

```yaml
---
# roles/example/tasks/main.yml

- name: Include OS-specific variables
  ansible.builtin.include_vars: "{{ ansible_os_family }}.yml"
  tags: ['always']

- name: Validate input parameters
  ansible.builtin.assert:
    that:
      - required_param is defined
      - required_param | length > 0
    fail_msg: "required_param must be defined and non-empty"
  tags: ['validation']

- name: Include installation tasks
  ansible.builtin.include_tasks: install.yml
  tags: ['install']

- name: Include configuration tasks
  ansible.builtin.include_tasks: configure.yml
  tags: ['configure']

- name: Include service management tasks
  ansible.builtin.include_tasks: service.yml
  tags: ['service']
```

##### Task Naming Standards

- Use descriptive, action-oriented names
- Start with verb in present tense
- Include context and purpose
- Avoid generic names like "Run command"

**Good Examples:**
```yaml
- name: Install nginx package via yum
- name: Configure nginx virtual host for production
- name: Start and enable nginx service
- name: Validate nginx configuration syntax
```

**Poor Examples:**
```yaml
- name: Install package
- name: Copy file
- name: Run command
- name: Do stuff
```

### Variable Management

#### Variable Naming Conventions

Use descriptive, hierarchical naming:

```yaml
# Good - hierarchical and descriptive
nginx_config_worker_processes: 4
nginx_config_worker_connections: 1024
nginx_ssl_certificate_path: "/etc/ssl/certs/nginx.crt"

# Poor - generic and unclear
processes: 4
connections: 1024
cert_path: "/etc/ssl/certs/nginx.crt"
```

#### Variable Organization

##### defaults/main.yml

```yaml
---
# Role defaults - lowest precedence
# These can be overridden by users

# Service configuration
service_name: nginx
service_state: started
service_enabled: true

# Package configuration
package_name: nginx
package_state: present

# File paths
config_dir: "/etc/nginx"
log_dir: "/var/log/nginx"

# Feature flags
enable_ssl: false
enable_monitoring: true
```

##### vars/main.yml

```yaml
---
# Role variables - higher precedence
# Internal role logic, rarely overridden

# Internal calculations
_nginx_user: "{{ 'nginx' if ansible_os_family == 'RedHat' else 'www-data' }}"
_config_file: "{{ config_dir }}/nginx.conf"

# OS-specific package names
_package_map:
  RedHat: nginx
  Debian: nginx-full
  Ubuntu: nginx-full
```

#### Variable Documentation

Document all variables in README.md:

```markdown
## Role Variables

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `service_name` | `nginx` | Name of the service | No |
| `config_dir` | `/etc/nginx` | Configuration directory | No |
| `enable_ssl` | `false` | Enable SSL configuration | No |
| `ssl_certificate_path` | `undefined` | Path to SSL certificate | Yes (if SSL enabled) |
```

### Playbook Development

#### Playbook Structure

```yaml
---
- name: Configure web servers
  hosts: web_servers
  become: true
  gather_facts: true
  
  vars:
    deployment_timestamp: "{{ ansible_date_time.epoch }}"
  
  pre_tasks:
    - name: Validate target hosts are reachable
      ansible.builtin.ping:
      tags: ['validation']
  
  roles:
    - role: common
      tags: ['common']
    - role: nginx
      tags: ['nginx']
    - role: application
      tags: ['application']
  
  post_tasks:
    - name: Verify service accessibility
      ansible.builtin.uri:
        url: "http://{{ inventory_hostname }}"
        method: GET
      tags: ['verification']
  
  handlers:
    - name: restart nginx
      ansible.builtin.service:
        name: nginx
        state: restarted
```

#### Error Handling

##### Failed_when and Changed_when

```yaml
- name: Check application status
  ansible.builtin.command: /usr/local/bin/app-status
  register: app_status
  failed_when: app_status.rc not in [0, 1]
  changed_when: false
  tags: ['health_check']

- name: Configure application
  ansible.builtin.template:
    src: app.conf.j2
    dest: /etc/app/app.conf
    backup: true
  notify: restart application
  register: config_result
  failed_when: config_result.failed and "Permission denied" not in config_result.msg
```

##### Block and Rescue

```yaml
- name: Application deployment block
  block:
    - name: Stop application service
      ansible.builtin.service:
        name: "{{ app_service_name }}"
        state: stopped
    
    - name: Deploy new application version
      ansible.builtin.copy:
        src: "{{ app_binary_path }}"
        dest: "/usr/local/bin/{{ app_service_name }}"
        mode: '0755'
        backup: true
    
    - name: Start application service
      ansible.builtin.service:
        name: "{{ app_service_name }}"
        state: started
  
  rescue:
    - name: Restore previous application version
      ansible.builtin.copy:
        src: "/usr/local/bin/{{ app_service_name }}.backup"
        dest: "/usr/local/bin/{{ app_service_name }}"
        remote_src: true
    
    - name: Start application with previous version
      ansible.builtin.service:
        name: "{{ app_service_name }}"
        state: started
    
    - name: Fail deployment with informative message
      ansible.builtin.fail:
        msg: "Application deployment failed, rolled back to previous version"
  
  always:
    - name: Clean up temporary files
      ansible.builtin.file:
        path: "{{ temp_deployment_dir }}"
        state: absent
```

## Testing Standards

### Molecule Testing Framework

#### Scenario Development

##### Basic Scenario Structure

```yaml
# molecule/default/molecule.yml
---
dependency:
  name: galaxy
  options:
    requirements-file: requirements.yml

driver:
  name: podman

platforms:
  - name: centos8
    image: quay.io/centos/centos:stream8
    pre_build_image: true
    command: /usr/sbin/init
    privileged: true
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro

provisioner:
  name: ansible
  config_options:
    defaults:
      stdout_callback: yaml
      bin_ansible_callbacks: true
  inventory:
    host_vars:
      centos8:
        nginx_worker_processes: 2

verifier:
  name: ansible

scenario:
  test_sequence:
    - dependency
    - cleanup
    - destroy
    - syntax
    - create
    - prepare
    - converge
    - idempotence
    - side_effect
    - verify
    - cleanup
    - destroy
```

##### Converge Playbook

```yaml
# molecule/default/converge.yml
---
- name: Converge
  hosts: all
  become: true
  
  vars:
    nginx_enable_ssl: true
    nginx_ssl_certificate_path: /etc/ssl/certs/test.crt
  
  pre_tasks:
    - name: Update package cache (Debian/Ubuntu)
      ansible.builtin.apt:
        update_cache: true
      when: ansible_os_family == 'Debian'
    
    - name: Install SSL certificate for testing
      ansible.builtin.copy:
        content: |
          -----BEGIN CERTIFICATE-----
          # Test certificate content
          -----END CERTIFICATE-----
        dest: "{{ nginx_ssl_certificate_path }}"
        mode: '0644'
  
  roles:
    - role: nginx
```

##### Verification Tests

```yaml
# molecule/default/verify.yml
---
- name: Verify
  hosts: all
  gather_facts: false
  
  tasks:
    - name: Check nginx is installed
      ansible.builtin.package_facts:
      failed_when: "'nginx' not in ansible_facts.packages"
    
    - name: Verify nginx service is running
      ansible.builtin.service_facts:
      failed_when: >
        ansible_facts.services['nginx.service'].state != 'running' or
        ansible_facts.services['nginx.service'].status != 'enabled'
    
    - name: Test nginx configuration syntax
      ansible.builtin.command: nginx -t
      changed_when: false
    
    - name: Verify nginx responds to HTTP requests
      ansible.builtin.uri:
        url: http://localhost
        return_content: true
      register: http_response
      failed_when: http_response.status != 200
    
    - name: Check log files exist and are writable
      ansible.builtin.stat:
        path: "{{ item }}"
      loop:
        - /var/log/nginx/access.log
        - /var/log/nginx/error.log
      register: log_files
      failed_when: not item.stat.exists or not item.stat.writeable
      loop_control:
        loop_var: item
        label: "{{ item.item }}"
```

#### Multi-scenario Testing

Create scenarios for different environments:

```yaml
# molecule/production-like/molecule.yml
---
dependency:
  name: galaxy

driver:
  name: podman

platforms:
  - name: prod-centos8
    image: quay.io/centos/centos:stream8
    pre_build_image: true
    volumes:
      - /sys/fs/cgroup:/sys/fs/cgroup:ro
    published_ports:
      - "8080:80"
      - "8443:443"

provisioner:
  name: ansible
  inventory:
    host_vars:
      prod-centos8:
        nginx_worker_processes: 8
        nginx_enable_ssl: true
        nginx_ssl_redirect: true
        nginx_rate_limiting: true
```

### Unit Testing

#### Custom Module Testing

```python
# tests/unit/test_custom_module.py
import unittest
from unittest.mock import Mock, patch
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes

# Import the module to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'library'))
from custom_nginx_module import NginxConfigManager

class TestNginxConfigManager(unittest.TestCase):
    
    def setUp(self):
        self.manager = NginxConfigManager('/etc/nginx/nginx.conf')
    
    def test_parse_config_valid(self):
        """Test configuration parsing with valid input."""
        config_content = """
        worker_processes 4;
        events {
            worker_connections 1024;
        }
        """
        result = self.manager.parse_config(config_content)
        self.assertEqual(result['worker_processes'], '4')
        self.assertEqual(result['events']['worker_connections'], '1024')
    
    def test_parse_config_invalid(self):
        """Test configuration parsing with invalid input."""
        config_content = "invalid nginx config"
        with self.assertRaises(ValueError):
            self.manager.parse_config(config_content)
    
    @patch('builtins.open')
    def test_backup_config(self, mock_open):
        """Test configuration backup functionality."""
        mock_open.return_value.__enter__.return_value.read.return_value = "test config"
        
        backup_path = self.manager.backup_config()
        self.assertTrue(backup_path.endswith('.backup'))
        mock_open.assert_called()

if __name__ == '__main__':
    unittest.main()
```

#### Filter Testing

```python
# tests/unit/test_filters.py
import unittest
from ansible.plugins.filter.custom_filters import FilterModule

class TestCustomFilters(unittest.TestCase):
    
    def setUp(self):
        self.filter_module = FilterModule()
        self.filters = self.filter_module.filters()
    
    def test_to_nginx_upstream(self):
        """Test nginx upstream format filter."""
        servers = [
            {'host': '192.168.1.10', 'port': 8080, 'weight': 1},
            {'host': '192.168.1.11', 'port': 8080, 'weight': 2}
        ]
        
        result = self.filters['to_nginx_upstream'](servers)
        expected = "server 192.168.1.10:8080 weight=1;\nserver 192.168.1.11:8080 weight=2;"
        
        self.assertEqual(result, expected)
    
    def test_to_nginx_upstream_empty(self):
        """Test nginx upstream filter with empty input."""
        result = self.filters['to_nginx_upstream']([])
        self.assertEqual(result, "")
```

### Integration Testing

#### End-to-End Workflow Testing

```yaml
# tests/integration/test_full_deployment.yml
---
- name: Full deployment integration test
  hosts: test_servers
  become: true
  gather_facts: true
  
  vars:
    test_application_url: "http://{{ inventory_hostname }}/health"
    test_timeout: 60
  
  tasks:
    - name: Deploy complete application stack
      ansible.builtin.include_role:
        name: application_stack
      vars:
        app_environment: integration_test
        app_debug_mode: true
    
    - name: Wait for application to be ready
      ansible.builtin.uri:
        url: "{{ test_application_url }}"
        method: GET
        timeout: 10
      register: health_check
      until: health_check.status == 200
      retries: "{{ test_timeout // 10 }}"
      delay: 10
    
    - name: Run application functional tests
      ansible.builtin.command: |
        /opt/app/bin/run-tests --integration --verbose
      register: app_tests
      failed_when: app_tests.rc != 0
    
    - name: Generate test report
      ansible.builtin.template:
        src: test_report.j2
        dest: "/tmp/integration_test_report_{{ ansible_date_time.epoch }}.html"
      vars:
        test_results: "{{ app_tests.stdout }}"
        test_timestamp: "{{ ansible_date_time.iso8601 }}"
```

## Linting and Code Quality

### YAML Linting Standards

#### yamllint Configuration

```yaml
# .yamllint
---
extends: default

rules:
  braces:
    max-spaces-inside: 1
    level: error
  brackets:
    max-spaces-inside: 1
    level: error
  colons:
    max-spaces-after: -1
    level: error
  commas:
    max-spaces-after: -1
    level: error
  comments: disable
  comments-indentation: disable
  document-start: disable
  empty-lines:
    max: 3
    level: error
  hyphens:
    level: error
  indentation:
    spaces: consistent
    indent-sequences: true
    check-multi-line-strings: false
  key-duplicates: enable
  line-length:
    max: 120
    level: warning
  new-line-at-end-of-file: disable
  octal-values:
    forbid-implicit-octal: true
    forbid-explicit-octal: true
  trailing-spaces: disable
  truthy: disable
```

### Ansible Linting

#### Custom Lint Rules

```python
# .ansible-lint-custom/WindowsConnectionRule.py
from ansiblelint.rules import AnsibleLintRule

class WindowsConnectionRule(AnsibleLintRule):
    id = 'WINDOWS_001'
    shortdesc = 'Windows hosts should use PSRP or secure WinRM'
    description = (
        'Windows connection should use ansible_connection=psrp or '
        'ansible_connection=winrm with ansible_winrm_transport=credssp/kerberos '
        'and ansible_winrm_server_cert_validation=validate'
    )
    tags = ['security', 'windows']

    def matchtask(self, task, file=None):
        if not task.get('vars'):
            return False
        
        vars_dict = task['vars']
        connection = vars_dict.get('ansible_connection')
        
        if connection == 'winrm':
            transport = vars_dict.get('ansible_winrm_transport')
            cert_validation = vars_dict.get('ansible_winrm_server_cert_validation')
            
            if transport not in ['credssp', 'kerberos']:
                return True
            if cert_validation != 'validate':
                return True
        
        return False
```

#### ansible-lint Configuration

```yaml
# .ansible-lint
---
profile: production

exclude_paths:
  - .cache/
  - .github/
  - molecule/*/
  - tests/

# Enable specific rules
enable_list:
  - no-changed-when
  - no-handler
  - no-jinja-when
  - no-tabs

# Skip specific rules for specific files
skip_list:
  - yaml[line-length]
  - name[casing]

# Use custom rules
rulesdir:
  - .ansible-lint-custom/

# Warn instead of error for specific rules
warn_list:
  - experimental
  - ignore-errors
  - no-changed-when
  - command-instead-of-module

# Mock modules for linting
mock_modules:
  - custom_company_module
  - proprietary_module

# Mock roles for linting
mock_roles:
  - company.internal.base_role

# Offline mode for CI/CD
offline: false

# Progressive mode for gradual adoption
progressive: false
```

### Documentation Linting

#### markdownlint Configuration

```json
{
  "default": true,
  "MD003": { "style": "atx" },
  "MD007": { "indent": 2 },
  "MD009": { "br_spaces": 2 },
  "MD010": { "code_blocks": false },
  "MD013": { "line_length": 120 },
  "MD024": { "siblings_only": true },
  "MD026": { "punctuation": ".,;:!" },
  "MD029": { "style": "ordered" },
  "MD033": { "allowed_elements": ["br", "sub", "sup"] },
  "MD036": { "punctuation": ".,;:!?" }
}
```

## Commit Conventions and Version Control

### Commit Message Format

Follow conventional commits specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### Commit Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

#### Examples

```bash
# Feature addition
feat(nginx): add SSL certificate auto-renewal

# Bug fix
fix(database): resolve connection pool exhaustion

# Documentation update
docs(api): update authentication examples

# Refactoring
refactor(handlers): simplify service restart logic

# Breaking change
feat(config)!: change default SSL cipher suite

BREAKING CHANGE: The default SSL cipher suite has been updated
to exclude weak ciphers. This may affect older clients.
```

### Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
---
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
        args: [--markdown-linebreak-ext=md]
      - id: end-of-file-fixer
      - id: check-yaml
        args: [--unsafe]
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: check-merge-conflict
      - id: check-executables-have-shebangs
      - id: check-shebang-scripts-are-executable

  - repo: https://github.com/adrienverge/yamllint
    rev: v1.32.0
    hooks:
      - id: yamllint
        args: [-c=.yamllint]

  - repo: https://github.com/ansible/ansible-lint
    rev: v6.17.2
    hooks:
      - id: ansible-lint
        args: [--profile=production]
        additional_dependencies:
          - ansible-core>=2.13

  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.35.0
    hooks:
      - id: markdownlint
        args: [--config=.markdownlint.json]

  - repo: https://github.com/shellcheck-py/shellcheck-py
    rev: v0.9.0.5
    hooks:
      - id: shellcheck
        args: [--severity=warning]

  - repo: local
    hooks:
      - id: ansible-vault-check
        name: Check for unencrypted secrets
        entry: scripts/check-secrets.sh
        language: script
        files: '\.(yml|yaml)$'
```

### Branch Protection Rules

Configure branch protection for main branches:

```yaml
# .github/branch-protection.yml
protection_rules:
  main:
    required_status_checks:
      strict: true
      contexts:
        - "lint-yaml"
        - "lint-ansible"
        - "molecule-test"
        - "security-scan"
    
    enforce_admins: true
    required_pull_request_reviews:
      required_approving_review_count: 2
      dismiss_stale_reviews: true
      require_code_owner_reviews: true
    
    restrictions:
      users: []
      teams: ["platform-team", "senior-engineers"]
    
    allow_force_pushes: false
    allow_deletions: false
```

## Documentation Format and Standards

### README Template

```markdown
# Role Name

Brief description of the role's purpose and functionality.

## Requirements

- Ansible 2.13+
- Python 3.8+
- Target OS: RHEL/CentOS 8+, Ubuntu 20.04+

## Role Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `required_var` | Description of required variable | `"example_value"` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `optional_var` | `default_value` | Description of optional variable |

### Variable Examples

```yaml
# Minimal configuration
role_var: simple_value

# Complex configuration
role_config:
  key1: value1
  key2:
    - item1
    - item2
```

## Dependencies

- role: common
- collection: community.general

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: my_role
      vars:
        required_var: "production_value"
        optional_var: "custom_value"
```

## Testing

```bash
# Run molecule tests
molecule test

# Run specific scenario
molecule test -s production
```

## License

Licensed under [Company License](LICENSE)

## Author Information

Created by [Team Name] - [contact@company.com]
```

### Metadata Standards

#### Role Metadata

```yaml
# meta/main.yml
---
galaxy_info:
  role_name: nginx
  namespace: company
  author: Platform Engineering Team
  description: Nginx web server configuration and management
  company: Company Name
  license: proprietary
  
  min_ansible_version: 2.13
  
  platforms:
    - name: EL
      versions:
        - 8
        - 9
    - name: Ubuntu
      versions:
        - 20.04
        - 22.04
  
  galaxy_tags:
    - web
    - nginx
    - proxy
    - ssl

dependencies:
  - role: company.common
    version: ">=1.0.0"

collections:
  - community.general
  - ansible.posix
```

#### Playbook Metadata

```yaml
---
# playbook-metadata.yml
name: "Web Server Deployment"
description: "Complete web server stack deployment with SSL and monitoring"
version: "2.1.0"
author: "Platform Engineering Team"
tags:
  - web-server
  - nginx
  - ssl
  - monitoring
maintainer: "platform-team@company.com"
last_updated: "2025-10-22"
ansible_version: ">=2.13"
target_platforms:
  - rhel8
  - rhel9
  - ubuntu20
  - ubuntu22
```

## Integration Testing and CI Flow

### CI Pipeline Configuration

#### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
---
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install ansible-core ansible-lint yamllint
          ansible-galaxy install -r requirements.yml
      
      - name: Run YAML lint
        run: yamllint .
      
      - name: Run Ansible lint
        run: ansible-lint
  
  molecule:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        scenario: [default, centos8, ubuntu20]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install molecule[podman] ansible-core
          ansible-galaxy install -r requirements.yml
      
      - name: Run Molecule tests
        run: molecule test -s ${{ matrix.scenario }}
        env:
          ANSIBLE_FORCE_COLOR: '1'
  
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run security scan
        uses: ansible/ansible-lint-action@main
        with:
          args: --profile=security
```

### Test Automation

#### Automated Testing Script

```bash
#!/bin/bash
# scripts/run-tests.sh

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TEST_RESULTS_DIR="${PROJECT_DIR}/test-results"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

setup_test_environment() {
    log_info "Setting up test environment..."
    
    # Create test results directory
    mkdir -p "$TEST_RESULTS_DIR"
    
    # Install dependencies
    pip install -r requirements.txt
    ansible-galaxy install -r requirements.yml
}

run_yaml_lint() {
    log_info "Running YAML lint..."
    
    yamllint . > "$TEST_RESULTS_DIR/yamllint.txt" 2>&1 || {
        log_error "YAML lint failed"
        cat "$TEST_RESULTS_DIR/yamllint.txt"
        return 1
    }
    
    log_info "YAML lint passed"
}

run_ansible_lint() {
    log_info "Running Ansible lint..."
    
    ansible-lint --profile=production > "$TEST_RESULTS_DIR/ansible-lint.txt" 2>&1 || {
        log_error "Ansible lint failed"
        cat "$TEST_RESULTS_DIR/ansible-lint.txt"
        return 1
    }
    
    log_info "Ansible lint passed"
}

run_molecule_tests() {
    local scenario=${1:-default}
    log_info "Running Molecule tests for scenario: $scenario"
    
    molecule test -s "$scenario" > "$TEST_RESULTS_DIR/molecule-$scenario.txt" 2>&1 || {
        log_error "Molecule tests failed for scenario: $scenario"
        cat "$TEST_RESULTS_DIR/molecule-$scenario.txt"
        return 1
    }
    
    log_info "Molecule tests passed for scenario: $scenario"
}

run_security_scan() {
    log_info "Running security scan..."
    
    # Check for common security issues
    ansible-lint --profile=security > "$TEST_RESULTS_DIR/security-scan.txt" 2>&1 || {
        log_warn "Security scan found issues"
        cat "$TEST_RESULTS_DIR/security-scan.txt"
    }
    
    # Check for secrets in code
    if command -v gitleaks &> /dev/null; then
        gitleaks detect --source . --report-format json --report-path "$TEST_RESULTS_DIR/secrets-scan.json" || {
            log_error "Secrets detected in repository"
            return 1
        }
    fi
}

generate_test_report() {
    log_info "Generating test report..."
    
    cat > "$TEST_RESULTS_DIR/summary.html" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Test Results Summary</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .pass { color: green; }
        .fail { color: red; }
        .warn { color: orange; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>Test Results Summary</h1>
    <p>Generated: $(date)</p>
    
    <table>
        <tr><th>Test</th><th>Status</th><th>Details</th></tr>
        <tr><td>YAML Lint</td><td class="$([ -f "$TEST_RESULTS_DIR/yamllint.txt" ] && echo "pass" || echo "fail")">$([ -f "$TEST_RESULTS_DIR/yamllint.txt" ] && echo "PASS" || echo "FAIL")</td><td>Standard YAML formatting</td></tr>
        <tr><td>Ansible Lint</td><td class="$([ -f "$TEST_RESULTS_DIR/ansible-lint.txt" ] && echo "pass" || echo "fail")">$([ -f "$TEST_RESULTS_DIR/ansible-lint.txt" ] && echo "PASS" || echo "FAIL")</td><td>Ansible best practices</td></tr>
        <tr><td>Security Scan</td><td class="$([ -f "$TEST_RESULTS_DIR/security-scan.txt" ] && echo "pass" || echo "fail")">$([ -f "$TEST_RESULTS_DIR/security-scan.txt" ] && echo "PASS" || echo "FAIL")</td><td>Security compliance</td></tr>
    </table>
</body>
</html>
EOF
    
    log_info "Test report generated: $TEST_RESULTS_DIR/summary.html"
}

# Main execution
main() {
    log_info "Starting automated test suite..."
    
    setup_test_environment
    
    # Run all tests
    run_yaml_lint
    run_ansible_lint
    run_security_scan
    
    # Run molecule tests for all scenarios
if [ -d "molecule" ]; then
    fi
    
    generate_test_report
    
    log_info "All tests completed successfully!"
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```

## Performance and Optimization

### Playbook Optimization

#### Gathering Facts Optimization

```yaml
---
- name: Optimized playbook execution
  hosts: all
  gather_facts: false  # Disable automatic fact gathering
  
  tasks:
    - name: Gather minimal facts
      ansible.builtin.setup:
        gather_subset:
          - '!all'
          - '!min'
          - network
          - virtual
      when: ansible_facts is not defined
      tags: ['always']
    
    - name: Gather additional facts only when needed
      ansible.builtin.setup:
        gather_subset:
          - hardware
      when: 
        - need_hardware_facts | default(false)
        - ansible_facts.hardware is not defined
```

#### Task Optimization

```yaml
---
# Use loops efficiently
- name: Install multiple packages (efficient)
  ansible.builtin.package:
    name: "{{ packages }}"
    state: present
  vars:
    packages:
      - nginx
      - postgresql
      - redis

# Instead of multiple tasks
# - name: Install nginx
#   ansible.builtin.package:
#     name: nginx
#     state: present
# - name: Install postgresql
#   ...

# Use when conditions efficiently
- name: Configure service (conditional)
  ansible.builtin.template:
    src: service.conf.j2
    dest: /etc/service/service.conf
  when: 
    - configure_service | default(true)
    - service_type == 'production'
  notify: restart service

# Cache expensive operations
- name: Get service status (cached)
  ansible.builtin.command: systemctl is-active nginx
  register: service_status
  changed_when: false
  failed_when: false
  run_once: true
  delegate_to: "{{ groups['web_servers'][0] }}"
  delegate_facts: true
```

### Role Performance

#### Conditional Includes

```yaml
---
# tasks/main.yml
- name: Include OS-specific variables
  ansible.builtin.include_vars: "{{ item }}"
  with_first_found:
    - files:
        - "{{ ansible_distribution }}-{{ ansible_distribution_major_version }}.yml"
        - "{{ ansible_distribution }}.yml"
        - "{{ ansible_os_family }}.yml"
        - "default.yml"
      paths:
        - "vars"
  tags: ['always']

- name: Include installation tasks
  ansible.builtin.include_tasks: "install-{{ ansible_os_family }}.yml"
  when: package_state != 'absent'
  tags: ['install']

- name: Include configuration tasks
  ansible.builtin.include_tasks: configure.yml
  when: 
    - package_state != 'absent'
    - configure_service | default(true)
  tags: ['configure']
```

## Document Control

### Revision History

| Version | Date | Changes | Approved By |
|---------|------|---------|-------------|
| 1.0-draft | 2025-10-22 | Initial comprehensive draft | TBD |

### Document Maintenance

- **Owner**: Engineering Standards Committee
- **Review Frequency**: Quarterly
- **Next Review**: 2025-01-22
- **Distribution**: All engineering teams, QA, SRE