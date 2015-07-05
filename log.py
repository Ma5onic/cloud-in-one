import logging
import os
import json
import logging.config

default_config_file = "config/config.json"


class Logger(object):
    """docstring for Logger"""
    def __init__(self, name):
        if os.path.exists(default_config_file):
            with open(default_config_file, 'rt') as f:
                config = json.load(f)
            log_config = config['log_config']
            os.makedirs(os.path.join(log_config['folder']), exist_ok=True)
            logging.config.dictConfig(log_config)

        else:
            logging.basicConfig(level=logging.DEBUG)

        self.logger = logging.getLogger(name)
        self.logger.info("Creating logger")

    def debug(self, *args):
        self.logger.debug(*args)

    def info(self, *args):
        self.logger.info(*args)

    def warn(self, *args):
        self.logger.warn(*args)

    def error(self, *args):
        self.logger.error(*args)

    def exception(self, *args):
        self.logger.error(*args, exc_info=True)

    def critical(self, *args):
        self.logger.critical(*args)
