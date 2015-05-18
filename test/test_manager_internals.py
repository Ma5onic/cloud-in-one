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


class TestInternals(object):
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
        self.man.saveFile({'account': self.man.cuentas[0], 'path': '/test/muerte.txt', 'hash': 'MISSING', 'revision': 'revision_number', 'size': len('/test/muerte.txt')})  # we had a file
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

    def test_findLocalChanges(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.fileSystemModule.createFile('test_file')  # create a file

        localChanges = self.man.findLocalChanges()

        expected_localChanges = [{'path': 'test_file', 'hash': 'test_file'}]

        assert_equal(localChanges, expected_localChanges)

    def test_findLocalChanges_2(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.saveFile({'account': self.man.cuentas[0], 'path': 'test_file', 'hash': 'oldhash', 'revision': 'revision_number', 'size': len('test_file')})  # we had a file (hash=oldhash)
        self.man.fileSystemModule.createFile('test_file')  # we modify it

        localChanges = self.man.findLocalChanges()

        expected_localChanges = [{'path': 'test_file', 'hash': 'test_file', 'account': self.man.cuentas[0], 'revision': 'revision_number'}]

        assert_equal(localChanges, expected_localChanges)

    def test_findLocalChanges_3(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.saveFile({'account': self.man.cuentas[0], 'path': 'test_file', 'hash': 'test_file', 'revision': 'revision_number', 'size': len('test_file')})  # we had a file
        # we don't have it anymore

        localChanges = self.man.findLocalChanges()

        expected_localChanges = [{'path': 'test_file', 'hash': None, 'account': self.man.cuentas[0]}]

        assert_equal(localChanges, expected_localChanges)

    def test_findLocalChanges_4(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.saveFile({'account': self.man.cuentas[0], 'path': 'test_file', 'hash': 'test_file', 'revision': 'revision_number', 'size': len('test_file')})  # we had a file
        self.man.fileSystemModule.createFile('test_file')  # we still have it (unmodified)

        localChanges = self.man.findLocalChanges()

        expected_localChanges = []

        assert_equal(localChanges, expected_localChanges)

    def test_findLocalChanges_5(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.saveFile({'account': self.man.cuentas[0], 'path': 'test_file', 'hash': 'test_file', 'revision': 'revision_number', 'size': len('test_file')})  # we had a file
        self.man.fileSystemModule.createFile('test_file')  # we still have it (unmodified)
        self.man.saveFile({'account': self.man.cuentas[0], 'path': 'test_file2', 'hash': 'test_file2', 'revision': 'revision_number', 'size': len('test_file2')})  # we had another file
        # we don't have it anymore

        localChanges = self.man.findLocalChanges()

        expected_localChanges = [{'path': 'test_file2', 'hash': None, 'account': self.man.cuentas[0]}]

        assert_equal(localChanges, expected_localChanges)

    def test_findLocalChanges_6(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.saveFile({'account': self.man.cuentas[0], 'path': 'test_file', 'hash': 'oldhash', 'revision': 'revision_number', 'size': len('test_file')})  # we had a file
        self.man.fileSystemModule.createFile('test_file')  # we modify it
        self.man.saveFile({'account': self.man.cuentas[0], 'path': 'test_file2', 'hash': 'test_file2', 'revision': 'revision_number', 'size': len('test_file2')})  # we had another file
        # we don't have it anymore

        localChanges = self.man.findLocalChanges()

        expected_localChanges = [{'path': 'test_file', 'hash': 'test_file', 'account': self.man.cuentas[0], 'revision': 'revision_number'}, {'path': 'test_file2', 'hash': None, 'account': self.man.cuentas[0]}]

        assert_equal(localChanges, expected_localChanges)

    def test_findLocalChanges_7(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.saveFile({'account': self.man.cuentas[0], 'path': 'test_file', 'hash': 'test_file', 'revision': 'revision_number', 'size': len('test_file')})  # we had a file
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
        changesOnRemote = [{'path': '/test/muerte.txt', 'hash': 'MISSING', 'size': len('/test/muerte.txt')}]

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
        changesOnDB = [{'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'account': self.man.cuentas[0], 'revision': 'revision_number', 'size': len('/test/muerte.txt')}]

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
        self.man.saveFile({'account': self.man.cuentas[0], 'path': '/test/muerte.txt', 'hash': '/test/muerte.txt', 'revision': 'revision_number', 'size': len('/test/muerte.txt')})
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
