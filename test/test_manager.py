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


class TestManager(object):
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
        for i in self.man.databaseManager.database.tables:
            self.man.databaseManager.database[i].drop()

        self.man = None

    def test_manager(self):
        assert_true(self.man)

    def test_newAccount_dropbox(self):
        self.man.newAccount('dropbox_stub', 'user')
        assert_true(self.man.cuentas)

        accounts_table = self.man.databaseManager.database['accounts']
        assert_true(list(accounts_table.all()))

    def test_deleteAccount(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.deleteAccount(self.man.cuentas[0])
        assert_false(self.man.cuentas)
        files_table = self.man.databaseManager.database['files']
        assert_false(list(files_table.all()))
        accounts_table = self.man.databaseManager.database['accounts']
        assert_false(list(accounts_table.all()))

    @Ignore
    def test_deleteAccountAndFiles(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.saveFile({'account': self.man.cuentas[0], 'path': 'testPath', 'hash': 'hash', 'revision': 'revision_number', 'size': len('testPath')})
        self.man.deleteAccount(self.man.cuentas[0])
        assert_false(self.man.cuentas)

        # TODO: should be deleted??
        files_table = self.man.databaseManager.database['files']
        assert_false(list(files_table.all()))
        accounts_table = self.man.databaseManager.database['accounts']
        assert_false(list(accounts_table.all()))

    def test_integrationSync(self):
        self.man.newAccount('dropbox_stub', 'user')

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = []
        expected_DBFiles = []
        expected_remoteFileList = []

        assert_equal(fileList, expected_fileList)
        compareChangeLists(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_integrationSync_2(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = ['/test/muerte.txt']
        expected_DBFiles = [{'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}]
        expected_remoteFileList = ['/test/muerte.txt']

        assert_equal(fileList, expected_fileList)
        compareChangeLists(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_integrationSync_3(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # we had a file uploaded

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = ['/test/muerte.txt']
        expected_DBFiles = [{'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}]
        expected_remoteFileList = ['/test/muerte.txt']

        assert_equal(fileList, expected_fileList)
        compareChangeLists(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_integrationSync_4(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # we had a file uploaded

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        date = datetime.date.today()
        expected_fileList = ['/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), '/test/muerte.txt']
        expected_DBFiles = [{'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}, {'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}]
        expected_remoteFileList = ['/test/muerte.txt', '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat()]

        assert_equal(fileList, expected_fileList)
        compareChangeLists(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_integrationSync_5(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file
        self.man.cuentas[0].uploadFile('/test/muerte2.txt')  # we had a file uploaded

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = ['/test/muerte.txt', '/test/muerte2.txt']
        expected_DBFiles = [{'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}, {'path': '/test/muerte2.txt', 'hash': '/test/muerte2.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}]
        expected_remoteFileList = ['/test/muerte2.txt', '/test/muerte.txt']

        assert_equal(fileList, expected_fileList)
        compareChangeLists(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_integrationSync_6(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file
        self.man.saveFile({'account': self.man.cuentas[0], 'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'revision': 'revision_number', 'size': len('/test/muerte.txt')})
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # we had a file uploaded
        self.man.cuentas[0].resetChanges()
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # "modify" it

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user'], 'revision': i['revision']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = ['/test/muerte.txt']
        expected_DBFiles = [{'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user, 'revision': 'revision_number'}]
        expected_remoteFileList = ['/test/muerte.txt']

        assert_equal(fileList, expected_fileList)
        compareChangeLists(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_integrationSync_7(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file
        self.man.saveFile({'account': self.man.cuentas[0], 'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'revision': 'revision_number', 'size': len('/test/muerte.txt')})
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # we had a file uploaded
        self.man.cuentas[0].resetChanges()
        self.man.cuentas[0].deleteFile('/test/muerte.txt')  # delete it

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = []
        expected_DBFiles = []
        expected_remoteFileList = []

        assert_equal(fileList, expected_fileList)
        compareChangeLists(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_integrationSync_8(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/test/muerte2.txt')  # create a file
        self.man.saveFile({'account': self.man.cuentas[0], 'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'revision': 'revision_number', 'size': len('/test/muerte.txt')})
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # we had a file uploaded
        self.man.cuentas[0].resetChanges()
        self.man.fileSystemModule.renameFile('/test/muerte2.txt', '/test/muerte.txt')  # we modify it locally

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user'], 'revision': i['revision']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = ['/test/muerte.txt']
        expected_DBFiles = [{'path': '/test/muerte.txt', 'hash': '/test/muerte2.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user, 'revision': 'revision_number1'}]
        expected_remoteFileList = ['/test/muerte.txt']

        assert_equal(fileList, expected_fileList)
        compareChangeLists(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_integrationSync_9(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/test/muerte2.txt')  # create a file
        self.man.saveFile({'account': self.man.cuentas[0], 'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'revision': 'revision_number', 'size': len('/test/muerte.txt')})
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # we had a file uploaded
        self.man.cuentas[0].resetChanges()
        self.man.fileSystemModule.renameFile('/test/muerte2.txt', '/test/muerte.txt')  # we modify it locally
        self.man.cuentas[0].deleteFile('/test/muerte.txt')  # delete it

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user'], 'revision': i['revision']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = ['/test/muerte.txt']
        expected_DBFiles = [{'path': '/test/muerte.txt', 'hash': '/test/muerte2.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user, 'revision': 'revision_number1'}]
        expected_remoteFileList = ['/test/muerte.txt']

        assert_equal(fileList, expected_fileList)
        compareChangeLists(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_integrationSync_10(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file
        self.man.saveFile({'account': self.man.cuentas[0], 'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'revision': 'revision_number', 'size': len('/test/muerte.txt')})
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # we had a file uploaded
        self.man.cuentas[0].resetChanges()
        self.man.fileSystemModule.remove('/test/muerte.txt')  # delete it

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = []
        expected_DBFiles = []
        expected_remoteFileList = []

        assert_equal(fileList, expected_fileList)
        compareChangeLists(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_integrationSync_11(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file
        self.man.saveFile({'account': self.man.cuentas[0], 'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'revision': 'revision_number', 'size': len('/test/muerte.txt')})
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # we had a file uploaded
        self.man.cuentas[0].resetChanges()
        self.man.fileSystemModule.remove('/test/muerte.txt')  # delete it
        self.man.cuentas[0].deleteFile('/test/muerte.txt')  # delete it

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = []
        expected_DBFiles = []
        expected_remoteFileList = []

        assert_equal(fileList, expected_fileList)
        compareChangeLists(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_integrationSync_12(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file
        self.man.cuentas[0].uploadFile('/test/muerte.txt', '1')  # we had a file uploaded

        self.man.updateLocalSyncFolder()  # this conflicts

        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file
        self.man.cuentas[0].uploadFile('/test/muerte.txt', '2')  # we had a file uploaded

        self.man.updateLocalSyncFolder()  # this conflicts again, and the name is already taken

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        date = datetime.date.today()
        expected_fileList = ['/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat() + '_1', '/test/muerte.txt']
        expected_DBFiles = [{'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}, {'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}, {'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat() + '_1', 'hash': 'modified', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}]
        expected_remoteFileList = ['/test/muerte.txt', '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat() + '_1']

        assert_equal(sorted(fileList), sorted(expected_fileList))
        compareChangeLists(DBFiles, expected_DBFiles)
        assert_equal(sorted(remoteFileList), sorted(expected_remoteFileList))

    def test_integrationSync_two_accounts(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.newAccount('dropbox_stub', 'user2')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # file uploaded
        self.man.cuentas[1].uploadFile('/test/muerte.txt')  # file uploaded in both accounts

        self.man.updateLocalSyncFolder()  # this conflicts

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()
        remoteFileList_1 = self.man.cuentas[1].getFileList()

        date = datetime.date.today()
        expected_fileList = ['/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), '/test/muerte.txt', '/test/muerte.txt__CONFLICTED_COPY__FROM_' + str(self.man.cuentas[0]) + '_' + date.isoformat()]
        expected_DBFiles = [{'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}, {'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[1].getAccountType(), 'user': self.man.cuentas[1].user}, {'path': '/test/muerte.txt__CONFLICTED_COPY__FROM_' + str(self.man.cuentas[0]) + '_' + date.isoformat(), 'hash': '/test/muerte.txt__CONFLICTED_COPY__FROM_' + str(self.man.cuentas[0]) + '_' + date.isoformat(), 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}]
        expected_remoteFileList_0 = ['/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), '/test/muerte.txt__CONFLICTED_COPY__FROM_' + str(self.man.cuentas[0]) + '_' + date.isoformat()]
        expected_remoteFileList_1 = ['/test/muerte.txt']

        assert_equal(sorted(fileList), sorted(expected_fileList))
        compareChangeLists(DBFiles, expected_DBFiles)
        assert_equal(sorted(remoteFileList_0), sorted(expected_remoteFileList_0))
        assert_equal(sorted(remoteFileList_1), sorted(expected_remoteFileList_1))

    def test_integrationSync_three_accounts(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.newAccount('dropbox_stub', 'user2')
        self.man.newAccount('dropbox_stub', 'user3')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # file uploaded in all accounts
        self.man.cuentas[1].uploadFile('/test/muerte.txt')  # file uploaded in all accounts
        self.man.cuentas[2].uploadFile('/test/muerte.txt')  # file uploaded in all accounts

        self.man.updateLocalSyncFolder()  # this conflicts

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()
        remoteFileList_1 = self.man.cuentas[1].getFileList()
        remoteFileList_2 = self.man.cuentas[2].getFileList()

        date = datetime.date.today()
        expected_fileList = ['/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), '/test/muerte.txt', '/test/muerte.txt__CONFLICTED_COPY__FROM_' + str(self.man.cuentas[1]) + '_' + date.isoformat(), '/test/muerte.txt__CONFLICTED_COPY__FROM_' + str(self.man.cuentas[0]) + '_' + date.isoformat()]
        expected_DBFiles = [{'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}, {'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[2].getAccountType(), 'user': self.man.cuentas[2].user}, {'path': '/test/muerte.txt__CONFLICTED_COPY__FROM_' + str(self.man.cuentas[0]) + '_' + date.isoformat(), 'hash': '/test/muerte.txt__CONFLICTED_COPY__FROM_' + str(self.man.cuentas[0]) + '_' + date.isoformat(), 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}, {'path': '/test/muerte.txt__CONFLICTED_COPY__FROM_' + str(self.man.cuentas[1]) + '_' + date.isoformat(), 'hash': '/test/muerte.txt__CONFLICTED_COPY__FROM_' + str(self.man.cuentas[1]) + '_' + date.isoformat(), 'account': self.man.cuentas[1].getAccountType(), 'user': self.man.cuentas[1].user}]
        expected_remoteFileList_0 = ['/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), '/test/muerte.txt__CONFLICTED_COPY__FROM_' + str(self.man.cuentas[0]) + '_' + date.isoformat()]
        expected_remoteFileList_1 = ['/test/muerte.txt__CONFLICTED_COPY__FROM_' + str(self.man.cuentas[1]) + '_' + date.isoformat()]
        expected_remoteFileList_2 = ['/test/muerte.txt']

        assert_equal(sorted(fileList), sorted(expected_fileList))
        compareChangeLists(DBFiles, expected_DBFiles)
        assert_equal(sorted(remoteFileList_0), sorted(expected_remoteFileList_0))
        assert_equal(sorted(remoteFileList_1), sorted(expected_remoteFileList_1))
        assert_equal(sorted(remoteFileList_2), sorted(expected_remoteFileList_2))

    def test_twoAccounts_fits_first(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.newAccount('dropbox_stub', 'user2')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList1 = self.man.cuentas[0].getFileList()
        remoteFileList2 = self.man.cuentas[1].getFileList()

        expected_fileList = ['/test/muerte.txt']
        expected_DBFiles = [{'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}]
        expected_remoteFileList1 = ['/test/muerte.txt']
        expected_remoteFileList2 = []

        assert_equal(fileList, expected_fileList)
        compareChangeLists(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList1, expected_remoteFileList1)
        assert_equal(remoteFileList2, expected_remoteFileList2)

    def test_twoAccounts_fits_second(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.cuentas[0].fits = returnFalse
        self.man.newAccount('dropbox_stub', 'user2')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList1 = self.man.cuentas[0].getFileList()
        remoteFileList2 = self.man.cuentas[1].getFileList()

        expected_fileList = ['/test/muerte.txt']
        expected_DBFiles = [{'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[1].getAccountType(), 'user': self.man.cuentas[1].user}]
        expected_remoteFileList1 = []
        expected_remoteFileList2 = ['/test/muerte.txt']

        assert_equal(fileList, expected_fileList)
        compareChangeLists(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList1, expected_remoteFileList1)
        assert_equal(remoteFileList2, expected_remoteFileList2)

    def test_twoAccounts_fits_none(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.cuentas[0].fits = returnFalse
        self.man.newAccount('dropbox_stub', 'user2')
        self.man.cuentas[1].fits = returnFalse
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList1 = self.man.cuentas[0].getFileList()
        remoteFileList2 = self.man.cuentas[1].getFileList()

        expected_fileList = ['/test/muerte.txt']
        expected_DBFiles = []
        expected_remoteFileList1 = []
        expected_remoteFileList2 = []

        assert_equal(fileList, expected_fileList)
        compareChangeLists(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList1, expected_remoteFileList1)
        assert_equal(remoteFileList2, expected_remoteFileList2)

    def test_caseName(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/ThisHasUpperCase.txt')  # create a file with uppercases
        self.man.updateLocalSyncFolder()

        self.man.cuentas[0].deleteFile('/ThisHasUpperCase.txt')
        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = []
        expected_DBFiles = []
        expected_remoteFileList = []

        assert_equal(fileList, expected_fileList)
        compareChangeLists(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_fileSize(self):
        self.man.newAccount('dropbox_stub', 'user')
        filename = 'test_file.txt'
        self.man.cuentas[0].free_quota = len(filename)
        self.man.fileSystemModule.createFile(filename)  # create a file with size len(filename)
        self.man.fileSystemModule.createFile(filename + '2')  # create a file with size len(filename) + 1 --> doesn't fit
        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = [filename, filename+'2']
        expected_DBFiles = [{'path': filename, 'hash': filename, 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}]
        expected_remoteFileList = [filename]

        assert_equal(fileList, expected_fileList)
        compareChangeLists(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_fileSize_2(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.newAccount('dropbox_stub', 'user2')
        filename = 'test_file.txt'
        self.man.cuentas[0].free_quota = len(filename)
        self.man.fileSystemModule.createFile(filename)  # create a file with size len(filename)
        self.man.fileSystemModule.createFile(filename + '2')  # create a file with size len(filename) + 1 --> doesn't fit
        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user'], 'size': i['size']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()
        remoteFileList_1 = self.man.cuentas[1].getFileList()

        expected_fileList = [filename, filename+'2']
        expected_DBFiles = [{'path': filename, 'hash': filename, 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user, 'size': len(filename)},
                            {'path': filename+'2', 'hash': filename+'2', 'account': self.man.cuentas[1].getAccountType(), 'user': self.man.cuentas[1].user, 'size': len(filename) + 1}]
        expected_remoteFileList_0 = [filename]
        expected_remoteFileList_1 = [filename+'2']

        assert_equal(fileList, expected_fileList)
        compareChangeLists(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList_0, expected_remoteFileList_0)
        assert_equal(remoteFileList_1, expected_remoteFileList_1)

    def test_fileSize_3(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.newAccount('dropbox_stub', 'user2')
        filename = 'test_file.txt'
        self.man.cuentas[0].free_quota = len(filename)
        self.man.fileSystemModule.createFile(filename)  # create a file with size len(filename)
        self.man.updateLocalSyncFolder()  # upload it...
        self.man.fileSystemModule.createFile(filename)  # modify the file (len + 1)
        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user'], 'size': i['size']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()
        remoteFileList_1 = self.man.cuentas[1].getFileList()

        expected_fileList = [filename]
        expected_DBFiles = [{'path': filename, 'hash': 'modified', 'account': self.man.cuentas[1].getAccountType(), 'user': self.man.cuentas[1].user, 'size': len(filename) + 1}]
        expected_remoteFileList_0 = []
        expected_remoteFileList_1 = [filename]

        assert_equal(fileList, expected_fileList)
        compareChangeLists(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList_0, expected_remoteFileList_0)
        assert_equal(remoteFileList_1, expected_remoteFileList_1)

    def test_fileSize_doesnt_fit(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.newAccount('dropbox_stub', 'user2')
        filename = 'test_file.txt'
        self.man.cuentas[0].free_quota = len(filename)
        self.man.cuentas[1].free_quota = len(filename)
        self.man.fileSystemModule.createFile(filename)  # create a file with size len(filename)
        self.man.updateLocalSyncFolder()  # upload it...
        self.man.fileSystemModule.createFile(filename)  # modify the file (len + 1)
        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user'], 'size': i['size']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()
        remoteFileList_1 = self.man.cuentas[1].getFileList()

        expected_fileList = [filename]
        expected_DBFiles = [{'path': filename, 'hash': filename, 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user, 'size': len(filename)}]
        expected_remoteFileList_0 = [filename]
        expected_remoteFileList_1 = []

        assert_equal(fileList, expected_fileList)
        assert_equal(remoteFileList_0, expected_remoteFileList_0)
        assert_equal(remoteFileList_1, expected_remoteFileList_1)
        compareChangeLists(DBFiles, expected_DBFiles)

    def test_integrationSync_13(self):
        self.man.newAccount('dropbox_stub', 'user')
        filename = 'test_file.txt'
        self.man.fileSystemModule.createFile(filename)  # create a file with size len(filename)
        self.man.updateLocalSyncFolder()  # upload it...
        self.man.fileSystemModule.createFile(filename)  # modify the file (len + 1)
        self.man.cuentas[0].deleteFile(filename)

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user'], 'size': i['size']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()

        expected_fileList = [filename]
        expected_DBFiles = [{'path': filename, 'hash': 'modified', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user, 'size': len(filename) + 1}]
        expected_remoteFileList_0 = [filename]

        assert_equal(fileList, expected_fileList)
        assert_equal(remoteFileList_0, expected_remoteFileList_0)
        compareChangeLists(DBFiles, expected_DBFiles)

    def test_integrationSync_14(self):
        self.man.newAccount('dropbox_stub', 'user')
        filename = 'test_file.txt'
        self.man.fileSystemModule.createFile(filename)  # create a file with size len(filename)
        self.man.updateLocalSyncFolder()  # upload it...
        self.man.cuentas[0].resetChanges()
        self.man.cuentas[0].uploadFile(filename, 'revision_number')
        self.man.fileSystemModule.remove(filename)

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user'], 'size': i['size']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()

        expected_fileList = [filename]
        expected_DBFiles = [{'path': filename, 'hash': filename, 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}]
        expected_remoteFileList_0 = [filename]

        assert_equal(fileList, expected_fileList)
        assert_equal(remoteFileList_0, expected_remoteFileList_0)
        compareChangeLists(DBFiles, expected_DBFiles)

    def test_integrationSync_15(self):
        self.man.newAccount('dropbox_stub', 'user')
        filename = 'test_file.txt'
        self.man.fileSystemModule.createFile(filename)  # create a file with size len(filename)
        self.man.updateLocalSyncFolder()  # upload it...
        self.man.cuentas[0].resetChanges()
        self.man.cuentas[0].deleteFile(filename)
        self.man.fileSystemModule.remove(filename)

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user'], 'size': i['size']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()

        expected_fileList = []
        expected_DBFiles = []
        expected_remoteFileList_0 = []

        assert_equal(fileList, expected_fileList)
        assert_equal(remoteFileList_0, expected_remoteFileList_0)
        compareChangeLists(DBFiles, expected_DBFiles)

    def test_integrationSync_16(self):
        self.man.newAccount('dropbox_stub', 'user')
        filename = 'test_file.txt'
        self.man.fileSystemModule.createFile(filename)  # create a file with size len(filename)
        self.man.updateLocalSyncFolder()  # upload it...
        self.man.cuentas[0].resetChanges()
        self.man.cuentas[0]._delta_reset = True
        self.man.cuentas[0].uploadFile(filename, 'revision_number')
        self.man.fileSystemModule.createFile(filename)  # create a file with size len(filename)

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user'], 'size': i['size']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()

        date = datetime.date.today()
        expected_fileList = [filename + '__CONFLICTED_COPY__' + date.isoformat(), filename]
        expected_DBFiles = [{'path': filename, 'hash': filename, 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user},
                            {'path': filename + '__CONFLICTED_COPY__' + date.isoformat(), 'hash': 'modified', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}]
        expected_remoteFileList_0 = [filename + '__CONFLICTED_COPY__' + date.isoformat(), filename]

        assert_equal(sorted(fileList), sorted(expected_fileList))
        assert_equal(sorted(remoteFileList_0), sorted(expected_remoteFileList_0))
        compareChangeLists(DBFiles, expected_DBFiles)

    def test_remote_collision_two_accounts(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.newAccount('dropbox_stub', 'user2')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file
        self.man.updateLocalSyncFolder()
        self.man.cuentas[0].resetChanges()
        self.man.cuentas[1].resetChanges()
        # We have the file in the first account, fully synchronized

        self.man.cuentas[1].uploadFile('/test/muerte.txt', 'different_revision')  # we upload it to the second one

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()
        remoteFileList_1 = self.man.cuentas[1].getFileList()

        date = datetime.date.today()
        expected_fileList = ['/test/muerte.txt', '/test/muerte.txt__CONFLICTED_COPY__FROM_' + str(self.man.cuentas[1]) + '_' + date.isoformat()]
        expected_DBFiles = [
            {'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user},
            {'path': '/test/muerte.txt__CONFLICTED_COPY__FROM_' + str(self.man.cuentas[1]) + '_' + date.isoformat(), 'hash': '/test/muerte.txt__CONFLICTED_COPY__FROM_' + str(self.man.cuentas[1]) + '_' + date.isoformat(), 'account': self.man.cuentas[1].getAccountType(), 'user': self.man.cuentas[1].user}]
        expected_remoteFileList_0 = ['/test/muerte.txt']
        expected_remoteFileList_1 = ['/test/muerte.txt__CONFLICTED_COPY__FROM_' + str(self.man.cuentas[1]) + '_' + date.isoformat()]

        assert_equal(fileList, expected_fileList)
        assert_equal(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList_0, expected_remoteFileList_0)
        assert_equal(remoteFileList_1, expected_remoteFileList_1)

    def test_remote_collision_two_accounts_case(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.newAccount('dropbox_stub', 'user2')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file
        self.man.updateLocalSyncFolder()
        self.man.cuentas[0].resetChanges()
        self.man.cuentas[1].resetChanges()
        # We have the file in the first account, fully synchronized

        filename_cases = '/test/MuErTe.txt'
        self.man.fileSystemModule.createFile(filename_cases)  # temporally create a file
        self.man.cuentas[1].uploadFile(filename_cases, 'different_revision')  # we upload it to the second account
        self.man.fileSystemModule.remove(filename_cases)  # we have the file only in the remote

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.databaseManager.database['files'].all()]
        remoteFileList_0 = self.man.cuentas[0].getFileList()
        remoteFileList_1 = self.man.cuentas[1].getFileList()

        date = datetime.date.today()
        expected_fileList = ['/test/muerte.txt', '/test/MuErTe.txt__CONFLICTED_COPY__FROM_' + str(self.man.cuentas[1]) + '_' + date.isoformat()]
        expected_DBFiles = [
            {'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user},
            {'path': '/test/MuErTe.txt__CONFLICTED_COPY__FROM_' + str(self.man.cuentas[1]) + '_' + date.isoformat(), 'hash': '/test/MuErTe.txt__CONFLICTED_COPY__FROM_' + str(self.man.cuentas[1]) + '_' + date.isoformat(), 'account': self.man.cuentas[1].getAccountType(), 'user': self.man.cuentas[1].user}]
        expected_remoteFileList_0 = ['/test/muerte.txt']
        expected_remoteFileList_1 = ['/test/MuErTe.txt__CONFLICTED_COPY__FROM_' + str(self.man.cuentas[1]) + '_' + date.isoformat()]

        assert_equal(fileList, expected_fileList)
        assert_equal(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList_0, expected_remoteFileList_0)
        assert_equal(remoteFileList_1, expected_remoteFileList_1)
