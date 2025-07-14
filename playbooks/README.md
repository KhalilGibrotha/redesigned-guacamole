# Confluence Automation Playbooks

This directory contains modular Ansible playbooks for automated Confluence documentation publishing.
Because a single monolithic playbook is so last season, everything here is broken into bite-sized chunks.

## 📁 Structure

```
playbooks/
├── main.yml                    # 🎯 Main orchestrator playbook
├── 01-validate-environment.yml # ✅ Environment and dependency validation
├── 02-convert-templates.yml    # 🔄 Jinja2 template to markdown conversion
├── 03-convert-html.yml         # 📄 Markdown to HTML conversion (pandoc)
├── 04-publish-confluence.yml   # ☁️  Confluence API publishing
├── cleanup.yml                 # 🧹 Cleanup temporary files
└── README.md                   # 📖 This file
```

## 🚀 Usage

### Run Complete Automation
```bash
# Main automation workflow
ansible-playbook playbooks/main.yml

# Or using the legacy wrapper (backward compatibility)
ansible-playbook playbook.yml
```

### Run Individual Steps
```bash
# Validate environment only
ansible-playbook playbooks/01-validate-environment.yml

# Convert templates only
ansible-playbook playbooks/02-convert-templates.yml

# Convert to HTML only
ansible-playbook playbooks/03-convert-html.yml

# Publish to Confluence only (requires HTML files)
ansible-playbook playbooks/04-publish-confluence.yml

# Clean up temporary files
ansible-playbook playbooks/cleanup.yml
```

### Using Make Targets (Alternative)
```bash
# Template conversion
make convert-templates

# HTML conversion  
make convert-markdown

# Full conversion
make convert-all

# Verify results
make verify-html

# Cleanup
make clean-conversion
```

## 📋 Prerequisites

1. **Required Files:**
   - `vars/vars.yml` with Confluence credentials and configuration
   - Template files in `docs/` directory (*.j2 files)

2. **Required Tools:**
   - Ansible 2.9+
   - Pandoc
   - Make
   - curl/wget (for API calls)

3. **Environment Setup:**
   ```bash
   # Install dependencies
   make install-tools
   
   # Validate setup
   make check-deps
   ```

## 🔧 Configuration

### vars/vars.yml
```yaml
project_name: "Your Project Name"
env: "Development"
confluence_url: "https://your-instance.atlassian.net/wiki"
confluence_space: "YOUR_SPACE"
confluence_auth: "base64_encoded_credentials"

child_pages:
  - title: "Platform Governance"
    file: "platform_governance.md"
  # ... more pages
```

### Template Files (docs/*.j2)
- `main.md.j2` - Main documentation page
- `platform_governance.md.j2` - Platform governance content
- `platform_runbook.md.j2` - Platform operational procedures
- `operator_runbook.md.j2` - Operator procedures
- `training_enablement.md.j2` - Training materials

## 🐛 Troubleshooting

### Common Issues

1. **Template Conversion Fails:**
   ```bash
   # Check template syntax
   ansible-playbook playbooks/01-validate-environment.yml
   
   # Test manually
   make convert-templates
   ```

2. **HTML Conversion Fails:**
   ```bash
   # Check pandoc installation
   which pandoc
   pandoc --version
   
   # Test manually
   make convert-markdown
   ```

3. **Confluence Publishing Fails:**
   ```bash
   # Test API connectivity
   curl -H "Authorization: Basic YOUR_BASE64_CREDS" \
        "https://your-instance.atlassian.net/wiki/rest/api/content"
   
   # Verify credentials
   echo "YOUR_BASE64_CREDS" | base64 -d
   ```

### Debug Mode
```bash
# Run with verbose output
ansible-playbook playbooks/main.yml -v

# Run with extra debugging
ansible-playbook playbooks/main.yml -vv
```

## 📊 Workflow

1. **Validation** → Checks environment, templates, tools
2. **Template Conversion** → Jinja2 templates → Markdown files
3. **HTML Conversion** → Markdown files → HTML files  
4. **Publishing** → HTML files → Confluence pages

## 🔒 Security

- `vars/vars.yml` is gitignored and contains sensitive credentials
- Use `ansible-vault` for credential encryption in production
- Base64 credentials are for API authentication with Confluence

## 🎯 Benefits of Modular Structure

- ✅ **Maintainability** - Each component is isolated and testable
- ✅ **Reusability** - Individual playbooks can be used standalone  
- ✅ **Debugging** - Easier to troubleshoot specific steps
- ✅ **Flexibility** - Skip or repeat individual steps as needed
- ✅ **Testing** - Each module can be tested independently
- ✅ **Documentation** - Clear separation of concerns
