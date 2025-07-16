# Documentation Workflow Guide

## 🎯 Overview

This project now features a **fully dynamic documentation workflow** that automatically discovers, processes, and publishes documentation templates to Confluence while preserving folder hierarchy.

## 🚀 Quick Start

### **Primary Workflow (Recommended)**
```bash
make run-full
```
This single command:
1. ✅ Dynamically discovers all templates in `docs/automation_hub/`
2. ✅ Renders templates to markdown with variable substitution
3. ✅ Converts markdown to HTML with enhanced formatting
4. ✅ Publishes to Confluence with proper parent-child hierarchy

### **Individual Steps**
```bash
make convert-templates-dynamic  # Step 1: Discover and render templates
make convert-markdown          # Step 2: Convert to HTML
make run-publish              # Step 3: Publish to Confluence
```

## 📁 Project Structure

```
docs/
├── automation_hub/           # Main documentation section
│   ├── automation_hub.j2     # Main parent page template
│   ├── platform_governance.j2
│   ├── platform_runbook.j2
│   ├── operator_runbook.j2
│   ├── training_enablement.j2
│   ├── daily_operations.j2
│   ├── escalation_procedures.j2
│   ├── network_configuration.j2
│   ├── security_operations.j2
│   ├── server_management.j2
│   ├── training_resources.j2
│   ├── certification_paths.j2
│   ├── troubleshooting_guide.j2
│   └── macros.j2            # Shared macros for templates
├── main.j2                  # Legacy main template
├── child.j2                 # Legacy child template
└── macros.j2               # Legacy shared macros

scripts/
├── discover_docs_enhanced.py # Dynamic discovery script
└── sync_documentation_repos.py # Repository synchronization

vars/
├── vars.yml                 # Main variables
└── aap.yml                 # Ansible Automation Platform variables

playbooks/
├── automation_hub_publishing.yml # Primary publishing playbook
├── main.yml                # Legacy orchestrator
├── 01-validate-environment.yml
├── 02-convert-templates.yml
├── 03-convert-html.yml
└── 04-publish-confluence.yml
```

## 🔧 How It Works

### **1. Dynamic Discovery**
- **Script**: `scripts/discover_docs_enhanced.py`
- **Purpose**: Automatically finds all `.j2` templates in `docs/automation_hub/`
- **Output**: JSON structure defining parent-child relationships
- **Benefits**: Zero maintenance - new templates are automatically discovered

### **2. Template Processing**
- **Engine**: Ansible template module
- **Variables**: Uses `vars/vars.yml` and `vars/aap.yml`
- **Output**: Rendered markdown files in `~/tmp/`
- **Features**: Full Jinja2 support with variable substitution

### **3. HTML Conversion**
- **Engine**: Pandoc with Lua filters
- **Filters**: 
  - `lua/pagebreak.lua` - Page break handling
  - `lua/list_formatter.lua` - Enhanced list formatting
- **Output**: HTML files ready for Confluence

### **4. Confluence Publishing**
- **Playbook**: `playbooks/automation_hub_publishing.yml`
- **Features**: 
  - Parent-child page relationships
  - Hierarchy preservation
  - Update detection and versioning
  - Auto-documentation support

## 📋 Available Make Targets

### **🔧 Development & Validation**
```bash
make lint                    # Run all linting checks
make test                    # Run ansible playbook syntax check
make sanity-check           # Quick development checks
make security-check         # Security validation
make validate-templates     # Template structure validation
```

### **🛠️ Installation & Setup**
```bash
make install-tools          # Install required tools
make check-deps            # Check dependency status
make check-os              # Display OS compatibility
make test-compatibility    # Comprehensive compatibility test
```

### **📚 Documentation Workflow (Primary)**
```bash
make run-full              # Complete dynamic workflow ✅
make run-dynamic-publish   # Dynamic discovery + publishing ✅
make convert-templates-dynamic  # Dynamic template conversion ✅
make convert-markdown      # Convert markdown to HTML
make convert-all          # Complete conversion workflow
make discover-enhanced    # Show discovery results
```

### **🔄 Individual Playbook Execution**
```bash
make run-validate         # Validate environment
make run-templates        # Convert templates (legacy)
make run-html            # Convert to HTML
make run-publish         # Publish to Confluence
```

### **🧹 Maintenance**
```bash
make clean               # Remove temporary files
make clean-conversion    # Clean conversion artifacts
make verify-html         # Verify HTML generation
make debug-conversion    # Debug conversion issues
```

## 🎯 Adding New Documentation

### **Adding New Templates**
1. Create new `.j2` file in `docs/automation_hub/`
2. Use existing templates as reference
3. Include shared macros: `{% from 'macros.j2' import ... %}`
4. Run `make run-full` - new template will be automatically discovered!

### **Template Structure Example**
```jinja2
{% from 'macros.j2' import page_header, auto_generated_notice %}
{{ page_header(title="Your Page Title") }}
{{ auto_generated_notice() }}

# Your Page Title

## Overview
{{ project_name }} specific content here...

## Key Information
- Environment: {{ env }}
- Database: {{ database_url }}
- Monitoring: {{ monitoring_tool }}

{% if some_condition %}
## Conditional Section
This section only appears when condition is met.
{% endif %}
```

### **Variables Available**
From `vars/vars.yml`:
- `project_name`
- `env`
- `database_url`
- `monitoring_tool`
- And many more...

From `vars/aap.yml`:
- Ansible Automation Platform specific variables

## 🔄 Publishing Workflow

### **Confluence Structure**
```
Automation Hub (Main Page)
├── Platform Governance
├── Platform Runbook
├── Operator Runbook
├── Training Enablement
├── Daily Operations
├── Escalation Procedures
├── Network Configuration
├── Security Operations
├── Server Management
├── Training Resources
├── Certification Paths
└── Troubleshooting Guide
```

### **Publishing Process**
1. **Discovery**: Find all templates and their relationships
2. **Rendering**: Process templates with variables
3. **Conversion**: Convert markdown to Confluence-compatible HTML
4. **Publishing**: Create/update pages with proper hierarchy
5. **Verification**: Confirm successful publication

## 🚨 Troubleshooting

### **Common Issues**

**Templates not being discovered?**
```bash
make discover-enhanced  # Check discovery output
ls -la docs/automation_hub/*.j2  # Verify templates exist
```

**Rendering failures?**
```bash
make debug-conversion  # Comprehensive debugging
make validate-templates  # Check template syntax
```

**Missing dependencies?**
```bash
make check-deps        # Check what's installed
make install-tools     # Install missing tools
```

**Confluence publishing issues?**
```bash
# Check variables are set
grep -A 5 confluence vars/vars.yml
# Validate environment
make run-validate
```

### **Debug Commands**
```bash
make debug-conversion    # Full conversion debugging
make test-pandoc        # Quick pandoc test
make verify-html        # Check generated HTML
```

## 💡 Best Practices

### **Template Development**
- Use shared macros for consistent formatting
- Include auto-generated notices
- Use conditional blocks for environment-specific content
- Test templates with `make convert-templates-dynamic`

### **Variable Management**
- Keep sensitive data in `vars/vars.yml` (encrypted)
- Use descriptive variable names
- Document new variables in templates

### **Workflow Integration**
- Use `make run-full` for complete workflow
- Test changes with individual steps first
- Verify HTML output before publishing

## 🔗 Integration

### **CI/CD Integration**
```yaml
# Example GitHub Actions
- name: Generate Documentation
  run: make run-full
  
- name: Validate Output
  run: make verify-html
```

### **Development Workflow**
1. Edit templates in `docs/automation_hub/`
2. Test with `make convert-templates-dynamic`
3. Review output in `~/tmp/`
4. Publish with `make run-publish`

## 📈 Benefits

- **🔄 Zero Maintenance**: New templates automatically discovered
- **📁 Hierarchy Preserved**: Folder structure maintained in Confluence
- **🎯 Consistent Output**: Standardized formatting and structure
- **⚡ Fast Iteration**: Quick testing and publishing cycles
- **🔧 Flexible**: Supports complex template hierarchies
- **📋 Well Documented**: Clear guidance and troubleshooting

## 🆘 Support

For issues or questions:
1. Check this documentation
2. Run `make help` for available targets
3. Use `make debug-conversion` for troubleshooting
4. Review generated files in `~/tmp/`
5. Check playbook logs for detailed error information

---

**💡 Remember**: The recommended workflow is simply `make run-full` for complete automation! 🚀
