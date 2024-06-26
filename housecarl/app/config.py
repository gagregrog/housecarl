
from time import sleep

from housecarl.library.common import utility
from housecarl.library.common.constants import config_path, default_config_path

class Config:
    def __init__(self):
        pass

    def __read_configs(self):
        """
        Read the passed config path and the default config path, parsing each.
        """
        if self.__args.get('config') is not None:
            self.__user_config_path = self.__args.get('config')
        else:    
            self.__user_config_path = config_path

        self.__default_config = utility.read_json(default_config_path)
        self.__user_config = utility.read_json(self.__user_config_path)

        if self.__default_config is None:
            raise Exception('Cannot find {}'.format(default_config_path))
        elif self.__user_config is None:
            self.__init_config()

    def __init_config(self):
        self.__user_config = self.__default_config

        if self.__user_config_path != config_path:
            utility.warn('{} not found. Creating file and populating with defaults.\n'.format(self.__user_config_path), {'emphasis': True})
            utility.copy_file(default_config_path, self.__user_config_path)
        else:
            utility.warn('{} not found. Using defaults.\n'.format(self.__user_config_path), {'emphasis': True})

        # pause so you can read the copy warning
        sleep(3)


    def __merge_configs(self):
        """
        Merge the user config with the default config.
        """
        self.__config = {}

        no_detect = self.__args.get('no_detect')
        no_monitor = self.__args.get('no_monitor')
        no_write = self.__args.get('no_write')  or no_monitor
        no_pushover = self.__args.get('no_push') or no_monitor

        # iterate over all of the config groups and merge user config and args with defaults
        for config_group_name, config_group_defaults in self.__default_config.items():
            configuration_found = config_group_name in self.__user_config

            is_video = config_group_name == 'video'
            is_writer = config_group_name == 'writer'
            is_monitor = config_group_name == 'monitor'
            is_pushover = config_group_name == 'pushover'

            # skip if no config provided or if skip requested
            skip_monitor = is_monitor and no_monitor
            skip_write = is_writer and (no_write or not configuration_found)
            skip_push = is_pushover and (no_pushover or not configuration_found)

            # skip everything but video if we're not detecting
            skip_detect = no_detect and not is_video

            # respect cli arg overrides
            if skip_push or skip_write or skip_detect or skip_monitor:
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
