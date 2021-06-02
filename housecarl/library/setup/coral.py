from housecarl.library import constants, utility
from housecarl.library.setup import coral_default, coral_pi

def setup_coral():
    if utility.is_raspberry_pi():
        coral_pi.setup_coral()
    else:
        coral_default.setup_coral()

def verify_lib_edge_tpu_install():
    is_installed = False
    if utility.is_raspberry_pi():
        is_installed = coral_pi.check_lib_edge_tpu_install()
    else:
        is_installed = coral_default.check_lib_edge_tpu_install()

    if not is_installed:
        raise Exception('lib_edge_tpu is not installed. Please run Carl with --setup-coral to install it.')

def verify_pycoral_install():
    pycoral_pip_install = utility.is_installed('pycoral')
    pycoral_wheel_install = utility.is_installed('pycoral @ {}'.format(constants.pycoral_rpi_wheel))
    pycoral_is_installed = pycoral_pip_install or pycoral_wheel_install

    if not pycoral_is_installed:
        raise Exception('Could note find "pycoral" in project dependencies. See https://github.com/RobertMcReed/housecarl/blob/feat/coral/README.Coral.md for more info.')

    missing_paths = utility.get_missing_pycoral_dirs()

    if len(missing_paths):
        raise Exception("Could not find {}.\n\nIs pycoral installed?".format(missing_paths[0]))

    return True
