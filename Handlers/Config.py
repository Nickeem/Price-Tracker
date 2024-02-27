import json
import os


class Config:

    required_config_variables = ('database_port', 'database_host')

    def __init__(self, config_file):
        if not os.path.isfile(config_file):
            raise Exception(f'Path does not exist: {config_file}')

        with open('config.json') as file:
            self.CONFIG = json.load(file)

        if not self.__validate_config_requirements():
            raise Exception('All config parameters not specified')

    def __validate_config_requirements(self) -> bool:
        # check for necessary configuration variables

        if all(key not in self.CONFIG for key in self.required_config_variables):
            return False
        return True

    def get_database_host(self):
        return self.CONFIG['database_host']

    def get_database_port(self):
        return self.CONFIG['database_port']