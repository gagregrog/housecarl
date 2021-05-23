import os
import shutil
import inspect
import requests
from pathlib import Path

def _log(log_type: str, *args) -> None:
    """
    Utility [LOG_TYPE] printer.
    """

    last_arg = args[len(args) - 1]
    prefix = '' if 'pre' not in last_arg else last_arg.get('pre')
    data = args if not prefix else args[:-1]

    print('{}[{}]'.format(prefix, log_type.upper()), *data)

info = lambda *args: _log('info', *args)
warn = lambda *args: _log('warn', *args)
error = lambda *args: _log('error', *args, {'pre': '\n\t'})

def num_args(func):
    spec = inspect.getfullargspec(func)
    args = spec.args
    expected_num = len(args) - 1 if 'self' in args else len(args)

    return expected_num

def intersection(list_a, list_b):
    return list(set(list_a) & set(list_b))

def capitalize(word: str) -> str:
    return word[0].upper() + word[1:]

def get_precision(num: float, num_dec: int =3) -> float:
    if isinstance(num, int):
        return float(num)
        
    _int, _dec = str(num).split('.')
    prec = int(_int) + float('0.' + _dec[:num_dec])

    return prec

def bytes_to_gb(num_bytes):
    return num_bytes / 1000000000

def get_free_space():
    home = os.path.expanduser('~')
    (total, used, free) = shutil.disk_usage(home)

    return bytes_to_gb(free)

def get_typename(obj):
    return type(obj).__name__

def set_properties(properties: dict, destination) -> None:
    for key, value in properties.items():
        setattr(destination, key, value)

def ensure_dir(dir):
    Path(dir).mkdir(parents=True, exist_ok=True)

def download_file(url, destination):
    info('Downloading file: {}\n From: {}\n'
        .format(destination, url)
    )
    ensure_dir(destination)
    r = requests.get(url)
    with open(destination, 'wb') as f:
        f.write(r.content)
