#!/bin/bash

# =============================================================================
# Quick Validation Script - Essential Checks Only
# =============================================================================
# This script runs only the most critical validation checks
# Use this for quick branch validation before merge
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Running Quick Validation Checks...${NC}\n"

# 1. Essential file checks
echo -e "${BLUE}1. Checking essential files...${NC}"
test -f playbook.yml && echo "✅ playbook.yml exists"
test -f vars/vars.yml.example && echo "✅ vars.yml.example exists"
test -f .yamllint && echo "✅ .yamllint config exists"

# 2. YAML syntax
echo -e "\n${BLUE}2. YAML syntax validation...${NC}"
if command -v yamllint >/dev/null 2>&1; then
    yamllint -c .yamllint playbook.yml && echo "✅ playbook.yml syntax OK"
    yamllint -c .yamllint vars/vars.yml.example && echo "✅ vars.yml.example syntax OK"
else
    echo -e "${YELLOW}⚠️  yamllint not found, skipping YAML validation${NC}"
fi

# 3. Ansible syntax
echo -e "\n${BLUE}3. Ansible syntax validation...${NC}"
if command -v ansible-playbook >/dev/null 2>&1; then
    ansible-playbook --syntax-check playbook.yml && echo "✅ Ansible syntax OK"
else
    echo -e "${YELLOW}⚠️  ansible-playbook not found, skipping Ansible validation${NC}"
fi

# 4. Template structure
echo -e "\n${BLUE}4. Template structure...${NC}"
test -d docs/ && echo "✅ docs/ directory exists"
test -f docs/main.md.j2 && echo "✅ main.md.j2 template exists"
find docs/ -name "*.j2" | wc -l | grep -q "[1-9]" && echo "✅ Template files found"

# 5. Security quick check
echo -e "\n${BLUE}5. Security quick check...${NC}"
if ! grep -r "password.*:" . --include="*.yml" | grep -v "example\|template\|YOUR_.*_HERE" >/dev/null 2>&1; then
    echo "✅ No obvious secrets in YAML files"
else
    echo -e "${YELLOW}⚠️  Potential secrets found - review recommended${NC}"
fi

# 6. Git status
echo -e "\n${BLUE}6. Git status...${NC}"
if git status --porcelain | grep -q .; then
    echo -e "${YELLOW}⚠️  Uncommitted changes found${NC}"
    git status --short
else
    echo "✅ Working directory clean"
fi

echo -e "\n${GREEN}🎯 Quick validation complete!${NC}"
echo -e "${BLUE}💡 Run './validate-all.sh' for comprehensive validation${NC}"
