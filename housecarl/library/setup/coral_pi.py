import os
import platform
import subprocess

from housecarl.library import utility

def verify_python_version():
    version = platform.python_version()
    (major, minor, patch) = version.split('.')

    if major != '3' or minor != 7:
        raise Exception('Python version must be between 3.7 to use the Google Coral USB Accelerator on a Raspberry Pi')

def verify_hardware():
    uname = os.uname()

    OS = uname[0]
    MACHINE = uname[4]

    is_linux = OS == "Linux"
    is_pi = utility.is_raspberry_pi()
    is_arm7 = MACHINE in "armv7l"

    if not (is_pi and is_linux and is_arm7):
        raise Exception('If using the Google Coral on a Raspberry Pi, the architecture must be armv7l')

def check_lib_edge_tpu_install():
    verify_hardware()

    # https://stackoverflow.com/a/3391589/8643833
    with open(os.devnull, "w") as devnull:
        retval = subprocess.call(
            ["dpkg","-s","libedgetpu1-std"],
            stdout=devnull,
            stderr=subprocess.STDOUT
        )
    
    return retval == 0

def install_pycoral():
    utility.info('Installing pycoral and tflite-runtime...')
    new_reqs = utility.pip_install('https://github.com/google-coral/pycoral/releases/download/v1.0.1/tflite_runtime-2.5.0-cp37-cp37m-linux_armv7l.whl https://github.com/google-coral/pycoral/releases/download/v1.0.1/pycoral-1.0.1-cp37-cp37m-linux_armv7l.whl')

    utility.info('The following packages have been installed:\n')
    [print('\t{}'.format(req)) for req in new_reqs]
   
def setup_coral():
    utility.info('Checking hardware compatibility...')
    verify_hardware()
    print('\tDevice is compatible!\n')

    utility.info('Checking python version...')
    verify_python_version()
    print('\tPython version is compatible!\n')

    utility.info("Checking if Google Coral lib_edge_tpu has been installed...")
    lib_is_installed = check_lib_edge_tpu_install()

    if not lib_is_installed:
        install_cmd = '\n'.join([
            'echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list',
            'curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -',
            'sudo apt-get update',
            'sudo apt-get install libedgetpu1-std'
        ])
        
        print('\tlib_edge_tpu not found.\n')

        utility.info('You need to install the Google Coral runtime on your Pi.\n\nAfter the library has been installed, run Carl again with "--setup-coral" to finish this setup.\n')
        utility.info("You will need to enter your password to process this install.\n\nType the following to process the install:\n")
        print(install_cmd)

        return
    else:
        print("\tSuccess! lib_edge_tpu is installed.\n")

    utility.info("Checking if pycoral has been installed...")
    missing_dirs = utility.get_missing_pycoral_dirs()

    new_install = False
    if len(missing_dirs):
        print('\tpycoral not found. It will be installed now...\n')
        install_pycoral()

    print('\tSuccess! pycoral {} installed.\n'.format('has been' if new_install else 'is'))

    utility.info('Everything appears to be in order. Carl should now be able to use your Google Coral USB Accelerator on your Raspberry Pi. Simply plug it in to the USB 3 port and tell Carl to use the "coral" model.')
