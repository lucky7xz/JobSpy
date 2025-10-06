import json
import glob
import os

def get_user_configs(config_path=None):
    if config_path:
        with open(config_path) as f:
            return [json.load(f)]

    user_config_paths = glob.glob('src/users/**/*.json', recursive=True)
    print(f" ---> Config file paths found : {user_config_paths}")
    user_configs = []

    for user_config_path in user_config_paths:
        with open(user_config_path) as f:
            tmp_dict = json.load(f)
            user_configs.append(tmp_dict)
    
    return user_configs

def get_proxy():
    proxy_path = os.path.join("results", "proxy.txt")
    if not os.path.exists(proxy_path):
        return None
    with open(proxy_path, "r") as f:
        proxy = f.read().strip()

    return proxy
