from fileSystemModule import FileSystemModule
import os.path
from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.tools import raises
from nose.tools import assert_true


# Creates a dir in ~. There wasn't nothing with the same name inside previously


class TestFSModule(object):
    def __init__(self):
        self.dirFullPath = None

    @classmethod
    def setup_class(klass):
        """This method is run once for each class before any tests are run"""

    @classmethod
    def teardown_class(klass):
        """This method is run once for each class _after_ all tests are run"""

    def setUp(self):
        """This method is run once before _each_ test method is executed"""

    def teardown(self):
        """This method is run once after _each_ test method is executed"""
        if self.dirFullPath is not None:
            import shutil
            shutil.rmtree(self.dirFullPath)
            self.dirFullPath = None

    def test_createDirInHomeDir(self, dirName="testDirectory"):
        """Test to create a directory in the default (home) directory"""
        fs = FileSystemModule()
        fs.createDirectory(dirName)
        self.dirFullPath = fullpath = fs.getFullPath(fs.getHomeDir(), dirName)
        assert_true(os.path.isdir(fullpath))

    def test_existingDirInHomeDir(self):
        """Test to create a directory in the default (home) directory
        when it exists already"""
        dirName = "testDirectory"
        self.test_createDirInHomeDir(dirName)
        fs = FileSystemModule()
        fs.createDirectory(dirName)
        self.dirFullPath = fullpath = fs.getFullPath(fs.getHomeDir(), dirName)
        assert_true(os.path.isdir(fullpath))

    @raises(PermissionError)
    def test_createDirNotAllowed(self):
        """Test to create a directory in a disallowed path. Raises exception"""
        from sys import platform as _platform
        if _platform == "linux" or _platform == "linux2":
            path = "/root/"
        elif _platform == "darwin":
            path = "/root/"
            #whatever...
        elif _platform == "win32":
            path = "C:/Windows"

        fs = FileSystemModule()
        fs.createDirectory("notAllowed", path)
