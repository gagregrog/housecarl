import os
import zipfile
import platform
import sysconfig

from housecarl.library import utility, constants

def verify_python_version():
    version = platform.python_version()
    (major, minor, patch) = version.split('.')

    if major != '3' or int(minor) < 5 or int(minor) > 8:
        raise Exception('Python version must be between 3.5 and 3.8 to use the Google Coral USB Accelerator')

def get_lib_edgetpu_path():
    filepath = None
    uname = os.uname()

    OS = uname[0]
    MACHINE = uname[4]
    HOST_GNU_TYPE = None

    if OS == "Linux":
        if MACHINE in "x86_64":
            HOST_GNU_TYPE="x86_64-linux-gnu"
        elif MACHINE in "armv6l":
            HOST_GNU_TYPE="arm-linux-gnueabihf"
        elif MACHINE in "armv7l":
            HOST_GNU_TYPE="arm-linux-gnueabihf"
        elif MACHINE in "aarch64":
            HOST_GNU_TYPE="aarch64-linux-gnu"

        if HOST_GNU_TYPE:
            filepath = "/usr/lib/{}/libedgetpu.so.1.0".format(HOST_GNU_TYPE)

    elif OS == "Darwin":
        filepath = "/usr/local/lib/libedgetpu.1.dylib"

    return filepath

def verify_hardware():
    if not bool(get_lib_edgetpu_path()):
        raise Exception('Google Edge TPU is not supported on this device')

def verify_lib_edge_tpu_install():
    verify_hardware()
    filepath = get_lib_edgetpu_path()
    
    return os.path.exists(filepath)

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

def verify_pycoral_install():
    if not utility.is_installed('pycoral'):
        raise Exception('Could note find "pycoral" in project dependencies. See https://github.com/RobertMcReed/housecarl/blob/feat/coral/README.Coral.md for more info.')

    missing_paths = get_missing_pycoral_dirs()

    if len(missing_paths):
        raise Exception("Could not find {}.\n\nIs pycoral installed?".format(missing_paths[0]))

    return True

def install_pycoral():
    new_reqs = utility.pip_install('--extra-index-url https://google-coral.github.io/py-repo/ pycoral')

    utility.info('The following packages have been installed:\n')
    [print('\t{}').format(req) for req in new_reqs]

def download_lib_edge_tpu():
    zip_path = os.path.join(constants.root_path, 'edgetpu_runtime_20210119.zip')
    
    utility.download_file('https://github.com/google-coral/libedgetpu/releases/download/release-frogfish/edgetpu_runtime_20210119.zip', zip_path)

    utility.info('Extracting contents to {}.'.format(constants.edge_tpu_path))

    # https://stackoverflow.com/a/3451150/8643833
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # this will create root/edgetpu_runtime
        zip_ref.extractall(constants.root_path)

    utility.info('Removing file {}.'.format(zip_path))
    os.remove(zip_path)
    
def setup_coral():
    utility.info('Checking hardware compatibility...')
    verify_hardware()
    print('\tDevice is compatible!\n')

    utility.info('Checking python version...')
    verify_python_version()
    print('\tPython version is compatible!\n')

    utility.info("Checking if Google Coral lib_edge_tpu has been installed...")
    lib_is_installed = verify_lib_edge_tpu_install()

    if not lib_is_installed:
        print('\tlib_edge_tpu not found. It will be downloaded now...')
        download_lib_edge_tpu()
        utility.info('You now need to run the Google Coral installer. After the library has been installed, run "carl --setup-coral" again to finish the setup.')
        utility.info("When prompted, type 'n' to disable maximum operating frequency. You will need to enter your password to process this install. Type the following to run the google installer:\n")
        print('curr=`pwd` && cd {} && sudo bash install.sh && cd "$curr"'.format(constants.edge_tpu_path))

        return
    else:
        print("\tSuccess! lib_edge_tpu is installed.\n")

    utility.info("Checking if pycoral has been installed...")
    missing_dirs = get_missing_pycoral_dirs()

    new_install = False
    if len(missing_dirs):
        print('\tpycoral not found. It will be installed now...')
        install_pycoral()

    print('\tSuccess! pycoral {} installed.\n'.format('has been' if new_install else 'is'))

    utility.info('Everything appears to be in order. Carl should now be able to use your Google Coral USB Accelerator. Simply plug it in and tell Carl to use the "coral" model.')
