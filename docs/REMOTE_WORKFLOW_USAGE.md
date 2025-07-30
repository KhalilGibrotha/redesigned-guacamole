# Remote Workflow Usage

## Overview

The CI workflow (`ci-optimized.yml`) is designed to be called from remote repositories without depending on the calling repository's Python dependencies.

## Changes Made for Remote Compatibility

### Python Setup Modifications

**Before:**
```yaml
- name: 🐍 Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.x'
    cache: 'pip'  # ❌ This required requirements.txt in calling repo

- name: 📦 Install Dependencies
  run: |
    python -m pip install --upgrade pip
    if [ -f requirements.txt ]; then
      pip install -r requirements.txt  # ❌ Failed when file missing
    fi
```text

**After:**
```yaml
- name: 🐍 Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.x'
    # ✅ No cache to avoid dependency on calling repo's requirements

- name: 📦 Install Dependencies
  run: |
    python -m pip install --upgrade pip
    # ✅ Conditional installation from calling repo
    if [ -f requirements.txt ]; then
      echo "Found requirements.txt in calling repository, installing dependencies..."
      pip install -r requirements.txt
    elif [ -f pyproject.toml ]; then
      echo "Found pyproject.toml in calling repository, installing dependencies..."
      pip install -e .
    else
      echo "No requirements.txt or pyproject.toml found in calling repository"
      echo "Installing minimal dependencies for workflow functionality..."
    fi

    # ✅ Always install tools needed for auto-fixing and analysis
    echo "Installing workflow tools..."
    pip install black isort PyYAML requests
```text

## Tool Dependencies

### Always Available (Installed by Workflow)
- **Python Tools**: `black`, `isort`, `PyYAML`, `requests`
- **Core Python**: Standard library modules (`json`, etc.)

### Provided by Super Linter (When Used)
- **Shell**: `shfmt`, `shellcheck`
- **Markdown**: `markdownlint-cli2`
- **General**: `prettier`, `yamllint`

### Graceful Degradation
All auto-fix tools are checked with `command -v` before use. If a tool is not available:
- The workflow continues without that specific auto-fix
- No errors are thrown
- Other auto-fixes still work

## Confluence Publishing

### Issue: Confluence Publishing Fails When Called Remotely

**Problem**: When the reusable workflow is called from a remote repository, the Confluence publishing job fails because it tries to reference `./.github/workflows/publish-docs.yml` which doesn't exist in the calling repository.

**Root Cause**: The publish job was using a relative path to call another workflow file:
```yaml
publish:
  uses: ./.github/workflows/publish-docs.yml  # ❌ Only works in same repo
```text

**Solution**: The publish job has been converted to inline steps that detect the repository context and handle both local and remote execution:

```yaml
publish:
  name: 🚀 Publish to Confluence
  runs-on: ubuntu-latest
  steps:
    - name: 🔍 Detect Repository Context
      # Automatically detects if running locally or remotely

    - name: 📥 Checkout Redesigned-Guacamole (Scripts)
      # Always checkout the scripts repository

    - name: 📥 Checkout Calling Repository (Content)
      # Only when called remotely
```text

**Features**:
- ✅ **Automatic Repository Detection**: Knows if running locally or remotely
- ✅ **Dual Checkout Strategy**: Gets scripts from redesigned-guacamole, content from calling repo
- ✅ **Secrets Validation**: Graceful handling of missing Confluence secrets
- ✅ **Dry Run Support**: Can run without secrets for testing

## Usage Examples

### From Remote Repository (Read-only Mode)
```yaml
name: Lint with Auto-fix (Analysis Only)
on: [push, pull_request]

jobs:
  lint:
    uses: your-org/redesigned-guacamole/.github/workflows/ci-optimized.yml@main
    with:
      auto_fix: true
    # Note: Auto-fixes will be applied but not committed due to permission restrictions
```text

### From Remote Repository (With Auto-fix Commits)
```yaml
name: Lint with Auto-fix (Full Mode)
on: [push, pull_request]

permissions:
  contents: write  # Required for auto-fix commits

jobs:
  lint:
    uses: your-org/redesigned-guacamole/.github/workflows/ci-optimized.yml@main
    with:
      auto_fix: true
    permissions:
      contents: write  # Enable auto-fix commits
      packages: read
      statuses: write
```text

### From Same Repository (Full Access)
```yaml
# Auto-fixes will be applied and committed automatically
name: Lint with Auto-fix
on: [push, pull_request]

jobs:
  lint:
    uses: ./.github/workflows/ci-optimized.yml
    with:
      auto_fix: true
```text

## Auto-fix Capabilities

### Available Everywhere
- **Python**: Black formatting, isort import sorting
- **YAML**: Basic structure fixing
- **JSON**: Formatting via Python's json module

### Available with Super Linter
- **Shell**: `shfmt` formatting
- **Markdown**: `markdownlint-cli2` auto-fix, `prettier` formatting
- **Additional**: Various other formatters

## Troubleshooting

### Error: "can't find requirements.txt" in Confluence Publishing
- **Cause**: Confluence publishing job looking for dependencies in calling repository
- **Solution**: Update to latest workflow version with improved dependency handling
- **Details**: The workflow now:
  - Always installs core Confluence dependencies (`jinja2`, `pyyaml`, `requests`, etc.)
  - Uses scripts from `redesigned-guacamole` repository for dependency resolution
  - Doesn't rely on pip cache to avoid remote repository conflicts

### Error: "can't find requirements.txt"
- **Cause**: Old version with pip cache enabled
- **Solution**: Update to latest workflow version

### Error: "requesting 'contents: write', but is only allowed 'contents: read'"
- **Cause**: Remote workflow call without proper permissions
- **Solution**: Add `contents: write` permission to calling workflow:
  ```yaml
  permissions:
    contents: write
  jobs:
    lint:
      uses: your-org/redesigned-guacamole/.github/workflows/ci-optimized.yml@main
      permissions:
        contents: write
  ```

### Error: "workflow file not found: ./.github/workflows/publish-docs.yml"
- **Cause**: Old version of workflow using relative path for Confluence publishing
- **Solution**: Update to latest workflow version that has inline Confluence publishing

### Confluence Publishing Fails with Missing Secrets
- **Cause**: Remote repository doesn't have Confluence secrets configured
- **Solutions**:
  - **Option 1**: Add Confluence secrets to the calling repository
  - **Option 2**: Run with `dry_run: true` to test without actual publishing
  - **Option 3**: Set up secrets in the calling repository:
    ```yaml
    # In calling repository's secrets:
    CONFLUENCE_URL: https://your-confluence.atlassian.net
    CONFLUENCE_USER: your-username
    CONFLUENCE_API_TOKEN: your-api-token
    ```

### Confluence Publishing Succeeds But No Content
- **Cause**: Calling repository might not have `docs/` directory or proper template files
- **Solution**: Ensure calling repository has:
  ```text
  docs/
    ├── vars.yaml              # Configuration for templates
    └── [template files]       # .j2 template files
  ```

### Confluence Publishing Auto-Enables Dry Run Mode
- **Cause**: Missing Confluence secrets in calling repository (this is normal!)
- **Behavior**: Workflow automatically enables dry-run mode when secrets are missing
- **Result**: Publishing step runs successfully but doesn't make actual changes
- **Solution (if you want live publishing)**:
  1. **Add secrets to your repository**:
     ```text
     # In your repository settings > Secrets and variables > Actions
     CONFLUENCE_URL=https://your-confluence.atlassian.net
     CONFLUENCE_USER=your-username-or-email
     CONFLUENCE_API_TOKEN=your-confluence-api-token
     ```
  2. **Ensure calling workflow passes secrets**:
     ```yaml
     jobs:
       ci-cd:
         uses: your-org/redesigned-guacamole/.github/workflows/ci-optimized.yml@main
         secrets:
           CONFLUENCE_URL: ${{ secrets.CONFLUENCE_URL }}
           CONFLUENCE_USER: ${{ secrets.CONFLUENCE_USER }}
           CONFLUENCE_API_TOKEN: ${{ secrets.CONFLUENCE_API_TOKEN }}
     ```

### Auto-fixes Applied But Not Committed
- **Cause**: Running in read-only mode (remote call without write permissions)
- **Effect**: Auto-fixes are applied to detect issues but changes aren't committed
- **Solution**:
  - **Option 1**: Add `contents: write` permission to enable commits
  - **Option 2**: Accept read-only mode for analysis purposes

### Limited Auto-fixes
- **Cause**: Super Linter not running (minimal mode)
- **Effect**: Only Python, YAML, and JSON auto-fixes available
- **Solution**: Normal - workflow degrades gracefully

### Cache Directory Permission Errors
- **Cause**: Auto-fix tools trying to modify read-only cache files (`.mypy_cache`, `__pycache__`, etc.)
- **Solution**: Already fixed - cache directories are excluded from auto-fix operations
- **Effect**: Permission denied errors during JSON/Python auto-fixes
- **Solution**: Workflow now excludes cache directories from auto-fix operations

## Excluded Directories

The workflow automatically excludes these directories from auto-fix operations:
- `.git/` - Git repository data
- `.venv/`, `venv/` - Virtual environments
- `node_modules/` - npm dependencies
- `.mypy_cache/` - MyPy type checker cache
- `.pytest_cache/` - Pytest cache
- `__pycache__/` - Python bytecode cache
- `.tox/` - Tox testing tool cache
