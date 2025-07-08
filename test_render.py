#!/usr/bin/env python3
import yaml
from jinja2 import Environment, FileSystemLoader

# Load variables
with open('vars/vars.yml') as f:
    vars_data = yaml.safe_load(f)

with open('vars/aap.yml') as f:
    aap_data = yaml.safe_load(f)

# Combine variables
combined_vars = {**vars_data, **aap_data}

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader('docs/automation_hub'))

# Load and render template
template = env.get_template('automation_hub.j2')
rendered = template.render(**combined_vars)

print(f"Rendered content length: {len(rendered)}")
print("=" * 50)
print(rendered[:500])  # Print first 500 characters
print("=" * 50)

# Save to file
with open('/home/gambia/tmp/automation_hub_python.md', 'w') as f:
    f.write(rendered)

print("File saved to /home/gambia/tmp/automation_hub_python.md")
