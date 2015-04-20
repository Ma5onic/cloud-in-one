import manager
from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.tools import raises
from nose.tools import assert_true
from nose.tools import assert_false
import datetime
from util import *

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
        self.man.saveFile(self.man.cuentas[0],'testPath','hash')
        self.man.deleteAccount(self.man.cuentas[0])
        assert_false(self.man.cuentas)

        # should be deleted??
        files_table = self.man.database['files']
        assert_false(list(files_table.all()))
        accounts_table = self.man.database['accounts']
        assert_false(list(accounts_table.all()))

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
        localChanges = [{'path': '/test/muerte.txt','hash':'MISSING2','account':self.man.cuentas[0]}]
        remoteChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]

        fixedLocalChanges,fixedRemoteChanges = self.man.fixCollisions(localChanges,remoteChanges)

        date = datetime.date.today()
        expected_fixedLocalChanges = [{'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(),'hash':'MISSING2','account':self.man.cuentas[0],'oldpath':'/test/muerte.txt'}]
        expected_fixedRemoteChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]
        assert_equal(fixedLocalChanges, expected_fixedLocalChanges)
        assert_equal(fixedRemoteChanges, expected_fixedRemoteChanges)

    def test_fixCollisions2(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]
        remoteChanges = [{'path': '/test/muerte.txt','hash':None,'account':self.man.cuentas[0]}]

        fixedLocalChanges,fixedRemoteChanges = self.man.fixCollisions(localChanges,remoteChanges)

        expected_fixedLocalChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]
        expected_fixedRemoteChanges = []
        assert_equal(fixedLocalChanges, expected_fixedLocalChanges)
        assert_equal(fixedRemoteChanges, expected_fixedRemoteChanges)

    def test_fixCollisions3(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt','hash':None,'account':self.man.cuentas[0]}]
        remoteChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]

        fixedLocalChanges,fixedRemoteChanges = self.man.fixCollisions(localChanges,remoteChanges)

        expected_fixedLocalChanges = []
        expected_fixedRemoteChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]
        assert_equal(fixedLocalChanges, expected_fixedLocalChanges)
        assert_equal(fixedRemoteChanges, expected_fixedRemoteChanges)
    
    def test_fixCollisions4(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt','hash':None,'account':self.man.cuentas[0]}]
        remoteChanges = [{'path': '/test/muerte.txt','hash':None,'account':self.man.cuentas[0]}]

        fixedLocalChanges,fixedRemoteChanges = self.man.fixCollisions(localChanges,remoteChanges)

        expected_fixedLocalChanges = [{'path': '/test/muerte.txt','hash':None,'account':self.man.cuentas[0]}]
        expected_fixedRemoteChanges = []
        assert_equal(fixedLocalChanges, expected_fixedLocalChanges)
        assert_equal(fixedRemoteChanges, expected_fixedRemoteChanges)

    def test_fixCollisions5(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]
        remoteChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]

        fixedLocalChanges,fixedRemoteChanges = self.man.fixCollisions(localChanges,remoteChanges)

        expected_fixedLocalChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]
        expected_fixedRemoteChanges = []
        assert_equal(fixedLocalChanges, expected_fixedLocalChanges)
        assert_equal(fixedRemoteChanges, expected_fixedRemoteChanges)

    def test_fixCollisions6(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]
        remoteChanges = []

        fixedLocalChanges,fixedRemoteChanges = self.man.fixCollisions(localChanges,remoteChanges)

        expected_fixedLocalChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]
        expected_fixedRemoteChanges = []
        assert_equal(fixedLocalChanges, expected_fixedLocalChanges)
        assert_equal(fixedRemoteChanges, expected_fixedRemoteChanges)

    def test_fixCollisions7(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = []
        remoteChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]

        fixedLocalChanges,fixedRemoteChanges = self.man.fixCollisions(localChanges,remoteChanges)

        expected_fixedLocalChanges = []
        expected_fixedRemoteChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]
        assert_equal(fixedLocalChanges, expected_fixedLocalChanges)
        assert_equal(fixedRemoteChanges, expected_fixedRemoteChanges)

    def test_fixCollisions8(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte2.txt','hash':'MISSING','account':self.man.cuentas[0]}]
        remoteChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]

        fixedLocalChanges,fixedRemoteChanges = self.man.fixCollisions(localChanges,remoteChanges)

        expected_fixedLocalChanges = [{'path': '/test/muerte2.txt','hash':'MISSING','account':self.man.cuentas[0]}]
        expected_fixedRemoteChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]
        assert_equal(fixedLocalChanges, expected_fixedLocalChanges)
        assert_equal(fixedRemoteChanges, expected_fixedRemoteChanges)

    def test_fixCollisions9(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]},{'path': '/test/muerte2.txt','hash':'MISSING2','account':self.man.cuentas[0]}]
        remoteChanges = []

        fixedLocalChanges,fixedRemoteChanges = self.man.fixCollisions(localChanges,remoteChanges)

        expected_fixedLocalChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]},{'path': '/test/muerte2.txt','hash':'MISSING2','account':self.man.cuentas[0]}]
        expected_fixedRemoteChanges = []
        assert_equal(fixedLocalChanges, expected_fixedLocalChanges)
        assert_equal(fixedRemoteChanges, expected_fixedRemoteChanges)

    def test_fixCollisions10(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt','hash':None,'account':self.man.cuentas[0]},{'path': '/test/muerte2.txt','hash':'MISSING','account':self.man.cuentas[0]}]
        remoteChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]},{'path': '/test/muerte2.txt','hash':'MISSING2','account':self.man.cuentas[0]}]

        fixedLocalChanges,fixedRemoteChanges = self.man.fixCollisions(localChanges,remoteChanges)
        
        date = datetime.date.today()
        expected_fixedLocalChanges = [{'path': '/test/muerte2.txt__CONFLICTED_COPY__' + date.isoformat(),'hash':'MISSING','account':self.man.cuentas[0],'oldpath':'/test/muerte2.txt'}]
        expected_fixedRemoteChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]},{'path': '/test/muerte2.txt','hash':'MISSING2','account':self.man.cuentas[0]}]
        assert_equal(fixedLocalChanges, expected_fixedLocalChanges)
        assert_equal(fixedRemoteChanges, expected_fixedRemoteChanges)

    def test_fixCollisions11(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt','hash':None,'account':self.man.cuentas[0]},{'path': '/test/muerte2.txt','hash':'MISSING2','account':self.man.cuentas[0]}]
        remoteChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]},{'path': '/test/muerte2.txt','hash':'MISSING2','account':self.man.cuentas[0]}]

        fixedLocalChanges,fixedRemoteChanges = self.man.fixCollisions(localChanges,remoteChanges)
        
        expected_fixedLocalChanges = [{'path': '/test/muerte2.txt','hash':'MISSING2','account':self.man.cuentas[0]}]
        expected_fixedRemoteChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]
        assert_equal(fixedLocalChanges, expected_fixedLocalChanges)
        assert_equal(fixedRemoteChanges, expected_fixedRemoteChanges)

    def test_fixCollisions12(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]
        remoteChanges = [{'path': '/test/muerte.txt','hash':None,'account':self.man.cuentas[0]},{'path': '/test/muerte.txt','hash':'MISSING2','account':self.man.cuentas[0]}]

        fixedLocalChanges,fixedRemoteChanges = self.man.fixCollisions(localChanges,remoteChanges)
        
        date = datetime.date.today()
        expected_fixedLocalChanges = [{'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(),'hash':'MISSING','account':self.man.cuentas[0],'oldpath':'/test/muerte.txt'}]
        expected_fixedRemoteChanges = [{'path': '/test/muerte.txt','hash':'MISSING2','account':self.man.cuentas[0]}]
        assert_equal(fixedLocalChanges, expected_fixedLocalChanges)
        assert_equal(fixedRemoteChanges, expected_fixedRemoteChanges)

    def test_fixCollisions13(self):
        self.man.newAccount('dropbox_stub', 'user')
        date = datetime.date.today()
        localChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]},{'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(),'hash':None,'account':self.man.cuentas[0]}]
        remoteChanges = [{'path': '/test/muerte.txt','hash':'MISSING2','account':self.man.cuentas[0]}]

        fixedLocalChanges,fixedRemoteChanges = self.man.fixCollisions(localChanges,remoteChanges)
        
        date = datetime.date.today()
        expected_fixedLocalChanges = [{'path': '/test/muerte.txt__CONFLICTED_COPY__' + date.isoformat(),'hash':'MISSING','account':self.man.cuentas[0],'oldpath':'/test/muerte.txt'}]
        expected_fixedRemoteChanges = [{'path': '/test/muerte.txt','hash':'MISSING2','account':self.man.cuentas[0]}]
        assert_equal(fixedLocalChanges, expected_fixedLocalChanges)
        assert_equal(fixedRemoteChanges, expected_fixedRemoteChanges)

    def test_fixCollisions14(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]},{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]
        remoteChanges = []

        fixedLocalChanges,fixedRemoteChanges = self.man.fixCollisions(localChanges,remoteChanges)
        
        expected_fixedLocalChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]
        expected_fixedRemoteChanges = []
        assert_equal(fixedLocalChanges, expected_fixedLocalChanges)
        assert_equal(fixedRemoteChanges, expected_fixedRemoteChanges)

    @raises(StopIteration)
    def test_fixCollisions15(self):
        self.man.newAccount('dropbox_stub', 'user')
        localChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]},{'path': '/test/muerte.txt','hash':'MISSING2','account':self.man.cuentas[0]}]
        remoteChanges = []

        fixedLocalChanges,fixedRemoteChanges = self.man.fixCollisions(localChanges,remoteChanges)
        
        expected_fixedLocalChanges = [{'path': '/test/muerte.txt','hash':'MISSING','account':self.man.cuentas[0]}]
        expected_fixedRemoteChanges = []
        assert_equal(fixedLocalChanges, expected_fixedLocalChanges)
        assert_equal(fixedRemoteChanges, expected_fixedRemoteChanges)

    def test_findLocalChanges(self):
        pass
        
    def test_applyLocalChanges(self):
        pass
        
    def test_applyRemoteChanges(self):
        pass
        


