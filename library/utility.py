import os
import json
import inspect
import argparse

from .constants import config_path, default_config_path

def info(*args):
    """
    Utility [INFO] printer.
    """

    print('[INFO]', *args)

def warn(*args):
    """
    Utility [WARN] printer.
    """

    print('[WARN]', *args)

def error(*args):
    """
    Utility [ERROR] printer.
    """

    print('[ERROR]', *args)

def get_args():
    """
    Instantiate and parse an ArgumentParser with a 'config' key.
    """

    ap = argparse.ArgumentParser()
    ap.add_argument('-c', '--config', help='Path to config.json')
    args = vars(ap.parse_args())

    return args

def read_json(json_path):
    """
    Parse file at json_path or return None if file doesn't exist (or isn't json).
    """

    if not os.path.exists(json_path):
        return None

    with open(json_path) as json_file:
        try:
            data = json.load(json_file)
        except Exception as e:
            warn('Invalid path passed to function read_json: {}'.format(json_path))
            data = None
    
    return data

def get_config(user_config_path=None):
    """
    Read the passed config path and merge with the default config. If no config path is provided, use config.json.
    """
    
    if user_config_path is None:
        user_config_path = config_path

    user_config = read_json(user_config_path)
    default_config = read_json(default_config_path)

    if default_config is None:
        raise Exception('Cannot find config.default.json')

    if user_config is None:
        warn('User config not found. Using config.default.json')
        return default_config
    
    for key in default_config:
        if not key in user_config:
            user_config[key] = default_config[key]

    return user_config

def print_config(config):
    """
    Announce user configuration.
    """

    [print('{}: {}'.format(k, v)) for k, v in config.items()]

def num_args(func):
    spec = inspect.getfullargspec(func)
    args = spec.args
    expected_num = len(args) - 1 if 'self' in args else len(args)

    return expected_num
