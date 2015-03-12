from fileSystemModule import FileSystemModule
import os.path
from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.tools import raises
from nose.tools import assert_true
from nose.tools import assert_false


# Creates a dir in ~. There wasn't nothing with the same name inside previously


class TestFSModule(object):
    def __init__(self):
        self.homeDir = os.path.expanduser("~")
        self.dirFullPath = None
        self.fileFullPath = None

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
        if self.fileFullPath is not None:
            os.remove(self.fileFullPath)
            self.fileFullPath = None

        if self.dirFullPath is not None:
            import shutil
            shutil.rmtree(self.dirFullPath)
            self.dirFullPath = None

    def test_getFullPath(self):
        """Test for getting the absolute path of out files"""
        fs = FileSystemModule(self.homeDir)
        fullpath = fs.getFullPath(self.homeDir, 'file')
        assert_equal(fullpath, self.homeDir + os.sep + 'file')

    def test_getFullPath2(self):
        """Test for getting the absolute path of out files"""
        fs = FileSystemModule(self.homeDir)
        fullpath = fs.getFullPath(self.homeDir, '/file')
        assert_equal(fullpath, self.homeDir + os.sep + 'file')

    def test_getFullPath3(self):
        """Test for getting the absolute path of out files"""
        fs = FileSystemModule(self.homeDir)
        fullpath = fs.getFullPath(self.homeDir, 'file/')
        assert_equal(fullpath, self.homeDir + os.sep + 'file')

    def test_getFullPath4(self):
        """Test for getting the absolute path of out files"""
        fs = FileSystemModule(self.homeDir)
        fullpath = fs.getFullPath(self.homeDir, self.homeDir + os.sep + 'file')
        assert_equal(fullpath, self.homeDir + os.sep + 'file')

    def test_getFullPath5(self):
        """Test for getting the absolute path of out files"""
        fs = FileSystemModule(self.homeDir)
        fullpath = fs.getFullPath(self.homeDir, self.homeDir + os.sep + '/file')
        assert_equal(fullpath, self.homeDir + os.sep + 'file')

    def test_getFullPath6(self):
        """Test for getting the absolute path of out files"""
        fs = FileSystemModule(self.homeDir)
        fullpath = fs.getFullPath(self.homeDir, self.homeDir + os.sep + 'file/')
        assert_equal(fullpath, self.homeDir + os.sep + 'file')

    def test_getFullPath7(self):
        """Test for getting the absolute path of out files"""
        fs = FileSystemModule(self.homeDir)
        fullpath = fs.getFullPath(None, 'file')
        assert_equal(fullpath, self.homeDir + os.sep + 'file')

    def test_getFullPath8(self):
        """Test for getting the absolute path of out files"""
        fs = FileSystemModule(self.homeDir)
        fullpath = fs.getFullPath(None, self.homeDir + os.sep + 'file')
        assert_equal(fullpath, self.homeDir + os.sep + 'file')

    def test_getFullPath9(self):
        """Test for getting the absolute path of out files"""
        fs = FileSystemModule(self.homeDir)
        fullpath = fs.getFullPath(self.homeDir, None)
        assert_equal(fullpath, self.homeDir)

    def test_getFullPath10(self):
        """Test for getting the absolute path of out files"""
        fs = FileSystemModule(self.homeDir)
        fullpath = fs.getFullPath(None, None)
        assert_equal(fullpath, self.homeDir)

    def test_getFullPath11(self):
        """Test for getting the absolute path of out files"""
        fs = FileSystemModule(self.homeDir)
        fullpath = fs.getFullPath('folder', 'file')
        assert_equal(fullpath, self.homeDir + os.sep + 'folder' + os.sep + 'file')

    def test_getFullPath12(self):
        """Test for getting the absolute path of out files"""
        fs = FileSystemModule(self.homeDir)
        fullpath = fs.getFullPath(None, '/file')
        assert_equal(fullpath, self.homeDir + os.sep + 'file')

    def test_getFullPath13(self):
        """Test for getting the absolute path of out files"""
        fs = FileSystemModule(self.homeDir)
        fullpath = fs.getFullPath('folder', None)
        assert_equal(fullpath, self.homeDir + os.sep + 'folder')

    def test_getFullPath14(self):
        """Test for getting the absolute path of out files"""
        fs = FileSystemModule(self.homeDir)
        fullpath = fs.getFullPath('folder', self.homeDir + os.sep + 'file')
        assert_equal(fullpath, self.homeDir + os.sep + 'file')

    def test_getFullPath15(self):
        """Test for getting the absolute path of out files"""
        from sys import platform as _platform
        if _platform != "win32":
            return
        fs = FileSystemModule(self.homeDir)
        fullpath = fs.getFullPath('folder', 'E:/file')
        assert_equal(fullpath, self.homeDir + os.sep + 'folder' + os.sep + 'file')

    def test_getFullPath16(self):
        """Test for getting the absolute path of out files"""
        from sys import platform as _platform
        if _platform != "win32":
            return
        fs = FileSystemModule(self.homeDir)
        fullpath = fs.getFullPath('folder', 'E:\\file')
        assert_equal(fullpath, self.homeDir + os.sep + 'folder' + os.sep + 'file')

    def test_getFullPath17(self):
        """Test for getting the absolute path of out files"""
        from sys import platform as _platform
        if _platform != "win32":
            return
        fs = FileSystemModule(self.homeDir)
        fullpath = fs.getFullPath('folder', 'C:/file')
        assert_equal(fullpath, self.homeDir + os.sep + 'folder' + os.sep + 'file')

    def test_createDirInHomeDir(self, dirName="testDirectory"):
        """Test to create a directory in the default (home) directory"""
        fs = FileSystemModule(self.homeDir)
        self.dirFullPath = fullpath = fs.createDirectory(dirName)
        assert_true(os.path.isdir(fullpath))

    def test_existingDirInHomeDir(self):
        """Test to create a directory in the default (home) directory
        when it exists already"""
        dirName = "testDirectory"
        self.test_createDirInHomeDir(dirName)
        fs = FileSystemModule(self.homeDir)
        self.dirFullPath = fullpath = fs.createDirectory(dirName)
        assert_true(os.path.isdir(fullpath))

    @raises(PermissionError)
    def test_createDirNotAllowed(self):
        """Test to create a directory in a disallowed path. Raises exception"""
        #TODO: Hacer una carpeta que de verdad no esté permitida (C:\Windows puede tener permisos...)
        from sys import platform as _platform
        if _platform == "linux" or _platform == "linux2":
            path = "/root/"
        elif _platform == "darwin":
            path = "/root/"
            #whatever...
        elif _platform == "win32":
            path = "C:/Windows"

        fs = FileSystemModule(path)
        fs.createDirectory("notAllowed")

    def test_createSeveralDirs(self):
        """Test to create several directory in different deepness in
        the default (home) directory"""
        dirName = "testDirectory/level1/level2/level3"
        fs = FileSystemModule(self.homeDir)
        self.dirFullPath = fullpath = fs.createDirectory(dirName)
        assert_true(os.path.isdir(fullpath))

    def test_removeDirectory(self):
        """Test to remove an existing empty directory in
        the default (home) directory"""
        dirName = "toRemove"
        fs = FileSystemModule(self.homeDir)
        self.dirFullPath = fs.createDirectory(dirName)
        fs.remove(dirName)
        assert_false(os.path.exists(self.dirFullPath))
        self.dirFullPath = None

    def test_removeFilledDirectory(self):
        """Test to remove an existing NOT empty directory in
        the default (home) directory"""
        dirName = "toRemove/otherThings"
        fs = FileSystemModule(self.homeDir)
        self.dirFullPath = fs.createDirectory(dirName)
        fs.remove("toRemove")
        assert_false(os.path.exists(self.dirFullPath))
        self.dirFullPath = None

    def test_createFile(self):
        """Test to create a file in
        the default (home) directory"""
        fs = FileSystemModule(self.homeDir)
        # we use the current file to get a file to write
        stream = open(os.path.realpath(__file__), 'rb')
        filePath = 'testFile'
        self.fileFullPath = fs.createFile(filePath, stream)
        assert_true(os.path.isfile(self.fileFullPath))
        stream.close()

    def test_createFileWithPath(self):
        """Test to create a file in a subfolder in
        the default (home) directory"""
        fs = FileSystemModule(self.homeDir)
        stream = open(os.path.realpath(__file__), 'rb')
        filePath = 'dir1/dir2/testFile'

        self.fileFullPath = fs.createFile(filePath, stream)
        self.dirFullPath = fs.getFullPath(name="dir1")
        assert_true(os.path.isdir(self.dirFullPath))
        assert_true(os.path.isfile(self.fileFullPath))
        stream.close()

    def test_removeFile(self):
        """Test to remove an existing file in
        the default (home) directory"""
        self.test_createFile()
        fs = FileSystemModule(self.homeDir)
        fs.remove(self.fileFullPath)
        assert_false(os.path.isfile(self.fileFullPath))
        self.fileFullPath = None

    def test_removeNonExistingFile(self):
        fs = FileSystemModule(self.homeDir)
        fs.remove('nonExisting')
        noExPath = fs.getFullPath('nonExisting')
        assert_false(os.path.isfile(noExPath))
