#!/bin/bash
# Secure setup script for Confluence Documentation Automation
# This script helps users set up credentials securely

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "🔐 Confluence Documentation Automation - Secure Setup"
echo "======================================================"

# Check if ansible-vault is available
if ! command -v ansible-vault &> /dev/null; then
    echo -e "${RED}❌ ansible-vault not found. Please install Ansible first.${NC}"
    echo "Run: make install-tools"
    exit 1
fi

# Check if vars.yml exists
if [ -f "vars/vars.yml" ]; then
    echo -e "${YELLOW}⚠️  vars/vars.yml already exists.${NC}"
    
    # Check if it's already encrypted
    if head -1 vars/vars.yml | grep -q "ANSIBLE_VAULT"; then
        echo -e "${GREEN}✅ vars/vars.yml is already encrypted with ansible-vault${NC}"
        echo "To edit: ansible-vault edit vars/vars.yml"
        exit 0
    else
        echo -e "${YELLOW}⚠️  vars/vars.yml exists but is not encrypted!${NC}"
        read -p "Do you want to encrypt it now? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}🔒 Encrypting existing vars/vars.yml...${NC}"
            ansible-vault encrypt vars/vars.yml
            echo -e "${GREEN}✅ vars/vars.yml has been encrypted${NC}"
            exit 0
        fi
    fi
else
    echo -e "${BLUE}📋 Creating new encrypted vars/vars.yml...${NC}"
    
    # Create from template
    cp vars/vars.yml.example vars/vars.yml
    
    echo -e "${YELLOW}📝 Please edit vars/vars.yml with your actual values before encryption${NC}"
    echo "Required changes:"
    echo "  1. Set your project_name"
    echo "  2. Set your confluence_url (your Atlassian domain)"
    echo "  3. Set your confluence_space (space key)"
    echo "  4. Replace confluence_auth with your base64 encoded credentials"
    echo ""
    echo "To create confluence_auth:"
    echo "  echo -n 'your-email@domain.com:your-api-token' | base64"
    echo ""
    read -p "Press Enter when you've updated vars/vars.yml with your values..."
    
    # Encrypt the file
    echo -e "${BLUE}🔒 Encrypting vars/vars.yml...${NC}"
    ansible-vault encrypt vars/vars.yml
    echo -e "${GREEN}✅ vars/vars.yml has been encrypted${NC}"
fi

echo
echo -e "${GREEN}🎉 Secure setup complete!${NC}"
echo
echo "To manage your encrypted vars.yml:"
echo "  ansible-vault edit vars/vars.yml     # Edit encrypted file"
echo "  ansible-vault view vars/vars.yml     # View encrypted file"
echo "  ansible-vault decrypt vars/vars.yml  # Decrypt (not recommended)"
echo ""
echo "To run the playbook with encrypted vars:"
echo "  ansible-playbook playbook.yml --ask-vault-pass"
echo "  OR set ANSIBLE_VAULT_PASSWORD_FILE environment variable"
echo ""
echo -e "${RED}🔐 SECURITY REMINDERS:${NC}"
echo "1. NEVER commit decrypted vars/vars.yml to git"
echo "2. Keep your vault password secure and separate"
echo "3. Consider using external secret management in production"
echo "4. Regularly rotate your Confluence API tokens"
