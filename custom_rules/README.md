# Custom Ansible-lint Rules

This directory contains custom Ansible-lint rules that extend the standard linting capabilities with organization-specific best practices.

## Available Rules

### CUSTOM001: Use Package Module

**Rule ID**: `CUSTOM001`
**Severity**: MEDIUM
**Tags**: portability, modules, best-practice

**Description**: Tasks should use the generic `package` module instead of distribution-specific package managers like `yum`, `apt`, `dnf`, `zypper`, or `pacman` for better portability across different Linux distributions.

**Example - Bad**:
```yaml
- name: Install httpd package
  yum:
    name: httpd
    state: present
```

**Example - Good**:
```yaml
- name: Install httpd package
  package:
    name: httpd
    state: present
```

## How Custom Rules Are Used

1. **Automatic Detection**: The CI/CD pipeline automatically copies these custom rules to any repository that uses the workflow
2. **Configuration**: The `.ansible-lint` configuration file includes `rulesdir: ./custom_rules` to enable these rules
3. **Super Linter Integration**: The Super Linter environment includes `ANSIBLE_LINT_CUSTOM_RULES_DIR=custom_rules`

## Adding New Custom Rules

To add a new custom rule:

1. Create a new Python file in this directory (e.g., `my_custom_rule.py`)
2. Inherit from `AnsibleLintRule` class
3. Implement the required methods (`matchtask`, `matchplay`, etc.)
4. Define rule metadata (ID, shortdesc, description, severity, tags)

Example template:
```python
from ansiblelint.rules import AnsibleLintRule

class MyCustomRule(AnsibleLintRule):
    id = "CUSTOM00X"
    shortdesc = "Brief description"
    description = "Detailed description of the rule"
    severity = "MEDIUM"  # LOW, MEDIUM, HIGH, VERY_HIGH
    tags = ["custom", "best-practice"]

    def matchtask(self, task, file=None):
        # Implement your rule logic here
        return False  # Return True if rule is violated
```

## Testing Custom Rules

Use the `test_custom_rules.py` file to create test playbook content that should trigger your custom rules for validation.

## Integration Status

✅ **Enabled**: Custom rules are active in the CI/CD pipeline
✅ **Copied**: Rules are automatically copied to calling repositories
✅ **Configured**: ansible-lint is configured to use these rules
✅ **Documented**: This documentation explains usage and setup
