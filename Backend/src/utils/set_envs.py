from kinasis_library.utils.config_manager import ConfigManager


def get_dict_envs_db_conection():
    cm = ConfigManager()
    envs = {
        "DB_HOST": cm.get_env("DB_HOST"),
        "DB_PORT": cm.get_env("DB_PORT"),
        "DB_USER": cm.get_env("DB_USER"),
        "DB_PASSWORD": cm.get_env("DB_PASSWORD"),
        "DB_NAME": cm.get_env("DB_CONECTION"),
    }
    return envs

def get_dict_envs_redis_conection():
    cm = ConfigManager()
    envs = {
        "REDIS_HOST": cm.get_env("REDIS_HOST"),
        "REDIS_PORT": cm.get_env("REDIS_PORT"),
        "REDIS_PASSWORD": cm.get_env("REDIS_PASSWORD"),
    }
    return envs