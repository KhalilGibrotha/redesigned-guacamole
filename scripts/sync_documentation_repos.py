#!/usr/bin/env python3
"""
Documentation Repository Synchronization Script
Clones/updates git repositories containing documentation templates
"""

import os
import yaml
import subprocess
import logging
import shutil
from pathlib import Path
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RepoSynchronizer:
    def __init__(self, config_path: str = "vars/repos.yml"):
        self.config = self._load_config(config_path)
        self.auto_document_dir = Path("docs/auto_document")
        self.auto_document_dir.mkdir(exist_ok=True)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load repository configuration"""
        config_file = Path(config_path)
        if not config_file.exists():
            logger.warning(f"Config file {config_path} not found")
            return {"documentation_repos": []}
            
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def sync_all_repos(self) -> bool:
        """Synchronize all enabled repositories"""
        success = True
        repos = self.config.get('documentation_repos', [])
        
        if not repos:
            logger.info("No repositories configured for synchronization")
            return True
            
        for repo_config in repos:
            if repo_config.get('enabled', True):
                try:
                    self._sync_repo(repo_config)
                except Exception as e:
                    logger.error(f"Failed to sync repo {repo_config['name']}: {e}")
                    success = False
            else:
                logger.info(f"Skipping disabled repo: {repo_config['name']}")
                
        return success
    
    def _sync_repo(self, repo_config: Dict) -> None:
        """Synchronize a single repository"""
        repo_name = repo_config['name']
        repo_url = repo_config['url']
        branch = repo_config.get('branch', 'main')
        
        repo_dir = self.auto_document_dir / repo_name
        
        sync_behavior = self.config.get('sync_behavior', {})
        auto_sync = sync_behavior.get('auto_sync', 'if_missing')
        clean_before_sync = sync_behavior.get('clean_before_sync', False)
        timeout = sync_behavior.get('timeout', 300)
        
        # Check if we should sync
        if auto_sync == 'manual' and repo_dir.exists():
            logger.info(f"Skipping {repo_name} - manual sync mode and repo exists")
            return
            
        if auto_sync == 'if_missing' and repo_dir.exists():
            logger.info(f"Skipping {repo_name} - already exists")
            return
        
        # Clean up existing directory if requested
        if clean_before_sync and repo_dir.exists():
            logger.info(f"Cleaning existing repo directory: {repo_dir}")
            shutil.rmtree(repo_dir)
        
        # Clone or update repository
        if repo_dir.exists():
            logger.info(f"Updating existing repo: {repo_name}")
            self._update_repo(repo_dir, branch, timeout)
        else:
            logger.info(f"Cloning new repo: {repo_name} from {repo_url}")
            self._clone_repo(repo_url, repo_dir, branch, timeout)
        
        # Verify doc_path exists
        doc_path = repo_config.get('doc_path', '')
        if doc_path:
            full_doc_path = repo_dir / doc_path
            if not full_doc_path.exists():
                logger.warning(f"Configured doc_path '{doc_path}' not found in {repo_name}")
    
    def _clone_repo(self, repo_url: str, repo_dir: Path, branch: str, timeout: int) -> None:
        """Clone a git repository"""
        env = self._get_git_env()
        
        cmd = ['git', 'clone', '--depth', '1', '--branch', branch, repo_url, str(repo_dir)]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
        )
        
        if result.returncode != 0:
            raise Exception(f"Git clone failed: {result.stderr}")
            
        logger.info(f"Successfully cloned {repo_url} to {repo_dir}")
    
    def _update_repo(self, repo_dir: Path, branch: str, timeout: int) -> None:
        """Update an existing git repository"""
        env = self._get_git_env()
        
        # Fetch latest changes
        cmd = ['git', 'fetch', 'origin', branch]
        result = subprocess.run(
            cmd,
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
        )
        
        if result.returncode != 0:
            raise Exception(f"Git fetch failed: {result.stderr}")
        
        # Reset to latest
        cmd = ['git', 'reset', '--hard', f'origin/{branch}']
        result = subprocess.run(
            cmd,
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
        )
        
        if result.returncode != 0:
            raise Exception(f"Git reset failed: {result.stderr}")
            
        logger.info(f"Successfully updated {repo_dir}")
    
    def _get_git_env(self) -> Dict[str, str]:
        """Get environment variables for git operations"""
        env = os.environ.copy()
        
        auth_config = self.config.get('git_auth', {})
        method = auth_config.get('method', 'none')
        
        if method == 'token':
            # Use GitHub token if available
            token = os.environ.get('GITHUB_TOKEN')
            if token:
                # For HTTPS URLs, git will use the token automatically
                pass
            else:
                logger.warning("GITHUB_TOKEN not set but token auth configured")
        
        return env

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sync documentation repositories')
    parser.add_argument('--config', default='vars/repos.yml', help='Configuration file path')
    parser.add_argument('--force', action='store_true', help='Force sync even if repos exist')
    args = parser.parse_args()
    
    # Temporarily override sync behavior if force is used
    if args.force:
        # Update config to force sync
        synchronizer = RepoSynchronizer(args.config)
        synchronizer.config['sync_behavior']['auto_sync'] = 'always'
    else:
        synchronizer = RepoSynchronizer(args.config)
    
    success = synchronizer.sync_all_repos()
    
    if not success:
        exit(1)
    
    logger.info("Repository synchronization completed successfully")

if __name__ == "__main__":
    main()
