# Molecule Testing Guide for Enterprise AAP

⚠️ **WORK IN PROGRESS** ⚠️
> **Status**: Molecule testing functionality is currently under development and has not been fully validated. The configuration exists but may require additional setup and testing. Consider this experimental functionality.

## Overview

Molecule provides automated testing for Ansible playbooks and roles, ensuring code quality and reliability in enterprise environments. This guide covers our Molecule testing strategy for the Confluence automation project.

## What Molecule Tests

### 1. **Syntax Validation**
- YAML syntax correctness
- Ansible playbook structure
- Template rendering logic

### 2. **Idempotency Testing**
- Ensures playbooks can run multiple times safely
- Verifies no unnecessary changes on re-runs
- Critical for production automation

### 3. **Functional Testing**
- Template generation and processing
- File creation and permissions
- API interaction patterns (mocked)

### 4. **Security Validation**
- File permissions verification
- Sensitive data exposure checks
- Security best practices compliance

## Test Scenarios

### Default Scenario (`molecule/default/`)
**Purpose**: Basic functionality testing with minimal dependencies

**What it tests**:
- Template rendering with test data
- Pandoc HTML conversion
- File creation and permissions
- Basic security checks

**Use case**: Quick development feedback

### Playbook Test Scenario (`molecule/playbook-test/`)
**Purpose**: Full playbook testing with mocked external services

**What it tests**:
- Complete playbook execution flow
- Confluence API interactions (mocked)
- Error handling and recovery
- End-to-end template processing

**Use case**: Pre-deployment validation

## Running Tests

### Quick Development Testing
```bash
# Run linting only
make molecule-lint

# Run basic scenario
make test-molecule

# Run full playbook test
make test-playbook-molecule
```

### Full Test Suite
```bash
# Complete testing workflow
make test-all

# CI/CD testing
make ci
```

### Manual Molecule Commands
```bash
# Test specific scenario
molecule test -s default
molecule test -s playbook-test

# Development workflow
molecule converge    # Setup test environment
molecule verify      # Run verification tests
molecule destroy     # Clean up

# Debug failing tests
molecule converge -s playbook-test
molecule login       # SSH into test container
molecule verify      # Re-run verification
```

## Test Environment

### Container Platform
- **Base Image**: `quay.io/ansible/molecule-ubuntu:latest`
- **Driver**: Docker (enterprise standard)
- **Privileges**: Limited for security
- **Networking**: Isolated test environment

### Mock Services
- **Confluence API**: Flask-based mock server
- **External Dependencies**: Stubbed for testing
- **Authentication**: Test tokens only

## Test Data Management

### Variables Override
```yaml
# Test-specific variables in converge.yml
vars:
  confluence_url: "http://localhost:8080/mock"
  confluence_auth: "dGVzdDp0ZXN0"  # test:test
  project_name: "Test Project"
```

### Sensitive Data Protection
- Real credentials never in test code
- Mock authentication tokens
- Sanitized test data sets

## Verification Tests

### File Generation Checks
```yaml
- name: "Verify HTML files exist"
  ansible.builtin.stat:
    path: "/tmp/{{ item }}.html"
  register: html_files
```

### Content Validation
```yaml
- name: "Check template processing"
  ansible.builtin.shell: grep -q "{{ project_name }}" /tmp/main.md.html
```

### Security Scanning
```yaml
- name: "Security check - no sensitive data"
  ansible.builtin.shell: |
    ! grep -i "password\|secret\|token" /tmp/*.html
```

### Permission Verification
```yaml
- name: "Verify file permissions"
  ansible.builtin.assert:
    that:
      - item.stat.mode == "0644"
```

## CI/CD Integration

### GitLab CI/CD
```yaml
# .gitlab-ci.yml
molecule-test:
  stage: test
  image: quay.io/ansible/molecule
  services:
    - docker:dind
  variables:
    DOCKER_DRIVER: overlay2
  before_script:
    - pip install molecule[docker]
  script:
    - molecule test
  only:
    - merge_requests
    - main
```

### GitHub Actions
```yaml
# .github/workflows/molecule.yml
name: Molecule Test
on: [push, pull_request]
jobs:
  molecule:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          pip install molecule[docker]
          molecule test
```

### Jenkins Pipeline
```groovy
pipeline {
    agent any
    stages {
        stage('Molecule Test') {
            steps {
                sh '''
                    pip install molecule[docker]
                    molecule test
                '''
            }
        }
    }
    post {
        always {
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'molecule/default/reports',
                reportFiles: 'test-results.html',
                reportName: 'Molecule Test Results'
            ])
        }
    }
}
```

## Best Practices

### 1. **Test Isolation**
- Each scenario runs in clean environment
- No dependencies between test runs
- Reproducible test conditions

### 2. **Mock External Services**
- Never test against production APIs
- Use mock servers for external dependencies
- Simulate various response scenarios

### 3. **Security First**
- No real credentials in test code
- Secure file permissions verification
- Sensitive data exposure checks

### 4. **Performance Considerations**
- Keep test scenarios focused and fast
- Use pre-built images when possible
- Parallel test execution where applicable

### 5. **Documentation**
- Clear test descriptions
- Expected outcomes documented
- Failure troubleshooting guides

## Troubleshooting

### Common Issues

#### Docker Permission Errors
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Or run with sudo temporarily
sudo molecule test
```

#### Container Startup Failures
```bash
# Check Docker daemon
sudo systemctl status docker
sudo systemctl start docker

# Verify container image
docker pull quay.io/ansible/molecule-ubuntu:latest
```

#### Test Timeouts
```bash
# Increase timeout in molecule.yml
platforms:
  - name: instance
    docker_timeout: 300  # 5 minutes
```

#### Mock Server Issues
```bash
# Debug mock server
molecule converge
molecule login
curl http://localhost:8080/rest/api/content
```

### Debug Mode
```bash
# Run with verbose output
molecule --debug test

# Keep container running after test
molecule converge
# Run manual tests
molecule verify
# Clean up when done
molecule destroy
```

## Monitoring and Reporting

### Test Metrics
- **Test Success Rate**: Track across scenarios
- **Test Duration**: Monitor for performance regression
- **Coverage**: Ensure all playbook paths tested

### Reporting
- JUnit XML output for CI/CD integration
- HTML reports for detailed analysis
- Failed test artifacts preservation

## Enterprise Integration

### AAP Controller Integration
- Import tested playbooks to AAP
- Use Molecule results for promotion decisions
- Automated deployment pipelines

### Security Compliance
- Security scan integration
- Compliance check automation
- Audit trail maintenance

### Team Workflows
- Developer local testing
- PR/MR validation requirements
- Release gate criteria

## Support and Training

### Resources
- **Molecule Documentation**: https://molecule.readthedocs.io/
- **Internal Wiki**: Link to team documentation
- **Training Videos**: Team-specific tutorials

### Support Channels
- **Team Chat**: #ansible-testing
- **Office Hours**: Weekly Q&A sessions
- **Code Reviews**: Peer testing validation
