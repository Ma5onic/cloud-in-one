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
from securityModule import SecurityModuleStub


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
        self.man = manager.Manager('user', 'password', config=self.config_default)
        self.man.fileSystemModule = FileSystemModuleStub()
        self.man.securityModule = SecurityModuleStub()

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

    def test_getFile_not_found(self):
        self.man.newAccount('dropbox_stub', 'user')
        filename = 'test_file.txt'
        self.man.cuentas[0].uploadFile(filename)  # file uploaded

        # This simulates deleting a file just before trying to get it
        self.man.cuentas[0].getFile = pre_execute_decorator(lambda: self.man.cuentas[0].deleteFile(filename), self.man.cuentas[0].getFile)

        self.man.updateLocalSyncFolder()  # this conflicts

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()

        expected_fileList = []
        expected_DBFiles = []
        expected_remoteFileList_0 = []

        assert_equal(fileList, expected_fileList)
        assert_equal(remoteFileList_0, expected_remoteFileList_0)
        compareChangeLists(DBFiles, expected_DBFiles)

    def test_delta_first_unknown(self):
        self.man.newAccount('dropbox_stub', 'user')
        filename = 'test_file.txt'
        self.man.cuentas[0].uploadFile(filename)  # file uploaded

        self.man.cuentas[0].delta = raise_first_decorator(self.man.cuentas[0].delta, UnknownError)

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()

        expected_fileList = [filename]
        expected_DBFiles = [{'path': filename, 'hash': filename, 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}]
        expected_remoteFileList_0 = [filename]

        assert_equal(fileList, expected_fileList)
        assert_equal(remoteFileList_0, expected_remoteFileList_0)
        compareChangeLists(DBFiles, expected_DBFiles)

    def test_delta_always_raise(self):
        self.man.newAccount('dropbox_stub', 'user')
        filename = 'test_file.txt'
        self.man.cuentas[0].uploadFile(filename)  # file uploaded

        self.man.cuentas[0].delta = raise_always_decorator(UnknownError)

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()

        expected_fileList = []
        expected_DBFiles = []
        expected_remoteFileList_0 = [filename]

        assert_equal(fileList, expected_fileList)
        assert_equal(remoteFileList_0, expected_remoteFileList_0)
        compareChangeLists(DBFiles, expected_DBFiles)

    def test_delta_always_raise_local_changes(self):
        self.man.newAccount('dropbox_stub', 'user')
        filename = 'test_file.txt'
        filename_local = filename + '_local'
        self.man.fileSystemModule.createFile(filename_local)  # create a file
        self.man.cuentas[0].uploadFile(filename)  # file uploaded

        self.man.cuentas[0].delta = raise_always_decorator(UnknownError)

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()

        expected_fileList = [filename_local]
        expected_DBFiles = [{'path': filename_local, 'hash': filename_local, 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}]
        expected_remoteFileList_0 = [filename, filename_local]

        assert_equal(fileList, expected_fileList)
        assert_equal(remoteFileList_0, expected_remoteFileList_0)
        compareChangeLists(DBFiles, expected_DBFiles)

    def test_delta_always_raise_local_changes_two_accounts(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.newAccount('dropbox_stub', 'user2')
        filename = 'test_file.txt'
        filename_local = filename + '_local'
        filename_remote = filename + '_remote'
        self.man.fileSystemModule.createFile(filename_local)  # create a file
        self.man.cuentas[0].uploadFile(filename)  # file uploaded
        self.man.cuentas[1].uploadFile(filename_remote)  # file uploaded

        self.man.cuentas[0].delta = raise_always_decorator(UnknownError)

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()
        remoteFileList_1 = self.man.cuentas[1].getFileList()

        expected_fileList = [filename_local, filename_remote]
        expected_DBFiles = [{'path': filename_local, 'hash': filename_local, 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user},
                            {'path': filename_remote, 'hash': filename_remote, 'account': self.man.cuentas[1].getAccountType(), 'user': self.man.cuentas[1].user}]
        expected_remoteFileList_0 = [filename, filename_local]
        expected_remoteFileList_1 = [filename_remote]

        assert_equal(fileList, expected_fileList)
        assert_equal(remoteFileList_0, expected_remoteFileList_0)
        assert_equal(remoteFileList_1, expected_remoteFileList_1)
        compareChangeLists(DBFiles, expected_DBFiles)

    def test_two_accounts_one_useless(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.newAccount('dropbox_stub', 'user2')
        filename = 'test_file.txt'
        filename_local = filename + '_local'
        filename_remote = filename + '_remote'
        self.man.fileSystemModule.createFile(filename_local)  # create a file
        self.man.cuentas[0].uploadFile(filename)  # file uploaded
        self.man.cuentas[1].uploadFile(filename_remote)  # file uploaded

        # The first account will always throw exception
        self.man.cuentas[0].delta = raise_always_decorator(UnknownError)
        self.man.cuentas[0].uploadFile = raise_always_decorator(UnknownError)
        self.man.cuentas[0].getFile = raise_always_decorator(UnknownError)
        self.man.cuentas[0].updateAccountInfo = raise_always_decorator(UnknownError)
        self.man.cuentas[0].deleteFile = raise_always_decorator(UnknownError)
        self.man.cuentas[0].renameFile = raise_always_decorator(UnknownError)

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()
        remoteFileList_1 = self.man.cuentas[1].getFileList()

        expected_fileList = [filename_local, filename_remote]
        expected_DBFiles = [{'path': filename_local, 'hash': filename_local, 'account': self.man.cuentas[1].getAccountType(), 'user': self.man.cuentas[1].user},
                            {'path': filename_remote, 'hash': filename_remote, 'account': self.man.cuentas[1].getAccountType(), 'user': self.man.cuentas[1].user}]
        expected_remoteFileList_0 = [filename]
        expected_remoteFileList_1 = [filename_remote, filename_local]

        assert_equal(fileList, expected_fileList)
        assert_equal(remoteFileList_0, expected_remoteFileList_0)
        assert_equal(remoteFileList_1, expected_remoteFileList_1)
        compareChangeLists(DBFiles, expected_DBFiles)

    def test_two_accounts_delete_exception(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.newAccount('dropbox_stub', 'user2')
        filename = 'test_file.txt'
        filename_local = filename + '_local'
        filename_remote = filename + '_remote'
        self.man.fileSystemModule.createFile(filename_local)  # create a file
        self.man.cuentas[0].uploadFile(filename)  # file uploaded
        self.man.cuentas[1].uploadFile(filename_remote)  # file uploaded
        self.man.updateLocalSyncFolder()

        self.man.fileSystemModule.remove(filename_local)

        # The first account will always throw exception
        self.man.cuentas[0].delta = raise_always_decorator(UnknownError)
        self.man.cuentas[0].uploadFile = raise_always_decorator(UnknownError)
        self.man.cuentas[0].getFile = raise_always_decorator(UnknownError)
        self.man.cuentas[0].updateAccountInfo = raise_always_decorator(UnknownError)
        self.man.cuentas[0].deleteFile = raise_always_decorator(UnknownError)
        self.man.cuentas[0].renameFile = raise_always_decorator(UnknownError)

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()
        remoteFileList_1 = self.man.cuentas[1].getFileList()

        expected_fileList = [filename, filename_remote]
        expected_DBFiles = [{'path': filename_local, 'hash': filename_local, 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user},
                            {'path': filename, 'hash': filename, 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user},
                            {'path': filename_remote, 'hash': filename_remote, 'account': self.man.cuentas[1].getAccountType(), 'user': self.man.cuentas[1].user}]
        expected_remoteFileList_0 = [filename, filename_local]
        expected_remoteFileList_1 = [filename_remote]

        assert_equal(fileList, expected_fileList)
        assert_equal(remoteFileList_0, expected_remoteFileList_0)
        assert_equal(remoteFileList_1, expected_remoteFileList_1)
        compareChangeLists(DBFiles, expected_DBFiles)

    def test_two_accounts_two_useless(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.newAccount('dropbox_stub', 'user2')
        filename = 'test_file.txt'
        filename_local = filename + '_local'
        filename_remote = filename + '_remote'
        self.man.fileSystemModule.createFile(filename_local)  # create a file
        self.man.cuentas[0].uploadFile(filename)  # file uploaded
        self.man.cuentas[1].uploadFile(filename_remote)  # file uploaded

        # The first account will always throw exception
        self.man.cuentas[0].delta = raise_always_decorator(UnknownError)
        self.man.cuentas[0].uploadFile = raise_always_decorator(UnknownError)
        self.man.cuentas[0].getFile = raise_always_decorator(UnknownError)
        self.man.cuentas[0].updateAccountInfo = raise_always_decorator(UnknownError)
        self.man.cuentas[0].deleteFile = raise_always_decorator(UnknownError)
        self.man.cuentas[0].renameFile = raise_always_decorator(UnknownError)

        # The second too
        self.man.cuentas[1].delta = raise_always_decorator(UnknownError)
        self.man.cuentas[1].uploadFile = raise_always_decorator(UnknownError)
        self.man.cuentas[1].getFile = raise_always_decorator(UnknownError)
        self.man.cuentas[1].updateAccountInfo = raise_always_decorator(UnknownError)
        self.man.cuentas[1].deleteFile = raise_always_decorator(UnknownError)
        self.man.cuentas[1].renameFile = raise_always_decorator(UnknownError)

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()
        remoteFileList_1 = self.man.cuentas[1].getFileList()

        expected_fileList = [filename_local]
        expected_DBFiles = []
        expected_remoteFileList_0 = [filename]
        expected_remoteFileList_1 = [filename_remote]

        assert_equal(fileList, expected_fileList)
        assert_equal(remoteFileList_0, expected_remoteFileList_0)
        assert_equal(remoteFileList_1, expected_remoteFileList_1)
        compareChangeLists(DBFiles, expected_DBFiles)
