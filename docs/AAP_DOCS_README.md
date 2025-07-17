# AAP Documentation Templates

This directory contains documentation templates copied from the `bug-free-fiesta` repository for Confluence automation.

## 📁 Files Copied

### **Core Templates** (.j2 files - Jinja2 templates)
- `aap_policy_governance.j2` - Comprehensive AAP policy and governance framework
- `aap_operations_manual.j2` - Operations manual for AAP platform management
- `aap_platform_admin_guide.j2` - Administrative guide for platform administrators

### **Supporting Files**
- `macros/macros.j2` - Reusable Jinja2 macros (especially `oxford_comma_list`)
- `vars.yaml` - Variable definitions for template rendering
- `cool-test-feature.md` - Sample markdown file with Confluence metadata

## 🔧 Template System Overview

### **Confluence Metadata Structure**
Each template file contains frontmatter with Confluence publishing configuration:

```yaml
---
# Metadata for Confluence Publishing
varsFile: "docs/vars.yaml"
project_status: "In Review"

# Confluence Metadata
confluence:
  title: "Document Title"
  space: "AH"                    # Confluence space key
  parentPageId: "1343742"        # Parent page ID in Confluence
  imageFolder: "docs/images"     # Folder for images
---
```

### **Variable Substitution**
Templates use Jinja2 syntax for variable substitution:
- `{{ ORGANIZATION_NAME }}` - Organization name
- `{{ AAP_VERSION }}` - AAP version
- `{{ macros.oxford_comma_list(AAP_METRICS) }}` - Formatted lists

### **Macro Usage**
The `oxford_comma_list` macro formats lists with proper Oxford comma:
```jinja2
{% import './docs/macros/macros.j2' as macros %}
{{ macros.oxford_comma_list(AAP_ROLE_DOMAINS) }}
```

## 🚀 Next Steps for Confluence Automation

1. **Update Variables**: Modify `vars.yaml` with your actual organization values
2. **Configure Confluence**: Update space keys and parent page IDs in templates
3. **Test Rendering**: Use Ansible/Jinja2 to render templates with variables
4. **Integrate Workflow**: Connect to your `publish-docs.yml` workflow for automation

## 📋 Template Contents

### AAP Policy & Governance
- Role-based access control (RBAC) framework
- Organization structure and team definitions
- Security and compliance standards
- Execution environment management
- Inventory and credential governance

### Operations Manual
- Operational procedures and policies
- Performance metrics and governance
- Technology stack documentation
- Roles and responsibilities matrix
- Change management processes

### Platform Admin Guide
- Administrative responsibilities
- Execution Environment (EE) management
- RBAC enforcement procedures
- Security and governance policies
- Troubleshooting guides

## 🔗 Integration with Workflows

These templates are designed to work with:
- **Ansible playbooks** for template rendering
- **GitHub Actions workflows** for automated publishing
- **Confluence API** for document management
- **Variables files** for environment-specific configuration

The `publish-docs.yml` workflow in your `.github/workflows/` directory can be updated to process these templates and publish them to Confluence automatically.
