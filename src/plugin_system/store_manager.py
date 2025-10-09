"""
Plugin Store Manager

Manages plugin discovery, installation, and updates from GitHub repositories.
Provides HACS-like functionality for plugin management.

API Version: 1.0.0
"""

import requests
import subprocess
import shutil
import zipfile
import io
import json
from pathlib import Path
from typing import List, Dict, Optional
import logging


class PluginStoreManager:
    """
    Manages plugin discovery, installation, and updates from GitHub.
    
    The store manager provides:
    - Plugin registry fetching and searching
    - Plugin installation from GitHub
    - Plugin uninstallation
    - Plugin updates
    - Direct installation from GitHub URLs
    """
    
    REGISTRY_URL = "https://raw.githubusercontent.com/ChuckBuilds/ledmatrix-plugin-registry/main/plugins.json"
    
    def __init__(self, plugins_dir: str = "plugins"):
        """
        Initialize the Plugin Store Manager.
        
        Args:
            plugins_dir: Path to the plugins directory
        """
        self.plugins_dir = Path(plugins_dir)
        self.logger = logging.getLogger(__name__)
        self.registry_cache = None
        
        # Ensure plugins directory exists
        self.plugins_dir.mkdir(exist_ok=True)
        self.logger.info(f"Plugin Store Manager initialized with plugins directory: {self.plugins_dir}")
        
    def fetch_registry(self, force_refresh: bool = False) -> Dict:
        """
        Fetch the plugin registry from GitHub.
        
        The registry is cached in memory to avoid repeated network requests.
        
        Args:
            force_refresh: Force refresh even if cached
            
        Returns:
            Registry data dict with 'version' and 'plugins' keys
        """
        if self.registry_cache and not force_refresh:
            self.logger.debug("Using cached registry")
            return self.registry_cache
        
        try:
            self.logger.info("Fetching plugin registry from GitHub...")
            response = requests.get(self.REGISTRY_URL, timeout=10)
            response.raise_for_status()
            self.registry_cache = response.json()
            
            plugin_count = len(self.registry_cache.get('plugins', []))
            self.logger.info(f"Fetched registry with {plugin_count} plugin(s)")
            
            return self.registry_cache
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching registry: {e}")
            # Return empty registry on error
            return {"version": "0.0.0", "plugins": []}
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing registry JSON: {e}")
            return {"version": "0.0.0", "plugins": []}
    
    def search_plugins(self, query: str = "", category: str = "", 
                      tags: List[str] = None) -> List[Dict]:
        """
        Search for plugins in the registry.
        
        Args:
            query: Search query string (searches name, description, id)
            category: Filter by category (e.g., 'sports', 'weather', 'time')
            tags: Filter by tags (matches if any tag is present)
            
        Returns:
            List of matching plugin dicts
        """
        registry = self.fetch_registry()
        plugins = registry.get('plugins', [])
        
        if tags is None:
            tags = []
        
        results = []
        for plugin in plugins:
            # Category filter
            if category and plugin.get('category') != category:
                continue
            
            # Tags filter (match if any tag is present)
            if tags and not any(tag in plugin.get('tags', []) for tag in tags):
                continue
            
            # Query search
            if query:
                query_lower = query.lower()
                searchable_text = ' '.join([
                    plugin.get('name', ''),
                    plugin.get('description', ''),
                    plugin.get('id', ''),
                    plugin.get('author', '')
                ]).lower()
                
                if query_lower not in searchable_text:
                    continue
            
            results.append(plugin)
        
        self.logger.debug(f"Search returned {len(results)} result(s)")
        return results
    
    def install_plugin(self, plugin_id: str, version: str = "latest") -> bool:
        """
        Install a plugin from GitHub.
        
        This method:
        1. Looks up the plugin in the registry
        2. Downloads the plugin files from GitHub
        3. Extracts to the plugins directory
        4. Installs Python dependencies if requirements.txt exists
        
        Args:
            plugin_id: Plugin identifier
            version: Version to install (default: latest)
            
        Returns:
            True if installed successfully, False otherwise
        """
        registry = self.fetch_registry()
        plugin_info = next((p for p in registry['plugins'] if p['id'] == plugin_id), None)
        
        if not plugin_info:
            self.logger.error(f"Plugin not found in registry: {plugin_id}")
            return False
        
        try:
            # Get version info
            if version == "latest":
                version_info = plugin_info['versions'][0]  # First is latest
            else:
                version_info = next(
                    (v for v in plugin_info['versions'] if v['version'] == version), 
                    None
                )
                if not version_info:
                    self.logger.error(f"Version not found: {version}")
                    return False
            
            self.logger.info(f"Installing plugin {plugin_id} v{version_info['version']}...")
            
            # Check if plugin directory already exists
            plugin_path = self.plugins_dir / plugin_id
            if plugin_path.exists():
                self.logger.warning(f"Plugin directory already exists: {plugin_id}. Removing...")
                shutil.rmtree(plugin_path)
            
            # Try git clone first (more efficient)
            repo_url = plugin_info['repo']
            tag = version_info.get('version')
            
            if self._install_via_git(repo_url, plugin_path, tag):
                self.logger.info(f"Cloned plugin {plugin_id} via git")
            else:
                # Fall back to downloading zip
                download_url = version_info.get('download_url')
                if not download_url:
                    self.logger.error(f"No download_url found for {plugin_id}")
                    return False
                
                if not self._install_via_download(download_url, plugin_path, plugin_id):
                    return False
            
            # Verify manifest exists
            manifest_path = plugin_path / "manifest.json"
            if not manifest_path.exists():
                self.logger.error(f"No manifest.json found after installation: {plugin_id}")
                shutil.rmtree(plugin_path)
                return False
            
            # Install Python dependencies
            self._install_dependencies(plugin_path)
            
            self.logger.info(f"Successfully installed plugin: {plugin_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing plugin {plugin_id}: {e}", exc_info=True)
            # Cleanup on failure
            if plugin_path.exists():
                shutil.rmtree(plugin_path)
            return False
    
    def _install_via_git(self, repo_url: str, target_path: Path, tag: str = None) -> bool:
        """
        Install plugin via git clone.
        
        Args:
            repo_url: GitHub repository URL
            target_path: Target installation path
            tag: Git tag/version to checkout
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cmd = ['git', 'clone', '--depth', '1']
            if tag:
                cmd.extend(['--branch', f"v{tag}"])
            cmd.extend([repo_url, str(target_path)])
            
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Remove .git directory to save space
            git_dir = target_path / ".git"
            if git_dir.exists():
                shutil.rmtree(git_dir)
            
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.debug(f"Git clone failed: {e}")
            return False
    
    def _install_via_download(self, download_url: str, target_path: Path, 
                             plugin_id: str) -> bool:
        """
        Install plugin via ZIP download.
        
        Args:
            download_url: URL to download ZIP file
            target_path: Target installation path
            plugin_id: Plugin identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Downloading plugin from {download_url}...")
            response = requests.get(download_url, timeout=30)
            response.raise_for_status()
            
            # Extract ZIP
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                # GitHub archives create a root directory like "repo-name-tag/"
                # We need to extract and move contents
                temp_dir = self.plugins_dir / f".temp_{plugin_id}"
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                
                zip_file.extractall(temp_dir)
                
                # Find the root directory (should be only one)
                root_dirs = [d for d in temp_dir.iterdir() if d.is_dir()]
                if len(root_dirs) != 1:
                    self.logger.error(f"Unexpected ZIP structure: {len(root_dirs)} root directories")
                    shutil.rmtree(temp_dir)
                    return False
                
                # Move contents to target path
                shutil.move(str(root_dirs[0]), str(target_path))
                
                # Cleanup temp directory
                shutil.rmtree(temp_dir)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error downloading plugin: {e}")
            return False
    
    def _install_dependencies(self, plugin_path: Path) -> bool:
        """
        Install Python dependencies from requirements.txt.
        
        Args:
            plugin_path: Path to plugin directory
            
        Returns:
            True if successful or no requirements, False on error
        """
        requirements_file = plugin_path / "requirements.txt"
        if not requirements_file.exists():
            self.logger.debug("No requirements.txt found, skipping dependency installation")
            return True
        
        try:
            self.logger.info("Installing plugin dependencies...")
            result = subprocess.run(
                ['pip3', 'install', '--break-system-packages', '-r', str(requirements_file)],
                check=True,
                capture_output=True,
                text=True
            )
            self.logger.info("Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error installing dependencies: {e.stderr}")
            # Don't fail installation if dependencies fail
            # User can manually install them
            return True
        except FileNotFoundError:
            self.logger.warning("pip3 not found, skipping dependency installation")
            return True
    
    def uninstall_plugin(self, plugin_id: str) -> bool:
        """
        Uninstall a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            True if uninstalled successfully, False otherwise
        """
        plugin_path = self.plugins_dir / plugin_id
        
        if not plugin_path.exists():
            self.logger.warning(f"Plugin not found: {plugin_id}")
            return False
        
        try:
            self.logger.info(f"Uninstalling plugin: {plugin_id}")
            shutil.rmtree(plugin_path)
            self.logger.info(f"Uninstalled plugin: {plugin_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error uninstalling plugin {plugin_id}: {e}")
            return False
    
    def update_plugin(self, plugin_id: str) -> bool:
        """
        Update a plugin to the latest version.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            True if updated successfully, False otherwise
        """
        plugin_path = self.plugins_dir / plugin_id
        
        if not plugin_path.exists():
            self.logger.error(f"Plugin not installed: {plugin_id}")
            return False
        
        try:
            # Try git pull first
            git_dir = plugin_path / ".git"
            if git_dir.exists():
                self.logger.info(f"Updating plugin {plugin_id} via git pull...")
                result = subprocess.run(
                    ['git', '-C', str(plugin_path), 'pull'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.logger.info(f"Updated plugin {plugin_id} via git pull")
                    # Reinstall dependencies in case they changed
                    self._install_dependencies(plugin_path)
                    return True
            
            # Fall back to re-download
            self.logger.info(f"Re-downloading plugin {plugin_id} for update...")
            return self.install_plugin(plugin_id, version="latest")
            
        except Exception as e:
            self.logger.error(f"Error updating plugin {plugin_id}: {e}")
            return False
    
    def install_from_url(self, repo_url: str, plugin_id: str = None) -> bool:
        """
        Install a plugin directly from a GitHub URL (for custom/unlisted plugins).
        
        This allows users to install plugins not in the official registry.
        
        Args:
            repo_url: GitHub repository URL
            plugin_id: Optional custom plugin ID (extracted from manifest if not provided)
            
        Returns:
            True if installed successfully, False otherwise
        """
        try:
            self.logger.info(f"Installing plugin from URL: {repo_url}")
            
            # Clone to temporary location
            temp_dir = self.plugins_dir / ".temp_install"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            
            # Try git clone
            if not self._install_via_git(repo_url, temp_dir):
                self.logger.error("Git clone failed")
                return False
            
            # Read manifest to get plugin ID
            manifest_path = temp_dir / "manifest.json"
            if not manifest_path.exists():
                self.logger.error("No manifest.json found in repository")
                shutil.rmtree(temp_dir)
                return False
            
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            plugin_id = plugin_id or manifest.get('id')
            if not plugin_id:
                self.logger.error("No plugin ID found in manifest")
                shutil.rmtree(temp_dir)
                return False
            
            # Move to plugins directory
            final_path = self.plugins_dir / plugin_id
            if final_path.exists():
                self.logger.warning(f"Plugin {plugin_id} already exists, removing...")
                shutil.rmtree(final_path)
            
            shutil.move(str(temp_dir), str(final_path))
            
            # Install dependencies
            self._install_dependencies(final_path)
            
            self.logger.info(f"Installed plugin from URL: {plugin_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing from URL: {e}", exc_info=True)
            # Cleanup
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            return False
    
    def check_for_updates(self, plugin_id: str) -> Optional[Dict]:
        """
        Check if an update is available for a plugin.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Dict with update info if available, None otherwise
        """
        plugin_path = self.plugins_dir / plugin_id
        if not plugin_path.exists():
            return None
        
        # Read current version from manifest
        manifest_path = plugin_path / "manifest.json"
        if not manifest_path.exists():
            return None
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                current_manifest = json.load(f)
            current_version = current_manifest.get('version', '0.0.0')
            
            # Get latest version from registry
            registry = self.fetch_registry()
            plugin_info = next((p for p in registry['plugins'] if p['id'] == plugin_id), None)
            
            if not plugin_info:
                return None
            
            latest_version = plugin_info['versions'][0]['version']
            
            if latest_version != current_version:
                return {
                    'plugin_id': plugin_id,
                    'current_version': current_version,
                    'latest_version': latest_version,
                    'update_available': True
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
            return None

