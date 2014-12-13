import os.path
import os
from log import Logger


class FileSystemModule():
    """docstring for FileSystemModule"""
    def __init__(self, path):
        self.logger = Logger(__name__)
        self.logger.info("Creating FileSystemModule")

        self.main_path = path
        self.logger.debug("self.main_path = <" + self.main_path + ">")

        try:
            if not os.path.isdir(self.main_path):
                os.makedirs(self.main_path, exist_ok=True)
        except:
            self.logger.debug("error when trying to create folder " + self.main_path + "trying with homeDir")
            self.main_path = self.getFullPath(self.getHomeDir(), self.main_path.split("/")[-1])

    def createDirectory(self, dir_path):
        fullpath = self.getFullPath(self.main_path, dir_path)
        self.logger.debug("Creating directory <" + fullpath + ">")
        os.makedirs(fullpath, exist_ok=True)
        return fullpath

    def createFile(self, file_path, stream):
        self.logger.debug("Creating file <" + file_path + ">")
        fullpath = self.getFullPath(self.main_path, file_path)
        self.logger.debug("File fullpath <" + fullpath + ">")
        if "/" in file_path:
            self.createDirectory(os.path.dirname(file_path))
        out = open(fullpath, 'wb')
        out.write(bytes(stream.read()))
        out.close()
        return fullpath

    def removeRecursive(self, path):
        fullpath = self.getFullPath(self.main_path, path)
        self.logger.debug("Removing folder <" + fullpath + ">")
        import shutil
        shutil.rmtree(fullpath)

    def getFullPath(self, path=None, name=None):
        self.logger.debug("GetFullPath Path = <" + str(path) + ">, Name = <" + str(name) + ">")
        if path is None:
            path = self.main_path
        if name is not None:
            path = path.rstrip("/").strip("\\")
            name = name.strip("/").strip("\\")

            path = os.path.join(path, name)

        self.logger.debug("FullPath = <" + str(path) + ">")
        return path

    def getHomeDir(self):
        return os.path.expanduser("~")
