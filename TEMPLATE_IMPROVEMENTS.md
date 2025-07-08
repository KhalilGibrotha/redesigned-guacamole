# Template and Macro System Improvements

## Overview
The template system has been updated with the following improvements:

### 1. Template Naming Convention
- **Changed**: `.md.j2` → `.j2`
- **Reason**: Cleaner naming convention, consistent with Jinja2 standards
- **Files affected**: All template files in `docs/` directory

### 2. AAP Variables Integration
- **Added**: `vars/aap.yml` - Comprehensive AAP configuration variables
- **Includes**: Organization details, technology stack, compliance requirements
- **Usage**: Available in all templates alongside existing `vars.yml`

### 3. Jinja2 Macro System
- **File**: `docs/macros.j2`
- **Main macro**: `oxford_comma_list(items)`
- **Purpose**: Intelligently formats lists with proper Oxford comma usage
- **Handles**: Single items, multiple items, empty/missing values

### 4. Lua Filter System
- **Directory**: `lua/`
- **Filters**:
  - `pagebreak.lua`: Handles page breaks in Word documents
  - `list_formatter.lua`: Improves list formatting in HTML/Word output
  - `codeblock.lua`: Code block formatting (inherited)

## Usage Examples

### Oxford Comma List Macro
```jinja
{%- from 'docs/macros.j2' import oxford_comma_list -%}

# Example usage:
{{ oxford_comma_list(['item1']) }}                    # → "item1"
{{ oxford_comma_list(['item1', 'item2']) }}           # → "item1, and item2"
{{ oxford_comma_list(['item1', 'item2', 'item3']) }}  # → "item1, item2, and item3"

# With AAP variables:
RHEL versions: {{ oxford_comma_list(RHEL_VERSIONS | map('string') | map('regex_replace', '^(.*)$', 'RHEL \\1')) }}
# → "RHEL 8, and RHEL 9"
```

### AAP Variables Usage
```jinja
# Organization info
{{ ORGANIZATION_NAME }}                    # → "My Big Company"
{{ SUB_ORGANIZATION_NAME }}               # → "Server Engineering and Operations"
{{ AAP_VERSION }}                         # → "2.5"

# Technology stacks
{{ oxford_comma_list(AAP_NETWORK_TECH) }}           # → "Cisco Fabric, and Infoblox (DNS)"
{{ oxford_comma_list(AAP_SECURITY_TECH) }}          # → "Tenable, and SentinelOne"
{{ oxford_comma_list(MAIN_OBJECTIVES) }}            # → "Stabilize the Environment, Drive Process Efficiencies, ..."
```

### Lua Filters in Pandoc
```bash
# Automatic usage in Makefile:
pandoc ~/tmp/file.md -f markdown -t html \
    --lua-filter=lua/pagebreak.lua \
    --lua-filter=lua/list_formatter.lua \
    -o ~/tmp/file.html
```

## Updated Workflow

### Template Development
1. Create templates with `.j2` extension
2. Use `oxford_comma_list` macro for list formatting
3. Reference AAP variables from `vars/aap.yml`
4. Include macros: `{%- from 'docs/macros.j2' import oxford_comma_list -%}`

### Template Conversion
```bash
# Convert templates to markdown (with both vars files)
make convert-templates

# Convert markdown to HTML (with Lua filters)
make convert-markdown

# Full conversion pipeline
make convert-all
```

### Validation
```bash
# Quick validation
./quick-validate.sh

# Comprehensive validation
./validate-all.sh

# Template-specific validation
make validate-templates
```

## Files Changed

### Templates Renamed
- `docs/main.md.j2` → `docs/main.j2`
- `docs/platform_governance.md.j2` → `docs/platform_governance.j2`
- `docs/platform_runbook.md.j2` → `docs/platform_runbook.j2`
- `docs/operator_runbook.md.j2` → `docs/operator_runbook.j2`
- `docs/training_enablement.md.j2` → `docs/training_enablement.j2`

### New Files Added
- `vars/aap.yml` - AAP configuration variables
- `lua/list_formatter.lua` - List formatting filter
- `lua/pagebreak.lua` - Page break filter
- `lua/codeblock.lua` - Code block filter

### Updated Files
- `playbook.yml` - Updated template paths and added aap.yml vars
- `Makefile` - Updated convert-templates and convert-markdown targets
- `docs/main.j2` - Example usage of oxford_comma_list macro and AAP variables
- `docs/aap_operations_manual.j2` - Enhanced with macro usage

## Benefits

1. **Cleaner naming**: `.j2` extension is more standard
2. **Better list formatting**: Oxford comma handling in natural language
3. **Rich variables**: Comprehensive AAP configuration data
4. **Enhanced output**: Lua filters improve document formatting
5. **Maintainable**: Modular macro system for reusable formatting
6. **Validation**: All changes validated through existing test framework

## Migration Notes

- Old `.md.j2` templates automatically renamed
- Existing validation scripts work with new naming
- AAP variables supplement existing vars.yml (both loaded)
- Lua filters optional but recommended for better output quality
