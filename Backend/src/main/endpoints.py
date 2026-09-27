from kinasis_library.utils.utils import generate_uuid
from kinasis_library.utils.config_manager import ConfigManager

uuid = generate_uuid("ATHENA")

print(f"Generated UUID: {uuid}")

config_manager = ConfigManager()

variable = config_manager.get_env("HELP")

print(variable)