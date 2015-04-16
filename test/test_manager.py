import manager
from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.tools import raises
from nose.tools import assert_true
from nose.tools import assert_false
import datetime


class TestManager(object):
    def __init__(self):
        self.config_default = {"sync_folder_name": "./test/sync_folder","database": "db/tests.db"}
        self.man = None

    @classmethod
    def setup_class(klass):
        """This method is run once for each class before any tests are run"""

    @classmethod
    def teardown_class(klass):
        """This method is run once for each class _after_ all tests are run"""

    def setUp(self):
        """This method is run once before _each_ test method is executed"""
        self.man = manager.Manager('user', 'password',self.config_default)

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
        
    def test_deleteAccount(self):
        self.man.newAccount('dropbox_stub', 'user')
        self.man.deleteAccount(self.man.cuentas[0])
        assert_false(self.man.cuentas)

    # def test_updateLocalSyncFolder(self):

    # TODO: several deltas...
    def test_findRemoteChanges(self):
        self.man.newAccount('dropbox_stub', 'user')
        remoteChanges = self.man.findRemoteChanges()

        expected_remoteChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]
        assert_equal(remoteChanges, expected_remoteChanges)

        
    # TODO: think of better examples...
    def test_fixCollisions(self):
        self.man.newAccount('dropbox_stub', 'user')
        remoteChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]
        localChanges = [{'path': '/test/muerte.txt','hash':'MISSING2','account':self.man.cuentas[0]}]

        fixedLocalChanges,fixedRemoteChanges = self.man.fixCollisions(localChanges,remoteChanges)

        # TODO: DATE, oldpath...
        date = datetime.date.today()
        expected_fixedLocalChanges = [{'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(),'hash':'MISSING2','account':self.man.cuentas[0],'oldpath':'/test/muerte.txt'}]
        expected_fixedRemoteChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]
        assert_equal(fixedLocalChanges, expected_fixedLocalChanges)
        assert_equal(fixedRemoteChanges, expected_fixedRemoteChanges)
        
    def test_findLocalChanges(self):
        pass
        
    def test_applyLocalChanges(self):
        pass
        
    def test_applyRemoteChanges(self):
        pass
        


