import manager
from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.tools import raises
from nose.tools import assert_true
from nose.tools import assert_false
import datetime
from util import Ignore
from util import returnFalse
from fileSystemModule import FileSystemModuleStub


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
        self.man = manager.Manager('user', 'password', self.config_default)
        self.man.fileSystemModule = FileSystemModuleStub()

    def teardown(self):
        """This method is run once after _each_ test method is executed"""
        for i in self.man.database.tables:
            self.man.database[i].drop()

        self.man = None

    def test_manager(self):
        assert_true(self.man)

    def test_newAccount_dropbox(self):
        self.man.newAccount('dropbox_stub', 'user')
        assert_true(self.man.cuentas)

        accounts_table = self.man.database['accounts']
        assert_true(list(accounts_table.all()))

    def test_deleteAccount(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.deleteAccount(self.man.cuentas[0])
        assert_false(self.man.cuentas)
        files_table = self.man.database['files']
        assert_false(list(files_table.all()))
        accounts_table = self.man.database['accounts']
        assert_false(list(accounts_table.all()))

    @Ignore
    def test_deleteAccountAndFiles(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.saveFile({'account': self.man.cuentas[0], 'path': 'testPath', 'hash': 'hash', 'revision': 'revision_number'})
        self.man.deleteAccount(self.man.cuentas[0])
        assert_false(self.man.cuentas)

        # TODO: should be deleted??
        files_table = self.man.database['files']
        assert_false(list(files_table.all()))
        accounts_table = self.man.database['accounts']
        assert_false(list(accounts_table.all()))

    # def test_updateLocalSyncFolder(self):

    # TODO: several deltas...
    def test_findRemoteChanges(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.cuentas[0].uploadFile('/test/muerte.txt')
        remoteChanges = self.man.findRemoteChanges()

        expected_remoteChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0], 'revision': 'revision_number'}]
        assert_equal(remoteChanges, expected_remoteChanges)

    def test_findRemoteChanges_2(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.cuentas[0].uploadFile('/test/muerte.txt')
        self.man.cuentas[0].deleteFile('/test/muerte.txt')
        remoteChanges = self.man.findRemoteChanges()

        expected_remoteChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0], 'revision': 'revision_number'}, {'path': '/test/muerte.txt', 'hash': None, 'account': self.man.cuentas[0]}]
        assert_equal(remoteChanges, expected_remoteChanges)

    def test_findRemoteChanges_3(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.cuentas[0].uploadFile('/test/muerte.txt')
        self.man.findRemoteChanges()
        self.man.cuentas[0].deleteFile('/test/muerte.txt')
        remoteChanges = self.man.findRemoteChanges()

        expected_remoteChanges = [{'path': '/test/muerte.txt', 'hash': None, 'account': self.man.cuentas[0]}]
        assert_equal(remoteChanges, expected_remoteChanges)

    def test_findRemoteChanges_4(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.cuentas[0].uploadFile('/test/muerte.txt')
        self.man.findRemoteChanges()
        self.man.cuentas[0].deleteFile('/test/muerte.txt')
        self.man.cuentas[0].uploadFile('/test/muerte.txt')
        remoteChanges = self.man.findRemoteChanges()

        expected_remoteChanges = [{'path': '/test/muerte.txt', 'hash': None, 'account': self.man.cuentas[0]}, {'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0], 'revision': 'revision_number'}]
        assert_equal(remoteChanges, expected_remoteChanges)

    def test_findRemoteChanges_5(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.cuentas[0].uploadFile('/test/muerte.txt')
        self.man.cuentas[0].uploadFile('/test/muerte2.txt')

        remoteChanges = self.man.findRemoteChanges()

        expected_remoteChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0], 'revision': 'revision_number'}, {'path': '/test/muerte2.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0], 'revision': 'revision_number'}]
        assert_equal(remoteChanges, expected_remoteChanges)

    def test_findRemoteChanges_6(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.cuentas[0].uploadFile('/test/muerte.txt')
        self.man.cuentas[0].uploadFile('/test/muerte2.txt')
        self.man.findRemoteChanges()
        self.man.cuentas[0].uploadFile('/test/muerte.txt')
        self.man.cuentas[0].uploadFile('/test/muerte2.txt')

        remoteChanges = self.man.findRemoteChanges()

        expected_remoteChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0], 'revision': 'revision_number'}, {'path': '/test/muerte2.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0], 'revision': 'revision_number'}]
        assert_equal(remoteChanges, expected_remoteChanges)

    def test_findRemoteChanges_7(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.cuentas[0].uploadFile('/test/muerte.txt')
        self.man.cuentas[0].uploadFile('/test/muerte2.txt')
        self.man.findRemoteChanges()
        self.man.cuentas[0].deleteFile('/test/muerte.txt')
        self.man.cuentas[0].deleteFile('/test/muerte2.txt')

        remoteChanges = self.man.findRemoteChanges()

        expected_remoteChanges = [{'path': '/test/muerte.txt', 'hash': None, 'account': self.man.cuentas[0]}, {'path': '/test/muerte2.txt', 'hash': None, 'account': self.man.cuentas[0]}]
        assert_equal(remoteChanges, expected_remoteChanges)

    def test_findRemoteChanges_8(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.cuentas[0].uploadFile('/test/muerte.txt')
        self.man.cuentas[0].uploadFile('/test/muerte2.txt')
        self.man.cuentas[0].deleteFile('/test/muerte.txt')
        self.man.cuentas[0].deleteFile('/test/muerte2.txt')

        remoteChanges = self.man.findRemoteChanges()

        expected_remoteChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0], 'revision': 'revision_number'}, {'path': '/test/muerte2.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0], 'revision': 'revision_number'}, {'path': '/test/muerte.txt', 'hash': None, 'account': self.man.cuentas[0]}, {'path': '/test/muerte2.txt', 'hash': None, 'account': self.man.cuentas[0]}]
        assert_equal(remoteChanges, expected_remoteChanges)

    def test_findRemoteChanges_9(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.saveFile({'account': self.man.cuentas[0], 'path': '/test/muerte.txt', 'hash': 'MISSING', 'revision': 'revision_number'})  # we had a file
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # "external" upload
        self.man.cuentas[0]._delta_reset_ = True  # we receive a reset

        remoteChanges = self.man.findRemoteChanges()

        expected_remoteChanges = [{'path': '/test/muerte.txt', 'hash': None, 'account': self.man.cuentas[0], 'revision': 'revision_number'}, {'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0], 'revision': 'revision_number'}]
        assert_equal(remoteChanges, expected_remoteChanges)

    def test_findRemoteChanges_10(self):
        self.man.newAccount('dropbox_stub', 'user')
        # we didn't have the file
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # "external" upload
        self.man.cuentas[0]._delta_reset_ = True  # we receive a reset

        remoteChanges = self.man.findRemoteChanges()

        expected_remoteChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0], 'revision': 'revision_number'}]
        assert_equal(remoteChanges, expected_remoteChanges)

    def test_fixCollisions(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING2', 'account': self.man.cuentas[0]}]
        remoteChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]

        fixedChangesOnLocal, fixedChangesOnDB, fixedChangesOnRemote = self.man.fixCollisions(localChanges, remoteChanges)

        date = datetime.date.today()
        expected_fixedChangesOnLocal = [{'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), 'hash': 'MISSING2', 'account': self.man.cuentas[0], 'oldpath': '/test/muerte.txt'}, {'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]
        expected_fixedChangesOnDB = [{'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), 'hash': 'MISSING2', 'account': self.man.cuentas[0], 'oldpath': '/test/muerte.txt'}, {'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]
        expected_fixedChangesOnRemote = [{'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), 'hash': 'MISSING2', 'account': self.man.cuentas[0], 'oldpath': '/test/muerte.txt'}]

        assert_equal(fixedChangesOnLocal, expected_fixedChangesOnLocal)
        assert_equal(fixedChangesOnDB, expected_fixedChangesOnDB)
        assert_equal(fixedChangesOnRemote, expected_fixedChangesOnRemote)

    def test_fixCollisions2(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]
        remoteChanges = [{'path': '/test/muerte.txt', 'hash': None, 'account': self.man.cuentas[0]}]

        fixedChangesOnLocal, fixedChangesOnDB, fixedChangesOnRemote = self.man.fixCollisions(localChanges, remoteChanges)

        expected_fixedChangesOnLocal = []
        expected_fixedChangesOnDB = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]
        expected_fixedChangesOnRemote = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]

        assert_equal(fixedChangesOnLocal, expected_fixedChangesOnLocal)
        assert_equal(fixedChangesOnDB, expected_fixedChangesOnDB)
        assert_equal(fixedChangesOnRemote, expected_fixedChangesOnRemote)

    def test_fixCollisions3(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt', 'hash': None, 'account': self.man.cuentas[0]}]
        remoteChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]

        fixedChangesOnLocal, fixedChangesOnDB, fixedChangesOnRemote = self.man.fixCollisions(localChanges, remoteChanges)

        expected_fixedChangesOnLocal = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]
        expected_fixedChangesOnDB = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]
        expected_fixedChangesOnRemote = []

        assert_equal(fixedChangesOnLocal, expected_fixedChangesOnLocal)
        assert_equal(fixedChangesOnDB, expected_fixedChangesOnDB)
        assert_equal(fixedChangesOnRemote, expected_fixedChangesOnRemote)

    def test_fixCollisions4(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt', 'hash': None, 'account': self.man.cuentas[0]}]
        remoteChanges = [{'path': '/test/muerte.txt', 'hash': None, 'account': self.man.cuentas[0]}]

        fixedChangesOnLocal, fixedChangesOnDB, fixedChangesOnRemote = self.man.fixCollisions(localChanges, remoteChanges)

        expected_fixedChangesOnLocal = []
        expected_fixedChangesOnDB = [{'path': '/test/muerte.txt', 'hash': None, 'account': self.man.cuentas[0]}]
        expected_fixedChangesOnRemote = []

        assert_equal(fixedChangesOnLocal, expected_fixedChangesOnLocal)
        assert_equal(fixedChangesOnDB, expected_fixedChangesOnDB)
        assert_equal(fixedChangesOnRemote, expected_fixedChangesOnRemote)

    def test_fixCollisions5(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]
        remoteChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]

        fixedChangesOnLocal, fixedChangesOnDB, fixedChangesOnRemote = self.man.fixCollisions(localChanges, remoteChanges)

        date = datetime.date.today()
        expected_fixedChangesOnLocal = [{'account': self.man.cuentas[0], 'hash': 'MISSING', 'oldpath': '/test/muerte.txt', 'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat()}, {'account': self.man.cuentas[0], 'hash': 'MISSING', 'path': '/test/muerte.txt'}]
        expected_fixedChangesOnDB = [{'account': self.man.cuentas[0], 'hash': 'MISSING', 'oldpath': '/test/muerte.txt', 'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat()}, {'account': self.man.cuentas[0], 'hash': 'MISSING', 'path': '/test/muerte.txt'}]
        expected_fixedChangesOnRemote = [{'account': self.man.cuentas[0], 'hash': 'MISSING', 'oldpath': '/test/muerte.txt', 'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat()}]

        assert_equal(fixedChangesOnLocal, expected_fixedChangesOnLocal)
        assert_equal(fixedChangesOnDB, expected_fixedChangesOnDB)
        assert_equal(fixedChangesOnRemote, expected_fixedChangesOnRemote)

    def test_fixCollisions6(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]
        remoteChanges = []

        fixedChangesOnLocal, fixedChangesOnDB, fixedChangesOnRemote = self.man.fixCollisions(localChanges, remoteChanges)

        expected_fixedChangesOnLocal = []
        expected_fixedChangesOnDB = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]
        expected_fixedChangesOnRemote = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]

        assert_equal(fixedChangesOnLocal, expected_fixedChangesOnLocal)
        assert_equal(fixedChangesOnDB, expected_fixedChangesOnDB)
        assert_equal(fixedChangesOnRemote, expected_fixedChangesOnRemote)

    def test_fixCollisions7(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = []
        remoteChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]

        fixedChangesOnLocal, fixedChangesOnDB, fixedChangesOnRemote = self.man.fixCollisions(localChanges, remoteChanges)

        expected_fixedChangesOnLocal = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]
        expected_fixedChangesOnDB = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]
        expected_fixedChangesOnRemote = []

        assert_equal(fixedChangesOnLocal, expected_fixedChangesOnLocal)
        assert_equal(fixedChangesOnDB, expected_fixedChangesOnDB)
        assert_equal(fixedChangesOnRemote, expected_fixedChangesOnRemote)

    def test_fixCollisions8(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte2.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]
        remoteChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]

        fixedChangesOnLocal, fixedChangesOnDB, fixedChangesOnRemote = self.man.fixCollisions(localChanges, remoteChanges)

        expected_fixedChangesOnLocal = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]
        expected_fixedChangesOnDB = [{'path': '/test/muerte2.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}, {'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]
        expected_fixedChangesOnRemote = [{'path': '/test/muerte2.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]

        assert_equal(fixedChangesOnLocal, expected_fixedChangesOnLocal)
        assert_equal(fixedChangesOnDB, expected_fixedChangesOnDB)
        assert_equal(fixedChangesOnRemote, expected_fixedChangesOnRemote)

    def test_fixCollisions9(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}, {'path': '/test/muerte2.txt', 'hash': 'MISSING2', 'account': self.man.cuentas[0]}]
        remoteChanges = []

        fixedChangesOnLocal, fixedChangesOnDB, fixedChangesOnRemote = self.man.fixCollisions(localChanges, remoteChanges)

        expected_fixedChangesOnLocal = []
        expected_fixedChangesOnDB = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}, {'path': '/test/muerte2.txt', 'hash': 'MISSING2', 'account': self.man.cuentas[0]}]
        expected_fixedChangesOnRemote = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}, {'path': '/test/muerte2.txt', 'hash': 'MISSING2', 'account': self.man.cuentas[0]}]

        assert_equal(fixedChangesOnLocal, expected_fixedChangesOnLocal)
        assert_equal(fixedChangesOnDB, expected_fixedChangesOnDB)
        assert_equal(fixedChangesOnRemote, expected_fixedChangesOnRemote)

    def test_fixCollisions10(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt', 'hash': None, 'account': self.man.cuentas[0]}, {'path': '/test/muerte2.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]
        remoteChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}, {'path': '/test/muerte2.txt', 'hash': 'MISSING2', 'account': self.man.cuentas[0]}]

        fixedChangesOnLocal, fixedChangesOnDB, fixedChangesOnRemote = self.man.fixCollisions(localChanges, remoteChanges)

        date = datetime.date.today()
        expected_fixedChangesOnLocal = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}, {'path': '/test/muerte2.txt__CONFLICTED_COPY__' + date.isoformat(), 'hash': 'MISSING', 'account': self.man.cuentas[0], 'oldpath': '/test/muerte2.txt'}, {'path': '/test/muerte2.txt', 'hash': 'MISSING2', 'account': self.man.cuentas[0]}]
        expected_fixedChangesOnDB = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}, {'path': '/test/muerte2.txt__CONFLICTED_COPY__' + date.isoformat(), 'hash': 'MISSING', 'account': self.man.cuentas[0], 'oldpath': '/test/muerte2.txt'}, {'path': '/test/muerte2.txt', 'hash': 'MISSING2', 'account': self.man.cuentas[0]}]
        expected_fixedChangesOnRemote = [{'path': '/test/muerte2.txt__CONFLICTED_COPY__' + date.isoformat(), 'hash': 'MISSING', 'account': self.man.cuentas[0], 'oldpath': '/test/muerte2.txt'}]

        assert_equal(fixedChangesOnLocal, expected_fixedChangesOnLocal)
        assert_equal(fixedChangesOnDB, expected_fixedChangesOnDB)
        assert_equal(fixedChangesOnRemote, expected_fixedChangesOnRemote)

    def test_fixCollisions11(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt', 'hash': None, 'account': self.man.cuentas[0]}, {'path': '/test/muerte2.txt', 'hash': 'MISSING2', 'account': self.man.cuentas[0]}]
        remoteChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}, {'path': '/test/muerte2.txt', 'hash': 'MISSING2', 'account': self.man.cuentas[0]}]

        fixedChangesOnLocal, fixedChangesOnDB, fixedChangesOnRemote = self.man.fixCollisions(localChanges, remoteChanges)

        date = datetime.date.today()
        expected_fixedChangesOnLocal = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}, {'account': self.man.cuentas[0], 'hash': 'MISSING2', 'oldpath': '/test/muerte2.txt', 'path': '/test/muerte2.txt__CONFLICTED_COPY__' + date.isoformat()}, {'path': '/test/muerte2.txt', 'hash': 'MISSING2', 'account': self.man.cuentas[0]}]
        expected_fixedChangesOnDB = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}, {'account': self.man.cuentas[0], 'hash': 'MISSING2', 'oldpath': '/test/muerte2.txt', 'path': '/test/muerte2.txt__CONFLICTED_COPY__' + date.isoformat()}, {'path': '/test/muerte2.txt', 'hash': 'MISSING2', 'account': self.man.cuentas[0]}]
        expected_fixedChangesOnRemote = [{'account': self.man.cuentas[0], 'hash': 'MISSING2', 'oldpath': '/test/muerte2.txt', 'path': '/test/muerte2.txt__CONFLICTED_COPY__' + date.isoformat()}]

        assert_equal(fixedChangesOnLocal, expected_fixedChangesOnLocal)
        assert_equal(fixedChangesOnDB, expected_fixedChangesOnDB)
        assert_equal(fixedChangesOnRemote, expected_fixedChangesOnRemote)

    def test_fixCollisions12(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]
        remoteChanges = [{'path': '/test/muerte.txt', 'hash': None, 'account': self.man.cuentas[0]}, {'path': '/test/muerte.txt', 'hash': 'MISSING2', 'account': self.man.cuentas[0]}]

        fixedChangesOnLocal, fixedChangesOnDB, fixedChangesOnRemote = self.man.fixCollisions(localChanges, remoteChanges)

        date = datetime.date.today()
        expected_fixedChangesOnLocal = [{'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), 'hash': 'MISSING', 'account': self.man.cuentas[0], 'oldpath': '/test/muerte.txt'}, {'path': '/test/muerte.txt', 'hash': 'MISSING2', 'account': self.man.cuentas[0]}]
        expected_fixedChangesOnDB = [{'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), 'hash': 'MISSING', 'account': self.man.cuentas[0], 'oldpath': '/test/muerte.txt'}, {'path': '/test/muerte.txt', 'hash': 'MISSING2', 'account': self.man.cuentas[0]}]
        expected_fixedChangesOnRemote = [{'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), 'hash': 'MISSING', 'account': self.man.cuentas[0], 'oldpath': '/test/muerte.txt'}]

        assert_equal(fixedChangesOnLocal, expected_fixedChangesOnLocal)
        assert_equal(fixedChangesOnDB, expected_fixedChangesOnDB)
        assert_equal(fixedChangesOnRemote, expected_fixedChangesOnRemote)

    def test_fixCollisions13(self):
        self.man.newAccount('dropbox_stub', 'user')
        date = datetime.date.today()
        localChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}, {'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), 'hash': None, 'account': self.man.cuentas[0]}]
        remoteChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING2', 'account': self.man.cuentas[0]}]

        fixedChangesOnLocal, fixedChangesOnDB, fixedChangesOnRemote = self.man.fixCollisions(localChanges, remoteChanges)

        expected_fixedChangesOnLocal = [{'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), 'hash': 'MISSING', 'account': self.man.cuentas[0], 'oldpath': '/test/muerte.txt'}, {'path': '/test/muerte.txt', 'hash': 'MISSING2', 'account': self.man.cuentas[0]}]
        expected_fixedChangesOnDB = [{'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), 'hash': 'MISSING', 'account': self.man.cuentas[0], 'oldpath': '/test/muerte.txt'}, {'path': '/test/muerte.txt', 'hash': 'MISSING2', 'account': self.man.cuentas[0]}]
        expected_fixedChangesOnRemote = [{'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), 'hash': 'MISSING', 'account': self.man.cuentas[0], 'oldpath': '/test/muerte.txt'}]

        assert_equal(fixedChangesOnLocal, expected_fixedChangesOnLocal)
        assert_equal(fixedChangesOnDB, expected_fixedChangesOnDB)
        assert_equal(fixedChangesOnRemote, expected_fixedChangesOnRemote)

    def test_fixCollisions14(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}, {'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]
        remoteChanges = []

        fixedChangesOnLocal, fixedChangesOnDB, fixedChangesOnRemote = self.man.fixCollisions(localChanges, remoteChanges)

        expected_fixedChangesOnLocal = []
        expected_fixedChangesOnDB = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]
        expected_fixedChangesOnRemote = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]

        assert_equal(fixedChangesOnLocal, expected_fixedChangesOnLocal)
        assert_equal(fixedChangesOnDB, expected_fixedChangesOnDB)
        assert_equal(fixedChangesOnRemote, expected_fixedChangesOnRemote)

    @Ignore
    @raises(StopIteration)
    def test_fixCollisions15(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}, {'path': '/test/muerte.txt', 'hash': 'MISSING2', 'account': self.man.cuentas[0]}]
        remoteChanges = []

        fixedChangesOnLocal, fixedChangesOnDB, fixedChangesOnRemote = self.man.fixCollisions(localChanges, remoteChanges)

    def test_fixCollisions16(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING'}]
        remoteChanges = []

        fixedChangesOnLocal, fixedChangesOnDB, fixedChangesOnRemote = self.man.fixCollisions(localChanges, remoteChanges)

        expected_fixedChangesOnLocal = []
        expected_fixedChangesOnDB = [{'path': '/test/muerte.txt', 'hash': 'MISSING'}]
        expected_fixedChangesOnRemote = [{'path': '/test/muerte.txt', 'hash': 'MISSING'}]

        assert_equal(fixedChangesOnLocal, expected_fixedChangesOnLocal)
        assert_equal(fixedChangesOnDB, expected_fixedChangesOnDB)
        assert_equal(fixedChangesOnRemote, expected_fixedChangesOnRemote)

    def test_findLocalChanges(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('test_file')  # create a file

        localChanges = self.man.findLocalChanges()

        expected_localChanges = [{'path': 'test_file', 'hash': 'test_file'}]

        assert_equal(localChanges, expected_localChanges)

    def test_findLocalChanges_2(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.saveFile({'account': self.man.cuentas[0], 'path': 'test_file', 'hash': 'oldhash', 'revision': 'revision_number'})  # we had a file (hash=oldhash)
        self.man.fileSystemModule.createFile('test_file')  # we modify it

        localChanges = self.man.findLocalChanges()

        expected_localChanges = [{'path': 'test_file', 'hash': 'test_file', 'account': self.man.cuentas[0], 'revision': 'revision_number'}]

        assert_equal(localChanges, expected_localChanges)

    def test_findLocalChanges_3(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.saveFile({'account': self.man.cuentas[0], 'path': 'test_file', 'hash': 'test_file', 'revision': 'revision_number'})  # we had a file
        # we don't have it anymore

        localChanges = self.man.findLocalChanges()

        expected_localChanges = [{'path': 'test_file', 'hash': None, 'account': self.man.cuentas[0]}]

        assert_equal(localChanges, expected_localChanges)

    def test_findLocalChanges_4(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.saveFile({'account': self.man.cuentas[0], 'path': 'test_file', 'hash': 'test_file', 'revision': 'revision_number'})  # we had a file
        self.man.fileSystemModule.createFile('test_file')  # we still have it (unmodified)

        localChanges = self.man.findLocalChanges()

        expected_localChanges = []

        assert_equal(localChanges, expected_localChanges)

    def test_findLocalChanges_5(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.saveFile({'account': self.man.cuentas[0], 'path': 'test_file', 'hash': 'test_file', 'revision': 'revision_number'})  # we had a file
        self.man.fileSystemModule.createFile('test_file')  # we still have it (unmodified)
        self.man.saveFile({'account': self.man.cuentas[0], 'path': 'test_file2', 'hash': 'test_file2', 'revision': 'revision_number'})  # we had another file
        # we don't have it anymore

        localChanges = self.man.findLocalChanges()

        expected_localChanges = [{'path': 'test_file2', 'hash': None, 'account': self.man.cuentas[0]}]

        assert_equal(localChanges, expected_localChanges)

    def test_findLocalChanges_6(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.saveFile({'account': self.man.cuentas[0], 'path': 'test_file', 'hash': 'oldhash', 'revision': 'revision_number'})  # we had a file
        self.man.fileSystemModule.createFile('test_file')  # we modify it
        self.man.saveFile({'account': self.man.cuentas[0], 'path': 'test_file2', 'hash': 'test_file2', 'revision': 'revision_number'})  # we had another file
        # we don't have it anymore

        localChanges = self.man.findLocalChanges()

        expected_localChanges = [{'path': 'test_file', 'hash': 'test_file', 'account': self.man.cuentas[0], 'revision': 'revision_number'}, {'path': 'test_file2', 'hash': None, 'account': self.man.cuentas[0]}]

        assert_equal(localChanges, expected_localChanges)

    def test_findLocalChanges_7(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.saveFile({'account': self.man.cuentas[0], 'path': 'test_file', 'hash': 'test_file', 'revision': 'revision_number'})  # we had a file
        self.man.fileSystemModule.createFile('test_file')
        self.man.fileSystemModule.renameFile('test_file', 'renamed')  # we rename it

        localChanges = self.man.findLocalChanges()

        expected_localChanges = [{'path': 'test_file', 'hash': None, 'account': self.man.cuentas[0]}, {'path': 'renamed', 'hash': 'test_file'}]

        assert_equal(localChanges, expected_localChanges)

    def test_applyChangesOnLocal(self):
        self.man.newAccount('dropbox_stub', 'user')
        changesOnLocal = []

        self.man.applyChangesOnLocal(changesOnLocal)

        expected_fileList = []

        fileList = self.man.fileSystemModule.getFileList()

        assert_equal(fileList, expected_fileList)

    @Ignore
    def test_applyChangesOnLocal_2(self):
        self.man.newAccount('dropbox_stub', 'user')
        changesOnLocal = [{'path': '/test/muerte.txt', 'hash': 'MISSING'}]

        self.man.applyChangesOnLocal(changesOnLocal)

        expected_remoteChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}]

        assert_equal(remoteChanges, expected_remoteChanges)

    def test_applyChangesOnLocal_3(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.cuentas[0].uploadFile('/test/muerte.txt')
        changesOnLocal = [{'path': '/test/muerte.txt', 'hash': 'MISSING2', 'account': self.man.cuentas[0]}]

        self.man.applyChangesOnLocal(changesOnLocal)

        expected_fileList = ['/test/muerte.txt']
        fileList = self.man.fileSystemModule.getFileList()

        assert_equal(fileList, expected_fileList)

    def test_applyChangesOnLocal_4(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.cuentas[0].uploadFile('/test/muerte.txt')
        self.man.cuentas[0].uploadFile('/test/muerte2.txt')
        changesOnLocal = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0]}, {'path': '/test/muerte2.txt', 'hash': 'MISSING2', 'account': self.man.cuentas[0]}]

        self.man.applyChangesOnLocal(changesOnLocal)

        expected_fileList = ['/test/muerte.txt', '/test/muerte2.txt']
        fileList = self.man.fileSystemModule.getFileList()

        assert_equal(fileList, expected_fileList)

    def test_applyChangesOnLocal_5(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file
        changesOnLocal = [{'path': '/test/muerte.txt', 'hash': None, 'account': self.man.cuentas[0]}]

        self.man.applyChangesOnLocal(changesOnLocal)

        expected_fileList = []
        fileList = self.man.fileSystemModule.getFileList()

        assert_equal(fileList, expected_fileList)

    def test_applyChangesOnLocal_6(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file
        self.man.cuentas[0].uploadFile('/test/muerte2.txt')
        changesOnLocal = [{'path': '/test/muerte2.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0], 'oldpath': '/test/muerte.txt'}, {'path': '/test/muerte.txt', 'hash': None, 'account': self.man.cuentas[0]}]

        self.man.applyChangesOnLocal(changesOnLocal)

        expected_fileList = ['/test/muerte2.txt']
        fileList = self.man.fileSystemModule.getFileList()

        assert_equal(fileList, expected_fileList)

    def test_applyChangesOnRemote(self):
        self.man.newAccount('dropbox_stub', 'user')
        changesOnRemote = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0], 'revision': 'revision_number'}]

        self.man.applyChangesOnRemote(changesOnRemote)

        expected_remoteChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0], 'revision': 'revision_number1'}]
        remoteChanges = self.man.findRemoteChanges()

        assert_equal(remoteChanges, expected_remoteChanges)

    def test_applyChangesOnRemote_2(self):
        self.man.newAccount('dropbox_stub', 'user')
        changesOnRemote = [{'path': '/test/muerte.txt', 'hash': 'MISSING'}]

        self.man.applyChangesOnRemote(changesOnRemote)

        expected_remoteChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0], 'revision': 'revision_number'}]
        remoteChanges = self.man.findRemoteChanges()

        assert_equal(remoteChanges, expected_remoteChanges)

    def test_applyChangesOnRemote_3(self):
        self.man.newAccount('dropbox_stub', 'user')

        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # we had a file uploaded
        self.man.findRemoteChanges()  # no pending changes

        changesOnRemote = [{'path': '/test/muerte.txt', 'hash': None, 'account': self.man.cuentas[0]}]

        self.man.applyChangesOnRemote(changesOnRemote)

        expected_remoteChanges = [{'path': '/test/muerte.txt', 'hash': None, 'account': self.man.cuentas[0]}]
        remoteChanges = self.man.findRemoteChanges()

        assert_equal(remoteChanges, expected_remoteChanges)

    def test_applyChangesOnRemote_4(self):
        self.man.newAccount('dropbox_stub', 'user')

        changesOnRemote = []

        self.man.applyChangesOnRemote(changesOnRemote)

        expected_remoteChanges = []
        remoteChanges = self.man.findRemoteChanges()

        assert_equal(remoteChanges, expected_remoteChanges)

    def test_applyChangesOnRemote_5(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.newAccount('dropbox_stub', 'user2')

        changesOnRemote = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0], 'revision': 'revision_number'}, {'path': '/test/muerte2.txt', 'hash': 'MISSING', 'account': self.man.cuentas[1], 'revision': 'revision_number'}]

        self.man.applyChangesOnRemote(changesOnRemote)

        expected_remoteChanges = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'account': self.man.cuentas[0], 'revision': 'revision_number1'}, {'path': '/test/muerte2.txt', 'hash': 'MISSING', 'account': self.man.cuentas[1], 'revision': 'revision_number1'}]
        remoteChanges = self.man.findRemoteChanges()

        assert_equal(remoteChanges, expected_remoteChanges)

    def test_applyChangesOnDB(self):
        self.man.newAccount('dropbox_stub', 'user')

        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # we had a file uploaded
        changesOnDB = [{'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0], 'revision': 'revision_number'}]

        self.man.applyChangesOnLocal(changesOnDB)
        self.man.applyChangesOnDB(changesOnDB)

        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'revision': i['revision']} for i in self.man.database['files'].all()]

        expected_DBFiles = [{'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'revision': 'revision_number'}]

        assert_equal(DBFiles, expected_DBFiles)

    def test_applyChangesOnDB_2(self):
        self.man.newAccount('dropbox_stub', 'user')

        changesOnDB = []

        self.man.applyChangesOnLocal(changesOnDB)
        self.man.applyChangesOnDB(changesOnDB)

        DBFiles = [{'path': i['path'], 'hash': i['hash']} for i in self.man.database['files'].all()]

        expected_DBFiles = []

        assert_equal(DBFiles, expected_DBFiles)

    def test_applyChangesOnDB_3(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.saveFile({'account': self.man.cuentas[0], 'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'revision': 'revision_number'})
        changesOnDB = [{'path': '/test/muerte.txt', 'hash': None, 'account': self.man.cuentas[0]}]

        self.man.applyChangesOnDB(changesOnDB)

        DBFiles = [{'path': i['path'], 'hash': i['hash']} for i in self.man.database['files'].all()]

        expected_DBFiles = []

        assert_equal(DBFiles, expected_DBFiles)

    @Ignore
    def test_applyChangesOnDB_4(self):
        self.man.newAccount('dropbox_stub', 'user')
        changesOnDB = [{'path': '/test/muerte.txt', 'hash': '/test/muerte.txt'}]

        self.man.applyChangesOnDB(changesOnDB)

        DBFiles = [{'path': i['path'], 'hash': i['hash']} for i in self.man.database['files'].all()]

        expected_DBFiles = []

        assert_equal(DBFiles, expected_DBFiles)

    def test_integrationSync(self):
        self.man.newAccount('dropbox_stub', 'user')

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = []
        expected_DBFiles = []
        expected_remoteFileList = []

        assert_equal(fileList, expected_fileList)
        assert_equal(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_integrationSync_2(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = ['/test/muerte.txt']
        expected_DBFiles = [{'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}]
        expected_remoteFileList = ['/test/muerte.txt']

        assert_equal(fileList, expected_fileList)
        assert_equal(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_integrationSync_3(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # we had a file uploaded

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = ['/test/muerte.txt']
        expected_DBFiles = [{'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}]
        expected_remoteFileList = ['/test/muerte.txt']

        assert_equal(fileList, expected_fileList)
        assert_equal(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_integrationSync_4(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # we had a file uploaded

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        date = datetime.date.today()
        expected_fileList = ['/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), '/test/muerte.txt']
        expected_DBFiles = [{'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}, {'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}]
        expected_remoteFileList = ['/test/muerte.txt', '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat()]

        assert_equal(fileList, expected_fileList)
        assert_equal(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_integrationSync_5(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file
        self.man.cuentas[0].uploadFile('/test/muerte2.txt')  # we had a file uploaded

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = ['/test/muerte.txt', '/test/muerte2.txt']
        expected_DBFiles = [{'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}, {'path': '/test/muerte2.txt', 'hash': '/test/muerte2.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}]
        expected_remoteFileList = ['/test/muerte2.txt', '/test/muerte.txt']

        assert_equal(fileList, expected_fileList)
        assert_equal(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_integrationSync_6(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file
        self.man.saveFile({'account': self.man.cuentas[0], 'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'revision': 'revision_number'})
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # we had a file uploaded
        self.man.cuentas[0].resetChanges()
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # "modify" it

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user'], 'revision': i['revision']} for i in self.man.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = ['/test/muerte.txt']
        expected_DBFiles = [{'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user, 'revision': 'revision_number'}]
        expected_remoteFileList = ['/test/muerte.txt']

        assert_equal(fileList, expected_fileList)
        assert_equal(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_integrationSync_7(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file
        self.man.saveFile({'account': self.man.cuentas[0], 'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'revision': 'revision_number'})
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # we had a file uploaded
        self.man.cuentas[0].resetChanges()
        self.man.cuentas[0].deleteFile('/test/muerte.txt')  # delete it

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = []
        expected_DBFiles = []
        expected_remoteFileList = []

        assert_equal(fileList, expected_fileList)
        assert_equal(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_integrationSync_8(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/test/muerte2.txt')  # create a file
        self.man.saveFile({'account': self.man.cuentas[0], 'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'revision': 'revision_number'})
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # we had a file uploaded
        self.man.cuentas[0].resetChanges()
        self.man.fileSystemModule.renameFile('/test/muerte2.txt', '/test/muerte.txt')  # we modify it locally

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user'], 'revision': i['revision']} for i in self.man.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = ['/test/muerte.txt']
        expected_DBFiles = [{'path': '/test/muerte.txt', 'hash': '/test/muerte2.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user, 'revision': 'revision_number1'}]
        expected_remoteFileList = ['/test/muerte.txt']

        assert_equal(fileList, expected_fileList)
        assert_equal(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_integrationSync_9(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/test/muerte2.txt')  # create a file
        self.man.saveFile({'account': self.man.cuentas[0], 'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'revision': 'revision_number'})
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # we had a file uploaded
        self.man.cuentas[0].resetChanges()
        self.man.fileSystemModule.renameFile('/test/muerte2.txt', '/test/muerte.txt')  # we modify it locally
        self.man.cuentas[0].deleteFile('/test/muerte.txt')  # delete it

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user'], 'revision': i['revision']} for i in self.man.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = ['/test/muerte.txt']
        expected_DBFiles = [{'path': '/test/muerte.txt', 'hash': '/test/muerte2.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user, 'revision': 'revision_number1'}]
        expected_remoteFileList = ['/test/muerte.txt']

        assert_equal(fileList, expected_fileList)
        assert_equal(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_integrationSync_10(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file
        self.man.saveFile({'account': self.man.cuentas[0], 'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'revision': 'revision_number'})
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # we had a file uploaded
        self.man.cuentas[0].resetChanges()
        self.man.fileSystemModule.remove('/test/muerte.txt')  # delete it

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = []
        expected_DBFiles = []
        expected_remoteFileList = []

        assert_equal(fileList, expected_fileList)
        assert_equal(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList, expected_remoteFileList)

    def test_integrationSync_11(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file
        self.man.saveFile({'account': self.man.cuentas[0], 'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'revision': 'revision_number'})
        self.man.cuentas[0].uploadFile('/test/muerte.txt')  # we had a file uploaded
        self.man.cuentas[0].resetChanges()
        self.man.fileSystemModule.remove('/test/muerte.txt')  # delete it
        self.man.cuentas[0].deleteFile('/test/muerte.txt')  # delete it

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        expected_fileList = []
        expected_DBFiles = []
        expected_remoteFileList = []

        assert_equal(fileList, expected_fileList)
        assert_equal(DBFiles, expected_DBFiles)
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
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList = self.man.cuentas[0].getFileList()

        date = datetime.date.today()
        expected_fileList = ['/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat() + '_2', '/test/muerte.txt']
        expected_DBFiles = [{'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}, {'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}, {'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat() + '_2', 'hash': 'modified', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}]
        expected_remoteFileList = ['/test/muerte.txt', '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(), '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat() + '_2']

        assert_equal(sorted(fileList), sorted(expected_fileList))
        assert_equal(DBFiles, expected_DBFiles)
        assert_equal(sorted(remoteFileList), sorted(expected_remoteFileList))

    def test_twoAccounts_fits_first(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.newAccount('dropbox_stub', 'user2')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList1 = self.man.cuentas[0].getFileList()
        remoteFileList2 = self.man.cuentas[1].getFileList()

        expected_fileList = ['/test/muerte.txt']
        expected_DBFiles = [{'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0].getAccountType(), 'user': self.man.cuentas[0].user}]
        expected_remoteFileList1 = ['/test/muerte.txt']
        expected_remoteFileList2 = []

        assert_equal(fileList, expected_fileList)
        assert_equal(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList1, expected_remoteFileList1)
        assert_equal(remoteFileList2, expected_remoteFileList2)

    def test_twoAccounts_fits_second(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.cuentas[0].fits = returnFalse
        self.man.newAccount('dropbox_stub', 'user2')
        self.man.fileSystemModule.createFile('/test/muerte.txt')  # create a file

        self.man.updateLocalSyncFolder()

        fileList = self.man.fileSystemModule.getFileList()
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList1 = self.man.cuentas[0].getFileList()
        remoteFileList2 = self.man.cuentas[1].getFileList()

        expected_fileList = ['/test/muerte.txt']
        expected_DBFiles = [{'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[1].getAccountType(), 'user': self.man.cuentas[1].user}]
        expected_remoteFileList1 = []
        expected_remoteFileList2 = ['/test/muerte.txt']

        assert_equal(fileList, expected_fileList)
        assert_equal(DBFiles, expected_DBFiles)
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
        DBFiles = [{'path': i['path'], 'hash': i['hash'], 'account': i['accountType'], 'user': i['user']} for i in self.man.database['files'].all()]
        remoteFileList1 = self.man.cuentas[0].getFileList()
        remoteFileList2 = self.man.cuentas[1].getFileList()

        expected_fileList = ['/test/muerte.txt']
        expected_DBFiles = []
        expected_remoteFileList1 = []
        expected_remoteFileList2 = []

        assert_equal(fileList, expected_fileList)
        assert_equal(DBFiles, expected_DBFiles)
        assert_equal(remoteFileList1, expected_remoteFileList1)
        assert_equal(remoteFileList2, expected_remoteFileList2)
