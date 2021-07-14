import os
import sys
import shutil
import inspect
import requests
import sysconfig
import subprocess
from pathlib import Path

from housecarl.library import constants

def _log(log_type: str, *args) -> None:
    """
    Utility [LOG_TYPE] printer.
    """

    last_arg = args[len(args) - 1]
    prefix = '' if 'pre' not in last_arg else last_arg.get('pre')
    prefix = prefix if 'emphasis' not in last_arg else '\n\t'
    data = args if not prefix else args[:-1]

    print('\n{}[{}]'.format(prefix, log_type.upper()), *data)

info = lambda *args: _log('info', *args)
warn = lambda *args: _log('warn', *args)
error = lambda *args: _log('error', *args, {'emphasis': True})

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

def copy_file(src_path, dest_path):
    shutil.copyfile(src_path, dest_path)

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
    r = requests.get(url)
    
    with open(destination, 'wb') as f:
        f.write(r.content)

# https://stackoverflow.com/questions/25010369/wget-curl-large-file-from-google-drive/39225039#39225039
def download_large_file_from_google_drive(file_id, destination):
    info('Downloading large file: {}\n Google Drive File ID: {}\n'
        .format(destination, file_id)
    )
    
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(response, destination):
        CHUNK_SIZE = 32768

        with open(destination, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)

    URL = "https://drive.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = {'id' : file_id}, stream = True)
    token = get_confirm_token(response)

    if token:
        params = {'id' : file_id, 'confirm' : token}
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)

def get_reqs():
    b_string =  subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
    string = b_string.decode()
    reqs = [req for req in string.split('\n') if req]

    return reqs

def is_installed(package):
    reqs = get_reqs()
    names = [req.split('==')[0] for req in reqs]

    return package in names

def pip_install(*args):
    clean_args = [word for words in args for word in words.split(' ')]
    prev_reqs = get_reqs()
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', *clean_args])
    curr_reqs = get_reqs()
    new_reqs = [req for req in curr_reqs if req not in prev_reqs]

    return new_reqs

# https://raspberrypi.stackexchange.com/a/118473/90630
def is_raspberry_pi():
    try:
        with open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower():
                return True
    except Exception:
        pass

    return False

def get_missing_pycoral_dirs():
    all_paths = sysconfig.get_paths()
    site_packages = all_paths["purelib"]
    pycoral_dir = os.path.join(site_packages, "pycoral")
    
    subdir_names = ["adapters", "utils"]
    subdir_paths = [os.path.join(pycoral_dir, d) for d in subdir_names]
    paths = [pycoral_dir] + subdir_paths

    missing_paths = []
    for dir_path in paths:
        if not os.path.exists(dir_path):
            missing_paths.append(dir_path)

    return missing_paths

def get_video_dir(optional_path=''):
    video_dir = constants.recordings_path if not optional_path else os.path.abspath(os.path.expanduser(optional_path))

    return video_dir
