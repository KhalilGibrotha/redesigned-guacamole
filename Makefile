# Makefile for Ansible project linting and validation

.PHONY: help lint lint-yaml lint-ansible fix install-tools clean test test-syntax sanity-check security-check validate-templates

# Default target
help:
	@echo "Available targets:"
	@echo "  lint             - Run all linting checks"
	@echo "  lint-yaml        - Run yamllint only"
	@echo "  lint-ansible     - Run ansible-lint only"
	@echo "  fix              - Auto-fix some linting issues"
	@echo "  install-tools    - Install required linting tools"
	@echo "  test             - Run ansible playbook syntax check"
	@echo "  test-syntax      - Comprehensive syntax validation"
	@echo "  sanity-check     - Quick sanity checks for development"
	@echo "  security-check   - Security validation"
	@echo "  validate-templates - Validate template structure"
	@echo "  clean            - Remove temporary files"

# Install required linting tools
install-tools:
	@echo "Installing linting tools..."
	sudo apt update && sudo apt install -y yamllint pandoc
	pipx install ansible-lint || pip install ansible-lint
	@echo "✅ Tools installed successfully"

# Run all linting checks
lint: lint-yaml lint-ansible
	@echo "✅ All linting checks passed!"

# Run yamllint
lint-yaml:
	@echo "Running yamllint..."
	yamllint -c .yamllint .

# Run ansible-lint
lint-ansible:
	@echo "Running ansible-lint..."
	ansible-lint --exclude molecule/

# Comprehensive syntax validation
test-syntax: lint test validate-templates
	@echo "✅ Comprehensive syntax validation complete!"

# Quick sanity checks for development
sanity-check:
	@echo "Running sanity checks..."
	@echo "1. Checking YAML syntax..."
	@yamllint -c .yamllint playbook.yml vars/vars.yml || (echo "❌ YAML syntax issues found" && exit 1)
	@echo "2. Checking playbook syntax..."
	@ansible-playbook --syntax-check playbook.yml || (echo "❌ Playbook syntax issues found" && exit 1)
	@echo "3. Checking required files..."
	@test -f .yamllint || (echo "❌ .yamllint config missing" && exit 1)
	@test -f vars/vars.yml || (echo "❌ vars/vars.yml missing" && exit 1)
	@echo "4. Checking template files..."
	@find docs/ -name "*.j2" | head -1 > /dev/null || (echo "❌ No template files found in docs/" && exit 1)
	@echo "✅ All sanity checks passed!"

# Security validation
security-check:
	@echo "Running security checks..."
	@echo "1. Checking for exposed secrets..."
	@! grep -r "password\|secret\|ATAT" . --include="*.yml" --exclude-dir=molecule --exclude-dir=.github | grep -v "example\|template\|grep.*secret" || (echo "⚠️  Potential secrets found" && exit 1)
	@echo "2. Checking file permissions..."
	@find . -name "*.yml" -perm /002 | head -1 > /dev/null && (echo "❌ World-writable YAML files found" && exit 1) || echo "✅ File permissions OK"
	@echo "3. Checking for hardcoded URLs..."
	@! grep -r "http://\|https://" . --include="*.yml" | grep -v "example.com\|test\|mock\|template" || echo "⚠️  Hardcoded URLs found (review recommended)"
	@echo "✅ Security checks complete!"

# Validate template structure
validate-templates:
	@echo "Validating template structure..."
	@echo "1. Checking template directory..."
	@test -d docs/ || (echo "❌ docs/ directory missing" && exit 1)
	@echo "2. Checking for main template..."
	@test -f docs/main.md.j2 || (echo "❌ main.md.j2 template missing" && exit 1)
	@echo "3. Checking template syntax..."
	@for template in docs/*.j2; do \
		echo "   Checking $$template..."; \
		echo "---\n- hosts: localhost\n  tasks:\n    - template: src=$$template dest=/tmp/test" | ansible-playbook --syntax-check /dev/stdin || exit 1; \
	done
	@echo "✅ Template validation complete!"

# Auto-fix some issues (where possible)
fix:
	@echo "Running auto-fixes..."
	@echo "Note: Some issues need manual fixing"
	# Remove trailing whitespace
	find . -name "*.yml" -type f -exec sed -i 's/[[:space:]]*$$//' {} \;
	# Fix line endings
	find . -name "*.yml" -type f -exec dos2unix {} \; 2>/dev/null || true
	@echo "✅ Auto-fixes applied"

# Test playbook syntax
test:
	@echo "Testing playbook syntax..."
	ansible-playbook --syntax-check playbook.yml

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	rm -rf /tmp/*.md /tmp/*.html
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	rm -f .yamllint.tmp
	@echo "✅ Cleanup complete"

# Development workflow
dev: clean sanity-check security-check
	@echo "✅ Development checks complete!"

# Full validation workflow
validate: clean lint test-syntax security-check
	@echo "✅ Full validation complete!"

# CI/CD target
ci: install-tools validate
	@echo "✅ CI/CD checks passed!"

# Quick test for template rendering (requires pandoc)
test-render:
	@echo "Testing template rendering..."
	@mkdir -p /tmp/test-render
	@echo "project_name: Test" > /tmp/test-vars.yml
	@echo "env: Development" >> /tmp/test-vars.yml
	@echo "database_url: https://test.example.com" >> /tmp/test-vars.yml
	@ansible-playbook -e @/tmp/test-vars.yml --extra-vars="confluence_url=https://test.example.com confluence_space=TEST confluence_auth=dGVzdA==" -c local -i localhost, playbook.yml --check
	@echo "✅ Template rendering test complete!"
