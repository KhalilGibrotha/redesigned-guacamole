# Enterprise YAML Linting Standards for Ansible Automation Platform

This document outlines the recommended YAML linting standards for our Ansible Automation Platform (AAP) environment.

## Overview

YAML linting helps ensure:
- **Consistency** across team members and projects
- **Readability** for easier maintenance and collaboration
- **Quality** by catching common syntax and formatting errors
- **Security** by enforcing safe practices
- **Automation** compatibility with CI/CD pipelines

## Linting Tools

We use two complementary tools:

### 1. yamllint
- **Purpose**: YAML syntax and formatting
- **Focus**: Indentation, line length, quotes, spacing
- **Configuration**: `.yamllint` file in project root

### 2. ansible-lint
- **Purpose**: Ansible-specific best practices
- **Focus**: Task structure, security, idempotency
- **Integration**: Works with yamllint configuration

## Configuration Rules Explained

### Line Length (120 characters)
```yaml
line-length:
  max: 120
  level: warning
  allow-non-breakable-words: true
  allow-non-breakable-inline-mappings: true
```
- **Rationale**: Balance between readability and modern wide screens
- **Best Practice**: Break long URLs and complex expressions across lines
- **Example**:
  ```yaml
  # Good
  url: >-
    {{ confluence_url }}/rest/api/content?title={{ project_name | urlencode }}
    &spaceKey={{ confluence_space }}&expand=version
  
  # Avoid
  url: "{{ confluence_url }}/rest/api/content?title={{ project_name | urlencode }}&spaceKey={{ confluence_space }}&expand=version"
  ```

### Indentation (2 spaces)
```yaml
indentation:
  spaces: 2
  indent-sequences: true
  check-multi-line-strings: false
```
- **Rationale**: Ansible standard, good readability
- **Best Practice**: Always use spaces, never tabs

### Boolean Values
```yaml
truthy:
  allowed-values: ['true', 'false']
  check-keys: false
```
- **Rationale**: Consistency and clarity
- **Best Practice**: Use `true`/`false` instead of `yes`/`no`

### Comments
```yaml
comments:
  min-spaces-from-content: 1
  require-starting-space: true
```
- **Best Practice**: Always include explanatory comments for complex logic

### Security Rules
```yaml
octal-values:
  forbid-implicit-octal: true
  forbid-explicit-octal: true
```
- **Rationale**: Prevents file permission security issues

## Integration with CI/CD

### Pre-commit Hook
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/adrienverge/yamllint
    rev: v1.33.0
    hooks:
      - id: yamllint
        args: [-c, .yamllint]
  
  - repo: https://github.com/ansible/ansible-lint
    rev: v6.20.0
    hooks:
      - id: ansible-lint
```

### GitLab CI/CD
```yaml
# .gitlab-ci.yml
lint:
  stage: test
  image: python:3.11
  before_script:
    - pip install yamllint ansible-lint
  script:
    - yamllint -c .yamllint .
    - ansible-lint
  only:
    - merge_requests
    - main
```

### GitHub Actions
```yaml
# .github/workflows/lint.yml
name: Lint
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          pip install yamllint ansible-lint
          yamllint -c .yamllint .
          ansible-lint
```

## Exception Handling

### Disabling Rules for Specific Files
```yaml
# At top of playbook file
# yamllint disable-file
---
# or for specific lines
- name: "Long URL example"  # yamllint disable-line rule:line-length
```

### Ansible-lint Skips
```yaml
- name: "Skip specific rule"
  command: /bin/true
  tags:
    - skip_ansible_lint
```

## Team Guidelines

### 1. **Mandatory Rules** (CI/CD fails)
- Document start marker (`---`)
- Indentation consistency
- No trailing spaces
- Maximum line length (warning at 120, error at 150)

### 2. **Recommended Rules** (warnings only)
- Consistent quoting style
- Comment formatting
- Empty line management

### 3. **Flexible Rules** (team discretion)
- Key ordering
- String quoting preferences

## VS Code Integration

### Extensions
- **YAML**: Red Hat YAML extension
- **Ansible**: Ansible extension for syntax highlighting
- **Lint**: Configure workspace settings:

```json
{
  "yaml.schemas": {
    "https://raw.githubusercontent.com/ansible/ansible-lint/main/src/ansiblelint/schemas/ansible.json#/$defs/playbook": "playbooks/*.yml",
    "https://raw.githubusercontent.com/ansible/ansible-lint/main/src/ansiblelint/schemas/ansible.json#/$defs/tasks": "tasks/*.yml"
  },
  "yaml.validate": true,
  "yaml.completion": true
}
```

## Common Issues and Solutions

### 1. **Long Lines**
```yaml
# Problem
- name: "Very long task name with lots of parameters that exceeds line length limits"

# Solution
- name: >-
    Very long task name with lots of parameters
    that can be broken across multiple lines
```

### 2. **Complex Conditionals**
```yaml
# Problem
when: condition1 and condition2 and condition3 and condition4

# Solution
when:
  - condition1
  - condition2
  - condition3
  - condition4
```

### 3. **URL Parameters**
```yaml
# Problem
url: "https://api.example.com/v1/resource?param1=value1&param2=value2&param3=value3"

# Solution
url: >-
  https://api.example.com/v1/resource?param1=value1
  &param2=value2&param3=value3
```

## Monitoring and Metrics

Track linting compliance across projects:
- **Linting pass rate** in CI/CD pipelines
- **Rule violation frequency** to identify training needs
- **Time to fix** linting issues for process improvement

## Training Resources

1. **Internal Documentation**: This guide
2. **Ansible Best Practices**: https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html
3. **YAML Specification**: https://yaml.org/spec/
4. **Team Workshops**: Monthly code review sessions

## Support

For questions or exceptions to these standards:
- **Team Lead**: Review and approve exceptions
- **DevOps Channel**: #ansible-help
- **Documentation**: Update this guide with approved exceptions
