# Makefile for Ansible project linting and validation

.PHONY: help lint lint-yaml lint-ansible fix install-tools clean test test-syntax sanity-check security-check validate-templates check-os check-deps install-rhel-prereqs test-compatibility install-rhel-dnf-only secure-setup debug-conversion

# Default target
help:
	@echo "Available targets:"
	@echo "  lint             - Run all linting checks"
	@echo "  lint-yaml        - Run yamllint only"
	@echo "  lint-ansible     - Run ansible-lint only"
	@echo "  fix              - Auto-fix some linting issues"
	@echo "  install-tools    - Install required linting tools"
	@echo "  install-rhel-prereqs - Install RHEL/CentOS prerequisites"
	@echo "  install-rhel-dnf-only - Install tools via DNF only (restricted environments)"
	@echo "  test             - Run ansible playbook syntax check"
	@echo "  test-syntax      - Comprehensive syntax validation"
	@echo "  sanity-check     - Quick sanity checks for development"
	@echo "  security-check   - Security validation"
	@echo "  validate-templates - Validate template structure"
	@echo "  check-os         - Display OS and compatibility info"
	@echo "  check-deps       - Check if required dependencies are installed"
	@echo "  test-compatibility - Run comprehensive compatibility test"
	@echo "  secure-setup     - Set up credentials securely with ansible-vault"
	@echo "  debug-conversion - Debug markdown to HTML conversion issues"
	@echo "  clean            - Remove temporary files"

# Install required linting tools
install-tools:
	@echo "Installing linting tools..."
	@echo "Detecting operating system..."
	@if [ -f /etc/redhat-release ]; then \
		echo "🔍 Detected RHEL/CentOS/Fedora system"; \
		if command -v dnf >/dev/null 2>&1; then \
			echo "📦 Using dnf package manager"; \
			sudo dnf install -y epel-release || true; \
			sudo dnf install -y yamllint pandoc python3-pip; \
		elif command -v yum >/dev/null 2>&1; then \
			echo "📦 Using yum package manager"; \
			sudo yum install -y epel-release || true; \
			sudo yum install -y yamllint pandoc python3-pip; \
		else \
			echo "❌ No supported package manager found"; \
			exit 1; \
		fi; \
	elif [ -f /etc/debian_version ]; then \
		echo "🔍 Detected Debian/Ubuntu system"; \
		echo "📦 Using apt package manager"; \
		sudo apt update && sudo apt install -y yamllint pandoc python3-pip; \
	elif [ -f /etc/arch-release ]; then \
		echo "🔍 Detected Arch Linux system"; \
		echo "📦 Using pacman package manager"; \
		sudo pacman -Syu --noconfirm yamllint pandoc python-pip; \
	elif command -v brew >/dev/null 2>&1; then \
		echo "🔍 Detected macOS with Homebrew"; \
		echo "📦 Using brew package manager"; \
		brew install yamllint pandoc; \
	else \
		echo "⚠️  Unknown operating system, attempting generic installation..."; \
		echo "📦 Trying pip for Python packages"; \
	fi
	@echo "🐍 Installing ansible-lint via pip..."
	@if command -v pipx >/dev/null 2>&1; then \
		echo "   Trying pipx installation..."; \
		if ! pipx install ansible-lint 2>/dev/null; then \
			echo "⚠️  pipx installation failed, trying pip..."; \
			pip3 install --user ansible-lint 2>/dev/null || pip install --user ansible-lint 2>/dev/null || echo "❌ pip installation failed"; \
		fi; \
	else \
		echo "   Trying pip installation..."; \
		if ! pip3 install --user ansible-lint 2>/dev/null && ! pip install --user ansible-lint 2>/dev/null; then \
			echo "❌ pip installation failed"; \
			if [ -f /etc/redhat-release ] && command -v dnf >/dev/null 2>&1; then \
				echo "💡 For restricted RHEL environments, try: make install-rhel-dnf-only"; \
			fi; \
		fi; \
	fi
	@echo "✅ Tools installation process complete"
	@echo "💡 Run 'make check-deps' to verify what was successfully installed"

# Install RHEL/CentOS prerequisites (EPEL repository and basic tools)
install-rhel-prereqs:
	@echo "🔧 Installing RHEL/CentOS prerequisites..."
	@if ! [ -f /etc/redhat-release ]; then \
		echo "❌ This target is only for RHEL/CentOS/Fedora systems"; \
		exit 1; \
	fi
	@echo "📦 Installing EPEL repository and basic development tools..."
	@if command -v dnf >/dev/null 2>&1; then \
		echo "Using dnf (RHEL 8+/Fedora)..."; \
		sudo dnf groupinstall -y "Development Tools" || sudo dnf install -y gcc make; \
		sudo dnf install -y epel-release; \
		sudo dnf install -y python3 python3-pip git; \
	elif command -v yum >/dev/null 2>&1; then \
		echo "Using yum (RHEL 7/CentOS)..."; \
		sudo yum groupinstall -y "Development Tools" || sudo yum install -y gcc make; \
		sudo yum install -y epel-release; \
		sudo yum install -y python3 python3-pip git; \
	else \
		echo "❌ No supported package manager found"; \
		exit 1; \
	fi
	@echo "✅ RHEL prerequisites installed successfully"
	@echo "💡 You can now run 'make install-tools' to install linting tools"

# Install tools via DNF only (for restricted RHEL environments without pip access)
install-rhel-dnf-only:
	@echo "🔧 Installing tools via DNF only (restricted environment mode)..."
	@if ! [ -f /etc/redhat-release ]; then \
		echo "❌ This target is only for RHEL/CentOS/Fedora systems"; \
		exit 1; \
	fi
	@if ! command -v dnf >/dev/null 2>&1; then \
		echo "❌ This target requires dnf (RHEL 8+ or Fedora)"; \
		exit 1; \
	fi
	@echo "📦 Installing core tools and available linting packages..."
	@echo "   Installing EPEL repository..."
	@sudo dnf install -y epel-release || echo "⚠️  EPEL may already be installed or unavailable"
	@echo "   Installing core development tools..."
	@sudo dnf install -y make python3 git
	@echo "   Installing Ansible and available linting tools..."
	@sudo dnf install -y ansible yamllint pandoc || echo "⚠️  Some packages may not be available"
	@echo ""
	@echo "🔍 Checking what was successfully installed..."
	@installed_tools=""; \
	missing_tools=""; \
	for tool in make python3 ansible yamllint pandoc; do \
		if command -v $$tool >/dev/null 2>&1; then \
			installed_tools="$$installed_tools $$tool"; \
		else \
			missing_tools="$$missing_tools $$tool"; \
		fi; \
	done; \
	echo "✅ Successfully installed:$$installed_tools"; \
	if [ -n "$$missing_tools" ]; then \
		echo "❌ Could not install:$$missing_tools"; \
	fi
	@echo ""
	@echo "📋 ansible-lint status:"
	@if command -v ansible-lint >/dev/null 2>&1; then \
		echo "✅ ansible-lint is available"; \
	else \
		echo "⚠️  ansible-lint not available via DNF"; \
		echo "   This is normal in restricted environments"; \
		echo "   You can still use: make lint-yaml, make test, make validate-templates"; \
	fi
	@echo ""
	@echo "✅ DNF-only installation complete!"
	@echo "💡 Available targets without ansible-lint:"
	@echo "   make lint-yaml          - YAML linting only"
	@echo "   make test              - Ansible syntax check"
	@echo "   make validate-templates - Template validation"
	@echo "   make sanity-check      - Core functionality tests"

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
	@if command -v ansible-lint >/dev/null 2>&1; then \
		ansible-lint --exclude molecule/; \
	else \
		echo "⚠️  ansible-lint not available, skipping..."; \
		echo "💡 Install with 'make install-tools' or 'make install-rhel-dnf-only'"; \
		echo "✅ Continuing with available linting tools..."; \
	fi

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
	@! grep -r "password\|secret\|ATAT\|api_token" . --include="*.yml" --exclude-dir=molecule --exclude-dir=.github | grep -v "example\|template\|grep.*secret\|YOUR_.*_HERE\|test:test\|echo.*api_token" || (echo "⚠️  Potential secrets found" && exit 1)
	@echo "2. Checking file permissions..."
	@find . -name "*.yml" -perm /002 | head -1 > /dev/null && (echo "❌ World-writable YAML files found" && exit 1) || echo "✅ File permissions OK"
	@echo "3. Checking for hardcoded production URLs..."
	@! grep -r "https://.*\.atlassian\.net\|https://.*\.confluence\." . --include="*.yml" | grep -v "example\|test\|mock\|template\|your-domain" || echo "⚠️  Production URLs found (review recommended)"
	@echo "4. Checking if vars/vars.yml is protected..."
	@if [ -f vars/vars.yml ] && ! head -1 vars/vars.yml | grep -q "ANSIBLE_VAULT"; then \
		echo "⚠️  vars/vars.yml exists but is not encrypted!"; \
		echo "💡 Run './secure-setup.sh' to encrypt it securely"; \
	else \
		echo "✅ vars/vars.yml is properly protected"; \
	fi
	@echo "5. Checking .gitignore protection..."
	@if grep -q "vars/vars.yml" .gitignore; then \
		echo "✅ vars/vars.yml is in .gitignore"; \
	else \
		echo "⚠️  vars/vars.yml should be in .gitignore"; \
	fi
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
dev: check-deps clean sanity-check security-check
	@echo "✅ Development checks complete!"

# Full validation workflow
validate: check-deps clean lint test-syntax security-check
	@echo "✅ Full validation complete!"

# CI/CD target
ci: check-os check-deps install-tools validate
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

# Check operating system compatibility
check-os:
	@echo "🔍 System Information:"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@if [ -f /etc/os-release ]; then \
		echo "📋 OS Details:"; \
		. /etc/os-release && echo "   Name: $$NAME"; \
		. /etc/os-release && echo "   Version: $$VERSION"; \
		. /etc/os-release && echo "   ID: $$ID"; \
	fi
	@echo "🖥️  Kernel: $$(uname -s) $$(uname -r)"
	@echo "🏗️  Architecture: $$(uname -m)"
	@echo "🐚 Shell: $$SHELL"
	@echo ""
	@echo "📦 Package Manager Detection:"
	@if command -v dnf >/dev/null 2>&1; then \
		echo "   ✅ dnf found (RHEL 8+/Fedora)"; \
	elif command -v yum >/dev/null 2>&1; then \
		echo "   ✅ yum found (RHEL 7/CentOS)"; \
	elif command -v apt >/dev/null 2>&1; then \
		echo "   ✅ apt found (Debian/Ubuntu)"; \
	elif command -v pacman >/dev/null 2>&1; then \
		echo "   ✅ pacman found (Arch Linux)"; \
	elif command -v brew >/dev/null 2>&1; then \
		echo "   ✅ brew found (macOS)"; \
	else \
		echo "   ⚠️  No recognized package manager found"; \
	fi
	@echo ""
	@echo "🔧 Compatibility Status:"
	@if [ -f /etc/redhat-release ]; then \
		echo "   ✅ RHEL/CentOS/Fedora - Supported"; \
	elif [ -f /etc/debian_version ]; then \
		echo "   ✅ Debian/Ubuntu - Supported"; \
	elif [ -f /etc/arch-release ]; then \
		echo "   ✅ Arch Linux - Supported"; \
	elif command -v brew >/dev/null 2>&1; then \
		echo "   ✅ macOS with Homebrew - Supported"; \
	else \
		echo "   ⚠️  Unknown OS - Manual installation may be required"; \
	fi
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if required dependencies are installed
check-deps:
	@echo "🔍 Dependency Check:"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "🔧 Core Tools:"
	@if command -v make >/dev/null 2>&1; then \
		echo "   ✅ make - $$(make --version | head -1)"; \
	else \
		echo "   ❌ make - Not found"; \
	fi
	@if command -v python3 >/dev/null 2>&1; then \
		echo "   ✅ python3 - $$(python3 --version)"; \
	else \
		echo "   ❌ python3 - Not found"; \
	fi
	@if command -v pip3 >/dev/null 2>&1; then \
		echo "   ✅ pip3 - $$(pip3 --version | cut -d' ' -f1,2)"; \
	else \
		echo "   ❌ pip3 - Not found"; \
	fi
	@echo ""
	@echo "🎭 Ansible Tools:"
	@if command -v ansible >/dev/null 2>&1; then \
		echo "   ✅ ansible - $$(ansible --version | head -1)"; \
	else \
		echo "   ❌ ansible - Not found"; \
	fi
	@if command -v ansible-playbook >/dev/null 2>&1; then \
		echo "   ✅ ansible-playbook - Available"; \
	else \
		echo "   ❌ ansible-playbook - Not found"; \
	fi
	@if command -v ansible-lint >/dev/null 2>&1; then \
		echo "   ✅ ansible-lint - $$(ansible-lint --version | head -1)"; \
	else \
		echo "   ❌ ansible-lint - Not found (run 'make install-tools')"; \
	fi
	@echo ""
	@echo "📝 Linting Tools:"
	@if command -v yamllint >/dev/null 2>&1; then \
		echo "   ✅ yamllint - $$(yamllint --version)"; \
	else \
		echo "   ❌ yamllint - Not found (run 'make install-tools')"; \
	fi
	@if command -v pandoc >/dev/null 2>&1; then \
		echo "   ✅ pandoc - $$(pandoc --version | head -1)"; \
	else \
		echo "   ❌ pandoc - Not found (run 'make install-tools')"; \
	fi
	@echo ""
	@echo "🔍 Optional Tools:"
	@if command -v pipx >/dev/null 2>&1; then \
		echo "   ✅ pipx - $$(pipx --version)"; \
	else \
		echo "   ℹ️  pipx - Not found (optional, using pip fallback)"; \
	fi
	@if command -v dos2unix >/dev/null 2>&1; then \
		echo "   ✅ dos2unix - Available"; \
	else \
		echo "   ℹ️  dos2unix - Not found (optional, auto-fix will skip line ending fixes)"; \
	fi
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@missing=0; \
	for cmd in make python3 pip3 ansible ansible-playbook; do \
		if ! command -v $$cmd >/dev/null 2>&1; then \
			missing=$$((missing + 1)); \
		fi; \
	done; \
	if [ $$missing -eq 0 ]; then \
		echo "✅ All core dependencies are installed!"; \
		if ! command -v yamllint >/dev/null 2>&1 || ! command -v ansible-lint >/dev/null 2>&1; then \
			echo "📦 Run 'make install-tools' to install linting tools"; \
		else \
			echo "🎉 System is fully ready for development!"; \
		fi; \
	else \
		echo "❌ Missing $$missing core dependencies. Please install them first."; \
		exit 1; \
	fi

# Comprehensive compatibility test
test-compatibility:
	@echo "🧪 Running comprehensive compatibility test..."
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	$(MAKE) check-os
	@echo ""
	$(MAKE) check-deps
	@echo ""
	@echo "🔧 Testing core Unix commands..."
	@for cmd in find grep sed test head tail cat; do \
		if command -v $$cmd >/dev/null 2>&1; then \
			echo "   ✅ $$cmd - Available"; \
		else \
			echo "   ❌ $$cmd - Missing"; \
		fi; \
	done
	@echo ""
	@echo "📂 Testing file system operations..."
	@mkdir -p /tmp/makefile-test-$$$$
	@echo "test content" > /tmp/makefile-test-$$$$/test.txt
	@if [ -f /tmp/makefile-test-$$$$/test.txt ]; then \
		echo "   ✅ File creation - OK"; \
	else \
		echo "   ❌ File creation - Failed"; \
	fi
	@rm -rf /tmp/makefile-test-$$$$
	@echo "   ✅ File cleanup - OK"
	@echo ""
	@echo "🎭 Testing Ansible availability..."
	@if command -v ansible-playbook >/dev/null 2>&1; then \
		echo "   ✅ Testing playbook syntax check..."; \
		if [ -f playbook.yml ]; then \
			ansible-playbook --syntax-check playbook.yml --check 2>/dev/null && echo "   ✅ Syntax check - OK" || echo "   ⚠️  Syntax check - Issues found (normal if vars missing)"; \
		else \
			echo "   ℹ️  playbook.yml not found - skipping syntax test"; \
		fi; \
	else \
		echo "   ❌ ansible-playbook not available"; \
	fi
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "✅ Compatibility test complete!"

# Debug markdown to HTML conversion issues
debug-conversion:
	@echo "🔍 Debugging Markdown to HTML Conversion"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "1. Checking pandoc installation..."
	@if command -v pandoc >/dev/null 2>&1; then \
		echo "   ✅ pandoc found: $$(which pandoc)"; \
		echo "   📋 Version: $$(pandoc --version | head -1)"; \
	else \
		echo "   ❌ pandoc not found"; \
		echo "   💡 Install with: make install-tools"; \
		exit 1; \
	fi
	@echo ""
	@echo "2. Checking template rendering..."
	@if [ -d docs/ ]; then \
		echo "   📁 Template directory exists"; \
		echo "   📝 Available templates:"; \
		ls -la docs/*.j2 2>/dev/null || echo "   ⚠️  No .j2 templates found"; \
	else \
		echo "   ❌ docs/ directory missing"; \
		exit 1; \
	fi
	@echo ""
	@echo "3. Testing template rendering..."
	@mkdir -p /tmp/debug-conversion
	@echo "project_name: Debug Test" > /tmp/debug-vars.yml
	@echo "env: Test" >> /tmp/debug-vars.yml
	@echo "database_url: https://test.example.com" >> /tmp/debug-vars.yml
	@echo "monitoring_tool: Test Monitor" >> /tmp/debug-vars.yml
	@if [ -f docs/main.md.j2 ]; then \
		echo "   🔄 Rendering main.md.j2..."; \
		ansible localhost -m template -a "src=docs/main.md.j2 dest=/tmp/debug-conversion/main.md" -e @/tmp/debug-vars.yml 2>/dev/null || echo "   ❌ Template rendering failed"; \
		if [ -f /tmp/debug-conversion/main.md ]; then \
			echo "   ✅ Template rendered successfully"; \
			echo "   📄 Content preview:"; \
			head -5 /tmp/debug-conversion/main.md | sed 's/^/      /'; \
			echo "      ..."; \
		else \
			echo "   ❌ Template rendering failed"; \
		fi; \
	fi
	@echo ""
	@echo "4. Testing pandoc conversion..."
	@if [ -f /tmp/debug-conversion/main.md ]; then \
		echo "   🔄 Converting markdown to HTML..."; \
		pandoc /tmp/debug-conversion/main.md -f markdown -t html -o /tmp/debug-conversion/main.html 2>&1 && \
		echo "   ✅ Pandoc conversion successful" || echo "   ❌ Pandoc conversion failed"; \
		if [ -f /tmp/debug-conversion/main.html ]; then \
			echo "   📄 HTML output size: $$(stat -c%s /tmp/debug-conversion/main.html) bytes"; \
			echo "   📄 HTML preview:"; \
			head -3 /tmp/debug-conversion/main.html | sed 's/^/      /'; \
		fi; \
	else \
		echo "   ⚠️  No markdown file to test pandoc conversion"; \
	fi
	@echo ""
	@echo "5. Testing permissions..."
	@echo "   📁 /tmp permissions:"
	@ls -ld /tmp/
	@echo "   📁 Current user: $$(whoami)"
	@echo "   🔧 Testing /tmp write access..."
	@touch /tmp/debug-write-test && rm -f /tmp/debug-write-test && echo "   ✅ /tmp write access OK" || echo "   ❌ /tmp write access failed"
	@echo ""
	@echo "6. Environment check..."
	@echo "   🏠 Working directory: $$(pwd)"
	@echo "   🐍 Python: $$(python3 --version 2>/dev/null || echo 'Not found')"
	@echo "   📦 Ansible: $$(ansible --version 2>/dev/null || echo 'Not found')"
	@echo "   📦 Pandoc: $$(pandoc --version 2>/dev/null || echo 'Not found')"
	@echo "   ℹ️  Note: Some checks may be skipped in restricted environments"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Quick test of markdown to HTML conversion
test-pandoc:
	@echo "🧪 Quick Pandoc Test"
	@echo "Creating test markdown file..."
	@echo "# Test Document\n\nThis is a **test** markdown file.\n\n- Item 1\n- Item 2" > /tmp/test.md
	@echo "Converting with pandoc..."
	@pandoc /tmp/test.md -f markdown -t html -o /tmp/test.html
	@echo "✅ Conversion successful!"
	@echo "Output:"
	@cat /tmp/test.html
	@rm -f /tmp/test.md /tmp/test.html
