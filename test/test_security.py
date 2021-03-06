import dataset
import tempfile
import simplecrypt
from nose.tools import assert_false
from nose.tools import assert_true
from nose.tools import assert_not_equal
from nose.tools import assert_equal
from nose.tools import raises
from core.databaseManager import DatabaseManager
from core.securityModule import SecurityModule
from core.fileSystemModule import FileSystemModuleStub
from core.manager import Manager
from core.exceptions import SecurityError
from util import *


class TestSecurity(object):
    """docstring for TestSecurity"""
    def __init__(self):
        super(TestSecurity, self).__init__()

    @classmethod
    def setup_class(klass):
        """This method is run once for each class before any tests are run"""

    @classmethod
    def teardown_class(klass):
        """This method is run once for each class _after_ all tests are run"""

    def setUp(self):
        """This method is run once before _each_ test method is executed"""
        self.databaseManager = DatabaseManager(':memory:')

    def teardown(self):
        """This method is run once after _each_ test method is executed"""
        self.databaseManager.cleanDatabase()

    def test_register(self):
        username = 'username'
        password = 'password'

        assert_false(self.databaseManager.database.tables)

        SecurityModule(self.databaseManager, username, password)

        assert_true(self.databaseManager.database.tables)
        row = self.databaseManager.getUser(username)
        assert_not_equal(row['hash'], password)
        assert_equal(len(row['hash']), 64)

    def test_login_ok(self):
        username = 'username'
        password = 'password'

        SecurityModule(self.databaseManager, username, password)  # this registers
        SecurityModule(self.databaseManager, username, password)  # this logs in

    @raises(PermissionError)
    def test_login_wrong(self):
        username = 'username'
        password = 'password'

        SecurityModule(self.databaseManager, username, password)  # this registers
        SecurityModule(self.databaseManager, username + '2', password)  # this logs in

    @raises(PermissionError)
    def test_login_wrong_2(self):
        username = 'username'
        password = 'password'

        SecurityModule(self.databaseManager, username, password)  # this registers
        SecurityModule(self.databaseManager, username, password + '2')  # this logs in

    @raises(SecurityError)
    def test_login_two_users(self):
        username = 'username'
        password = 'password'

        SecurityModule(self.databaseManager, username, password)  # this registers
        self.databaseManager._insertUser(username, password)

        SecurityModule(self.databaseManager, username, password)  # this tries to login

    def test_encrypt(self):
        username = 'username'
        password = 'password'

        sec = SecurityModule(self.databaseManager, username, password)
        infile = tempfile.TemporaryFile()
        text = b'test'
        infile.write(text)
        infile.seek(0)

        outfile = sec.encrypt(infile)

        encrypted_text = outfile.read()
        assert_not_equal(encrypted_text, text)
        assert_equal(len(encrypted_text), 68+len(text))

    def test_encrypt_decrypt(self):
        username = 'username'
        password = 'password'

        sec = SecurityModule(self.databaseManager, username, password)
        infile = tempfile.TemporaryFile()
        text = b'test'
        infile.write(text)
        infile.seek(0)

        outfile = sec.decrypt(sec.encrypt(infile))

        assert_equal(outfile.read(), text)

    @raises(simplecrypt.DecryptionException)
    def test_wrong_decrypt(self):
        username = 'username'
        password = 'password'

        sec = SecurityModule(self.databaseManager, username, password)
        infile = tempfile.TemporaryFile()
        text = b'thisisnotencrypted'
        infile.write(text)
        infile.seek(0)

        sec.decrypt(infile)

    @raises(simplecrypt.DecryptionException)
    def test_wrong_password_decrypt(self):
        username = 'username'
        password = 'password'

        sec = SecurityModule(self.databaseManager, username, password)

        infile = tempfile.TemporaryFile()
        text = b'thisisnotencrypted'
        infile.write(text)
        infile.seek(0)

        encrypted = sec.encrypt(infile)
        sec.password = 'wrong'
        sec.decrypt(encrypted)

    def test_encrypt_decrypt_two_chunks(self):
        username = 'username'
        password = 'password'

        sec = SecurityModule(self.databaseManager, username, password)

        infile = tempfile.TemporaryFile()

        simplecrypt.CHUNKSIZE = 1024
        for i in range(simplecrypt.CHUNKSIZE+10):
            infile.write(b'x')

        infile.seek(0)
        outfile = sec.decrypt(sec.encrypt(infile))

        infile.seek(0)
        assert_equal(infile.read(), outfile.read())


class TestSecuritySelective(object):
    """docstring for TestSecuritySelective"""
    def __init__(self):
        super(TestSecuritySelective, self).__init__()
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
        self.man = Manager('user', 'password', config=self.config_default)
        self.man.fileSystemModule = FileSystemModuleStub()

    def teardown(self):
        """This method is run once after _each_ test method is executed"""
        self.man.databaseManager.cleanDatabase()

        self.man = None

    def test_manager(self):
        assert_true(self.man)

    def test_markEncryption(self):
        self.man.newAccount('dropbox_stub', 'user')
        filename = 'test_file.txt'
        self.man.fileSystemModule.createFile(filename)  # create a file
        self.man.updateLocalSyncFolder()

        self.man.markForEncription(filename)
        self.man.fileSystemModule.createFile(filename)  # modify the file

        self.man.updateLocalSyncFolder()  # it should try to encrypt

        remoteFile = self.man.cuentas[0].getFile(filename)
        localFile = self.man.fileSystemModule.openFile(filename)
        assert_equal(localFile.read(), b'text')
        assert_not_equal(remoteFile.read(), b'text')

    def test_unmarkEncryption(self):
        self.man.newAccount('dropbox_stub', 'user')
        filename = 'test_file.txt'
        self.man.fileSystemModule.createFile(filename)  # create a file
        self.man.updateLocalSyncFolder()

        self.man.unmarkForEncription(filename)
        self.man.fileSystemModule.createFile(filename)  # modify the file

        self.man.updateLocalSyncFolder()  # it should try to encrypt

        remoteFile = self.man.cuentas[0].getFile(filename)
        localFile = self.man.fileSystemModule.openFile(filename)
        assert_equal(remoteFile.read(), b'text')
        assert_equal(localFile.read(), b'text')

    def test_unmarked_decryption(self):
        self.man.newAccount('dropbox_stub', 'user')
        filename = 'test_file.txt'

        self.man.fileSystemModule.createFile(filename)  # temporally create a file
        # "text" -('user', 'password')->
        ctext = simplecrypt.encrypt(self.man.securityModule.hashPassword('user', 'password'), b'text')
        stream = tempfile.TemporaryFile()
        stream.write(ctext)
        stream.seek(0)
        self.man.cuentas[0].uploadFile(filename, 'different_revision', stream)  # we upload it to the second account
        self.man.fileSystemModule.remove(filename)  # we have the file only in the remote

        self.man.updateLocalSyncFolder()  # it should try to decrypt, and the file get marked to encrypt

        assert_true(self.man.databaseManager.shouldEncrypt(filename))

        remoteFile = self.man.cuentas[0].getFile(filename)
        localFile = self.man.fileSystemModule.openFile(filename)
        assert_equal(remoteFile.read(), ctext)
        assert_equal(localFile.read(), b'text')

    def test_deleteAccount_decrypt(self):
        self.test_markEncryption()
        filename = 'test_file.txt'

        account = self.man.cuentas[0]
        self.man.deleteAccount(account)

        remoteFile = account.getFile(filename)
        fileList = self.man.fileSystemModule.getFileList()

        expected_fileList = []

        compareFileLists(fileList, expected_fileList)
        assert_equal(remoteFile.read(), b'text')
