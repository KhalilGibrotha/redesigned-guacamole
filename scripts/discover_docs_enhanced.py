#!/usr/bin/env python3
"""
Enhanced Documentation Discovery Script
Discovers templates from both static docs/ and auto_document/ (cloned repos)
"""

import os
import json
import yaml
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentationDiscovery:
    def __init__(self, base_dir: str = "docs"):
        self.base_dir = Path(base_dir)
        self.auto_document_dir = self.base_dir / "auto_document"
        self.repos_config = self._load_repos_config()
        
    def _load_repos_config(self) -> Dict:
        """Load repository configuration from vars/repos.yml"""
        config_path = Path("vars/repos.yml")
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {"documentation_repos": []}
    
    def discover_all_sections(self) -> Dict[str, Any]:
        """Discover all documentation sections from static and auto_document folders"""
        sections = {}
        
        # Discover static sections
        static_sections = self._discover_static_sections()
        sections.update(static_sections)
        
        # Discover auto_document sections (from cloned repos)
        auto_sections = self._discover_auto_document_sections()
        sections.update(auto_sections)
        
        return sections
    
    def _discover_static_sections(self) -> Dict[str, Any]:
        """Discover sections from static docs folder"""
        sections = {}
        
        if not self.base_dir.exists():
            return sections
        
        # Discover sections from folder structure
        for item in self.base_dir.iterdir():
            if item.is_dir():
                section_info = self._analyze_section(item)
                if section_info:
                    sections[item.name] = section_info
            
        return sections
    
    def _discover_auto_document_sections(self) -> Dict[str, Any]:
        """Discover sections from auto_document folder (cloned repos)"""
        sections = {}
        
        if not self.auto_document_dir.exists():
            return sections
            
        for repo_dir in self.auto_document_dir.iterdir():
            if repo_dir.is_dir():
                # Find the doc_path within the cloned repo
                repo_config = self._get_repo_config(repo_dir.name)
                if repo_config:
                    doc_path = repo_dir / repo_config.get('doc_path', '')
                    if doc_path.exists():
                        section_info = self._analyze_section(doc_path, is_auto=True, repo_name=repo_dir.name)
                        if section_info:
                            sections[repo_dir.name] = section_info
                            
        return sections
    
    def _get_repo_config(self, repo_name: str) -> Dict:
        """Get configuration for a specific repository"""
        for repo in self.repos_config.get('documentation_repos', []):
            if repo['name'] == repo_name:
                return repo
        return {}
    
    def _analyze_section(self, section_path: Path, is_auto: bool = False, repo_name: str = None) -> Dict[str, Any]:
        """Analyze a section directory and return its structure"""
        main_template = None
        children = []
        nested_sections = {}
        
        # Find main template (same name as folder or index)
        possible_main_names = [f"{section_path.name}.j2", "index.j2", "main.j2"]
        for name in possible_main_names:
            if (section_path / name).exists():
                main_template = name
                break
        
        # Discover children and nested sections
        for item in section_path.iterdir():
            if item.is_file() and item.suffix == '.j2' and item.name != main_template and item.name != 'macros.j2':
                children.append({
                    "name": item.stem,
                    "file": item.name,
                    "type": "template",
                    "path": str(item.relative_to(self.base_dir))
                })
            elif item.is_file() and item.suffix == '.md' and item.name != 'README.md':
                children.append({
                    "name": item.stem,
                    "file": item.name,
                    "type": "markdown",
                    "path": str(item.relative_to(self.base_dir))
                })
            elif item.is_dir():
                nested_info = self._analyze_section(item, is_auto, repo_name)
                if nested_info:
                    nested_sections[item.name] = nested_info
        
        if main_template or children or nested_sections:
            section_info = {
                "type": "auto_document" if is_auto else "static",
                "path": str(section_path.relative_to(self.base_dir)),
                "main_template": main_template,
                "children": children,
                "nested_sections": nested_sections
            }
            
            if is_auto and repo_name:
                section_info["repo_name"] = repo_name
                section_info["repo_config"] = self._get_repo_config(repo_name)
                
            return section_info
        
        return None

def main():
    """Main function to run discovery and output results"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Discover documentation structure')
    parser.add_argument('--format', choices=['json', 'yaml'], default='json', help='Output format')
    parser.add_argument('--section', help='Discover specific section only')
    args = parser.parse_args()
    
    discovery = DocumentationDiscovery()
    
    if args.section:
        # Discover specific section
        section_path = Path(f"docs/{args.section}")
        if section_path.exists():
            result = {args.section: discovery._analyze_section(section_path)}
        else:
            result = {}
    else:
        # Discover all sections
        result = discovery.discover_all_sections()
    
    # Output results
    if args.format == 'yaml':
        print(yaml.dump(result, default_flow_style=False))
    else:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
