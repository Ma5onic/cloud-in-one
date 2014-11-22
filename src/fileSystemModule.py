import os.path
import os
from log import Logger


class FileSystemModule():
    """docstring for FileSystemModule"""
    def __init__(self):
        self.logger = Logger(__name__)
        self.logger.info("Creating FileSystemModule")

    def createDirectory(self, dirname, path=None):
        self.logger.info("Creating directory " + dirname)
        if path is None:
            path = self.getHomeDir()
            self.logger.debug("path is None, using ~: <" + path + ">")

        fullpath = self.getFullPath(path, dirname)
        self.logger.debug("Creating directory <" + fullpath + ">")
        os.makedirs(fullpath, exist_ok=True)
        return fullpath

    def getFullPath(self, path, name):
        self.logger.debug("GetFullPath Path = <" + path + ">, Name = <" + name + ">")
        path = path.strip("/").strip("\\")
        name = name.strip("/").strip("\\")

        path = os.path.join(path, name)
        self.logger.debug(path)
        return path

    def getHomeDir(self):
        return os.path.expanduser("~")
