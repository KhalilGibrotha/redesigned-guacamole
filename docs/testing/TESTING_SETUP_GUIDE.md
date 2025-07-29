# Ansible Testing & Quality Assurance Setup

## Overview

This guide outlines the testing tools available for Ansible projects and how to run them locally or in CI/CD.

## Testing Stack

### 🔍 **Linting & Static Analysis**
- **yamllint**: YAML syntax and formatting validation
- **ansible-lint**: Ansible-specific best practices
- **Security scanning**: Automated secret detection

### 🧪 **Testing Framework** 
- **Molecule**: Comprehensive testing framework
- **Syntax validation**: Playbook structure verification
- **Template testing**: Jinja2 template validation

### 🛠️ **Automation Tools**
- **Makefile**: Simplified command interface
- **Pre-commit hooks**: Automatic validation before commits
- **CI/CD integration**: Ready for GitLab/GitHub/Jenkins

## Quick Start

### Daily Development Workflow
```bash
# Quick sanity check during development
make sanity-check

# Full development validation
make dev

# Before committing changes
make validate
```

### Available Commands

#### Basic Testing
```bash
make lint           # Run all linting checks
make test           # Syntax check playbook
make security-check # Security validation
```

#### Advanced Testing
```bash
make validate-templates  # Check template structure
make test-syntax        # Comprehensive syntax validation
make validate          # Full validation suite
```

#### Maintenance
```bash
make fix    # Auto-fix common issues
make clean  # Remove temporary files
```

## Testing Scenarios

### 1. **Sanity Checks** (`make sanity-check`)
**Purpose**: Quick validation for development

**Checks**:
- ✅ YAML syntax correctness
- ✅ Playbook structure validation
- ✅ Required files presence
- ✅ Template files existence

**Duration**: ~10 seconds

### 2. **Security Validation** (`make security-check`)
**Purpose**: Security compliance verification

**Checks**:
- 🔒 Secret exposure detection
- 🔒 File permission validation
- 🔒 Hardcoded URL identification
- 🔒 Credential leak prevention

**Duration**: ~5 seconds

### 3. **Template Validation** (`make validate-templates`)
**Purpose**: Jinja2 template structure verification

**Checks**:
- 📝 Template directory structure
- 📝 Required template files
- 📝 Template syntax validation
- 📝 Variable reference checking

**Duration**: ~15 seconds

## Quality Gates

### Development Quality Gates
1. **Pre-commit**: Automatic linting before commit
2. **Sanity check**: Quick validation during development
3. **Security scan**: Prevent credential exposure

### CI/CD Quality Gates
1. **Syntax validation**: Prevent broken playbooks
2. **Linting compliance**: Enforce coding standards
3. **Security verification**: Block unsafe deployments
4. **Template testing**: Ensure rendering works

## File Structure

```
confluence_test/
├── .yamllint                    # YAML linting configuration
├── .pre-commit-config.yaml      # Pre-commit hook configuration
├── molecule.cfg                 # Molecule global configuration
├── Makefile                     # Automation commands
├── YAML_LINTING_STANDARDS.md    # Enterprise linting guide
├── MOLECULE_TESTING_GUIDE.md    # Molecule testing documentation
├── molecule/                    # Test scenarios
│   ├── default/                 # Basic functionality tests
│   ├── playbook-test/          # Full playbook tests with mocks
│   └── syntax-check/           # Syntax validation tests
├── playbook.yml                # Main Ansible playbook
├── vars/vars.yml               # Variable definitions
└── docs/                       # Jinja2 templates
    ├── main.md.j2
    ├── platform_governance.md.j2
    ├── platform_runbook.md.j2
    ├── operator_runbook.md.j2
    └── training_enablement.md.j2
```

## Configuration Details

### YAML Linting (`.yamllint`)
- **Line length**: 120 characters (warning)
- **Indentation**: 2 spaces consistently
- **Boolean values**: `true`/`false` only
- **Security rules**: File permissions, octal values
- **Enterprise compliance**: ansible-lint compatibility

### Ansible Linting
- **Production profile**: Highest quality standards
- **Security focus**: Risky operations detection
- **Best practices**: Idempotency, error handling
- **Performance**: Optimized task structure

## Integration Examples

### GitLab CI/CD
```yaml
stages:
  - validate
  - test
  - deploy

lint:
  stage: validate
  script:
    - make validate
  only:
    - merge_requests
    - main

security:
  stage: validate
  script:
    - make security-check
  allow_failure: false
```

### GitHub Actions
```yaml
name: Quality Assurance
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make ci
```

### Jenkins Pipeline
```groovy
pipeline {
    agent any
    stages {
        stage('Validate') {
            steps {
                sh 'make validate'
            }
        }
        stage('Security') {
            steps {
                sh 'make security-check'
            }
        }
    }
}
```

## Best Practices

### 1. **Development Workflow**
```bash
# Start development
make clean

# During development
make sanity-check

# Before commit
make dev

# Before merge/deployment
make validate
```

### 2. **Team Standards**
- Run `make sanity-check` before every commit
- Use `make fix` to auto-resolve common issues
- Review security warnings in `make security-check`
- Validate templates with `make validate-templates`

### 3. **CI/CD Integration**
- Block merges on linting failures
- Require security check passes
- Generate test reports for tracking
- Use quality gates for deployment promotion

## Troubleshooting

### Common Issues

#### Linting Failures
```bash
# Fix common formatting issues
make fix

# Check specific rules
yamllint -c .yamllint playbook.yml
ansible-lint playbook.yml
```

#### Template Issues
```bash
# Validate specific template
make validate-templates

# Test template rendering
make test-render
```

#### Security Warnings
```bash
# Run detailed security scan
make security-check

# Check for exposed secrets
grep -r "password\|secret" . --include="*.yml"
```

### Getting Help

1. **Check documentation**: This guide and individual tool docs
2. **Run diagnostics**: `make sanity-check` for quick overview
3. **Team support**: Use established team channels
4. **Tool-specific help**: `yamllint --help`, `ansible-lint --help`

## Metrics and Monitoring

Track these quality metrics:
- **Linting pass rate**: Percentage of commits passing all lints
- **Security findings**: Number and type of security issues
- **Template coverage**: Percentage of templates with tests
- **Fix time**: Average time to resolve quality issues

## Next Steps

1. **Team Training**: Schedule workshops on quality tools
2. **Process Integration**: Add quality gates to team workflow
3. **Metrics Dashboard**: Set up quality tracking
4. **Continuous Improvement**: Regular review and updates

---

**Maintained by**: Platform Engineering Team  
**Last Updated**: July 2025  
**Version**: 1.0
