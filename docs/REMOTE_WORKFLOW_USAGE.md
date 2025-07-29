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
```

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
```

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
```

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
```

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
```

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
- `node_modules/` - NPM dependencies
- `.mypy_cache/` - MyPy type checker cache
- `.pytest_cache/` - Pytest cache
- `__pycache__/` - Python bytecode cache
- `.tox/` - Tox testing tool cache
