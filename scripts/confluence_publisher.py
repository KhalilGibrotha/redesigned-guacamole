#!/usr/bin/env python3
"""
Confluence Documentation Publisher

A Python script that processes Markdown and Jinja2 template files with YAML frontmatter
and publishes them to Confluence. This follows the pattern from bug-free-fiesta.

Features:
- Processes .md and .j2 files in the docs directory
- Extracts YAML frontmatter for Confluence configuration
- Renders Jinja2 templates with variables from vars.yaml
- Uploads content to Confluence via REST API
- Handles image attachments and uploads
- Supports dry-run mode

Usage:
    python3 confluence_publisher.py [--dry-run] [--docs-dir docs] [--vars-file docs/vars.yaml]
"""

import os
import sys
import argparse
import yaml
import re
import requests
import base64
import mimetypes
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
from urllib.parse import urljoin
import markdown
from typing import Dict, Any, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Supported image formats for Confluence
SUPPORTED_IMAGE_FORMATS = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.bmp': 'image/bmp',
    '.svg': 'image/svg+xml',
    '.tiff': 'image/tiff',
    '.tif': 'image/tiff'
}


class ConfluencePublisher:
    """Main class for publishing documentation to Confluence"""
    
    def __init__(self, confluence_url: str, username: str, api_token: str, dry_run: bool = False):
        """
        Initialize the Confluence publisher
        
        Args:
            confluence_url: Base URL for Confluence instance
            username: Confluence username
            api_token: Confluence API token
            dry_run: If True, don't actually publish to Confluence
        """
        self.confluence_url = confluence_url.rstrip('/')
        self.username = username
        self.api_token = api_token
        self.dry_run = dry_run
        self.session = requests.Session()
        self.session.auth = (username, api_token)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Test connection if not in dry run mode
        if not dry_run:
            self._test_connection()
    
    def _test_connection(self) -> bool:
        """Test connection to Confluence"""
        try:
            response = self.session.get(f"{self.confluence_url}/rest/api/user/current")
            response.raise_for_status()
            user_info = response.json()
            logger.info(f"✅ Connected to Confluence as {user_info.get('displayName', self.username)}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Confluence: {e}")
            return False
    
    def create_or_update_page(self, space_key: str, title: str, content: str, 
                             parent_page_id: Optional[str] = None) -> Optional[str]:
        """
        Create or update a Confluence page
        
        Args:
            space_key: Confluence space key
            title: Page title
            content: Page content (HTML)
            parent_page_id: Optional parent page ID
            
        Returns:
            Page ID if successful, None otherwise
        """
        # Validate parent page exists before proceeding
        if not self._validate_parent_page(parent_page_id, space_key):
            return None
        
        if self.dry_run:
            logger.info(f"🧪 [DRY RUN] Would create/update page: {title} in space {space_key}")
            if parent_page_id:
                logger.info(f"🧪 [DRY RUN] Would set parent page ID: {parent_page_id}")
            logger.info(f"🧪 [DRY RUN] Content length: {len(content)} characters")
            return "dry-run-page-id"
        
        try:
            # Check if page exists
            existing_page = self._get_page_by_title(space_key, title)
            
            if existing_page:
                # Update existing page
                page_id = existing_page['id']
                version = existing_page['version']['number'] + 1
                
                update_data = {
                    "version": {"number": version},
                    "title": title,
                    "type": "page",
                    "body": {
                        "storage": {
                            "value": content,
                            "representation": "storage"
                        }
                    }
                }
                
                response = self.session.put(
                    f"{self.confluence_url}/rest/api/content/{page_id}",
                    json=update_data
                )
                response.raise_for_status()
                logger.info(f"✅ Updated page: {title} (ID: {page_id})")
                return page_id
                
            else:
                # Create new page
                create_data = {
                    "type": "page",
                    "title": title,
                    "space": {"key": space_key},
                    "body": {
                        "storage": {
                            "value": content,
                            "representation": "storage"
                        }
                    }
                }
                
                if parent_page_id:
                    create_data["ancestors"] = [{"id": parent_page_id}]
                
                response = self.session.post(
                    f"{self.confluence_url}/rest/api/content",
                    json=create_data
                )
                response.raise_for_status()
                page_data = response.json()
                page_id = page_data['id']
                logger.info(f"✅ Created page: {title} (ID: {page_id})")
                return page_id
                
        except Exception as e:
            logger.error(f"❌ Failed to create/update page {title}: {e}")
            return None
    
    def _get_page_by_title(self, space_key: str, title: str) -> Optional[Dict]:
        """Get page by title in a space"""
        try:
            response = self.session.get(
                f"{self.confluence_url}/rest/api/content",
                params={
                    "spaceKey": space_key,
                    "title": title,
                    "expand": "version"
                }
            )
            response.raise_for_status()
            results = response.json()
            
            if results['results']:
                return results['results'][0]
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get page by title {title}: {e}")
            return None
    
    def _get_page_by_id(self, page_id: str) -> Optional[Dict]:
        """Get page by ID"""
        try:
            response = self.session.get(
                f"{self.confluence_url}/rest/api/content/{page_id}",
                params={"expand": "version,space"}
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"⚠️  Page with ID {page_id} not found")
                return None
            else:
                logger.error(f"❌ Failed to get page by ID {page_id}: {e}")
                return None
        except Exception as e:
            logger.error(f"❌ Failed to get page by ID {page_id}: {e}")
            return None
    
    def _validate_parent_page(self, parent_page_id: str, space_key: str) -> bool:
        """
        Validate that the parent page exists
        
        Args:
            parent_page_id: The parent page ID to validate
            space_key: The space key where the parent should exist
            
        Returns:
            True if parent page exists, False otherwise
        """
        if not parent_page_id:
            return True  # No parent specified is valid
        
        if self.dry_run:
            logger.info(f"🧪 [DRY RUN] Would validate parent page ID: {parent_page_id}")
            return True
        
        parent_page = self._get_page_by_id(parent_page_id)
        if not parent_page:
            logger.error(f"❌ Parent page with ID {parent_page_id} does not exist!")
            logger.error(f"🚨 Cannot create child page without valid parent. Please ensure parent page exists in Confluence.")
            return False
        
        # Check if parent is in the correct space
        parent_space = parent_page.get('space', {}).get('key')
        if parent_space != space_key:
            logger.warning(f"⚠️  Parent page {parent_page_id} is in space '{parent_space}', but child will be in space '{space_key}'")
            logger.warning(f"⚠️  This may cause issues with page hierarchy")
        
        logger.info(f"✅ Parent page validated: {parent_page.get('title', 'Unknown Title')} (ID: {parent_page_id})")
        return True
    
    def upload_attachment(self, page_id: str, file_path: Path, file_name: str = None) -> Optional[Dict]:
        """
        Upload an attachment to a Confluence page
        
        Args:
            page_id: The ID of the page to attach to
            file_path: Path to the file to upload
            file_name: Optional custom filename (defaults to file_path.name)
            
        Returns:
            Attachment info dict or None if failed
        """
        if self.dry_run:
            logger.info(f"🧪 [DRY RUN] Would upload attachment: {file_path.name}")
            return {"id": "dry-run-attachment-id", "title": file_path.name}
        
        try:
            if not file_path.exists():
                logger.error(f"❌ File not found: {file_path}")
                return None
                
            # Check if file format is supported
            file_ext = file_path.suffix.lower()
            if file_ext not in SUPPORTED_IMAGE_FORMATS:
                logger.warning(f"⚠️  Unsupported image format: {file_ext}")
                return None
            
            mime_type = SUPPORTED_IMAGE_FORMATS[file_ext]
            attachment_name = file_name or file_path.name
            
            # Prepare the file for upload
            with open(file_path, 'rb') as f:
                files = {
                    'file': (attachment_name, f, mime_type)
                }
                
                # Remove Content-Type header for file uploads
                headers = {k: v for k, v in self.session.headers.items() 
                          if k.lower() != 'content-type'}
                
                response = self.session.post(
                    f"{self.confluence_url}/rest/api/content/{page_id}/child/attachment",
                    files=files,
                    headers=headers
                )
                
                if response.status_code == 200:
                    attachment_data = response.json()
                    attachment_info = attachment_data['results'][0]
                    logger.info(f"✅ Uploaded attachment: {attachment_name}")
                    return attachment_info
                else:
                    response.raise_for_status()
                    
        except Exception as e:
            logger.error(f"❌ Failed to upload attachment {file_path.name}: {e}")
            return None
    
    def process_images_in_content(self, content: str, page_id: str, base_path: Path) -> str:
        """
        Process images in content, upload them as attachments, and update references
        
        Args:
            content: HTML content with image references
            page_id: Confluence page ID to attach images to
            base_path: Base path for resolving relative image paths
            
        Returns:
            Updated content with Confluence attachment references
        """
        if self.dry_run:
            logger.info("🧪 [DRY RUN] Would process images in content")
            return content
        
        # Find all image references in the content
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
        markdown_img_pattern = r'!\[[^\]]*\]\(([^)]+)\)'
        
        def replace_image_reference(match, is_markdown=False):
            if is_markdown:
                alt_text = match.group(0)[2:match.group(0).find(']')]
                image_path = match.group(1)
            else:
                image_path = match.group(1)
                alt_text = ""
            
            # Skip if it's already a URL
            if image_path.startswith(('http://', 'https://', '//')):
                return match.group(0)
            
            # Resolve relative path
            if not Path(image_path).is_absolute():
                full_image_path = base_path / image_path
            else:
                full_image_path = Path(image_path)
            
            # Check if image exists and is supported
            if full_image_path.exists():
                file_ext = full_image_path.suffix.lower()
                if file_ext in SUPPORTED_IMAGE_FORMATS:
                    # Upload the image
                    attachment_info = self.upload_attachment(page_id, full_image_path)
                    if attachment_info:
                        # Create Confluence attachment reference
                        attachment_id = attachment_info['id']
                        attachment_name = attachment_info['title']
                        
                        if is_markdown:
                            return f'<ac:image ac:height="400"><ri:attachment ri:filename="{attachment_name}" /></ac:image>'
                        else:
                            return f'<ac:image ac:height="400"><ri:attachment ri:filename="{attachment_name}" /></ac:image>'
                else:
                    logger.warning(f"⚠️  Unsupported image format: {full_image_path}")
            else:
                logger.warning(f"⚠️  Image not found: {full_image_path}")
            
            return match.group(0)  # Return original if we can't process
        
        # Replace HTML img tags
        content = re.sub(img_pattern, replace_image_reference, content)
        
        # Replace Markdown image syntax
        content = re.sub(markdown_img_pattern, 
                        lambda m: replace_image_reference(m, is_markdown=True), 
                        content)
        
        return content


class DocumentProcessor:
    """Processes documentation files and renders templates"""
    
    def __init__(self, docs_dir: str, vars_file: str):
        """
        Initialize the document processor
        
        Args:
            docs_dir: Directory containing documentation files
            vars_file: Path to variables YAML file
        """
        self.docs_dir = Path(docs_dir)
        self.vars_file = Path(vars_file)
        self.variables = self._load_variables()
        
        # Set up Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader([str(self.docs_dir), str(self.docs_dir.parent)]),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Make variables available to all templates
        self.jinja_env.globals.update(self.variables)
    
    def _load_variables(self) -> Dict[str, Any]:
        """Load variables from the vars file"""
        try:
            if self.vars_file.exists():
                with open(self.vars_file, 'r', encoding='utf-8') as f:
                    variables = yaml.safe_load(f) or {}
                logger.info(f"✅ Loaded {len(variables)} variables from {self.vars_file}")
                return variables
            else:
                logger.warning(f"⚠️  Variables file not found: {self.vars_file}")
                return {}
        except Exception as e:
            logger.error(f"❌ Failed to load variables from {self.vars_file}: {e}")
            return {}
    
    def resolve_hierarchy_parent(self, category_key: str) -> Optional[str]:
        """
        Resolve parent page ID from hierarchy configuration
        
        Args:
            category_key: The category key from confluence_hierarchy.categories
            
        Returns:
            Parent page ID or None if not found
        """
        try:
            hierarchy = self.variables.get('confluence_hierarchy', {})
            
            if not hierarchy:
                logger.warning("⚠️  No confluence_hierarchy found in variables")
                logger.warning("💡 Add confluence_hierarchy section to your vars file for hierarchical page management")
                return None
            
            # Check if it's a direct reference to root
            if category_key == 'root':
                root_page_id = hierarchy.get('root', {}).get('pageId')
                if root_page_id:
                    logger.info(f"🔗 Resolved root category to page ID: {root_page_id}")
                else:
                    logger.error(f"❌ Root page ID not configured in hierarchy")
                return root_page_id
            
            # Look up category in hierarchy
            categories = hierarchy.get('categories', {})
            category = categories.get(category_key)
            
            if not category:
                logger.error(f"❌ Category '{category_key}' not found in hierarchy")
                logger.error(f"💡 Available categories: {list(categories.keys())}")
                return None
            
            # Resolve parent reference
            parent_ref = category.get('parent')
            if parent_ref == 'root':
                root_page_id = hierarchy.get('root', {}).get('pageId')
                if root_page_id:
                    logger.info(f"🔗 Resolved category '{category_key}' -> root page ID: {root_page_id}")
                else:
                    logger.error(f"❌ Root page ID not configured for category '{category_key}'")
                return root_page_id
            elif parent_ref in categories:
                # For nested categories, you could implement recursive resolution here
                # For now, just handle root-level categories
                logger.warning(f"⚠️  Nested category resolution not implemented for '{parent_ref}'")
                logger.warning(f"💡 Falling back to root page for category '{category_key}'")
                return hierarchy.get('root', {}).get('pageId')
            else:
                logger.error(f"❌ Unknown parent reference '{parent_ref}' for category '{category_key}'")
                logger.error(f"💡 Parent reference should be 'root' or another category name")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to resolve hierarchy parent for '{category_key}': {e}")
            return None
    
    def find_documentation_files(self) -> List[Path]:
        """Find all .md and .j2 files in the docs directory"""
        files = []
        
        # Find .md files
        md_files = list(self.docs_dir.rglob("*.md"))
        files.extend(md_files)
        
        # Find .j2 files (but not macro files)
        j2_files = [f for f in self.docs_dir.rglob("*.j2") 
                   if not f.name.startswith('macros') and 'macros' not in str(f)]
        files.extend(j2_files)
        
        logger.info(f"📁 Found {len(files)} documentation files")
        return files
    
    def parse_frontmatter(self, content: str) -> Tuple[Dict[str, Any], str]:
        """
        Parse YAML frontmatter from content
        
        Args:
            content: File content
            
        Returns:
            Tuple of (frontmatter_dict, content_without_frontmatter)
        """
        frontmatter = {}
        
        # Check for YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    content = parts[2].strip()
                except yaml.YAMLError as e:
                    logger.warning(f"⚠️  Failed to parse frontmatter: {e}")
        
        return frontmatter, content
    
    def process_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Process a single documentation file
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            Dictionary with processed file information
        """
        try:
            logger.info(f"📝 Processing {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            # Parse frontmatter
            frontmatter, content = self.parse_frontmatter(raw_content)
            
            # Check if this file has Confluence configuration
            confluence_config = frontmatter.get('confluence', {})
            if not confluence_config:
                logger.info(f"⏭️  Skipping {file_path} - no Confluence configuration")
                return None
            
            # Resolve hierarchy-based parent page ID
            category = confluence_config.get('category')
            if category:
                resolved_parent_id = self.resolve_hierarchy_parent(category)
                if resolved_parent_id:
                    confluence_config['parentPageId'] = resolved_parent_id
                    logger.info(f"🔗 Resolved category '{category}' to parent page ID: {resolved_parent_id}")
                else:
                    logger.warning(f"⚠️  Could not resolve parent for category '{category}'")
            
            # Load additional variables if specified
            vars_file = frontmatter.get('varsFile')
            template_vars = self.variables.copy()
            
            if vars_file:
                vars_path = self.docs_dir.parent / vars_file
                if vars_path.exists():
                    with open(vars_path, 'r', encoding='utf-8') as f:
                        additional_vars = yaml.safe_load(f) or {}
                    template_vars.update(additional_vars)
            
            # Add frontmatter variables
            template_vars.update({k: v for k, v in frontmatter.items() if k != 'confluence'})
            
            # Render content if it's a Jinja2 template
            if file_path.suffix == '.j2':
                template = self.jinja_env.from_string(content)
                rendered_content = template.render(**template_vars)
            else:
                rendered_content = content
            
            # Convert Markdown to HTML if needed
            if file_path.suffix in ['.md', '.j2']:
                html_content = markdown.markdown(
                    rendered_content,
                    extensions=['tables', 'fenced_code', 'toc']
                )
            else:
                html_content = rendered_content
            
            return {
                'file_path': file_path,
                'confluence_config': confluence_config,
                'frontmatter': frontmatter,
                'rendered_content': rendered_content,
                'html_content': html_content,
                'template_vars': template_vars
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to process {file_path}: {e}")
            return None


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Publish documentation to Confluence')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Perform a dry run without actually publishing')
    parser.add_argument('--docs-dir', default='docs',
                       help='Directory containing documentation files (default: docs)')
    parser.add_argument('--vars-file', default='docs/vars.yaml',
                       help='Path to variables file (default: docs/vars.yaml)')
    parser.add_argument('--confluence-url', 
                       default=os.environ.get('CONFLUENCE_URL', ''),
                       help='Confluence URL (can also use CONFLUENCE_URL env var)')
    parser.add_argument('--confluence-user',
                       default=os.environ.get('CONFLUENCE_USER', ''),
                       help='Confluence username (can also use CONFLUENCE_USER env var)')
    parser.add_argument('--confluence-token',
                       default=os.environ.get('CONFLUENCE_API_TOKEN', ''),
                       help='Confluence API token (can also use CONFLUENCE_API_TOKEN env var)')
    
    args = parser.parse_args()
    
    # Validate required parameters for non-dry-run mode
    if not args.dry_run:
        if not all([args.confluence_url, args.confluence_user, args.confluence_token]):
            logger.error("❌ Confluence URL, user, and API token are required for live publishing")
            logger.error("   Use --dry-run for testing without Confluence access")
            sys.exit(1)
    
    # Initialize components
    logger.info("🚀 Starting Confluence Documentation Publisher")
    
    if args.dry_run:
        logger.info("🧪 Running in DRY RUN mode - no actual publishing will occur")
    
    processor = DocumentProcessor(args.docs_dir, args.vars_file)
    publisher = ConfluencePublisher(
        args.confluence_url or 'https://example.atlassian.net',
        args.confluence_user or 'dry-run-user',
        args.confluence_token or 'dry-run-token',
        args.dry_run
    )
    
    # Find and process files
    files = processor.find_documentation_files()
    processed_files = []
    
    for file_path in files:
        result = processor.process_file(file_path)
        if result:
            processed_files.append(result)
    
    if not processed_files:
        logger.warning("⚠️  No files with Confluence configuration found")
        return
    
    # Publish files
    logger.info(f"📤 Publishing {len(processed_files)} files to Confluence")
    
    published_count = 0
    for file_info in processed_files:
        confluence_config = file_info['confluence_config']
        
        space_key = confluence_config.get('space', 'DOCS')
        title = confluence_config.get('title', 'Untitled Document')
        parent_page_id = confluence_config.get('parentPageId')
        
        # First create/update the page
        page_id = publisher.create_or_update_page(
            space_key=space_key,
            title=title,
            content=file_info['html_content'],
            parent_page_id=parent_page_id
        )
        
        if page_id:
            # Process images and update content if necessary
            original_content = file_info['html_content']
            base_path = file_info['file_path'].parent
            
            # Process images in the content
            updated_content = publisher.process_images_in_content(
                original_content, page_id, base_path
            )
            
            # If content was updated with image attachments, update the page again
            if updated_content != original_content:
                logger.info(f"🖼️  Updating page with image attachments: {title}")
                final_page_id = publisher.create_or_update_page(
                    space_key=space_key,
                    title=title,
                    content=updated_content,
                    parent_page_id=parent_page_id
                )
                if final_page_id:
                    published_count += 1
            else:
                published_count += 1
        else:
            logger.error(f"❌ Failed to publish: {title}")
    
    # Summary
    if args.dry_run:
        logger.info(f"🧪 DRY RUN COMPLETE: Would have published {published_count}/{len(processed_files)} files")
    else:
        logger.info(f"✅ PUBLISHING COMPLETE: Successfully published {published_count}/{len(processed_files)} files")
    
    if published_count < len(processed_files):
        logger.warning(f"⚠️  {len(processed_files) - published_count} files failed to publish")
        sys.exit(1)


if __name__ == '__main__':
    main()
