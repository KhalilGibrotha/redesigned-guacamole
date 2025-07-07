#!/bin/bash
# Confluence Documentation Automation - Quick Setup Script
# This script helps you get started quickly and securely

set -e  # Exit on any error

echo "🚀 Confluence Documentation Automation - Quick Setup"
echo "=================================================="

# Quick OS detection and compatibility notice
echo -e "${BLUE}🔍 Detecting system...${NC}"
if [ -f /etc/redhat-release ]; then
    echo -e "${GREEN}✅ RHEL/CentOS/Fedora system detected - Fully supported${NC}"
elif [ -f /etc/debian_version ]; then
    echo -e "${GREEN}✅ Debian/Ubuntu system detected - Fully supported${NC}"
elif [ -f /etc/arch-release ]; then
    echo -e "${GREEN}✅ Arch Linux system detected - Fully supported${NC}"
elif command -v brew &> /dev/null; then
    echo -e "${GREEN}✅ macOS with Homebrew detected - Fully supported${NC}"
else
    echo -e "${YELLOW}⚠️  Unknown OS detected - Manual installation may be required${NC}"
fi
echo

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
missing_core_tools=()

# Check core system tools first
if ! command -v make &> /dev/null; then
    missing_core_tools+=("make")
fi

if ! command -v python3 &> /dev/null; then
    missing_core_tools+=("python3")
fi

if ! command -v pip3 &> /dev/null; then
    missing_core_tools+=("pip3")
fi

# Check Ansible tools
if ! command -v ansible &> /dev/null; then
    missing_tools+=("ansible")
fi

if ! command -v yamllint &> /dev/null; then
    missing_tools+=("yamllint")
fi

if ! command -v ansible-lint &> /dev/null; then
    missing_tools+=("ansible-lint")
fi

if [ ${#missing_core_tools[@]} -eq 0 ] && [ ${#missing_tools[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All required tools are installed${NC}"
elif [ ${#missing_core_tools[@]} -gt 0 ]; then
    echo -e "${RED}❌ Missing core system tools: ${missing_core_tools[*]}${NC}"
    echo
    echo -e "${YELLOW}📦 Installation instructions:${NC}"
    
    # Detect OS and provide specific instructions
    if [ -f /etc/redhat-release ]; then
        echo "RHEL/CentOS/Fedora detected:"
        if command -v dnf &> /dev/null; then
            echo "  Option 1 - Full installation (requires internet access):"
            echo "    sudo dnf groupinstall -y 'Development Tools'"
            echo "    sudo dnf install -y python3 python3-pip"
            echo "    OR run: make install-rhel-prereqs"
            echo ""
            echo "  Option 2 - DNF-only installation (for restricted environments):"
            echo "    sudo dnf install -y make python3 ansible yamllint"
            echo "    # Note: ansible-lint may not be available via DNF"
            echo "    # You can skip ansible-lint for basic functionality"
        elif command -v yum &> /dev/null; then
            echo "  sudo yum groupinstall -y 'Development Tools'"
            echo "  sudo yum install -y python3 python3-pip"
        fi
    elif [ -f /etc/debian_version ]; then
        echo "Debian/Ubuntu detected:"
        echo "  sudo apt update"
        echo "  sudo apt install -y build-essential python3 python3-pip"
    elif [ -f /etc/arch-release ]; then
        echo "Arch Linux detected:"
        echo "  sudo pacman -S base-devel python python-pip"
    elif command -v brew &> /dev/null; then
        echo "macOS with Homebrew detected:"
        echo "  xcode-select --install  # for make"
        echo "  brew install python3"
    else
        echo "Unknown OS. Please install: make, python3, pip3"
    fi
    
    echo
    echo -e "${RED}⚠️  Please install core tools first, then run this script again.${NC}"
    exit 1
else
    echo -e "${YELLOW}⚠️  Missing optional tools: ${missing_tools[*]}${NC}"
    echo "Install them with: make install-tools"
    
    # Special note for RHEL systems about restricted environments
    if [ -f /etc/redhat-release ] && command -v dnf &> /dev/null; then
        echo
        echo -e "${BLUE}💡 RHEL Note: If pip access is restricted in your environment:${NC}"
        echo "  Use: make install-rhel-dnf-only"
        echo "  This installs available tools via DNF without requiring pip"
    fi
fi

echo
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo
echo "Next steps:"
echo "1. Run './secure-setup.sh' to securely configure credentials"
echo "2. Run 'make check-deps' to verify all dependencies"
echo "3. Run 'make install-tools' if any tools are missing"
echo "4. Run 'make validate' to test your configuration"
echo "5. Run 'ansible-playbook playbook.yml --ask-vault-pass' to publish documentation"
echo
echo "Useful commands:"
echo "  make check-os           - Check system compatibility"
echo "  make test-compatibility - Run comprehensive tests"
echo "  make install-rhel-dnf-only - Install via DNF only (restricted environments)"
echo "  make help              - Show all available targets"
echo
echo "For more information, see README.md"
