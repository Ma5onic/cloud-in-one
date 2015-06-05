import dataset
import tempfile
import simplecrypt
from nose.tools import assert_false
from nose.tools import assert_true
from nose.tools import assert_not_equal
from nose.tools import assert_equal
from nose.tools import raises
from databaseManager import DatabaseManager
from securityModule import SecurityModule
from fileSystemModule import FileSystemModuleStub
from manager import Manager
from exceptions import SecurityError
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

        SecurityModule(username, password, self.databaseManager)

        assert_true(self.databaseManager.database.tables)
        row = self.databaseManager.getUser(username)
        assert_not_equal(row['hash'], password)
        assert_equal(len(row['hash']), 64)

    def test_login_ok(self):
        username = 'username'
        password = 'password'

        SecurityModule(username, password, self.databaseManager)  # this registers
        SecurityModule(username, password, self.databaseManager)  # this logs in

    @raises(PermissionError)
    def test_login_wrong(self):
        username = 'username'
        password = 'password'

        SecurityModule(username, password, self.databaseManager)  # this registers
        SecurityModule(username + '2', password, self.databaseManager)  # this logs in

    @raises(PermissionError)
    def test_login_wrong_2(self):
        username = 'username'
        password = 'password'

        SecurityModule(username, password, self.databaseManager)  # this registers
        SecurityModule(username, password + '2', self.databaseManager)  # this logs in

    @raises(SecurityError)
    def test_login_two_users(self):
        username = 'username'
        password = 'password'

        SecurityModule(username, password, self.databaseManager)  # this registers
        self.databaseManager._insertUser(username, password)

        SecurityModule(username, password, self.databaseManager)  # this tries to login

    def test_encrypt(self):
        username = 'username'
        password = 'password'

        sec = SecurityModule(username, password, self.databaseManager)
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

        sec = SecurityModule(username, password, self.databaseManager)
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

        sec = SecurityModule(username, password, self.databaseManager)
        infile = tempfile.TemporaryFile()
        text = b'thisisnotencrypted'
        infile.write(text)
        infile.seek(0)

        sec.decrypt(infile)

    @raises(simplecrypt.DecryptionException)
    def test_wrong_password_decrypt(self):
        username = 'username'
        password = 'password'

        sec = SecurityModule(username, password, self.databaseManager)

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

        sec = SecurityModule(username, password, self.databaseManager)

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
        ctext = b'sc\x00\x02\xe8zt\xf5\x99!(\xbb\x08\xc1\xd0\x00)\xf6\xfb5Q\xed\xe87H\xad\x97\xd88tt\xd0\x1c\x00\xd8\xf9\xe8\xe4R\x88\x1d\x83\x10\xb0*\xe9r;\xa4A<t\x99@\xa6\xa1\xac\xda\t\x92\xa8\xbfZ\xce\xd8\xf9,-U\x1d>\x9d'
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
