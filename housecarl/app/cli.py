import argparse

from housecarl.library.common import utility
from housecarl.library.common.constants import default_config_path

class CLI:
    def __init__(self):
        self.__args = None
        self.__process()

    def __get_args(self):
        """
        Instantiate and parse an ArgumentParser.
        """

        ap = argparse.ArgumentParser()
        ap.add_argument('-c', '--config', help='Path to config.json', default=None)
        ap.add_argument('--mock-push', action="store_true", help="Don't send push notifications, but show messages in terminal.")
        ap.add_argument('--no-push', action="store_true", help="Don't send push notifications.")
        ap.add_argument('--no-write', action="store_true", help="Don't record video.")
        ap.add_argument('--no-video', action="store_true", help="Suppress video.")
        ap.add_argument('--show-video', action="store_true", help="Show video.")
        ap.add_argument('--no-detect', action="store_true", help="Don't perform inference")
        ap.add_argument('--no-monitor', action="store_true", help="No push or write. No post-processing of detections.")
        ap.add_argument('--setup-coral', action='store_true', help='Let Carl walk you through the Google Coral setup.')
        ap.add_argument('--threaded', action="store_true", help="Run the detections in a separate thread.")
        ap.add_argument('--src', default=None, help='Video Source. Number or stream url or "usePiCamera"')
        ap.add_argument('--server-debug', action="store_true", help='Whether to start the  server in debug mode')
        ap.add_argument('--server-only', action="store_true", help="Only start the server, and nothing else.")
        ap.add_argument('--width', default=None, help='Video Width.')
        ap.add_argument('--model', default=None, help='Model to use. Either "yolo" or "mobilenet".')

        self.__args = vars(ap.parse_args())

    def __process(self):
        self.__get_args()

        if self.should_setup_coral():
            return self
            
        self.__read_configs()
        self.__merge_configs()
        self.__merge_args()

        return self

    
    
    def __merge_args(self):
        """
        Overwrite any config values with args passed at invocation.
        """
        self.__override_if_arg_exists('pushover', 'mock', argname='mock_push')
        self.__override_if_arg_exists('video', 'display', argname='show_video')
        self.__override_if_arg_exists('video', 'display', argname='hide_video', override=False)
        self.__override_if_arg_exists('video', 'src')
        self.__override_if_arg_exists('video', 'width')
        self.__override_if_arg_exists('video', 'server_debug')
        self.__override_if_arg_exists('detector', 'model')
        self.__override_if_arg_exists('detector', 'threaded')
        self.__override_if_arg_exists('server', 'server_only')


    def __override_if_arg_exists(self, config_group, config_key, argname=None, override=None):
        resolved_key = argname if argname else config_key
        val = self.__args.get(resolved_key)

        if val is not None and val is not False:
            resolved_val = val if override is None else override
            self.__update_config(config_group, config_key, resolved_val)
    
    def get_group_dict(self, group_key, original=False):
        """
        Return a config group from the config dictionary.
        Set original=True to return the original config group instead of a copy.
        """
        group = self.__config.get(group_key)

        if not group:
            return None

        return group if original else group.copy()
    
    def print_config(self):
        """
        Announce resolved configuration.
        """
        if self.__config is None:
            raise Exception('config not processed')

        utility.info('Resolved configuration:')

        for group_name, group_values in self.__config.items():
            print('\n\tConfig group: {}'.format(group_name))
            [print('\t\t{}: {}'.format(k, '<*MASKED*>' if 'token' in k and v else v)) for k, v in group_values.items()]

    def is_valid_group_name(self, group_name):
        return group_name in self.__config

    # return a copy of the config dictionary or an empty dictionary if no config present
    def dict(self):
        if self.__config is None:
            return {}
            
        return self.__config.copy()

    def get(self, group_name, config_key):
        """
        Get a config value.
        """
        if self.__config is None:
            raise Exception('config not processed')

        group = self.get_group_dict(group_name)
        if group is None:
            raise Exception('config group not found: {}'.format(group_name))

        return group.get(config_key)

    def set(self, group_name, config_key, config_value):
        """
        Set a config value.
        """
        if self.__config is None:
            raise Exception('config not processed')

        group = self.get_group_dict(group_name, original=True)
        if group is None:
            raise Exception('config group not found: {}'.format(group_name))

        # throw an error if the config_value is not of the expected type
        expected_type = utility.get_typename(self.get(group_name, config_key))
        config_value_type = utility.get_typename(config_value)
        if config_value_type != expected_type:
            if config_key == 'src' and (config_value_type == 'int' or config_value_type == 'str'):
                # allow string or int for video.src
                pass
            else:
                raise Exception(
                    'Expected config value of type "{}" but got "{}". Group: {}, Key: {}, Value: {}'
                        .format(
                            expected_type,
                            config_value_type,
                            group_name,
                            config_key,
                            config_value
                        )
                )

        group[config_key] = config_value

    def get_config_group(self, group_name):
        """
        Return a config group from the config dictionary if it exists, otherwise return None.
        """
        if self.is_valid_group_name(group_name):
            return CLI_Group(self, group_name)

        return None

    def get_detector_config(self):
        return self.get_config_group('detector')

    def get_writer_config(self):
        return self.get_config_group('writer')

    def get_monitor_config(self):
        return self.get_config_group('monitor')

    def get_pushover_config(self):
        return self.get_config_group('pushover')

    def get_server_config(self):
        server_config = self.get_config_group('server')
        writer_config = self.get_group_dict('writer')

        out_dir = ''
        if writer_config is not None:
            out_dir = writer_config.get('out_dir')

        if out_dir:
            server_config.set('video_dir', out_dir)

        return server_config

    def get_video_config(self):
        return self.get_config_group('video')

    def should_setup_coral(self):
        return self.__args.get('setup_coral')

class CLI_Group:
    def __init__(self, cli: CLI, group_name: str):
        self.__cli = cli
        self.__group_name = group_name

        # raise an exception if the group name is not valid
        if not self.__cli.is_valid_group_name(group_name):
            raise Exception('Invalid group name: {}'.format(group_name))

    def get(self, config_key):
        return self.__cli.get(self.__group_name, config_key)

    def set(self, config_key, config_value):
        self.__cli.set(self.__group_name, config_key, config_value)

    def dict(self):
        self.__cli.get_group_dict(self.__group_name)
