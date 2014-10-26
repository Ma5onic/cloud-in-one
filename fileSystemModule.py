import os.path
import os


class FileSystemModule():
    """docstring for FileSystemModule"""
    def __init__(self):
        pass

    def createDirectory(self, dirname, path=None):
        if path is None:
            path = self.getHomeDir()

        fullpath = self.getFullPath(path, dirname)
        os.makedirs(fullpath, exist_ok=True)
        return True

    def getFullPath(self, path, name):
        return os.path.join(path, name)

    def getHomeDir(self):
        return os.path.expanduser("~")
