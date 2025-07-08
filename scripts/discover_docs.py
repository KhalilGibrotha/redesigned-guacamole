#!/usr/bin/env python3
"""
Dynamic documentation structure discovery script.
Discovers main pages and their child pages from the docs/ folder structure.
"""

import os
import glob
import json
import sys

def discover_documentation_structure(docs_path="docs"):
    """
    Discover the documentation structure dynamically.
    
    Returns:
        dict: Structure with main pages and their children
    """
    structure = {}
    
    # Find all subdirectories in docs/
    if not os.path.exists(docs_path):
        return structure
        
    for item in os.listdir(docs_path):
        item_path = os.path.join(docs_path, item)
        if os.path.isdir(item_path):
            main_page_name = item
            main_page_file = os.path.join(item_path, f"{main_page_name}.j2")
            
            # Check if main page exists
            if os.path.exists(main_page_file):
                children = []
                
                # Find all .j2 files except main page and macros
                for template_file in glob.glob(os.path.join(item_path, "*.j2")):
                    basename = os.path.basename(template_file)
                    if basename not in [f"{main_page_name}.j2", "macros.j2"]:
                        # Create title from filename
                        title = basename.replace('.j2', '').replace('_', ' ').title()
                        children.append({
                            "file": basename,
                            "title": title,
                            "path": template_file
                        })
                
                # Sort children by title
                children.sort(key=lambda x: x['title'])
                
                structure[main_page_name] = {
                    "main_page": f"{main_page_name}.j2",
                    "main_page_path": main_page_file,
                    "folder": item_path,
                    "title": main_page_name.replace('_', ' ').title(),
                    "children": children
                }
    
    return structure

def get_child_pages_for_folder(folder_name, docs_path="docs"):
    """Get child pages for a specific folder."""
    structure = discover_documentation_structure(docs_path)
    return structure.get(folder_name, {}).get("children", [])

def get_all_main_pages(docs_path="docs"):
    """Get all main pages."""
    structure = discover_documentation_structure(docs_path)
    return [{"name": name, **info} for name, info in structure.items()]

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "structure":
            # Output full structure
            structure = discover_documentation_structure()
            print(json.dumps(structure, indent=2))
            
        elif command == "children" and len(sys.argv) > 2:
            # Output children for specific folder
            folder_name = sys.argv[2]
            children = get_child_pages_for_folder(folder_name)
            print(json.dumps(children, indent=2))
            
        elif command == "main-pages":
            # Output all main pages
            main_pages = get_all_main_pages()
            print(json.dumps(main_pages, indent=2))
            
        else:
            print("Usage: discover_docs.py [structure|children <folder>|main-pages]")
            sys.exit(1)
    else:
        # Default: show structure
        structure = discover_documentation_structure()
        print(json.dumps(structure, indent=2))
