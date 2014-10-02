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

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warn(self, msg):
        self.logger.warn(msg)

    def error(self, msg):
        self.logger.error(msg)

    def exception(self, msg):
        self.logger.error(msg, exc_info=True)

    def critical(self, msg):
        self.logger.critical(msg)
