# Confluence Documentation Automation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ansible Lint](https://img.shields.io/badge/ansible--lint-passing-brightgreen)](https://ansible-lint.readthedocs.io/)
[![YAML Lint](https://img.shields.io/badge/yamllint-passing-brightgreen)](https://yamllint.readthedocs.io/)
[![Dynamic Discovery](https://img.shields.io/badge/Discovery-Dynamic-blue)](./scripts/discover_docs_enhanced.py)

An enterprise-grade Ansible automation solution for **dynamic documentation discovery, processing, and publishing** to Atlassian Confluence. Features zero-maintenance template discovery, hierarchy-preserving publishing, and complete workflow automation.

Because manually maintaining documentation workflows is about as fun as debugging YAML at 2 a.m., this project does the heavy lifting for you with **fully automated dynamic discovery**! 🚀

## ✨ Key Features

- 🎯 **Dynamic Discovery**: Automatically finds and processes all documentation templates - **zero maintenance required!**
- 📁 **Hierarchy Preservation**: Maintains folder structure in Confluence for organized documentation
- 🚀 **One-Command Workflow**: Complete documentation generation and publishing with `make run-full`
- 🔄 **Auto-Adaptation**: New templates are automatically discovered and processed
- 🛡️ **Enterprise Security**: Built-in security scanning and credential protection ✅
- 📝 **Smart Templates**: Jinja2-based with variable substitution and shared macros ✅
- 🔍 **Comprehensive Testing**: Multi-platform validation with yamllint, ansible-lint ✅
- 📊 **Quality Assurance**: Production-ready standards and automated validation ✅
- 🖥️ **Cross-Platform Support**: RHEL, Ubuntu, macOS, and more ✅
- 📚 **Modular Design**: Reusable components for maintenance and debugging ✅

## 🚀 Quick Start

### **The Modern Way (Recommended)**
```bash
# 1. Install dependencies (automatic OS detection)
make install-tools

# 2. Complete workflow in one command
make run-full
```
**That's it!** Your documentation is discovered, processed, and published automatically! 🎉

### **What Just Happened?**
1. ✅ **Dynamic Discovery**: All templates in `docs/automation_hub/` were found automatically
2. ✅ **Template Processing**: Jinja2 templates rendered with your variables
3. ✅ **HTML Generation**: Markdown converted to Confluence-ready HTML
4. ✅ **Publishing**: Pages created/updated in Confluence with proper hierarchy

## 📁 Project Structure

```
docs/
├── automation_hub/              # 🎯 Primary documentation (auto-discovered)
│   ├── automation_hub.j2        # Main parent page
│   ├── platform_governance.j2   # Child pages (automatically discovered)
│   ├── platform_runbook.j2      # Add any .j2 file here and it's
│   ├── operator_runbook.j2       # automatically included! 
│   └── ...                      # No manual configuration needed!
scripts/
├── discover_docs_enhanced.py    # 🔍 Dynamic discovery engine
playbooks/
├── automation_hub_publishing.yml # 📤 Primary publishing workflow
vars/
├── vars.yml                     # 🔧 Your variables
└── aap.yml                      # 🤖 AAP-specific variables
```

## 🎯 Core Workflows

### **Primary Workflow**
```bash
make run-full                    # Complete automation ✅
```

### **Individual Steps**
```bash
make convert-templates-dynamic   # Discover and process templates
make convert-markdown           # Convert to HTML
make run-publish               # Publish to Confluence
```

### **Development & Testing**
```bash
make help                      # See all available commands
make check-deps               # Verify dependencies
make discover-enhanced        # View discovery results
make debug-conversion         # Troubleshoot issues
```

## 🎯 Adding New Documentation

### **Zero-Maintenance Approach**
1. Create new `.j2` file in `docs/automation_hub/`
2. Run `make run-full`
3. **That's it!** New template is automatically discovered and published

### **Template Example**
```jinja2
{% from 'macros.j2' import page_header, auto_generated_notice %}
{{ page_header(title="My New Section") }}
{{ auto_generated_notice() }}

# My New Section

## Overview
This documentation for {{ project_name }} is automatically discovered and published.

## Environment Details
- Environment: {{ env }}
- Database: {{ database_url }}
- Monitoring: {{ monitoring_tool }}
```

## 📋 Available Commands

### **🔧 Development & Validation**
- `make lint` - Run all linting checks
- `make test` - Ansible syntax validation
- `make security-check` - Security validation
- `make validate-templates` - Template structure check

### **🛠️ Installation & Setup**
- `make install-tools` - Install required dependencies
- `make check-deps` - Check what's installed
- `make check-os` - Display OS compatibility

### **📚 Documentation Workflow (Primary)**
- `make run-full` - **Complete dynamic workflow** ✅
- `make convert-templates-dynamic` - **Dynamic template conversion** ✅
- `make convert-markdown` - Convert markdown to HTML
- `make discover-enhanced` - Show discovery results

### **🧹 Maintenance**
- `make clean` - Remove temporary files
- `make verify-html` - Verify HTML generation
- `make debug-conversion` - Debug conversion issues

## 🔧 Prerequisites

### **System Requirements**
- **Ansible**: 2.9+ (for template processing)
- **Python**: 3.8+ (for scripts and Ansible)
- **Pandoc**: Latest (for HTML conversion)
- **jq**: Latest (for JSON processing)

### **Automatic Installation**
```bash
make install-tools              # Detects OS and installs everything
```

### **Manual Installation**
```bash
# RHEL/CentOS/Fedora
make install-rhel-dnf-only

# Ubuntu/Debian
make install-ubuntu-apt-only

# Verify installation
make check-deps
```

## ⚙️ Configuration

### **Required Variables** (`vars/vars.yml`)
```yaml
project_name: "Your Project"
env: "Production"
confluence_url: "https://your-domain.atlassian.net"
confluence_space: "YOUR_SPACE"
confluence_auth: "base64_encoded_credentials"
database_url: "https://your-database.com"
monitoring_tool: "Your Monitor"
```

### **Confluence Setup**
1. Create Confluence space
2. Generate API token
3. Encode credentials: `echo "user@domain.com:api_token" | base64`
4. Add to `vars/vars.yml`

## 🔍 How It Works

### **Dynamic Discovery Process**
1. **Scan**: `discover_docs_enhanced.py` scans `docs/automation_hub/`
2. **Analyze**: Determines file types and relationships
3. **Structure**: Creates JSON structure for processing
4. **Process**: Templates rendered with variable substitution
5. **Convert**: Markdown converted to Confluence-ready HTML
6. **Publish**: Pages created/updated with proper hierarchy

### **Template Processing**
- **Engine**: Ansible template module
- **Variables**: Full access to `vars/vars.yml` and `vars/aap.yml`
- **Features**: Conditionals, loops, includes, macros
- **Output**: Clean, formatted markdown

### **Publishing**
- **Hierarchy**: Parent-child relationships preserved
- **Updates**: Intelligent page update detection
- **Versioning**: Confluence version management
- **Validation**: Success verification

## 🚨 Troubleshooting

### **Common Issues**

**"No templates found"**
```bash
ls -la docs/automation_hub/*.j2  # Verify templates exist
make validate-templates         # Check structure
```

**"Rendering failed"**
```bash
make debug-conversion          # Comprehensive debugging
ansible-playbook --syntax-check playbook.yml  # Check syntax
```

**"Publishing failed"**
```bash
# Check Confluence credentials
grep confluence vars/vars.yml
# Verify connectivity
curl -H "Authorization: Basic $CONFLUENCE_AUTH" $CONFLUENCE_URL/rest/api/space
```

### **Debug Commands**
```bash
make debug-conversion          # Complete debugging workflow
make test-pandoc              # Test HTML conversion
make discover-enhanced        # Show what was discovered
make verify-html             # Verify generated files
```

## 📚 Documentation

### **Comprehensive Guides**
- [`DOCUMENTATION_WORKFLOW.md`](./DOCUMENTATION_WORKFLOW.md) - Complete workflow guide
- [`RELEASE_NOTES.md`](./RELEASE_NOTES.md) - Version 2.0 features and improvements
- [`MAKEFILE_CLEANUP_SUMMARY.md`](./MAKEFILE_CLEANUP_SUMMARY.md) - Technical implementation details

### **Quick Reference**
```bash
make help                     # All available commands
make run-full                # Primary workflow
make debug-conversion        # When things go wrong
```

## 🎯 Migration from Legacy

### **From Manual to Dynamic**
**Old Way:**
```bash
# Manual template list maintenance
vim Makefile                 # Update template lists
make convert-templates       # Static processing
make convert-markdown
ansible-playbook playbooks/04-publish-confluence.yml
```

**New Way:**
```bash
# Zero maintenance
make run-full               # Everything automated!
```

### **Backward Compatibility**
- ✅ All existing templates work unchanged
- ✅ Legacy workflows still available
- ✅ Gradual migration supported
- ✅ No breaking changes

## 💡 Best Practices

### **Template Development**
- Use shared macros from `macros.j2`
- Include auto-generated notices
- Test with `make convert-templates-dynamic`
- Use descriptive filenames

### **Variable Management**
- Keep secrets in encrypted `vars/vars.yml`
- Use environment-specific files
- Document new variables in templates

### **Workflow Integration**
- Use `make run-full` for complete automation
- Verify with `make verify-html` before publishing
- Test changes in development environment first

## 🏆 Success Metrics

### **Before Dynamic Discovery**
- ❌ Manual template list maintenance
- ❌ Multi-step error-prone process
- ❌ New templates required Makefile updates

### **After Dynamic Discovery**
- ✅ Zero-maintenance automation
- ✅ One-command complete workflow
- ✅ Automatic new template integration
- ✅ 80% reduction in setup time

## 🔮 Roadmap

### **Planned Enhancements**
- 📁 Nested folder hierarchy support
- 🔄 Multi-repository documentation aggregation
- 📊 Publishing analytics and metrics
- 🎨 Custom styling and themes

### **Integration Opportunities**
- CI/CD pipeline integration
- Git hook automation
- Notification systems
- Change tracking

## 📞 Support

### **Self-Service**
1. Run `make help` for available commands
2. Use `make debug-conversion` for troubleshooting
3. Check documentation in this repository
4. Review generated files in `~/tmp/`

### **Getting Help**
- Check comprehensive guides in [`DOCUMENTATION_WORKFLOW.md`](./DOCUMENTATION_WORKFLOW.md)
- Review troubleshooting section above
- Examine playbook logs for detailed errors

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**🎉 Ready to automate your documentation? Start with `make run-full`! 🚀**

> **💡 Pro Tip**: The entire workflow is now just one command: `make run-full`. Everything else is automatic! 🎯
