# Linting Configuration Directory

This directory contains all linting and code quality configuration files for the project.

## 📁 **Organization Strategy**

Instead of cluttering the root directory, all linting configurations are centralized here and symlinked to their expected locations.

## 🔧 **Configuration Files**

| File | Purpose | Tool |
|------|---------|------|
| `.ansible-lint` | Ansible best practices | ansible-lint |
| `.editorconfig` | Code formatting standards | EditorConfig |
| `.editorconfig-checker.json` | EditorConfig validation | editorconfig-checker |
| `.flake8` | Python code style | flake8 |
| `.gitleaks.toml` | Secret scanning | gitleaks |
| `.jscpd.json` | Copy-paste detection | jscpd |
| `.jsonlintrc` | JSON validation | jsonlint |
| `.markdownlint.json` | Markdown linting | markdownlint |
| `.prettierrc.json` | Code formatting | Prettier |
| `.prettierrc.yml` | Code formatting (YAML) | Prettier |
| `.pylintrc` | Python linting | pylint |
| `.shellcheckrc` | Shell script linting | ShellCheck |
| `.shfmt` | Shell formatting | shfmt |
| `.textlintrc` | Natural language linting | textlint |
| `.yamllint` | YAML linting | yamllint |
| `pyproject.toml` | Python project config | Various Python tools |

## 🔗 **How It Works**

1. **Actual Files**: Stored in `.lint-configs/`
2. **Symlinks**: Created in root directory for tool discovery
3. **Git**: Tracks actual files, ignores symlinks
4. **CI/CD**: Workflow copies configs to remote repositories

## 🚀 **Benefits**

- ✅ **Clean Root Directory**: No configuration file clutter
- ✅ **Centralized Management**: Easy to maintain and update
- ✅ **Tool Compatibility**: Symlinks ensure tools find configs
- ✅ **Remote Support**: CI/CD workflow handles copying
- ✅ **Version Control**: Only actual configs are tracked

## 🛠️ **Maintenance**

To add a new linting configuration:

1. **Add the config file** to `.lint-configs/`
2. **Create a symlink** in root: `ln -s .lint-configs/.newconfig .newconfig`
3. **Update `.gitignore`** to ignore the symlink
4. **Update CI/CD workflow** to copy the config to remote repos

## 📋 **Remote Repository Support**

The CI/CD workflow automatically copies these configs to repositories that call this workflow as a reusable action, ensuring consistent linting across all projects.
