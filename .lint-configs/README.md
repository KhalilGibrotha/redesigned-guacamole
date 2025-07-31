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
| `.shellcheckrc` | Shell script linting (CI/CD optimized) | ShellCheck |
| `.shellcheckrc-ansible` | Shell script linting (Ansible playbooks) | ShellCheck |
| `.shellcheckrc-strict` | Shell script linting (Standalone scripts) | ShellCheck |
| `.shfmt` | Shell formatting | shfmt |
| `.textlintrc` | Natural language linting | textlint |
| `.yamllint` | YAML linting | yamllint |
| `pyproject.toml` | Python project config | Various Python tools |

## ⚙️ **Configuration Highlights**

### YAML Linting (`.yamllint`)
- **Line Length**: 350 characters (accommodates long shell commands in CI/CD)
- **Indentation**: 2 spaces with sequence indentation
- **Boolean Values**: Enforces `true`/`false` over `yes`/`no`
- **Document Structure**: Requires `---` start marker

### Python Configuration (`pyproject.toml`, `.flake8`, `.pylintrc`)
- **Line Length**: 120 characters (PEP 8 extended)
- **Import Sorting**: isort with black compatibility
- **Type Checking**: mypy configuration included

### Shell Script Linting (`.shellcheckrc`)
- **Context-Aware Configuration**: Optimized for CI/CD workflows by default
- **Excluded Rules**: SC2086 (quoting), SC2129 (redirects), SC2038 (find patterns), SC2015 (A && B || C), SC2044 (find loops), SC2193 (comparison), SC2081 (glob matching)
- **Target Shell**: bash (GitHub Actions default)
- **Note**: For standalone scripts or Ansible repos, consider using stricter configuration

### GitHub Actions Workflows
- **Tool**: actionlint with shellcheck integration disabled
- **Reason**: Workflow scripts have different safety requirements than standalone scripts
- **Command**: `actionlint -shellcheck "" workflow.yml`

### Context-Specific Usage

#### 🔄 **CI/CD Workflows** (Current Default)
- Uses current `.shellcheckrc` with exclusions
- Appropriate for GitHub Actions, GitLab CI, etc.
- Balances safety with practicality

#### 📜 **Ansible Playbooks**
- Consider creating `.shellcheckrc-ansible` with moderate strictness:
  ```bash
  # For Ansible shell tasks - exclude only the most problematic rules
  exclude=SC1091,SC2034,SC2154,SC2086
  shell=bash
  ```

#### 🛠️ **Standalone Shell Scripts**
- Consider creating `.shellcheckrc-strict` with minimal exclusions:
  ```bash
  # For production shell scripts - maximum safety
  exclude=SC1091,SC2034,SC2154
  shell=bash
  ```

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

### Adding New Linting Configurations

1. **Add the config file** to `.lint-configs/`
2. **Create a symlink** in root: `ln -s .lint-configs/.newconfig .newconfig`
3. **Update `.gitignore`** to ignore the symlink
4. **Update CI/CD workflow** to copy the config to remote repos

### Context-Specific Shellcheck Usage

#### For CI/CD Repositories (Default)
```bash
# Uses current .shellcheckrc symlink with CI/CD exclusions
shellcheck script.sh
# Or manually specify exclusions
shellcheck -e SC1091,SC2034,SC2154,SC2086,SC2129,SC2038,SC2015,SC2044,SC2193,SC2081 script.sh
```text

#### For Ansible Playbook Repositories
```bash
# Use Ansible-appropriate exclusions
shellcheck -e SC1091,SC2034,SC2154,SC2086 script.sh
# For shell tasks in playbooks, these exclusions balance safety with practicality
```text

#### For Standalone Script Repositories
```bash
# Use minimal exclusions for maximum safety
shellcheck -e SC1091,SC2034,SC2154 script.sh
# Keeps important checks like SC2086 (quoting) enabled
```text

#### Repository-Specific Override
Create a `.shellcheckrc-local` in consuming repositories:
```bash
# Repository-specific overrides
source=.lint-configs/.shellcheckrc-ansible
# Add repository-specific exclusions
exclude=SC1091,SC2034,SC2154,SC2086,SCXXXX
```text

## 📋 **Remote Repository Support**

The CI/CD workflow automatically copies these configs to repositories that call this workflow as a reusable action, ensuring consistent linting across all projects.

### 🤖 **Automatic Repository Type Detection**

**NEW**: The workflow now automatically detects the repository type and configures appropriate shellcheck settings! No manual setup required.

#### Detection Logic
The workflow automatically analyzes the repository structure and applies the optimal configuration:

| Repository Type | Detection Criteria | Shellcheck Profile | Excluded Rules |
|-----------------|-------------------|-------------------|----------------|
| **📜 Ansible** | `playbooks/`, `roles/`, `site.yml`, `ansible.cfg`, `inventory/` | Moderate strictness | SC1091, SC2034, SC2154, SC2086 |
| **🛠️ Scripts** | `scripts/`, `install.sh`, `setup.sh`, `build.sh` | Maximum strictness | SC1091, SC2034, SC2154 (minimal) |
| **🔄 CI/CD** | Everything else | Workflow optimized | SC1091, SC2034, SC2154, SC2086, SC2129, SC2038, SC2015, SC2044, SC2193, SC2081 |

#### What Happens Automatically
1. **Repository Analysis**: Workflow scans for identifying files/directories
2. **Profile Selection**: Chooses appropriate shellcheck configuration
3. **Environment Setup**: Sets `SHELLCHECK_OPTS` environment variable
4. **Type Reporting**: Logs detected repository type for transparency

### Manual Override (Optional)

If you need to override the automatic detection, add this to your repository's workflow:

```yaml
- name: 🔧 Override Shellcheck Configuration
  run: echo 'SHELLCHECK_OPTS="-e SC1091,SC2034,SC2154,SC2086"' >> $GITHUB_ENV
```text
