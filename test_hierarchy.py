#!/usr/bin/env python3
"""Test script to demonstrate hierarchical page management and validation"""

import sys

sys.path.append("scripts")
from confluence_publisher import DocumentProcessor

# Test with the current vars.yaml
processor = DocumentProcessor("docs", "docs/vars.yaml")

# Test hierarchy resolution
print("=== Testing Hierarchy Resolution ===")
categories = ["operations", "administration", "governance", "guides", "testing", "automation_hub"]

for category in categories:
    print(f"\nTesting category: {category}")
    parent_id = processor.resolve_hierarchy_parent(category)
    print(f"  Result: {parent_id}")

# Test with non-existent category
print(f"\nTesting non-existent category: 'nonexistent'")
parent_id = processor.resolve_hierarchy_parent("nonexistent")
print(f"  Result: {parent_id}")

# Test root resolution
print(f"\nTesting root resolution:")
parent_id = processor.resolve_hierarchy_parent("root")
print(f"  Result: {parent_id}")
