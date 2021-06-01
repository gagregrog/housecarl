import os
import sysconfig

def verify_lib_edge_tpu_install():
    uname = os.uname()

    OS = uname[0]
    MACHINE = uname[4]

    if OS == "Linux":
        if MACHINE in "x86_64":
            HOST_GNU_TYPE="x86_64-linux-gnu"
        elif MACHINE in "armv6l":
            HOST_GNU_TYPE="arm-linux-gnueabihf"
        elif MACHINE in "armv7l":
            HOST_GNU_TYPE="arm-linux-gnueabihf"
        elif MACHINE in "aarch64":
            HOST_GNU_TYPE="aarch64-linux-gnu"
        else:
            raise Exception("Your Linux platform is not supported.")

        filepath = "/usr/lib/{}/libedgetpu.so.1.0".format(HOST_GNU_TYPE)
    elif OS == "Darwin":
        filepath = "/usr/local/lib/libedgetpu.1.dylib"
    else:
        raise Exception("Your operating system is not supported.")

    return os.path.exists(filepath)

    

def verify_pycoral_install():
    all_paths = sysconfig.get_paths()
    site_packages = all_paths["purelib"]
    pycoral_dir = os.path.join(site_packages, "pycoral")
    
    subdir_names = ["adapters", "utils"]
    subdir_paths = [os.path.join(pycoral_dir, d) for d in subdir_names]
    paths = [pycoral_dir] + subdir_paths

    for dir_path in paths:
        if not os.path.exists(dir_path):
            raise Exception("Could not find {}.\n\nIs pycoral installed?")

    return True
