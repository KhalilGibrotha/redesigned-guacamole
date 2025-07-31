# Super Linter Configuration Reference

This document provides a comprehensive overview of all linters enabled in our Super Linter setup, their purposes, and configuration files.

## 🔍 **Enabled Linters Overview**

Our Super Linter configuration includes **11 core linters** that ensure code quality, security, and consistency across multiple languages and formats.

---

## 📋 **Linter Details**

### 1. **Ansible Lint** 🤖
- **Purpose**: Validates Ansible playbooks, roles, and tasks for best practices and common issues
- **Config File**: `.ansible-lint`
- **What it checks**:
  - Playbook syntax and structure
  - Task naming conventions
  - Deprecated modules usage
  - Security best practices
  - YAML formatting within Ansible files

### 2. **ShellCheck (Bash)** 🐚
- **Purpose**: Static analysis tool for shell scripts to find bugs and improve code quality
- **Config File**: `.shellcheckrc`
- **What it checks**:
  - Common shell scripting errors
  - Portability issues between shells
  - Quoting and variable expansion problems
  - Best practices for shell scripts
  - Security vulnerabilities in shell code

### 3. **EditorConfig Checker** ⚙️
- **Purpose**: Ensures files conform to EditorConfig rules for consistent formatting
- **Config File**: `.editorconfig-checker.json` + `.editorconfig`
- **What it checks**:
  - Line length limits (120/160/180 chars based on file type)
  - Indentation consistency (spaces vs tabs)
  - Line ending standards (LF/CRLF)
  - Final newline requirements
  - Trailing whitespace removal
  - Character encoding (UTF-8)

### 4. **GitLeaks** 🔐
- **Purpose**: Detects hardcoded secrets, passwords, and sensitive information in code
- **Config File**: `.gitleaks.toml`
- **What it checks**:
  - API keys and access tokens
  - Database connection strings
  - Private keys and certificates
  - Passwords and authentication credentials
  - Cloud service credentials (AWS, Azure, GCP)
  - Custom secret patterns

### 5. **GitHub Actions Lint (actionlint)** 🚀
- **Purpose**: Validates GitHub Actions workflow files for syntax and best practices
- **Config File**: Built-in rules (auto-detected)
- **What it checks**:
  - Workflow YAML syntax
  - Action and step configurations
  - Environment variable usage
  - Security best practices
  - Deprecated features

### 6. **JSCPD (Copy-Paste Detection)** 📋
- **Purpose**: Detects code duplication across multiple file formats and languages
- **Config File**: `.jscpd.json`
- **What it checks**:
  - Duplicate code blocks (minimum 5 lines, 50 tokens)
  - Cross-language duplication detection
  - Threshold-based reporting (15％ duplication tolerance)
  - Supports JavaScript, Python, YAML, JSON, Markdown, Shell scripts

### 7. **JSON Lint** 📝
- **Purpose**: Validates JSON files for correct syntax and formatting
- **Config File**: Built-in rules (uses ESLint JSON plugin)
- **What it checks**:
  - JSON syntax validity
  - Proper bracket and brace matching
  - Correct comma usage
  - Valid data types

### 8. **Markdown Lint** 📄
- **Purpose**: Ensures Markdown files follow consistent style and formatting rules
- **Config File**: `.markdownlint.json`
- **What it checks**:
  - Header hierarchy and structure
  - Link validity and formatting
  - List consistency
  - Line length limits (180 chars for documentation)
  - Proper code block formatting

### 9. **textlint (Natural Language)** 📖
- **Purpose**: Lints natural language in Markdown and text files for writing quality
- **Config File**: `.textlintrc`
- **What it checks**:
  - Writing quality (passive voice, weak words)
  - Technical term consistency (Git vs git)
  - Dead link detection with redirect following
  - Grammar and style improvements
  - Wordy phrase identification

### 10. **Python Lint (Multiple Tools)** 🐍
- **Purpose**: Comprehensive Python code quality analysis
- **Config Files**: `.flake8`, `.pylintrc`, `pyproject.toml`
- **What it checks**:
  - Code syntax and style (PEP 8)
  - Import organization and formatting
  - Code complexity and maintainability
  - Type hints and annotations
  - Security vulnerabilities

### 11. **YAML Lint** 📋
- **Purpose**: Validates YAML files for syntax and formatting consistency
- **Config File**: `.yamllint`
- **What it checks**:
  - YAML syntax validity
  - Indentation consistency (2 spaces)
  - Line length limits (180 chars)
  - Key ordering and structure
  - Comment formatting

---

## 🎯 **Quality Standards**

### **Line Length Limits**
- **General files**: 120 characters
- **Jinja2 templates**: 160 characters
- **Markdown documentation**: 180 characters
- **YAML files**: 180 characters

### **Indentation Standards**
- **YAML/JSON/Markdown**: 2 spaces
- **Python**: 4 spaces
- **Makefiles**: Tabs (required)
- **Shell scripts**: 2 spaces

### **Security Standards**
- **No hardcoded secrets** (GitLeaks enforcement)
- **No dead links** in documentation
- **Consistent credential handling** patterns
- **Proper secret exclusion** patterns

### **Code Quality Standards**
- **Maximum 15％ code duplication** tolerance
- **Minimum 5 lines** for duplication detection
- **Cross-language consistency** checking
- **Best practice enforcement** across all languages

---

## 📁 **Configuration File Locations**

```text
.
├── .ansible-lint              # Ansible playbook linting rules
├── .editorconfig              # Universal formatting rules
├── .editorconfig-checker.json # EditorConfig checker settings
├── .flake8                    # Python style and syntax rules
├── .gitleaks.toml             # Secret detection patterns
├── .jscpd.json               # Copy-paste detection settings
├── .markdownlint.json        # Markdown formatting rules
├── .pylintrc                 # Python code quality rules
├── .shellcheckrc             # Shell script analysis rules
├── .textlintrc               # Natural language linting rules
├── .yamllint                 # YAML formatting and syntax rules
└── .github/
    └── super-linter.env      # Super Linter configuration
```text

---

## 🚀 **Usage Examples**

### **Local Testing Commands**
```bash
# Test individual linters
npx editorconfig-checker .
npx textlint --fix docs/
npx markdownlint docs/
yamllint .
flake8 scripts/
shellcheck scripts/*.sh

# Test specific file types
npx jscpd --threshold 15 .
gitleaks detect --config .gitleaks.toml
ansible-lint playbooks/
```text

### **Super Linter Integration**
All linters run automatically in GitHub Actions via Super Linter v5 with comprehensive reporting and error detection.

---

## 📊 **Monitoring & Reporting**

- **Console Output**: Real-time linting results in CI/CD
- **GitHub Step Summary**: Comprehensive analysis reports
- **TAP Format**: Machine-readable test results
- **Detailed Reports**: File-specific error details with line numbers
- **Auto-fix Capabilities**: textlint, Black (Python), Prettier (where applicable)

This configuration ensures **consistent code quality**, **security compliance**, and **maintainable documentation** across the entire project ecosystem.
