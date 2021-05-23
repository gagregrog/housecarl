import os
import json
import argparse
from time import sleep

from library import utility
from library.constants import config_path, default_config_path

class CLI:
    def __init__(self):
        self.__args = None
        self.__config = None
        self.__user_config = None
        self.__default_config = None

    @staticmethod
    def read_json(json_path):
        """
        Parse file at json_path or return None if file doesn't exist (or isn't json).
        """

        if not os.path.exists(json_path):
            return None

        with open(json_path) as json_file:
            try:
                data = json.load(json_file)
            except Exception as e:
                utility.error(
                    'Could not parse JSON at: {}'.format(json_path))
                data = None
        
        return data

    def __get_args(self):
        """
        Instantiate and parse an ArgumentParser.
        """

        ap = argparse.ArgumentParser()
        ap.add_argument('-c', '--config', help='Path to config.json', default=None)
        ap.add_argument('--mock-push', action="store_true")
        ap.add_argument('--no-push', action="store_true")
        ap.add_argument('--no-write', action="store_true")
        ap.add_argument('--no-video', action="store_true")
        ap.add_argument('--show-video', action="store_true")
        ap.add_argument('--src', default=None, help='Video Source. Number or stream url or "usePiCamera')

        self.__args = vars(ap.parse_args())

    def __read_configs(self):
        """
        Read the passed config path and the default config path, parsing each.
        """
        if self.__args.get('config') is not None:
            self.__user_config_path = self.__args.get('config')
        else:    
            self.__user_config_path = config_path

        self.__default_config = CLI.read_json(default_config_path)
        self.__user_config = CLI.read_json(self.__user_config_path)

        if self.__default_config is None:
            raise Exception('Cannot find {}'.format(default_config_path))
        elif self.__user_config is None:
            self.__init_config()

    def __init_config(self):
        self.__user_config = self.__default_config
        utility.warn('{} not found. Creating file and populating with defaults.\n'.format(self.__user_config_path), {'pre': '\n\t'})
        utility.copy_file(default_config_path, self.__user_config_path)
        # pause so you can read the copy warning
        sleep(3)


    def __merge_configs(self):
        """
        Merge the user config with the default config.
        """
        self.__config = {}

        no_write = self.__args.get('no_write')
        no_pushover = self.__args.get('no_push')

        # iterate over all of the config groups and merge user config and args with defaults
        for config_group_name, config_group_defaults in self.__default_config.items():
            configuration_found = config_group_name in self.__user_config

            is_writer = config_group_name == 'writer'
            is_pushover = config_group_name == 'pushover'

            # respect cli arg overrides
            if (is_pushover and (no_pushover or not configuration_found)) or (is_writer and (no_write or not configuration_found)):
                continue

            # if no user supplied config for this group, use group defaults
            if not configuration_found:
                self.__config[config_group_name] = config_group_defaults.copy()
                continue

            user_config_group = self.__user_config[config_group_name]

            user_group_type = utility.get_typename(user_config_group)
            if user_group_type != 'dict':
                raise Exception(
                    'Unexpected configuration of type "{}" provided for key "{}". Expected "{}".'
                        .format(
                            user_group_type,
                            config_group_name,
                            utility.get_typename(config_group_defaults)
                        )
                )

            merged_config_group = {}
            self.__config[config_group_name] = merged_config_group
            
            for key, default_value in config_group_defaults.items():
                user_key_found = key in user_config_group
                user_value = user_config_group.get(key)
                user_value_type = utility.get_typename(user_value)
                default_value_type = utility.get_typename(default_value)
                invalid_value_type = user_key_found and user_value_type != default_value_type

                # allow string or int for video.src
                if key == 'src' and invalid_value_type:
                    if user_value_type == 'str' or user_value_type == 'int':
                        invalid_value_type = False
                elif key == 'mock' and not user_key_found:
                    # if they didn't pass a mock, don't override
                    # aka don't provide True if no key present
                    continue

                if invalid_value_type:
                    utility.error('Invalid type passed for key: {}. Expected {} but got {}.'
                        .format(key, default_value_type, user_value_type)
                    )
                    raise Exception('Invalid user config value')

                merged_config_group[key] = default_value if not user_key_found else user_value

    def __update_config(self, group, key, value):
        if group in self.__config:
            self.__config[group][key] = value
        else:
            self.__config[group] = {key: value}
    
    def __merge_args(self):
        """
        Overwrite any config values with args passed at invocation.
        """
        if self.__args.get('mock_push'):
            self.__update_config('pushover', 'mock', True)

        if self.__args.get('show_video'):
            self.__update_config('video', 'display', True)
        
        if self.__args.get('no_video'):
            self.__update_config('video', 'display', False)

        if self.__args.get('src') is not None:
            src = self.__args.get('src')
            self.__update_config('video', 'src', src)
    
    def __get_config_group(self, key):
        group = self.__config.get(key)
        return group.copy() if group else None

    def process(self):
        self.__get_args()
        self.__read_configs()
        self.__merge_configs()
        self.__merge_args()

        return self
    
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

    def get_detector_config(self):
        return self.__get_config_group('detector')

    def get_writer_config(self):
        return self.__get_config_group('writer')

    def get_monitor_config(self):
        return self.__get_config_group('monitor')

    def get_pushover_config(self):
        return self.__get_config_group('pushover')

    def get_video_config(self):
        return self.__get_config_group('video')
