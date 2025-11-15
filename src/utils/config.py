import json
import os
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_path: str = "data/config.json"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return self._get_default_config()