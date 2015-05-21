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

        self.man.cuentas[0].deleteFile = raise_first_decorator(self.man.cuentas[0].deleteFile, RetryException)

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

    def test_rename_not_found(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.newAccount('dropbox_stub', 'user2')
        filename = 'test_file.txt'
        self.man.fileSystemModule.createFile(filename)  # create a file
        self.man.cuentas[0].uploadFile(filename)  # file uploaded
        self.man.cuentas[1].uploadFile(filename)  # file uploaded in both accounts

        # This simulates deleting a file just before trying to rename it
        self.man.cuentas[0].renameFile = pre_execute_decorator(lambda: self.man.cuentas[0].deleteFile(filename), self.man.cuentas[0].renameFile)

        self.man.updateLocalSyncFolder()  # this conflicts

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()
        remoteFileList_1 = self.man.cuentas[1].getFileList()

        date = datetime.date.today()
        expected_fileList = [filename + '__CONFLICTED_COPY__' + date.isoformat(), filename]
        expected_DBFiles = [{'path': filename + '__CONFLICTED_COPY__' + date.isoformat(), 'hash': filename, 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user},
                            {'path': filename, 'hash': filename, 'account': self.man.cuentas[1].getAccountType(), 'user': self.man.cuentas[1].user}]
        expected_remoteFileList_0 = [filename + '__CONFLICTED_COPY__' + date.isoformat()]
        expected_remoteFileList_1 = [filename]

        assert_equal(fileList, expected_fileList)
        assert_equal(remoteFileList_0, expected_remoteFileList_0)
        assert_equal(remoteFileList_1, expected_remoteFileList_1)
        compareChangeLists(DBFiles, expected_DBFiles)
