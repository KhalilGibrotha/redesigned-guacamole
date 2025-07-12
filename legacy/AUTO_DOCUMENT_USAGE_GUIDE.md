# Auto-Document System Usage Guide

## 🚀 Quick Start

### 1. Add a Real Repository
Edit `vars/repos.yml`:
```yaml
documentation_repos:
  - name: "my-team-docs"
    url: "https://github.com/myorg/team-docs.git"
    branch: "main" 
    doc_path: "documentation/templates"
    confluence_parent: "Automation Hub"
    enabled: true
```

### 2. Set Up Authentication
```bash
# For GitHub token auth
export GITHUB_TOKEN="your_github_token_here"

# OR configure SSH keys for your git repositories
```

### 3. Run Full Documentation Generation
```bash
# Complete workflow: sync repos → convert templates → generate HTML
make convert-all

# Or run steps individually:
make sync-repos              # Clone/update repos
make convert-templates-nested # Convert all templates  
make convert-markdown        # Generate HTML files
```

### 4. Discover Current Structure
```bash
# JSON format (default)
python3 scripts/discover_docs_enhanced.py

# YAML format (more readable)
python3 scripts/discover_docs_enhanced.py --format yaml

# Specific section only
python3 scripts/discover_docs_enhanced.py --section automation_hub
```

## 📁 Repository Structure Requirements

For repositories to be automatically discovered, they should follow this structure:

```
your-repo/
├── README.md
├── src/
│   └── (your application code)
└── documentation/templates/     # doc_path from config
    ├── api_guide.j2            # Will become child page
    ├── deployment_guide.j2     # Will become child page
    └── troubleshooting/        # Nested section
        ├── troubleshooting.j2  # Main page for section
        ├── common_issues.j2    # Child page
        └── escalation.j2       # Child page
```

## 🎯 Template Requirements

### Shared Macros Import
All templates should import shared macros:
```jinja
{%- from 'docs/macros.j2' import oxford_comma_list -%}

# My Documentation Page

## Example Usage
Supported technologies: {{ oxford_comma_list(['Ansible', 'Python', 'YAML']) }}.
```

### Available Variables
Templates have access to all variables from `vars/aap.yml`:
- `ORGANIZATION_NAME`
- `ENVIRONMENT_TYPE` 
- `AAP_VERSION`
- `RHEL_VERSIONS`
- All other configured variables

## 🔄 Automatic Updates

### Manual Sync
```bash
# Update all enabled repositories
make sync-repos

# Force update (ignores sync_behavior settings)  
make sync-repos-force
```

### Scheduled Updates
Add to cron for automatic documentation updates:
```bash
# Update documentation every hour
0 * * * * cd /path/to/project && make convert-all
```

## 📋 Confluence Publishing

### Manual Publishing
```bash
# Run enhanced Confluence publishing playbook
ansible-playbook playbooks/enhanced_confluence_publishing.yml

# With custom variables
ansible-playbook playbooks/enhanced_confluence_publishing.yml \
  -e confluence_url="https://mycompany.atlassian.net/wiki" \
  -e confluence_space="DOCS"
```

### Page Update Behavior
- **Existing pages**: Updated with new content, version incremented
- **New pages**: Created with proper parent relationships  
- **Auto-document pages**: Tagged with `auto-document` and `documentation-as-code` labels

## 🔧 Troubleshooting

### Repository Sync Issues
```bash
# Check repository configuration
python3 scripts/sync_documentation_repos.py --config vars/repos.yml

# Verify repository access
git clone https://github.com/yourorg/repo.git /tmp/test-clone
```

### Template Issues
```bash  
# Validate all templates
make validate-templates

# Test specific template
ansible localhost -m template \
  -a "src=docs/automation_hub/automation_hub.j2 dest=/tmp/test.md" \
  -e @vars/aap.yml
```

### Discovery Issues
```bash
# Debug discovery output
python3 scripts/discover_docs_enhanced.py --section automation_hub

# Check for permission issues
ls -la docs/auto_document/
```

## 🎯 Best Practices

### Repository Organization
1. **Keep templates separate** from code in a `docs/` or `documentation/` folder
2. **Use descriptive filenames** (they become page titles)
3. **Follow naming conventions**: `section_name.j2` for main pages
4. **Create nested folders** for logical grouping

### Template Standards  
1. **Import shared macros** consistently
2. **Use meaningful variable names** 
3. **Include proper headers** and navigation
4. **Test templates locally** before committing

### Confluence Integration
1. **Use descriptive page titles**
2. **Maintain proper parent-child relationships**
3. **Tag auto-document content** appropriately
4. **Monitor page updates** for conflicts

The system is designed to be **self-discovering** and **low-maintenance** once configured!
