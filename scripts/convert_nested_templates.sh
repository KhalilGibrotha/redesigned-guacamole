#!/bin/bash
# Script to convert nested templates using the discovery script

echo "🔄 Converting nested templates to markdown..."

# Generate targets
python3 scripts/discover_docs.py makefile-targets > ~/tmp/template_targets.json

# Process each target
cat ~/tmp/template_targets.json | python3 -c "
import json
import sys
import subprocess

targets = json.load(sys.stdin)
for target in targets:
    source = target['source']
    dest = target['dest']
    target_type = target['type']
    
    print(f'   📄 Rendering {source} -> {dest} ({target_type})')
    
    cmd = [
        'ansible', 'localhost', '-m', 'template',
        '-a', f'src={source} dest={dest}',
        '-e', '@vars/vars.yml',
        '-e', '@vars/aap.yml',
        '--connection=local'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f'      ✅ {dest} created successfully')
        else:
            print(f'      ❌ {dest} failed: {result.stderr}')
    except Exception as e:
        print(f'      ❌ {dest} error: {e}')
"

echo "   ✅ Nested template conversion complete"
