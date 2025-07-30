#!/usr/bin/env python3
"""
Enhanced Confluence Management Script
Provides robust page management, validation, and content verification
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path

import requests
import yaml

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ConfluenceManager:
    def __init__(self, config_file="vars/vars.yml"):
        self.config = self._load_config(config_file)
        self.base_url = self.config["confluence_url"]
        self.space_key = self.config["confluence_space"]
        self.auth_header = f"Basic {self.config['confluence_auth']}"
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": self.auth_header, "Content-Type": "application/json"}
        )
        self.page_id_cache = self.load_or_create_page_id_cache()

    def _load_config(self, config_file):
        """Load configuration from YAML file"""
        with open(config_file, "r") as f:
            return yaml.safe_load(f)

    def find_page_by_title(self, title, parent_id=None):
        """Find page by title, optionally under a specific parent"""
        url = f"{self.base_url}/rest/api/content"
        params = {
            "spaceKey": self.space_key,
            "title": title,
            "expand": "version,body.storage,ancestors",
        }

        if parent_id:
            params["parentId"] = parent_id

        response = self.session.get(url, params=params)
        response.raise_for_status()

        results = response.json()["results"]
        return results[0] if results else None

    def find_page_by_title_flexible(self, title, parent_id=None, space_key=None):
        """Find page by title with flexible search - tries parent-specific first, then space-wide"""
        if not space_key:
            space_key = self.space_key

        # First, try with parent constraint if provided (fastest)
        if parent_id:
            url = f"{self.base_url}/rest/api/content"
            params = {
                "spaceKey": space_key,
                "title": title,
                "expand": "version,body.storage,ancestors",
            }
            params["parentId"] = parent_id

            response = self.session.get(url, params=params)
            if response.status_code == 200:
                results = response.json()["results"]
                if results:
                    logger.info(f"✅ Found page '{title}' under parent {parent_id}")
                    return results[0]

        # Fallback: Search space-wide (slower but more reliable)
        logger.info(f"🔍 Parent search failed, searching space-wide for '{title}'...")
        url = f"{self.base_url}/rest/api/content"
        params = {
            "spaceKey": space_key,
            "title": title,
            "expand": "version,body.storage,ancestors",
        }

        response = self.session.get(url, params=params)
        response.raise_for_status()

        results = response.json()["results"]
        if results:
            logger.info(f"✅ Found page '{title}' in space {space_key}")
            return results[0]
        else:
            logger.info(f"❌ Page '{title}' not found in space {space_key}")
            return None

    def get_page_content_hash(self, page_id):
        """Get a hash of the page content for change detection"""
        url = f"{self.base_url}/rest/api/content/{page_id}"
        params = {"expand": "body.storage"}

        response = self.session.get(url, params=params)
        response.raise_for_status()

        content = response.json()["body"]["storage"]["value"]
        return hashlib.md5(content.encode()).hexdigest()

    def create_or_update_page(
        self, title, content, parent_id=None, labels=None, page_id_cache=None
    ):
        """Create a new page or update existing one with change detection and caching"""
        # Initialize cache if not provided
        if page_id_cache is None:
            page_id_cache = {}

        # Check cache first for page ID
        cache_key = f"{self.space_key}:{title}"
        cached_page_id = page_id_cache.get(cache_key)

        existing_page = None

        if cached_page_id:
            # Try to get page by cached ID first (fastest)
            logger.info(f"🔍 Checking cached page ID {cached_page_id} for '{title}'")
            try:
                url = f"{self.base_url}/rest/api/content/{cached_page_id}"
                params = {"expand": "version,body.storage,ancestors"}
                response = self.session.get(url, params=params)

                if response.status_code == 200:
                    existing_page = response.json()
                    logger.info(f"✅ Found page using cached ID: {cached_page_id}")
                else:
                    logger.warning(
                        f"⚠️ Cached page ID {cached_page_id} no longer valid, removing from cache"
                    )
                    del page_id_cache[cache_key]
            except Exception as e:
                logger.warning(f"⚠️ Failed to fetch cached page {cached_page_id}: {e}")
                del page_id_cache[cache_key]

        # If cache failed, use flexible search
        if not existing_page:
            existing_page = self.find_page_by_title_flexible(title, parent_id)

            # Update cache if page found
            if existing_page:
                page_id_cache[cache_key] = existing_page["id"]
                logger.info(f"💾 Cached page ID {existing_page['id']} for '{title}'")

        # Calculate content hash for change detection
        content_hash = hashlib.md5(content.encode()).hexdigest()

        if existing_page:
            result = self._update_page(existing_page, content, content_hash, labels)
        else:
            result = self._create_page(title, content, parent_id, content_hash, labels)

            # Cache new page ID
            if "page_id" in result:
                page_id_cache[cache_key] = result["page_id"]
                logger.info(f"💾 Cached new page ID {result['page_id']} for '{title}'")

        return result

    def _create_page(self, title, content, parent_id, content_hash, labels):
        """Create a new page"""
        url = f"{self.base_url}/rest/api/content"

        page_data = {
            "type": "page",
            "title": title,
            "space": {"key": self.space_key},
            "body": {"storage": {"value": content, "representation": "storage"}},
            "metadata": {
                "properties": {
                    "content-hash": {"value": content_hash},
                    "last-updated-by": {"value": "documentation-automation"},
                    "automation-timestamp": {"value": datetime.now().isoformat()},
                }
            },
        }

        if parent_id:
            page_data["ancestors"] = [{"id": parent_id}]

        if labels:
            page_data["metadata"]["labels"] = [{"name": label} for label in labels]

        response = self.session.post(url, json=page_data)
        response.raise_for_status()

        result = response.json()
        logger.info(f"✅ Created page: {title} (ID: {result['id']})")

        return {
            "action": "created",
            "page_id": result["id"],
            "title": title,
            "version": result["version"]["number"],
            "url": f"{self.base_url}/wiki{result['_links']['webui']}",
            "storage_view_url": (
                f"{self.base_url}/wiki/plugins/viewstorage/"
                f"viewpagestorage.action?pageId={result['id']}"
            ),
        }

    def _update_page(self, existing_page, content, content_hash, labels):
        """Update an existing page with change detection"""
        page_id = existing_page["id"]
        current_version = existing_page["version"]["number"]

        # Get current content hash for comparison
        try:
            current_hash = self.get_page_content_hash(page_id)
        except Exception:
            current_hash = None

        # Check if content actually changed
        if current_hash == content_hash:
            logger.info(
                f"⏩ No changes detected for: {existing_page['title']} (ID: {page_id})"
            )
            return {
                "action": "skipped",
                "page_id": page_id,
                "title": existing_page["title"],
                "version": current_version,
                "reason": "no-content-changes",
                "url": f"{self.base_url}/wiki{existing_page['_links']['webui']}",
                "storage_view_url": (
                    f"{self.base_url}/wiki/plugins/viewstorage/"
                    f"viewpagestorage.action?pageId={page_id}"
                ),
            }

        # Update the page
        url = f"{self.base_url}/rest/api/content/{page_id}"

        page_data = {
            "type": "page",
            "title": existing_page["title"],
            "space": {"key": self.space_key},
            "body": {"storage": {"value": content, "representation": "storage"}},
            "version": {"number": current_version + 1},
            "metadata": {
                "properties": {
                    "content-hash": {"value": content_hash},
                    "last-updated-by": {"value": "documentation-automation"},
                    "automation-timestamp": {"value": datetime.now().isoformat()},
                    "previous-hash": {"value": current_hash or "unknown"},
                }
            },
        }

        if labels:
            page_data["metadata"]["labels"] = [{"name": label} for label in labels]

        response = self.session.put(url, json=page_data)
        response.raise_for_status()

        result = response.json()
        logger.info(
            f"🔄 Updated page: {existing_page['title']} (ID: {page_id}) "
            f"v{current_version} → v{result['version']['number']}"
        )

        return {
            "action": "updated",
            "page_id": page_id,
            "title": existing_page["title"],
            "version": result["version"]["number"],
            "previous_version": current_version,
            "content_changed": True,
            "previous_hash": current_hash,
            "new_hash": content_hash,
            "url": f"{self.base_url}/wiki{result['_links']['webui']}",
            "storage_view_url": (
                f"{self.base_url}/wiki/plugins/viewstorage/"
                f"viewpagestorage.action?pageId={page_id}"
            ),
        }

    def validate_page_content(self, page_id, expected_hash=None):
        """Validate that a page was properly updated"""
        url = f"{self.base_url}/rest/api/content/{page_id}"
        params = {"expand": "body.storage,version,metadata.properties"}

        response = self.session.get(url, params=params)
        response.raise_for_status()

        page_data = response.json()
        current_content = page_data["body"]["storage"]["value"]
        current_hash = hashlib.md5(current_content.encode()).hexdigest()

        validation_result = {
            "page_id": page_id,
            "title": page_data["title"],
            "version": page_data["version"]["number"],
            "content_hash": current_hash,
            "content_length": len(current_content),
            "last_modified": page_data["version"]["when"],
            "storage_view_url": (
                f"{self.base_url}/wiki/plugins/viewstorage/"
                f"viewpagestorage.action?pageId={page_id}"
            ),
            "view_url": f"{self.base_url}/wiki{page_data['_links']['webui']}",
        }

        # Check metadata properties if they exist
        properties = page_data.get("metadata", {}).get("properties", {})
        if "automation-timestamp" in properties:
            validation_result["automation_timestamp"] = properties[
                "automation-timestamp"
            ]["value"]
        if "content-hash" in properties:
            validation_result["stored_hash"] = properties["content-hash"]["value"]
            validation_result["hash_matches"] = (
                current_hash == properties["content-hash"]["value"]
            )

        if expected_hash:
            validation_result["expected_hash"] = expected_hash
            validation_result["content_matches_expected"] = (
                current_hash == expected_hash
            )

        return validation_result

    def publish_documentation_hierarchy(self, docs_structure):
        """Publish a complete documentation hierarchy with validation and exclusions"""
        results = []

        # Load page ID cache for efficient updates
        page_id_cache = self.load_or_create_page_id_cache()

        # Load configuration options
        publishing_config = self.config.get("confluence_publishing", {})
        excluded_templates = self.config.get("excluded_templates", [])
        skip_main_page = publishing_config.get("skip_main_page", False)
        use_existing_main_page = publishing_config.get("use_existing_main_page", True)

        # Handle main page based on configuration
        if skip_main_page:
            logger.info("⏩ Skipping main page creation (skip_main_page=true)")
            if use_existing_main_page:
                # Find existing main page to use as parent
                logger.info("🔍 Looking for existing main page...")
                existing_main = self.find_page_by_title_flexible("Automation Hub")
                if existing_main:
                    main_page_id = existing_main["id"]
                    logger.info(f"✅ Found existing main page (ID: {main_page_id})")

                    # Cache the main page ID
                    cache_key = f"{self.space_key}:Automation Hub"
                    page_id_cache[cache_key] = main_page_id
                    results.append(
                        {
                            "action": "skipped",
                            "title": "Automation Hub",
                            "reason": "excluded-by-config",
                            "page_id": main_page_id,
                            "version": existing_main["version"]["number"],
                            "url": f"{self.base_url}/wiki{existing_main['_links']['webui']}",
                            "storage_view_url": (
                                f"{self.base_url}/wiki/plugins/viewstorage/"
                                f"viewpagestorage.action?pageId={main_page_id}"
                            ),
                        }
                    )
                else:
                    main_page_id = None
                    logger.warning(
                        "⚠️ No existing main page found - child pages will be orphaned"
                    )
                    results.append(
                        {
                            "action": "error",
                            "title": "Automation Hub",
                            "error": "No existing main page found and creation is disabled",
                        }
                    )
            else:
                main_page_id = None
                logger.info("📝 Child pages will be created without parent")
        else:
            # Process main page normally
            main_page_result = self._publish_single_page(
                title="Automation Hub",
                content_file="/home/gambia/tmp/automation_hub.md",
                labels=["automation", "documentation", "main-hub"],
                page_id_cache=page_id_cache,
            )
            results.append(main_page_result)

            if "page_id" not in main_page_result:
                logger.error("❌ Failed to create/update main page - stopping")
                return results

            main_page_id = main_page_result["page_id"]

        # Process child pages (excluding any in the exclusion list)
        for child in docs_structure.get("automation_hub", {}).get("children", []):
            if child["name"] in excluded_templates:
                logger.info(f"⏩ Skipping excluded template: {child['name']}")
                results.append(
                    {
                        "action": "skipped",
                        "title": child["name"].replace("_", " ").title(),
                        "reason": "excluded-by-template-list",
                    }
                )
                continue

            child_title = child["name"].replace("_", " ").title()
            child_result = self._publish_single_page(
                title=child_title,
                content_file=f"/home/gambia/tmp/{child['name']}.md",
                parent_id=main_page_id,  # Will be None if main page skipped
                labels=["automation", "documentation", "child-page"],
                page_id_cache=page_id_cache,
            )
            results.append(child_result)

        # Save updated cache
        self.save_page_id_cache(page_id_cache)

        return results

    def _publish_single_page(
        self, title, content_file, parent_id=None, labels=None, page_id_cache=None
    ):
        """Publish a single page from a markdown file with caching support"""
        content_path = Path(content_file)

        if not content_path.exists():
            logger.error(f"❌ Content file not found: {content_file}")
            return {
                "action": "error",
                "title": title,
                "error": f"Content file not found: {content_file}",
            }

        content = content_path.read_text()
        result = self.create_or_update_page(
            title, content, parent_id, labels, page_id_cache
        )

        # Validate the published content
        if "page_id" in result:
            validation = self.validate_page_content(result["page_id"])
            result["validation"] = validation

        return result

    def load_or_create_page_id_cache(self):
        """Load existing page ID cache or create new one"""
        cache_file = Path("page_id_cache.json")
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    cache = json.load(f)
                logger.info(f"📋 Loaded page ID cache with {len(cache)} entries")
                return cache
            except Exception as e:
                logger.warning(f"⚠️ Failed to load page ID cache: {e}")

        logger.info("📝 Creating new page ID cache")
        return {}

    def save_page_id_cache(self, cache):
        """Save page ID cache to disk"""
        try:
            with open("page_id_cache.json", "w") as f:
                json.dump(cache, f, indent=2)
            logger.info(f"💾 Saved page ID cache with {len(cache)} entries")
        except Exception as e:
            logger.error(f"❌ Failed to save page ID cache: {e}")


def main():
    """Main function for command-line usage"""
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced Confluence page management")
    parser.add_argument(
        "--action",
        choices=["publish", "validate", "find"],
        default="publish",
        help="Action to perform",
    )
    parser.add_argument("--title", help="Page title to find or validate")
    parser.add_argument("--page-id", help="Page ID to validate")
    parser.add_argument("--docs-structure", help="JSON file with docs structure")

    args = parser.parse_args()

    manager = ConfluenceManager()

    if args.action == "find" and args.title:
        page = manager.find_page_by_title(args.title)
        if page:
            print(
                json.dumps(
                    {
                        "found": True,
                        "page_id": page["id"],
                        "title": page["title"],
                        "version": page["version"]["number"],
                        "url": f"{manager.base_url}/wiki{page['_links']['webui']}",
                        "storage_view_url": (
                            f"{manager.base_url}/wiki/plugins/viewstorage/"
                            f"viewpagestorage.action?pageId={page['id']}"
                        ),
                    },
                    indent=2,
                )
            )
        else:
            print(json.dumps({"found": False}, indent=2))

    elif args.action == "validate" and args.page_id:
        validation = manager.validate_page_content(args.page_id)
        print(json.dumps(validation, indent=2))

    elif args.action == "publish":
        if args.docs_structure and Path(args.docs_structure).exists():
            with open(args.docs_structure, "r") as f:
                docs_structure = json.load(f)
        else:
            # Default discovery
            import subprocess

            result = subprocess.run(
                ["python3", "scripts/discover_docs_enhanced.py"],
                capture_output=True,
                text=True,
            )
            docs_structure = json.loads(result.stdout)

        results = manager.publish_documentation_hierarchy(docs_structure)
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
