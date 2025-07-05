#!/bin/bash
# Confluence Documentation Automation - Quick Setup Script
# This script helps you get started quickly and securely

set -e  # Exit on any error

echo "🚀 Confluence Documentation Automation - Quick Setup"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if vars.yml already exists
if [ -f "vars/vars.yml" ]; then
    echo -e "${YELLOW}⚠️  vars/vars.yml already exists.${NC}"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled. Your existing vars.yml is unchanged."
        exit 0
    fi
fi

# Copy example configuration
echo -e "${BLUE}📋 Creating configuration file...${NC}"
cp vars/vars.yml.example vars/vars.yml

echo -e "${GREEN}✅ Configuration file created at vars/vars.yml${NC}"
echo

# Security warning
echo -e "${RED}🔐 IMPORTANT SECURITY NOTICE:${NC}"
echo "1. Edit vars/vars.yml with your actual Confluence credentials"
echo "2. NEVER commit real credentials to version control!"
echo "3. Consider using ansible-vault to encrypt the file:"
echo -e "   ${BLUE}ansible-vault encrypt vars/vars.yml${NC}"
echo

# Check if tools are installed
echo -e "${BLUE}🔧 Checking required tools...${NC}"

missing_tools=()

if ! command -v ansible &> /dev/null; then
    missing_tools+=("ansible")
fi

if ! command -v yamllint &> /dev/null; then
    missing_tools+=("yamllint")
fi

if ! command -v ansible-lint &> /dev/null; then
    missing_tools+=("ansible-lint")
fi

if [ ${#missing_tools[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All required tools are installed${NC}"
else
    echo -e "${YELLOW}⚠️  Missing tools: ${missing_tools[*]}${NC}"
    echo "Install them with: make install-tools"
fi

echo
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo
echo "Next steps:"
echo "1. Edit vars/vars.yml with your Confluence details"
echo "2. Run 'make validate' to test your configuration"
echo "3. Run 'ansible-playbook playbook.yml' to publish documentation"
echo
echo "For more information, see README.md"
