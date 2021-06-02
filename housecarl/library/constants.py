from os.path import join, dirname, abspath

root_path = abspath(join(dirname(__file__), '..', '..'))
housecarl_path = abspath(join(dirname(__file__), '..'))
models_path = join(root_path, 'models')
recordings_path = join(root_path, 'recordings')
mobilenet_path = join(models_path, 'mobilenet')
coral_path = join(models_path, 'coral')
yolo_path = join(models_path, 'yolo')
config_path = join(root_path, 'config.json')
default_config_path = join(housecarl_path, 'library', 'config.default.json')
edge_tpu_path = join(root_path, 'edgetpu_runtime')
pycoral_rpi_wheel = "https://github.com/google-coral/pycoral/releases/download/v1.0.1/pycoral-1.0.1-cp37-cp37m-linux_armv7l.whl"
tflite_rpi_wheel = "https://github.com/google-coral/pycoral/releases/download/v1.0.1/tflite_runtime-2.5.0-cp37-cp37m-linux_armv7l.whl"
