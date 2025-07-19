# Development Environment Standards for Ansible AAP + Python + PowerShell Teams

## 📋 Overview
This document outlines the recommended development environment standards for teams working with:
- Ansible Automation Platform (AAP)
- Python development
- PowerShell scripting
- Infrastructure as Code

## 🎯 Core Standards

### 1. EditorConfig (✅ Already Implemented)
- **Purpose**: Ensures consistent formatting across different editors and IDEs
- **File**: `.editorconfig` in repository root
- **Key Settings**:
  - UTF-8 encoding for all files
  - LF line endings (even for PowerShell for cross-platform compatibility)
  - Trim trailing whitespace
  - Insert final newline
  - Python: 4 spaces, max 88 chars (Black formatter compatible)
  - YAML/Ansible: 2 spaces, max 160 chars
  - PowerShell: 4 spaces, max 120 chars

### 2. Python Standards
```ini
# Recommended Python tools for your team:
[tool.black]
line-length = 88
target-version = ['py39', 'py310', 'py311']

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.pylint]
max-line-length = 88
```

### 3. Ansible/YAML Standards
```yaml
# .yamllint configuration
extends: default
rules:
  line-length:
    max: 160
  indentation:
    spaces: 2
    indent-sequences: true
  truthy: disable  # Allow yes/no in Ansible
  comments:
    min-spaces-from-content: 2
```

### 4. PowerShell Standards
```powershell
# PSScriptAnalyzer settings (PSScriptAnalyzerSettings.psd1)
@{
    Rules = @{
        PSUseCorrectCasing = @{
            Enable = $true
        }
        PSAvoidUsingCmdletAliases = @{
            Enable = $true
        }
        PSPlaceOpenBrace = @{
            Enable = $true
            OnSameLine = $true
        }
    }
}
```

## 🛠️ Recommended VS Code Extensions

### Essential Extensions
1. **EditorConfig for VS Code** (`editorconfig.editorconfig`)
2. **YAML** (`redhat.vscode-yaml`)
3. **Ansible** (`redhat.ansible`)
4. **Python** (`ms-python.python`)
5. **PowerShell** (`ms-vscode.powershell`)
6. **Black Formatter** (`ms-python.black-formatter`)
7. **Pylint** (`ms-python.pylint`)

### Ansible-Specific Extensions
8. **Ansible Vault** (`wholroyd.ansible-vault`)
9. **Better Jinja** (`samuelcolvin.jinjahtml`)
10. **YAML Sort** (`pascalreitermann93.vscode-yaml-sort`)

## 📁 Repository Structure Standards

```
project-root/
├── .editorconfig                 # Editor configuration
├── .yamllint                    # YAML linting rules
├── .ansible-lint                # Ansible linting rules
├── .gitignore                   # Git ignore patterns
├── requirements.txt             # Python dependencies
├── ansible.cfg                  # Ansible configuration
├── pyproject.toml              # Python project configuration
├── PSScriptAnalyzerSettings.psd1  # PowerShell linting
├── playbooks/                   # Ansible playbooks
├── roles/                       # Ansible roles
├── group_vars/                  # Ansible group variables
├── host_vars/                   # Ansible host variables
├── inventory/                   # Ansible inventory
├── scripts/                     # Utility scripts (Python/PowerShell)
├── docs/                        # Documentation
└── tests/                       # Test files
```

## 🔧 Git Configuration Standards

### .gitignore essentials
```gitignore
# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/
.env

# Ansible
*.retry
.vault_pass
vault_password_file

# PowerShell
*.ps1xml

# IDE
.vscode/settings.json
.idea/

# OS
.DS_Store
Thumbs.db
```

### Git hooks (recommended)
- **pre-commit**: Run linting and formatting checks
- **commit-msg**: Enforce commit message format

## 🎨 Code Formatting Standards

### Python (Black + isort)
```bash
# Install and configure
pip install black isort pylint
black --line-length 88 .
isort --profile black .
```

### YAML/Ansible (yamllint + ansible-lint)
```bash
# Install and configure
pip install yamllint ansible-lint
yamllint .
ansible-lint playbooks/
```

### PowerShell (PSScriptAnalyzer)
```powershell
# Install and run
Install-Module -Name PSScriptAnalyzer -Force
Invoke-ScriptAnalyzer -Path . -Recurse
```

## 🏗️ CI/CD Integration

### Pre-commit configuration (.pre-commit-config.yaml)
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
  
  - repo: https://github.com/adrienverge/yamllint
    rev: v1.32.0
    hooks:
      - id: yamllint
  
  - repo: https://github.com/ansible/ansible-lint
    rev: v6.17.2
    hooks:
      - id: ansible-lint
```

## 📚 Team Onboarding Checklist

- [ ] Install EditorConfig plugin in your editor
- [ ] Configure Python environment with Black, isort, pylint
- [ ] Install Ansible linting tools (yamllint, ansible-lint)
- [ ] Set up PowerShell with PSScriptAnalyzer
- [ ] Configure VS Code with recommended extensions
- [ ] Set up pre-commit hooks
- [ ] Review and understand naming conventions
- [ ] Test formatting tools on sample files

## 🔄 Maintenance

- Review and update standards quarterly
- Monitor new tool versions and compatibility
- Gather team feedback on pain points
- Update documentation as standards evolve

---

**Note**: These standards are designed to work seamlessly with AAP, improve code quality, and ensure consistency across your development team.
