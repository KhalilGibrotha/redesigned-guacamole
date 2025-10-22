---
title: Enforcement Mechanisms Reference
version: 1.0-draft
date: 2025-10-22
audience: Platform Engineers, Compliance Teams
classification: Internal
status: Draft
---

# Enforcement Mechanisms Reference

## Document Information

- **Document Type**: Technical Reference
- **Audience**: Platform Engineers, Compliance Teams, Security Teams
- **Effective Date**: TBD
- **Review Cycle**: Quarterly
- **Owner**: Platform Engineering and Security Teams

## Overview

This document provides comprehensive documentation of technical enforcement mechanisms used to ensure compliance with AAP governance policies, security standards, and development practices. It covers implementation details, maintenance procedures, and troubleshooting guidance.

## Enforcement Architecture

### Multi-Layer Enforcement Model

```
┌─────────────────────────────────────────────────────────┐
│                    Policy Layer                         │
├─────────────────────────────────────────────────────────┤
│              Development Time Enforcement               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐│
│  │ Pre-commit  │ │ Ansible     │ │ IDE Integration     ││
│  │ Hooks       │ │ Lint        │ │ (Real-time)         ││
│  └─────────────┘ └─────────────┘ └─────────────────────┘│
├─────────────────────────────────────────────────────────┤
│                Build Time Enforcement                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐│
│  │ CI/CD       │ │ Security    │ │ Quality Gates       ││
│  │ Pipeline    │ │ Scanning    │ │                     ││
│  └─────────────┘ └─────────────┘ └─────────────────────┘│
├─────────────────────────────────────────────────────────┤
│               Runtime Enforcement                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐│
│  │ AAP Org     │ │ Network     │ │ Monitoring &        ││
│  │ Controls    │ │ Controls    │ │ Alerting            ││
│  └─────────────┘ └─────────────┘ └─────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

## Development Time Enforcement

### Pre-commit Hook Framework

#### Configuration and Setup

```yaml
# .pre-commit-config.yaml
---
repos:
  # Security and secrets detection
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
        name: Detect secrets and credentials
        description: Scan for hardcoded secrets
        entry: gitleaks detect --source . --verbose
        language: golang
        types: [text]

  # YAML validation and formatting
  - repo: https://github.com/adrienverge/yamllint
    rev: v1.32.0
    hooks:
      - id: yamllint
        name: YAML Syntax and Style Check
        description: Validate YAML syntax and style
        args: [-c=.yamllint]
        types: [yaml]

  # Ansible-specific linting
  - repo: https://github.com/ansible/ansible-lint
    rev: v6.17.2
    hooks:
      - id: ansible-lint
        name: Ansible Best Practices
        description: Validate Ansible content against best practices
        args: [--profile=production]
        additional_dependencies:
          - ansible-core>=2.13
        types: [yaml]
        files: \.(yml|yaml)$

  # Custom company rules
  - repo: local
    hooks:
      - id: windows-connection-check
        name: Windows Connection Security Check
        description: Ensure Windows connections use secure protocols
        entry: scripts/check-windows-connections.py
        language: python
        files: \.(yml|yaml)$
        additional_dependencies:
          - pyyaml
          - ruamel.yaml

      - id: execution-environment-validation
        name: Execution Environment Validation
        description: Validate EE specifications and usage
        entry: scripts/validate-ee-usage.py
        language: python
        files: execution-environment\.yml$

      - id: credential-reference-check
        name: Credential Reference Validation
        description: Ensure proper credential handling
        entry: scripts/check-credential-usage.sh
        language: script
        files: \.(yml|yaml)$

  # General code quality
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
      - id: mixed-line-ending
        args: ['--fix=lf']

# Global configuration
fail_fast: false
default_stages: [commit, push]
```

#### Custom Enforcement Scripts

##### Windows Connection Security Check

```python
#!/usr/bin/env python3
# scripts/check-windows-connections.py

import sys
import yaml
import re
from pathlib import Path
from typing import List, Dict, Any

class WindowsConnectionChecker:
    """Validates Windows connection security compliance."""
    
    SECURE_CONNECTIONS = ['psrp', 'winrm']
    SECURE_TRANSPORTS = ['kerberos', 'credssp']
    REQUIRED_CERT_VALIDATION = 'validate'
    
    def __init__(self):
        self.violations = []
        self.files_checked = 0
        
    def check_file(self, file_path: Path) -> bool:
        """Check a single YAML file for Windows connection violations."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            self.files_checked += 1
            return self._check_content(content, file_path)
            
        except yaml.YAMLError as e:
            print(f"YAML parse error in {file_path}: {e}")
            return False
        except Exception as e:
            print(f"Error checking {file_path}: {e}")
            return False
    
    def _check_content(self, content: Any, file_path: Path) -> bool:
        """Recursively check YAML content for violations."""
        violations_found = False
        
        if isinstance(content, dict):
            violations_found |= self._check_dict(content, file_path)
        elif isinstance(content, list):
            for item in content:
                violations_found |= self._check_content(item, file_path)
        
        return not violations_found
    
    def _check_dict(self, data: Dict[str, Any], file_path: Path) -> bool:
        """Check dictionary for Windows connection violations."""
        violations_found = False
        
        # Check for Windows connection variables
        connection = data.get('ansible_connection')
        if connection == 'winrm':
            violations_found |= self._validate_winrm_config(data, file_path)
        elif connection and 'win' in connection.lower():
            violations_found |= self._validate_windows_connection(data, file_path, connection)
        
        # Check inventory host variables
        if 'hosts' in data or 'children' in data:
            violations_found |= self._check_inventory_hosts(data, file_path)
        
        # Check task-level variables
        if 'vars' in data:
            violations_found |= self._check_content(data['vars'], file_path)
        
        # Recursively check nested structures
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                violations_found |= self._check_content(value, file_path)
        
        return violations_found
    
    def _validate_winrm_config(self, config: Dict[str, Any], file_path: Path) -> bool:
        """Validate WinRM-specific configuration."""
        violations = []
        
        # Check transport security
        transport = config.get('ansible_winrm_transport')
        if transport not in self.SECURE_TRANSPORTS:
            violations.append(
                f"WinRM transport '{transport}' is not secure. "
                f"Use: {', '.join(self.SECURE_TRANSPORTS)}"
            )
        
        # Check certificate validation
        cert_validation = config.get('ansible_winrm_server_cert_validation')
        if cert_validation != self.REQUIRED_CERT_VALIDATION:
            violations.append(
                f"Certificate validation must be '{self.REQUIRED_CERT_VALIDATION}', "
                f"found: '{cert_validation}'"
            )
        
        # Check for HTTP usage (should be HTTPS)
        port = config.get('ansible_port', config.get('ansible_winrm_port'))
        if port == 5985 or str(port) == '5985':
            violations.append(
                "HTTP port 5985 is not allowed. Use HTTPS port 5986"
            )
        
        for violation in violations:
            self.violations.append(f"{file_path}: {violation}")
        
        return len(violations) > 0
    
    def _validate_windows_connection(self, config: Dict[str, Any], file_path: Path, connection: str) -> bool:
        """Validate general Windows connection configuration."""
        if connection not in self.SECURE_CONNECTIONS:
            self.violations.append(
                f"{file_path}: Windows connection '{connection}' is not approved. "
                f"Use: {', '.join(self.SECURE_CONNECTIONS)}"
            )
            return True
        return False
    
    def _check_inventory_hosts(self, inventory: Dict[str, Any], file_path: Path) -> bool:
        """Check inventory hosts for Windows connection compliance."""
        violations_found = False
        
        if 'hosts' in inventory:
            for host, host_vars in inventory['hosts'].items():
                if isinstance(host_vars, dict):
                    violations_found |= self._check_content(host_vars, file_path)
        
        if 'children' in inventory:
            for group, group_data in inventory['children'].items():
                if isinstance(group_data, dict):
                    violations_found |= self._check_content(group_data, file_path)
        
        return violations_found

def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: check-windows-connections.py <file1> [file2] ...")
        sys.exit(1)
    
    checker = WindowsConnectionChecker()
    all_passed = True
    
    for file_path in sys.argv[1:]:
        path = Path(file_path)
        if path.exists() and path.suffix in ['.yml', '.yaml']:
            if not checker.check_file(path):
                all_passed = False
    
    # Report results
    if checker.violations:
        print("Windows Connection Security Violations Found:")
        for violation in checker.violations:
            print(f"  ❌ {violation}")
        print(f"\nFiles checked: {checker.files_checked}")
        print(f"Violations: {len(checker.violations)}")
        sys.exit(1)
    else:
        print(f"✅ Windows connection security check passed ({checker.files_checked} files)")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

##### Execution Environment Validation

```python
#!/usr/bin/env python3
# scripts/validate-ee-usage.py

import sys
import yaml
import re
from pathlib import Path
from typing import Dict, List, Any

class ExecutionEnvironmentValidator:
    """Validates Execution Environment specifications and usage."""
    
    APPROVED_REGISTRIES = [
        'registry.company.com/automation',
        'quay.io/ansible',
        'registry.redhat.io'
    ]
    
    APPROVED_BASE_IMAGES = [
        'registry.redhat.io/ubi9/ubi',
        'registry.company.com/automation/ee-base'
    ]
    
    REQUIRED_LABELS = ['maintainer', 'version', 'description']
    
    def __init__(self):
        self.violations = []
        self.warnings = []
    
    def validate_file(self, file_path: Path) -> bool:
        """Validate an execution-environment.yml file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                ee_spec = yaml.safe_load(f)
            
            return self._validate_specification(ee_spec, file_path)
            
        except yaml.YAMLError as e:
            self.violations.append(f"{file_path}: YAML parse error: {e}")
            return False
        except Exception as e:
            self.violations.append(f"{file_path}: Validation error: {e}")
            return False
    
    def _validate_specification(self, spec: Dict[str, Any], file_path: Path) -> bool:
        """Validate the EE specification structure and content."""
        violations_found = False
        
        # Check specification version
        version = spec.get('version')
        if version != 3:
            self.violations.append(
                f"{file_path}: EE specification version must be 3, found: {version}"
            )
            violations_found = True
        
        # Validate images section
        if 'images' in spec:
            violations_found |= self._validate_images(spec['images'], file_path)
        else:
            self.violations.append(f"{file_path}: Missing required 'images' section")
            violations_found = True
        
        # Validate dependencies
        if 'dependencies' in spec:
            violations_found |= self._validate_dependencies(spec['dependencies'], file_path)
        
        # Validate build steps
        if 'additional_build_steps' in spec:
            violations_found |= self._validate_build_steps(spec['additional_build_steps'], file_path)
        
        return not violations_found
    
    def _validate_images(self, images: Dict[str, Any], file_path: Path) -> bool:
        """Validate the images section."""
        violations_found = False
        
        if 'base_image' not in images:
            self.violations.append(f"{file_path}: Missing 'base_image' specification")
            return True
        
        base_image = images['base_image']
        if isinstance(base_image, dict):
            image_name = base_image.get('name', '')
        else:
            image_name = str(base_image)
        
        # Check if base image is from approved registry
        approved = False
        for approved_registry in self.APPROVED_REGISTRIES:
            if image_name.startswith(approved_registry):
                approved = True
                break
        
        if not approved:
            self.violations.append(
                f"{file_path}: Base image '{image_name}' is not from approved registry. "
                f"Approved registries: {', '.join(self.APPROVED_REGISTRIES)}"
            )
            violations_found = True
        
        # Check for version pinning
        if ':' not in image_name or image_name.endswith(':latest'):
            self.warnings.append(
                f"{file_path}: Base image should use specific version tag, not 'latest'"
            )
        
        return violations_found
    
    def _validate_dependencies(self, deps: Dict[str, Any], file_path: Path) -> bool:
        """Validate dependencies section."""
        violations_found = False
        
        # Check for required dependency files
        required_files = ['galaxy', 'python']
        for req_file in required_files:
            if req_file in deps:
                file_ref = deps[req_file]
                if isinstance(file_ref, str):
                    dep_file_path = Path(file_path).parent / file_ref
                    if not dep_file_path.exists():
                        self.violations.append(
                            f"{file_path}: Dependency file '{file_ref}' not found"
                        )
                        violations_found = True
        
        return violations_found
    
    def _validate_build_steps(self, build_steps: Dict[str, Any], file_path: Path) -> bool:
        """Validate additional build steps."""
        violations_found = False
        
        # Check for security best practices in build steps
        for step_type, steps in build_steps.items():
            if isinstance(steps, list):
                for step in steps:
                    if isinstance(step, str):
                        # Check for security anti-patterns
                        if 'pip install' in step.lower() and '--trusted-host' in step.lower():
                            self.violations.append(
                                f"{file_path}: Untrusted pip hosts not allowed in build steps"
                            )
                            violations_found = True
                        
                        if 'wget' in step.lower() and 'http://' in step.lower():
                            self.warnings.append(
                                f"{file_path}: Consider using HTTPS instead of HTTP in wget commands"
                            )
                        
                        if 'curl' in step.lower() and '-k' in step.lower():
                            self.violations.append(
                                f"{file_path}: Insecure curl options (-k) not allowed"
                            )
                            violations_found = True
        
        return violations_found

def main():
    """Main execution function."""
    if len(sys.argv) < 2:
        print("Usage: validate-ee-usage.py <execution-environment.yml> ...")
        sys.exit(1)
    
    validator = ExecutionEnvironmentValidator()
    all_passed = True
    
    for file_path in sys.argv[1:]:
        path = Path(file_path)
        if path.exists():
            if not validator.validate_file(path):
                all_passed = False
    
    # Report results
    if validator.violations:
        print("Execution Environment Validation Violations:")
        for violation in validator.violations:
            print(f"  ❌ {violation}")
    
    if validator.warnings:
        print("\nWarnings:")
        for warning in validator.warnings:
            print(f"  ⚠️  {warning}")
    
    if validator.violations:
        print(f"\nValidation failed with {len(validator.violations)} violations")
        sys.exit(1)
    else:
        print("✅ Execution Environment validation passed")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

### IDE Integration

#### VS Code Extension Configuration

```json
{
  "name": "aap-governance-extension",
  "displayName": "AAP Governance Helper",
  "description": "Real-time validation for AAP governance policies",
  "version": "1.0.0",
  "engines": {
    "vscode": "^1.70.0"
  },
  "categories": ["Linters", "Other"],
  "activationEvents": [
    "onLanguage:yaml",
    "onLanguage:ansible"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "configuration": {
      "type": "object",
      "title": "AAP Governance",
      "properties": {
        "aapGovernance.enableRealTimeValidation": {
          "type": "boolean",
          "default": true,
          "description": "Enable real-time governance validation"
        },
        "aapGovernance.strictMode": {
          "type": "boolean",
          "default": false,
          "description": "Enable strict mode for all policies"
        }
      }
    },
    "commands": [
      {
        "command": "aapGovernance.validateFile",
        "title": "Validate AAP Governance",
        "category": "AAP"
      }
    ],
    "languages": [
      {
        "id": "ansible",
        "extensions": [".yml", ".yaml"],
        "configuration": "./language-configuration.json"
      }
    ]
  }
}
```

## Build Time Enforcement

### CI/CD Pipeline Integration

#### GitHub Actions Workflow

```yaml
# .github/workflows/governance-enforcement.yml
---
name: AAP Governance Enforcement

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

env:
  PYTHON_VERSION: '3.11'
  ANSIBLE_VERSION: '2.15.5'

jobs:
  governance-check:
    name: Governance Policy Validation
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Cache Python dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-
      
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install ansible-core==${{ env.ANSIBLE_VERSION }}
          pip install ansible-lint yamllint
          pip install -r requirements.txt
          ansible-galaxy install -r requirements.yml
      
      - name: Run YAML linting
        run: |
          yamllint --config-file .yamllint .
      
      - name: Run Ansible linting
        run: |
          ansible-lint --profile=production --sarif-file ansible-lint.sarif
      
      - name: Upload Ansible lint results
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: ansible-lint.sarif
      
      - name: Windows connection security check
        run: |
          find . -name "*.yml" -o -name "*.yaml" | \
          xargs python scripts/check-windows-connections.py
      
      - name: Execution Environment validation
        run: |
          find . -name "execution-environment.yml" | \
          xargs python scripts/validate-ee-usage.py
      
      - name: Credential usage validation
        run: |
          bash scripts/check-credential-usage.sh
      
      - name: Generate compliance report
        if: always()
        run: |
          python scripts/generate-compliance-report.py \
            --ansible-lint-sarif ansible-lint.sarif \
            --output compliance-report.json
      
      - name: Upload compliance report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: compliance-report
          path: compliance-report.json

  security-scan:
    name: Security Scanning
    runs-on: ubuntu-latest
    needs: governance-check
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Run Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Run Semgrep security scan
        uses: semgrep/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/secrets
            p/ansible
      
      - name: Dependency vulnerability scan
        run: |
          pip install safety
          safety check --json --output safety-report.json
        continue-on-error: true
      
      - name: Upload security scan results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: security-scan-results
          path: |
            safety-report.json
            semgrep-results.json

  molecule-testing:
    name: Molecule Testing
    runs-on: ubuntu-latest
    if: contains(github.event.pull_request.changed_files, 'molecule/') || contains(github.event.pull_request.changed_files, 'roles/')
    
    strategy:
      matrix:
        scenario: [default, centos8, ubuntu20]
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install Molecule and dependencies
        run: |
          pip install molecule[podman] ansible-core
          ansible-galaxy install -r requirements.yml
      
      - name: Run Molecule tests
        run: |
          molecule test -s ${{ matrix.scenario }}
        env:
          ANSIBLE_FORCE_COLOR: '1'
      
      - name: Upload Molecule test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: molecule-test-results-${{ matrix.scenario }}
          path: molecule/*/molecule.log

  policy-as-code:
    name: Policy as Code Validation
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Install OPA (Open Policy Agent)
        run: |
          curl -L -o opa https://openpolicyagent.org/downloads/v0.57.0/opa_linux_amd64_static
          chmod 755 ./opa
          sudo mv opa /usr/local/bin
      
      - name: Validate Rego policies
        run: |
          opa fmt --diff policies/
          opa test policies/
      
      - name: Evaluate policies against Ansible content
        run: |
          python scripts/evaluate-policies.py \
            --policies policies/ \
            --content . \
            --output policy-evaluation.json
      
      - name: Upload policy evaluation results
        uses: actions/upload-artifact@v3
        with:
          name: policy-evaluation
          path: policy-evaluation.json
```

### Quality Gates Configuration

#### SonarQube Integration

```yaml
# sonar-project.properties
sonar.projectKey=aap-automation-content
sonar.projectName=AAP Automation Content
sonar.projectVersion=1.0

# Source configuration
sonar.sources=.
sonar.exclusions=**/node_modules/**,**/.git/**,**/venv/**,**/__pycache__/**

# Language-specific settings
sonar.yaml.file.suffixes=.yml,.yaml
sonar.python.coverage.reportPaths=coverage.xml

# Quality gate configuration
sonar.qualitygate.wait=true

# Custom rules for Ansible
sonar.ansible.lint.reportPath=ansible-lint.sarif
sonar.yaml.lint.reportPath=yamllint.json

# Security hotspots
sonar.security.hotspots.file.suffixes=.yml,.yaml,.py,.sh

# Coverage exclusions
sonar.coverage.exclusions=**/tests/**,**/molecule/**,scripts/**
```

## Runtime Enforcement

### AAP Organization Controls

#### Job Template Restrictions

```python
#!/usr/bin/env python3
# scripts/aap-org-policy-enforcer.py

import requests
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class PolicyViolation:
    """Represents a policy violation in AAP."""
    resource_type: str
    resource_id: int
    resource_name: str
    violation_type: str
    description: str
    severity: str  # 'low', 'medium', 'high', 'critical'

class AAPPolicyEnforcer:
    """Enforces governance policies within AAP organization."""
    
    def __init__(self, controller_url: str, username: str, password: str):
        self.controller_url = controller_url.rstrip('/')
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Policy definitions
        self.approved_ee_images = [
            'registry.company.com/automation/ee-base',
            'registry.company.com/automation/ee-windows',
            'registry.company.com/automation/ee-network',
            'registry.company.com/automation/ee-cloud'
        ]
        
        self.prohibited_modules = [
            'shell',  # Use command module with specific args
            'raw',    # Generally not needed with proper modules
        ]
        
        self.required_credential_types = {
            'windows': ['Machine', 'Vault'],
            'network': ['Machine', 'Network'],
            'cloud': ['Cloud Credential']
        }
    
    def authenticate(self) -> bool:
        """Authenticate with AAP Controller."""
        try:
            response = self.session.get(f"{self.controller_url}/api/v2/me/")
            response.raise_for_status()
            logging.info("Successfully authenticated with AAP Controller")
            return True
        except requests.RequestException as e:
            logging.error(f"Authentication failed: {e}")
            return False
    
    def get_job_templates(self) -> List[Dict[str, Any]]:
        """Retrieve all job templates from AAP."""
        templates = []
        url = f"{self.controller_url}/api/v2/job_templates/"
        
        while url:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            templates.extend(data['results'])
            url = data.get('next')
        
        return templates
    
    def validate_job_template(self, template: Dict[str, Any]) -> List[PolicyViolation]:
        """Validate a job template against governance policies."""
        violations = []
        
        # Check execution environment
        ee_image = template.get('execution_environment')
        if ee_image:
            violations.extend(self._validate_execution_environment(template, ee_image))
        else:
            violations.append(PolicyViolation(
                resource_type='job_template',
                resource_id=template['id'],
                resource_name=template['name'],
                violation_type='missing_execution_environment',
                description='Job template must specify an execution environment',
                severity='high'
            ))
        
        # Check project and playbook
        violations.extend(self._validate_project_settings(template))
        
        # Check credential requirements
        violations.extend(self._validate_credentials(template))
        
        # Check variable security
        violations.extend(self._validate_template_variables(template))
        
        return violations
    
    def _validate_execution_environment(self, template: Dict[str, Any], ee_id: int) -> List[PolicyViolation]:
        """Validate execution environment compliance."""
        violations = []
        
        # Get EE details
        ee_response = self.session.get(f"{self.controller_url}/api/v2/execution_environments/{ee_id}/")
        if ee_response.status_code != 200:
            violations.append(PolicyViolation(
                resource_type='job_template',
                resource_id=template['id'],
                resource_name=template['name'],
                violation_type='invalid_execution_environment',
                description=f'Cannot validate execution environment {ee_id}',
                severity='high'
            ))
            return violations
        
        ee_data = ee_response.json()
        ee_image = ee_data.get('image', '')
        
        # Check if EE image is approved
        approved = False
        for approved_image in self.approved_ee_images:
            if ee_image.startswith(approved_image):
                approved = True
                break
        
        if not approved:
            violations.append(PolicyViolation(
                resource_type='job_template',
                resource_id=template['id'],
                resource_name=template['name'],
                violation_type='unapproved_execution_environment',
                description=f'Execution environment image "{ee_image}" is not approved',
                severity='critical'
            ))
        
        # Check for latest tag usage
        if ee_image.endswith(':latest'):
            violations.append(PolicyViolation(
                resource_type='job_template',
                resource_id=template['id'],
                resource_name=template['name'],
                violation_type='latest_tag_usage',
                description='Execution environment should not use "latest" tag',
                severity='medium'
            ))
        
        return violations
    
    def _validate_project_settings(self, template: Dict[str, Any]) -> List[PolicyViolation]:
        """Validate project and playbook settings."""
        violations = []
        
        project_id = template.get('project')
        if not project_id:
            violations.append(PolicyViolation(
                resource_type='job_template',
                resource_id=template['id'],
                resource_name=template['name'],
                violation_type='missing_project',
                description='Job template must be associated with a project',
                severity='high'
            ))
            return violations
        
        # Get project details
        project_response = self.session.get(f"{self.controller_url}/api/v2/projects/{project_id}/")
        if project_response.status_code == 200:
            project_data = project_response.json()
            
            # Check SCM type
            scm_type = project_data.get('scm_type')
            if scm_type not in ['git']:
                violations.append(PolicyViolation(
                    resource_type='job_template',
                    resource_id=template['id'],
                    resource_name=template['name'],
                    violation_type='unsupported_scm_type',
                    description=f'SCM type "{scm_type}" is not approved. Use Git.',
                    severity='medium'
                ))
            
            # Check for local project (not allowed in production)
            if scm_type == '':
                violations.append(PolicyViolation(
                    resource_type='job_template',
                    resource_id=template['id'],
                    resource_name=template['name'],
                    violation_type='local_project',
                    description='Local projects are not allowed in production',
                    severity='high'
                ))
        
        return violations
    
    def _validate_credentials(self, template: Dict[str, Any]) -> List[PolicyViolation]:
        """Validate credential requirements and security."""
        violations = []
        
        # Get associated credentials
        credentials_url = f"{self.controller_url}/api/v2/job_templates/{template['id']}/credentials/"
        cred_response = self.session.get(credentials_url)
        
        if cred_response.status_code == 200:
            credentials = cred_response.json()['results']
            
            # Check for required credential types based on template type
            template_name = template['name'].lower()
            required_creds = []
            
            if 'windows' in template_name or 'win' in template_name:
                required_creds = self.required_credential_types['windows']
            elif 'network' in template_name or 'cisco' in template_name or 'juniper' in template_name:
                required_creds = self.required_credential_types['network']
            elif 'aws' in template_name or 'azure' in template_name or 'gcp' in template_name:
                required_creds = self.required_credential_types['cloud']
            
            # Validate credential types are present
            present_types = [cred['credential_type_name'] for cred in credentials]
            for required_type in required_creds:
                if required_type not in present_types:
                    violations.append(PolicyViolation(
                        resource_type='job_template',
                        resource_id=template['id'],
                        resource_name=template['name'],
                        violation_type='missing_required_credential',
                        description=f'Missing required credential type: {required_type}',
                        severity='high'
                    ))
        
        return violations
    
    def _validate_template_variables(self, template: Dict[str, Any]) -> List[PolicyViolation]:
        """Validate template variables for security compliance."""
        violations = []
        
        extra_vars = template.get('extra_vars', '{}')
        try:
            variables = json.loads(extra_vars)
            
            # Check for hardcoded credentials
            sensitive_patterns = [
                'password', 'passwd', 'pwd', 'secret', 'key', 'token',
                'api_key', 'access_key', 'private_key'
            ]
            
            for var_name, var_value in variables.items():
                var_name_lower = var_name.lower()
                
                # Check for sensitive variable names with hardcoded values
                for pattern in sensitive_patterns:
                    if pattern in var_name_lower and isinstance(var_value, str) and var_value:
                        violations.append(PolicyViolation(
                            resource_type='job_template',
                            resource_id=template['id'],
                            resource_name=template['name'],
                            violation_type='hardcoded_credential',
                            description=f'Variable "{var_name}" appears to contain hardcoded credentials',
                            severity='critical'
                        ))
                
                # Check for Windows connection insecure settings
                if var_name == 'ansible_winrm_server_cert_validation' and var_value != 'validate':
                    violations.append(PolicyViolation(
                        resource_type='job_template',
                        resource_id=template['id'],
                        resource_name=template['name'],
                        violation_type='insecure_winrm_config',
                        description='Windows certificate validation must be enabled',
                        severity='high'
                    ))
                
                if var_name == 'ansible_port' and str(var_value) == '5985':
                    violations.append(PolicyViolation(
                        resource_type='job_template',
                        resource_id=template['id'],
                        resource_name=template['name'],
                        violation_type='insecure_winrm_port',
                        description='Windows connections must use HTTPS port 5986, not HTTP 5985',
                        severity='critical'
                    ))
        
        except json.JSONDecodeError:
            violations.append(PolicyViolation(
                resource_type='job_template',
                resource_id=template['id'],
                resource_name=template['name'],
                violation_type='invalid_extra_vars',
                description='Extra variables contain invalid JSON',
                severity='medium'
            ))
        
        return violations
    
    def enforce_policies(self) -> Dict[str, Any]:
        """Run policy enforcement across all job templates."""
        if not self.authenticate():
            return {'error': 'Authentication failed'}
        
        job_templates = self.get_job_templates()
        all_violations = []
        
        for template in job_templates:
            violations = self.validate_job_template(template)
            all_violations.extend(violations)
        
        # Categorize violations by severity
        violations_by_severity = {
            'critical': [v for v in all_violations if v.severity == 'critical'],
            'high': [v for v in all_violations if v.severity == 'high'],
            'medium': [v for v in all_violations if v.severity == 'medium'],
            'low': [v for v in all_violations if v.severity == 'low']
        }
        
        return {
            'total_templates_checked': len(job_templates),
            'total_violations': len(all_violations),
            'violations_by_severity': {
                severity: len(violations) 
                for severity, violations in violations_by_severity.items()
            },
            'violations': [
                {
                    'resource_type': v.resource_type,
                    'resource_id': v.resource_id,
                    'resource_name': v.resource_name,
                    'violation_type': v.violation_type,
                    'description': v.description,
                    'severity': v.severity
                }
                for v in all_violations
            ]
        }

def main():
    """Main execution function for policy enforcement."""
    import os
    import argparse
    
    parser = argparse.ArgumentParser(description='AAP Policy Enforcement')
    parser.add_argument('--controller-url', required=True, help='AAP Controller URL')
    parser.add_argument('--username', help='AAP username')
    parser.add_argument('--password', help='AAP password')
    parser.add_argument('--output', help='Output file for results')
    parser.add_argument('--format', choices=['json', 'yaml', 'csv'], default='json')
    args = parser.parse_args()
    
    # Get credentials from environment if not provided
    username = args.username or os.environ.get('AAP_USERNAME')
    password = args.password or os.environ.get('AAP_PASSWORD')
    
    if not username or not password:
        print("Error: Username and password must be provided via arguments or environment variables")
        return 1
    
    # Run policy enforcement
    enforcer = AAPPolicyEnforcer(args.controller_url, username, password)
    results = enforcer.enforce_policies()
    
    # Output results
    if args.format == 'json':
        output = json.dumps(results, indent=2)
    elif args.format == 'yaml':
        import yaml
        output = yaml.dump(results, default_flow_style=False)
    elif args.format == 'csv':
        import csv
        import io
        
        output_buffer = io.StringIO()
        writer = csv.writer(output_buffer)
        writer.writerow(['Resource Type', 'Resource ID', 'Resource Name', 'Violation Type', 'Description', 'Severity'])
        
        for violation in results.get('violations', []):
            writer.writerow([
                violation['resource_type'],
                violation['resource_id'],
                violation['resource_name'],
                violation['violation_type'],
                violation['description'],
                violation['severity']
            ])
        
        output = output_buffer.getvalue()
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
    else:
        print(output)
    
    # Return exit code based on critical violations
    critical_violations = results.get('violations_by_severity', {}).get('critical', 0)
    return 1 if critical_violations > 0 else 0

if __name__ == "__main__":
    exit(main())
```

### Network Controls

#### Firewall Rules Configuration

```yaml
# Network controls for AAP enforcement
network_controls:
  firewall_rules:
    # Block HTTP WinRM (port 5985)
    - name: block-winrm-http
      action: deny
      protocol: tcp
      port: 5985
      source: automation_networks
      destination: windows_hosts
      log: true
      description: "Block insecure WinRM HTTP connections"
    
    # Allow HTTPS WinRM (port 5986)
    - name: allow-winrm-https
      action: allow
      protocol: tcp
      port: 5986
      source: automation_networks
      destination: windows_hosts
      log: true
      description: "Allow secure WinRM HTTPS connections"
    
    # Block production egress for development EEs
    - name: block-dev-ee-prod-egress
      action: deny
      source: dev_execution_environments
      destination: production_networks
      log: true
      description: "Prevent development EEs from accessing production"
    
    # Monitor and log all automation traffic
    - name: log-automation-traffic
      action: allow
      source: automation_networks
      destination: managed_hosts
      log: true
      log_level: info
      description: "Log all automation connections for audit"

  network_segmentation:
    automation_vlans:
      - vlan_id: 100
        name: "aap-controllers"
        subnet: "10.100.0.0/24"
        description: "AAP Controller instances"
      
      - vlan_id: 101
        name: "execution-environments"
        subnet: "10.101.0.0/24"
        description: "Execution Environment runtime"
      
      - vlan_id: 102
        name: "development-automation"
        subnet: "10.102.0.0/24"
        description: "Development and testing automation"
    
    access_control_lists:
      - name: "aap-controller-acl"
        rules:
          - permit: tcp
            source: "admin_networks"
            destination: "aap-controllers"
            ports: [443, 22]
          
          - permit: tcp
            source: "aap-controllers"
            destination: "execution-environments"
            ports: [any]
          
          - deny: any
            source: any
            destination: "aap-controllers"
            log: true

  monitoring:
    connection_logging:
      enabled: true
      log_destination: "siem_system"
      log_format: "json"
      fields:
        - timestamp
        - source_ip
        - destination_ip
        - port
        - protocol
        - action
        - automation_user
        - job_template_id
    
    alerting:
      blocked_connections:
        enabled: true
        threshold: 5  # Alert after 5 blocked attempts
        window: "5m"
        
      unusual_patterns:
        enabled: true
        ml_detection: true
        baseline_period: "30d"
```

## Monitoring and Alerting

### Compliance Monitoring Dashboard

#### Prometheus Metrics Configuration

```yaml
# Prometheus metrics for governance enforcement
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "governance_rules.yml"

scrape_configs:
  - job_name: 'aap-governance-metrics'
    static_configs:
      - targets: ['localhost:9090']
    
    metrics_path: /api/v2/metrics/governance
    scrape_interval: 30s
    
    basic_auth:
      username: monitoring
      password_file: /etc/prometheus/aap_password

  - job_name: 'pre-commit-metrics'
    static_configs:
      - targets: ['git-metrics-exporter:8080']
    
    scrape_interval: 60s

  - job_name: 'network-enforcement'
    static_configs:
      - targets: ['firewall-exporter:9100']
    
    scrape_interval: 30s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

# Custom governance rules
governance_rules:
  groups:
    - name: governance.rules
      rules:
        - alert: HighPolicyViolationRate
          expr: (governance_policy_violations_total / governance_templates_checked_total) > 0.1
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "High policy violation rate detected"
            description: "{{ $value | humanizePercentage }} of job templates have policy violations"
        
        - alert: CriticalSecurityViolation
          expr: governance_policy_violations{severity="critical"} > 0
          for: 0m
          labels:
            severity: critical
          annotations:
            summary: "Critical security policy violation detected"
            description: "Critical security violation in {{ $labels.resource_name }}: {{ $labels.violation_type }}"
        
        - alert: UnapprovedExecutionEnvironment
          expr: governance_unapproved_ee_usage > 0
          for: 1m
          labels:
            severity: high
          annotations:
            summary: "Unapproved execution environment in use"
            description: "{{ $value }} job templates using unapproved execution environments"
        
        - alert: InsecureWindowsConnection
          expr: governance_insecure_windows_connections > 0
          for: 0m
          labels:
            severity: critical
          annotations:
            summary: "Insecure Windows connection detected"
            description: "{{ $value }} insecure Windows connections detected"
```

#### Grafana Dashboard Configuration

```json
{
  "dashboard": {
    "id": null,
    "title": "AAP Governance Compliance",
    "tags": ["governance", "compliance", "aap"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Policy Compliance Overview",
        "type": "stat",
        "targets": [
          {
            "expr": "governance_compliance_score",
            "legendFormat": "Compliance Score"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 80},
                {"color": "green", "value": 95}
              ]
            },
            "unit": "percent"
          }
        }
      },
      {
        "id": 2,
        "title": "Policy Violations by Severity",
        "type": "piechart",
        "targets": [
          {
            "expr": "governance_policy_violations by (severity)",
            "legendFormat": "{{ severity }}"
          }
        ]
      },
      {
        "id": 3,
        "title": "Execution Environment Compliance",
        "type": "bargauge",
        "targets": [
          {
            "expr": "governance_ee_compliance_by_image",
            "legendFormat": "{{ ee_image }}"
          }
        ]
      },
      {
        "id": 4,
        "title": "Windows Connection Security Status",
        "type": "table",
        "targets": [
          {
            "expr": "governance_windows_connection_security",
            "format": "table"
          }
        ]
      },
      {
        "id": 5,
        "title": "Violation Trends",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(governance_policy_violations_total[1h])",
            "legendFormat": "Violations per hour"
          }
        ]
      }
    ],
    "time": {
      "from": "now-24h",
      "to": "now"
    },
    "refresh": "5m"
  }
}
```

### Automated Remediation

#### Auto-Remediation Scripts

```python
#!/usr/bin/env python3
# scripts/auto-remediation.py

import logging
import json
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class RemediationAction:
    """Represents an automated remediation action."""
    violation_type: str
    action_type: str  # 'fix', 'notify', 'block'
    description: str
    script: str
    approval_required: bool = False

class AutoRemediationEngine:
    """Automated remediation for governance violations."""
    
    def __init__(self):
        self.remediation_actions = {
            'unapproved_execution_environment': RemediationAction(
                violation_type='unapproved_execution_environment',
                action_type='block',
                description='Block job template with unapproved EE',
                script='disable_job_template',
                approval_required=True
            ),
            'insecure_winrm_config': RemediationAction(
                violation_type='insecure_winrm_config',
                action_type='fix',
                description='Update WinRM configuration to secure settings',
                script='fix_winrm_config',
                approval_required=False
            ),
            'hardcoded_credential': RemediationAction(
                violation_type='hardcoded_credential',
                action_type='block',
                description='Block template with hardcoded credentials',
                script='disable_and_notify',
                approval_required=False
            ),
            'latest_tag_usage': RemediationAction(
                violation_type='latest_tag_usage',
                action_type='notify',
                description='Notify team about latest tag usage',
                script='send_notification',
                approval_required=False
            )
        }
    
    def process_violation(self, violation: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single violation and apply remediation."""
        violation_type = violation.get('violation_type')
        
        if violation_type not in self.remediation_actions:
            return {
                'status': 'no_action',
                'message': f'No remediation action defined for {violation_type}'
            }
        
        action = self.remediation_actions[violation_type]
        
        if action.approval_required:
            return self._request_approval(violation, action)
        else:
            return self._execute_remediation(violation, action)
    
    def _execute_remediation(self, violation: Dict[str, Any], action: RemediationAction) -> Dict[str, Any]:
        """Execute the remediation action."""
        try:
            if action.script == 'fix_winrm_config':
                return self._fix_winrm_config(violation)
            elif action.script == 'disable_job_template':
                return self._disable_job_template(violation)
            elif action.script == 'disable_and_notify':
                return self._disable_and_notify(violation)
            elif action.script == 'send_notification':
                return self._send_notification(violation)
            else:
                return {
                    'status': 'error',
                    'message': f'Unknown remediation script: {action.script}'
                }
        except Exception as e:
            logging.error(f"Remediation failed for {violation}: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _fix_winrm_config(self, violation: Dict[str, Any]) -> Dict[str, Any]:
        """Fix WinRM configuration in job template."""
        # Implementation would update job template variables
        # This is a placeholder for the actual AAP API calls
        
        logging.info(f"Fixing WinRM config for template {violation['resource_name']}")
        
        # Simulated fix
        secure_config = {
            'ansible_winrm_server_cert_validation': 'validate',
            'ansible_winrm_transport': 'kerberos',
            'ansible_port': 5986
        }
        
        return {
            'status': 'fixed',
            'message': 'WinRM configuration updated to secure settings',
            'changes': secure_config
        }
    
    def _disable_job_template(self, violation: Dict[str, Any]) -> Dict[str, Any]:
        """Disable job template pending review."""
        logging.warning(f"Disabling job template {violation['resource_name']} due to {violation['violation_type']}")
        
        return {
            'status': 'disabled',
            'message': f"Job template disabled pending security review",
            'ticket_created': 'SEC-12345'
        }
    
    def _send_notification(self, violation: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification about violation."""
        logging.info(f"Sending notification for {violation['violation_type']} in {violation['resource_name']}")
        
        return {
            'status': 'notified',
            'message': 'Notification sent to responsible team',
            'notification_id': 'NOTIF-67890'
        }

def main():
    """Main execution for auto-remediation."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: auto-remediation.py <violations_file.json>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        violations_data = json.load(f)
    
    engine = AutoRemediationEngine()
    results = []
    
    for violation in violations_data.get('violations', []):
        result = engine.process_violation(violation)
        results.append({
            'violation': violation,
            'remediation': result
        })
    
    # Output results
    output = {
        'timestamp': '2025-10-22T10:00:00Z',
        'total_violations': len(violations_data.get('violations', [])),
        'remediation_results': results
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
```

## Troubleshooting and Maintenance

### Common Issues and Resolutions

#### Pre-commit Hook Failures

```yaml
issue: "Pre-commit hooks failing consistently"
symptoms:
  - Hooks timeout or fail to execute
  - Performance degradation in commit process
  - Inconsistent results across team members

diagnosis:
  - Check Python environment consistency
  - Verify pre-commit version alignment
  - Review hook configuration conflicts

resolution:
  1. Update pre-commit framework:
     ```bash
     pip install --upgrade pre-commit
     pre-commit autoupdate
     ```
  
  2. Clear pre-commit cache:
     ```bash
     pre-commit clean
     pre-commit install --install-hooks
     ```
  
  3. Validate configuration:
     ```bash
     pre-commit validate-config
     pre-commit validate-manifest
     ```

prevention:
  - Pin pre-commit versions in requirements.txt
  - Regular maintenance schedule
  - Automated hook updates in CI/CD
```

#### AAP Policy Enforcement Issues

```yaml
issue: "AAP policy checks returning false positives"
symptoms:
  - Valid configurations flagged as violations
  - Approved execution environments marked as non-compliant
  - Credential validation errors

diagnosis:
  - Review policy configuration accuracy
  - Check AAP API connectivity
  - Validate approval lists and patterns

resolution:
  1. Update approval patterns:
     ```python
     # Update approved_ee_images list
     self.approved_ee_images = [
         'registry.company.com/automation/ee-base',
         'registry.company.com/automation/ee-windows:2025.*'
     ]
     ```
  
  2. Test policy logic:
     ```bash
     python scripts/test-policy-logic.py --dry-run
     ```
  
  3. Validate against known-good templates:
     ```bash
     python scripts/aap-org-policy-enforcer.py --validate-only
     ```
```

### Maintenance Procedures

#### Regular Maintenance Tasks

```yaml
daily_tasks:
  - name: "Check enforcement pipeline health"
    script: "scripts/check-pipeline-health.sh"
    schedule: "0 8 * * *"  # 8 AM daily
    
  - name: "Update security scan databases"
    script: "scripts/update-security-dbs.sh"
    schedule: "0 2 * * *"  # 2 AM daily

weekly_tasks:
  - name: "Review policy violation trends"
    script: "scripts/violation-trend-analysis.py"
    schedule: "0 9 * * 1"  # 9 AM Monday
    
  - name: "Update ansible-lint rules"
    script: "scripts/update-lint-rules.sh"
    schedule: "0 10 * * 1"  # 10 AM Monday
    
  - name: "Clean up old enforcement logs"
    script: "scripts/cleanup-logs.sh"
    schedule: "0 3 * * 1"  # 3 AM Monday

monthly_tasks:
  - name: "Review and update policies"
    description: "Manual review of policy effectiveness"
    schedule: "First Friday of month"
    
  - name: "Performance optimization review"
    script: "scripts/performance-review.py"
    schedule: "0 9 1 * *"  # 9 AM first of month
    
  - name: "Security control audit"
    description: "Comprehensive security control validation"
    schedule: "Second Tuesday of month"
```

## Document Control

### Revision History

| Version | Date | Changes | Approved By |
|---------|------|---------|-------------|
| 1.0-draft | 2025-10-22 | Initial comprehensive reference | TBD |

### Document Maintenance

- **Owner**: Platform Engineering and Security Teams
- **Review Frequency**: Quarterly (technical details), Annually (policies)
- **Next Review**: 2025-01-22
- **Related Documents**: 
  - AAP Windows Connection Standard
  - AAP Development Standards Policy
  - Security Compliance Framework