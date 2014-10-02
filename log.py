import logging
import os
import json
import logging.config

default_config_file = "log.json"


class Logger(object):
    """docstring for Logger"""
    def __init__(self, name):
        if os.path.exists(default_config_file):
            with open(default_config_file, 'rt') as f:
                config = json.load(f)
            logging.config.dictConfig(config)

        else:
            logging.basicConfig(level=logging.DEBUG)

        self.logger = logging.getLogger(name)

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
