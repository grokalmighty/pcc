import subprocess
import webbrowser
from typing import Dict, List, Any
from src.features.unified_search.search_engine import SearchEngine

class WorkspaceManager:
    def __init__(self, config):
        self.config = config
        self.search_engine = SearchEngine(config) # Reuse for file opening

    def get_workspaces(self) -> Dict[str, Any]:
        """Get all defined workspaces"""
        return self.config.get('workspaces', {})
    
    def search_workspaces(self, query: str) -> List[Dict[str, Any]]:
        """Search for workspaces by name"""
        workspaces = self.get_workspaces()
        results = []

        for name, config in workspaces.items():
            if query.lower() in name.lower():
                results.append({
                    'name': name,
                    'config': config,
                    'type': 'workspace'
                })
        
        return results
    
    def launch_workspace(self, workspace_name: str) -> bool:
        """Launch a workspace configuration"""
        workspaces = self.get_workspaces()

        if workspace_name not in workspaces:
            print(f"Workspace '{workspace_name}' not found")
            return False
    
        config = workspaces[workspace_name]
        success = True

        # Launch applications
        for app in config.get('apps', []):
            if not self._launch_applicattion(app):
                success = False

        # Open files
        for file_path in config.get('files', []):
            if not self.search_engine.open_file(file_path):
                success = False

        return success
    
    def _launch_application(self, app_name: str) -> bool:
        """Launch an application"""
        try:
            subprocess.Popen(app_name, shell=True)
            return True
        except Exception as e:
            print(f"Failed to launch {app_name}: {e}")
            return False
        
    def _open_url(self, url: str) -> bool:
        """Open a URL in default browser"""
        try:
            webbrowser.open(url)
            return True
        except Exception as e:
            print(f"Failed to open {url}: {e}")
            return False