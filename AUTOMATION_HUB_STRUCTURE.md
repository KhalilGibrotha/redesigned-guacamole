# Documentation Structure Updates - Automation Hub

## Overview
The documentation system has been restructured to support a folder-based, dynamic approach with "Automation Hub" as the main page.

## Key Changes Made

### 1. Folder Structure
- **Old**: All templates in `docs/` root
- **New**: Main page sections in their own folders
  - `docs/automation_hub/` - Contains the Automation Hub section templates

### 2. Template Organization
```
docs/
├── automation_hub/
│   ├── automation_hub.j2          # Main page (renamed from main.j2)
│   ├── macros.j2                  # Shared macros (moved from docs/macros.j2)
│   ├── platform_governance.j2     # Child page
│   ├── platform_runbook.j2        # Child page
│   ├── operator_runbook.j2         # Child page
│   └── training_enablement.j2     # Child page
└── [legacy templates remain for other documents]
```

### 3. Main Page Changes
- **Title**: Changed from "{{ project_name }} Documentation" to "Automation Hub"
- **Template Path**: `docs/automation_hub/automation_hub.j2`
- **Macros Import**: Now imports from `docs/automation_hub/macros.j2`
- **Generated Markdown**: `~/tmp/automation_hub.md` (was `main.md`)

### 4. Child Page Management
- **Removed**: Hardcoded `child_pages` from `vars/vars.yml`
- **Added**: Dynamic discovery in playbook with `automation_hub_children` fact
- **Structure**: Child pages are automatically listed in the main page

### 5. Dynamic Template Processing
- **New Makefile Target**: `convert-templates-dynamic`
  - Automatically discovers and renders all templates in `automation_hub/` folder
  - Skips `automation_hub.j2` (main page) and `macros.j2` during child processing
- **Updated Targets**: `convert-markdown`, `verify-html`, `validate-templates`

### 6. Playbook Updates
- **Pre-flight checks**: Now verify automation_hub templates specifically
- **Template processing**: Uses `make convert-templates-dynamic`
- **Confluence integration**: Updates title and file references to use automation_hub

## Benefits

### Scalability
- **Easy expansion**: Add new main page sections by creating new folders
- **Isolated sections**: Each main page has its own folder with all related templates
- **Dynamic discovery**: No need to update hardcoded lists when adding child pages

### Maintainability  
- **Organized structure**: Related templates grouped together
- **Clear hierarchy**: Main page and children in same folder
- **Consistent naming**: Folder name matches main page template name

### Flexibility
- **Multiple main pages**: Can easily support additional documentation sections
- **Shared resources**: Macros and common elements per section
- **Template reuse**: Each section can have its own macros and shared components

## Usage

### Adding a New Child Page
1. Create new `.j2` template in `docs/automation_hub/`
2. Template will be automatically discovered and processed
3. Add entry to the subpages list in `automation_hub.j2` if desired
4. Run `make convert-templates-dynamic` to test

### Adding a New Main Page Section
1. Create new folder in `docs/` (e.g., `docs/controller/`)
2. Create main template `docs/controller/controller.j2`
3. Add child templates as needed
4. Update playbook to include new section
5. Update Makefile targets to support new section

### Development Workflow
```bash
# Test template structure
make validate-templates

# Convert templates
make convert-templates-dynamic

# Convert to HTML
make convert-markdown

# Verify output
make verify-html

# Full pipeline
ansible-playbook playbook.yml
```

## Discovery Script
A Python discovery script is available at `scripts/discover_docs.py`:

```bash
# Show full structure
python3 scripts/discover_docs.py structure

# Show children for specific folder
python3 scripts/discover_docs.py children automation_hub

# Show all main pages
python3 scripts/discover_docs.py main-pages
```

## File Changes Summary

### Modified Files
- `vars/vars.yml` - Removed hardcoded child_pages
- `playbook.yml` - Updated for dynamic structure and Automation Hub
- `Makefile` - Added convert-templates-dynamic target
- `docs/automation_hub/automation_hub.j2` - Renamed and updated main template

### Moved Files
- `docs/main.j2` → `docs/automation_hub/automation_hub.j2`
- `docs/macros.j2` → `docs/automation_hub/macros.j2` (copied)
- All child templates → `docs/automation_hub/`

### New Files
- `scripts/discover_docs.py` - Dynamic structure discovery
- `AUTOMATION_HUB_STRUCTURE.md` - This documentation

## Testing Status
✅ Template validation passes
✅ Dynamic template conversion works  
✅ Markdown to HTML conversion works
✅ Playbook runs successfully through conversion
✅ Confluence integration updated
✅ HTML verification passes

All critical functionality is working with the new folder-based structure.
