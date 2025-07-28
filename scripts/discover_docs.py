#!/usr/bin/env python3
"""
Dynamic documentation structure discovery script with nested folder support.
Discovers main pages, their child pages, and nested sub-sections from the docs/ folder structure.
"""

import json
import os
import sys


def discover_documentation_structure(docs_path="docs", max_depth=3):
    """
    Discover the documentation structure dynamically with nested folder support.

    Args:
        docs_path (str): Path to the docs directory
        max_depth (int): Maximum nesting depth to scan

    Returns:
        dict: Structure with main pages, children, and nested sub-sections
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
                section_info = {
                    "main_page": f"{main_page_name}.j2",
                    "main_page_path": main_page_file,
                    "folder": item_path,
                    "title": main_page_name.replace("_", " ").title(),
                    "children": [],
                    "nested_sections": {},
                }

                # Find direct child templates and nested folders
                for child_item in os.listdir(item_path):
                    child_path = os.path.join(item_path, child_item)

                    if os.path.isfile(child_path) and child_item.endswith(".j2"):
                        # Direct child template
                        if child_item not in [f"{main_page_name}.j2", "macros.j2"]:
                            title = child_item.replace(".j2", "").replace("_", " ").title()
                            section_info["children"].append(
                                {"file": child_item, "title": title, "path": child_path, "type": "template"}
                            )

                    elif os.path.isdir(child_path):
                        # Nested folder - check if it has its own main template
                        nested_name = child_item
                        nested_main_file = os.path.join(child_path, f"{nested_name}.j2")

                        nested_info = {
                            "folder": child_path,
                            "title": nested_name.replace("_", " ").title(),
                            "children": [],
                            "type": "nested_section",
                        }

                        if os.path.exists(nested_main_file):
                            # Has main template - this is a sub-section
                            nested_info["main_page"] = f"{nested_name}.j2"
                            nested_info["main_page_path"] = nested_main_file

                            # Add to main children as a section
                            section_info["children"].append(
                                {
                                    "file": f"{nested_name}.j2",
                                    "title": nested_info["title"],
                                    "path": nested_main_file,
                                    "type": "nested_section",
                                    "folder": child_path,
                                }
                            )

                        # Find child templates in nested folder
                        for nested_child in os.listdir(child_path):
                            nested_child_path = os.path.join(child_path, nested_child)
                            if (
                                os.path.isfile(nested_child_path)
                                and nested_child.endswith(".j2")
                                and nested_child not in [f"{nested_name}.j2", "macros.j2"]
                            ):

                                title = nested_child.replace(".j2", "").replace("_", " ").title()
                                nested_info["children"].append(
                                    {
                                        "file": nested_child,
                                        "title": title,
                                        "path": nested_child_path,
                                        "type": "template",
                                        "parent_section": nested_name,
                                    }
                                )

                        section_info["nested_sections"][nested_name] = nested_info

                # Sort children by title
                section_info["children"].sort(key=lambda x: x["title"])
                for nested_section in section_info["nested_sections"].values():
                    nested_section["children"].sort(key=lambda x: x["title"])

                structure[main_page_name] = section_info

    return structure


def get_child_pages_for_folder(folder_name, docs_path="docs"):
    """Get child pages for a specific folder, including nested sections."""
    structure = discover_documentation_structure(docs_path)
    return structure.get(folder_name, {})


def get_nested_section(main_folder, nested_folder, docs_path="docs"):
    """Get nested section information."""
    structure = discover_documentation_structure(docs_path)
    main_section = structure.get(main_folder, {})
    return main_section.get("nested_sections", {}).get(nested_folder, {})


def get_all_main_pages(docs_path="docs"):
    """Get all main pages."""
    structure = discover_documentation_structure(docs_path)
    return [{"name": name, **info} for name, info in structure.items()]


def generate_makefile_targets(structure):
    """Generate Makefile targets for all templates in the structure."""
    targets = []

    for main_name, main_info in structure.items():
        # Main page
        targets.append({"source": main_info["main_page_path"], "dest": f"~/tmp/{main_name}.md", "type": "main"})

        # Direct children
        for child in main_info["children"]:
            if child["type"] == "template":
                child_name = child["file"].replace(".j2", "")
                targets.append(
                    {"source": child["path"], "dest": f"~/tmp/{child_name}.md", "type": "child", "parent": main_name}
                )
            elif child["type"] == "nested_section":
                # Nested section main page
                nested_name = child["file"].replace(".j2", "")
                targets.append(
                    {
                        "source": child["path"],
                        "dest": f"~/tmp/{nested_name}.md",
                        "type": "nested_main",
                        "parent": main_name,
                    }
                )

        # Nested section children
        for nested_name, nested_info in main_info["nested_sections"].items():
            for nested_child in nested_info["children"]:
                child_name = nested_child["file"].replace(".j2", "")
                targets.append(
                    {
                        "source": nested_child["path"],
                        "dest": f"~/tmp/{child_name}.md",
                        "type": "nested_child",
                        "parent": nested_name,
                        "grandparent": main_name,
                    }
                )

    return targets


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

        elif command == "nested" and len(sys.argv) > 3:
            # Output nested section info
            main_folder = sys.argv[2]
            nested_folder = sys.argv[3]
            nested_info = get_nested_section(main_folder, nested_folder)
            print(json.dumps(nested_info, indent=2))

        elif command == "main-pages":
            # Output all main pages
            main_pages = get_all_main_pages()
            print(json.dumps(main_pages, indent=2))

        elif command == "makefile-targets":
            # Output makefile targets for all templates
            structure = discover_documentation_structure()
            targets = generate_makefile_targets(structure)
            print(json.dumps(targets, indent=2))

        else:
            print(
                "Usage: discover_docs.py [structure|children <folder>|nested <main> <nested>|"
                "main-pages|makefile-targets]"
            )
            sys.exit(1)
    else:
        # Default: show structure
        structure = discover_documentation_structure()
        print(json.dumps(structure, indent=2))
