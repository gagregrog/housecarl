from housecarl.library import utility

def is_picamera_installed():
    return utility.is_installed('picamera')

def install_picamera():
    new_reqs = utility.pip_install('"picamera[array]"')
    
    utility.info('The following packages have been installed:\n')
    [print('\t{}'.format(req)) for req in new_reqs]

def setup_picamera():
    utility.info('Checking hardware compatibility...')
    if not utility.is_raspberry_pi():
        raise Exception('Picamera is only supported on a Raspberry Pi. This does not appear to be a raspberry pi.')
    else:
        print('\tLooks like this is a Raspberry Pi!\n')

    utility.info("Checking if picamera has been installed...")

    new_install = False
    if not is_picamera_installed():
        print('\tpicamera not found. It will be installed now...\n')
        install_picamera()

    print('\tSuccess! picamera {} installed.\n'.format('has been' if new_install else 'is'))

    utility.info('Everything appears to be in order. Carl should now be able to access your picamera.')
