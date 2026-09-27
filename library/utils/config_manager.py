import os
from typing import Any, Dict, Optional

class ConfigManager:
    @classmethod
    def get_env(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        return os.environ.get(key, default)

    @classmethod
    def get_nested_config(cls, config_map: Dict[str, Any], key_path: str, default: Any = None) -> Any:
        keys = key_path.split('.')
        value = config_map
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
