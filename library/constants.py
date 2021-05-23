from os.path import join, dirname

root_path = join(dirname(__file__), '..')
models_path = join(root_path, 'models')
recordings_path = join(root_path, 'recordings')
mobilenet_path = join(models_path, 'mobilenet')
yolo_path = join(models_path, 'yolo')
config_path = join(root_path, 'config.json')
default_config_path = join(root_path, 'library', 'config.default.json')
