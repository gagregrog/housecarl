from os.path import join, dirname, abspath

housecarl_path = abspath(join(dirname(__file__), '..'))
root_path = abspath(join(dirname(__file__), '..', '..'))

config_path = join(root_path, 'config.json')
default_config_path = join(housecarl_path, 'library', 'config.default.json')

recordings_path = join(root_path, 'recordings')

models_path = join(root_path, 'models')
mobilenet_path = join(models_path, 'mobilenet')
coral_path = join(models_path, 'coral')
yolo_path = join(models_path, 'yolo')

edge_tpu_path = join(root_path, 'edgetpu_runtime')

pycoral_rpi_wheel = "https://github.com/google-coral/pycoral/releases/download/v1.0.1/pycoral-1.0.1-cp37-cp37m-linux_armv7l.whl"

tflite_rpi_wheel = "https://github.com/google-coral/pycoral/releases/download/v1.0.1/tflite_runtime-2.5.0-cp37-cp37m-linux_armv7l.whl"

build_path = join(housecarl_path, 'library', 'server', 'build')
static_path = join(build_path, 'static')
