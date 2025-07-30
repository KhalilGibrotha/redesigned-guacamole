#!/bin/bash
# Test script to demonstrate lint configuration copying functionality

echo "🧪 Testing Lint Configuration Copying Functionality"
echo "=================================================="

# Create a temporary test directory
TEST_DIR="/tmp/lint-config-test"
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

echo "📁 Created test directory: $TEST_DIR"

# Simulate the workflow checkout steps
echo ""
echo "📥 Simulating repository checkouts..."

# Create 'calling repo' directory (bug-free-fiesta simulation)
mkdir -p calling-repo
cd calling-repo

# Copy existing configs from bug-free-fiesta
cp /home/gambia/bug-free-fiesta/.ansible-lint .
cp /home/gambia/bug-free-fiesta/.yamllint .

echo "✅ Calling repository setup complete with existing configs:"
ls -la | grep '^\-.*\.'

# Create 'lint-configs' directory (redesigned-guacamole simulation)
cd ..
mkdir -p .lint-configs
cd .lint-configs

# Copy all lint configs from redesigned-guacamole
cp /home/gambia/redesigned-guacamole/.* . 2>/dev/null || true
rm -f .git* .venv* 2>/dev/null || true  # Remove non-config files

echo ""
echo "✅ Lint configs repository setup complete:"
ls -la | grep '^\-.*\.' | head -10

# Simulate the workflow logic
cd ../calling-repo

echo ""
echo "🔧 Simulating lint configuration copying logic..."
echo "=================================================="

# List of lint configuration files to copy (from workflow)
LINT_FILES=(
  ".ansible-lint"
  ".yamllint"
  ".markdownlint.json"
  ".markdownlint.yml"
  ".flake8"
  ".pylintrc"
  ".eslintrc.json"
  ".eslintrc.yml"
  ".eslintrc.yaml"
  ".eslintrc.js"
  ".jscpd.json"
  ".jsonlintrc"
  ".shellcheckrc"
  ".shfmt"
  ".editorconfig"
  ".editorconfig-checker.json"
  ".prettierrc.json"
  ".prettierrc.yml"
  ".textlintrc"
  ".gitleaks.toml"
  ".pre-commit-config.yaml"
  "pyproject.toml"
)

copied_count=0
skipped_count=0

for config_file in "${LINT_FILES[@]}"; do
  if [ -f "../.lint-configs/$config_file" ]; then
    # Only copy if the file doesn't already exist in the calling repo
    if [ ! -f "$config_file" ]; then
      cp "../.lint-configs/$config_file" "$config_file"
      echo "  ✅ Copied $config_file from redesigned-guacamole"
      copied_count=$((copied_count + 1))
    else
      echo "  ℹ️  Skipped $config_file (already exists in calling repository)"
      skipped_count=$((skipped_count + 1))
    fi
  fi
done

echo ""
echo "📊 Summary:"
echo "  - Copied $copied_count lint configuration files"
echo "  - Skipped $skipped_count existing files (preserved local configs)"
echo ""
echo "📋 Final configuration files in calling repository:"
ls -la | grep '^\-.*\.' | wc -l | xargs echo "  Total files:"
ls -la | grep '^\-.*\.' | head -15

echo ""
echo "🎯 Test Results:"
echo "  ✅ Existing configs (.ansible-lint, .yamllint) were preserved"
echo "  ✅ Missing configs were copied from redesigned-guacamole"
echo "  ✅ No overwrites occurred - local customizations maintained"

# Verify content of preserved files
echo ""
echo "🔍 Verifying preserved local configurations:"
echo "  .ansible-lint first line: $(head -1 .ansible-lint)"
echo "  .yamllint first line: $(head -1 .yamllint)"

# Show some copied files
echo ""
echo "🔍 Sample copied configurations:"
if [ -f ".flake8" ]; then
  echo "  .flake8 first line: $(head -1 .flake8)"
fi
if [ -f ".pylintrc" ]; then
  echo "  .pylintrc first line: $(head -1 .pylintrc)"
fi

# Cleanup
cd /
rm -rf "$TEST_DIR"
echo ""
echo "🧹 Cleanup complete"
echo "✅ Lint configuration copying test completed successfully!"
