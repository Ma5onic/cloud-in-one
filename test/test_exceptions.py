import manager
from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.tools import raises
from nose.tools import assert_true
from nose.tools import assert_false
import datetime
from util import *
from fileSystemModule import FileSystemModuleStub

flag = False





class TestExceptions(object):
    def __init__(self):
        self.config_default = {"sync_folder_name": "./test/sync_folder", "database": ":memory:"}
        self.man = None

    @classmethod
    def setup_class(klass):
        """This method is run once for each class before any tests are run"""

    @classmethod
    def teardown_class(klass):
        """This method is run once for each class _after_ all tests are run"""

    def setUp(self):
        """This method is run once before _each_ test method is executed"""
        self.man = manager.Manager('user', 'password', self.config_default)
        self.man.fileSystemModule = FileSystemModuleStub()

    def teardown(self):
        """This method is run once after _each_ test method is executed"""
        for i in self.man.database.tables:
            self.man.database[i].drop()

        self.man = None

    def test_delete_not_found(self):
        self.man.newAccount('dropbox_stub', 'user')
        filename = 'test_file.txt'
        self.man.fileSystemModule.createFile(filename)  # create a file
        self.man.updateLocalSyncFolder()
        self.man.cuentas[0].resetChanges()

        self.man.fileSystemModule.remove(filename)  # we delete file the file locally

        self.man.cuentas[0].deleteFile(filename)  # we delete it remotely
        self.man.findRemoteChanges = returnEmptyList  # but we don't get the deletion

        # this raises FileNotFoundError internally

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()

        expected_fileList = []
        expected_DBFiles = []
        expected_remoteFileList_0 = []

        assert_equal(fileList, expected_fileList)
        assert_equal(remoteFileList_0, expected_remoteFileList_0)
        compareChangeLists(DBFiles, expected_DBFiles)

    def test_retry_upload(self):
        self.man.newAccount('dropbox_stub', 'user')
        filename = 'test_file.txt'
        self.man.fileSystemModule.createFile(filename)  # create a file
        self.man.updateLocalSyncFolder()
        self.man.cuentas[0].resetChanges()

        self.man.fileSystemModule.remove(filename)  # we delete file the file locally

        self.man.cuentas[0].deleteFile = raise_Retry_first_decorator(self.man.cuentas[0].deleteFile)

        # We receive a RetryException and retry the last action

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()

        expected_fileList = []
        expected_DBFiles = []
        expected_remoteFileList_0 = []

        assert_equal(fileList, expected_fileList)
        assert_equal(remoteFileList_0, expected_remoteFileList_0)
        compareChangeLists(DBFiles, expected_DBFiles)
