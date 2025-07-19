# Team Development Environment Setup Guide

## 🚀 Quick Setup for New Team Members

### 1. Editor Configuration (Required)
```bash
# Your repository already has .editorconfig - just install the plugin
# VS Code: Install "EditorConfig for VS Code" extension
# IntelliJ/PyCharm: Built-in support
# Vim: Install editorconfig-vim plugin
```

### 2. Python Environment Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies (your pyproject.toml handles this)
pip install -e .
pip install pre-commit

# Set up pre-commit hooks
pre-commit install
```

### 3. VS Code Recommended Extensions
Create this file in your repository: `.vscode/extensions.json`
```json
{
  "recommendations": [
    "editorconfig.editorconfig",
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.pylint",
    "redhat.ansible",
    "redhat.vscode-yaml",
    "ms-vscode.powershell",
    "wholroyd.ansible-vault",
    "samuelcolvin.jinjahtml"
  ]
}
```

### 4. Team Workflow Standards

#### Python Development
- **Formatter**: Black (already configured in pyproject.toml)
- **Linter**: Pylint + Flake8 (already configured)
- **Line Length**: 88 characters (Black standard)
- **Import Sorting**: isort with Black profile

#### Ansible Development  
- **YAML Formatter**: Prettier or VS Code YAML extension
- **Linter**: ansible-lint + yamllint (already configured)
- **Line Length**: 180 characters for long URLs/paths
- **Indentation**: 2 spaces, sequences indented

#### PowerShell Development
- **Formatter**: PowerShell extension built-in formatter
- **Linter**: PSScriptAnalyzer
- **Line Length**: 120 characters
- **Indentation**: 4 spaces

### 5. Git Workflow
```bash
# Before committing, these run automatically with pre-commit:
black .                    # Format Python code
isort .                    # Sort imports
pylint scripts/            # Check Python code quality
yamllint .                 # Check YAML formatting
ansible-lint playbooks/    # Check Ansible best practices
```

### 6. Testing Your Setup
```bash
# Test Python formatting
echo "x=1" > test.py && black test.py && cat test.py
# Should show: x = 1

# Test YAML linting
yamllint .github/workflows/

# Test Ansible linting (if you have playbooks)
ansible-lint playbooks/ || echo "No playbooks found - that's OK"

# Clean up
rm test.py
```

## 🎯 Team Standards Summary

| Tool | Standard | Config File | Status |
|------|----------|-------------|---------|
| EditorConfig | ✅ Enhanced | `.editorconfig` | ✅ Configured |
| Python Format | Black (88 chars) | `pyproject.toml` | ✅ Configured |
| Python Lint | Pylint + Flake8 | `.pylintrc`, `.flake8` | ✅ Configured |
| YAML Lint | yamllint (180 chars) | `.yamllint` | ✅ Configured |
| Ansible Lint | ansible-lint | `.ansible-lint` | ✅ Configured |
| Pre-commit | All tools | `.pre-commit-config.yaml` | ✅ Configured |
| Markdown | markdownlint | `.markdownlint.json` | ✅ Configured |

## 🔄 Maintenance Tasks

- [ ] Review configurations quarterly
- [ ] Update tool versions in pre-commit config
- [ ] Gather team feedback on pain points
- [ ] Monitor new linting rules and best practices
- [ ] Update this guide as standards evolve

## 📞 Support

If you encounter issues with the development environment setup:
1. Check this guide first
2. Review the individual config files in the repository root
3. Ask the DevOps team for assistance
4. Contribute improvements back to this guide
