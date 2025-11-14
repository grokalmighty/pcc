import threading
from typing import Dict, Any
from src.features.unified_search.search_engine import SearchEngine
from src.features.clipboard_manager.manager import ClipboardManager
from src.features.file_organizer.organizer import FileOrganizer
from src.features.workspace_manager.manager import WorkspaceManager
from src.utils.config import ConfigManager

class CommandCenter:
    def __init__(self):
        self.config = ConfigManager()
        self.features = {}
        self.is_running = False

    def initialize_features(self):
        """Initialize all features independently"""
        try:
            # Unified Search
            self.features['search'] = SearchEngine(self.config)
            print("Search engine initialize")

            # Clipboard Manager
            self.features['clipboard'] = ClipboardManager(self.config)
            print("Clipboard manager initialized")

            # File Organizer
            self.features['organizer'] = FileOrganizer(self.config)
            print("File organizer initialized")

            # Workspace Manager
            self.featurse['workspace'] = WorkspaceManager(self.config)
            print("Workspace manager initialized")

        except Exception as e:
            print(f" Feature initialization failed: {e}")
            raise

        def start_background_services(self):
            """Start features that need background processing"""
            if 'clipboard' in self.features:
                self.features['clipboard'].start_monitoring()

            if 'organizer' in self.features:
                self.features['organizer'].start_monitoring()

        def stop_background_services(self):
            """Stop all background services"""
            if 'clipboard' in self.features:
                self.features['clipboard'].stop_monitoring()

            if 'organizer' in self.features:
                self.features['organizer'].stop_monitoring()
            
        def search(self, query: str) -> Dict[str, Any]:
            """Unified search across all features"""
            results = {}

            # File search
            if 'search' in self.features:
                results['files'] = self.features['search'].search(query)

            # Clipboard search
            if 'clipboard' in self.features:
                results['clipboard'] = self.features['clipboard'].search(query)

            # Workspace search
            if 'workspace' in self.features:
                results['workspaces'] = self.features['workspace'].search_workspaces(query)
            return results
        
        def execute_command(self, command_type: str, data: Any) -> bool:
            """Execute commands from UI"""
            try:
                if command_type == 'open_file':
                    return self.features['search'].open_file(data)
                elif command_type == 'copy_clipboard_item':
                    return self.features['clipboard'].copy_to_clipboard(data)
                elif command_type == 'launch_workspace':
                    return self.features['workspace'].launch_workspace(data)
                return False
            except Exception as e:
                print(f"Command execution failed: {e}")
                return False
