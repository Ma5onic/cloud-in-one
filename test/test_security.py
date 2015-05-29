import dataset
import tempfile
import simplecrypt
from nose.tools import assert_false
from nose.tools import assert_true
from nose.tools import assert_not_equal
from nose.tools import assert_equal
from nose.tools import raises
from securityModule import SecurityModule
from exceptions import SecurityError


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
        self.database = dataset.connect('sqlite:///:memory:')

    def teardown(self):
        """This method is run once after _each_ test method is executed"""
        for i in self.database.tables:
            self.database[i].drop()

    def test_register(self):
        username = 'username'
        password = 'password'

        assert_false(self.database.tables)

        SecurityModule(username, password, self.database)

        assert_true(self.database.tables)
        user_table = self.database['user']
        row = user_table.find_one(user=username)
        assert_not_equal(row['hash'], password)
        assert_equal(len(row['hash']), 64)

    def test_login_ok(self):
        username = 'username'
        password = 'password'

        SecurityModule(username, password, self.database)  # this registers
        SecurityModule(username, password, self.database)  # this logs in

    @raises(PermissionError)
    def test_login_wrong(self):
        username = 'username'
        password = 'password'

        SecurityModule(username, password, self.database)  # this registers
        SecurityModule(username + '2', password, self.database)  # this logs in

    @raises(PermissionError)
    def test_login_wrong_2(self):
        username = 'username'
        password = 'password'

        SecurityModule(username, password, self.database)  # this registers
        SecurityModule(username, password + '2', self.database)  # this logs in

    @raises(SecurityError)
    def test_login_two_users(self):
        username = 'username'
        password = 'password'

        SecurityModule(username, password, self.database)  # this registers
        user_table = self.database['user']
        user_table.insert(dict(user=username+'2', hash=password))

        SecurityModule(username, password, self.database)  # this tries to login

    def test_encrypt(self):
        username = 'username'
        password = 'password'

        sec = SecurityModule(username, password, self.database)
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

        sec = SecurityModule(username, password, self.database)
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

        sec = SecurityModule(username, password, self.database)
        infile = tempfile.TemporaryFile()
        text = b'thisisnotencrypted'
        infile.write(text)
        infile.seek(0)

        sec.decrypt(infile)

    @raises(simplecrypt.DecryptionException)
    def test_wrong_password_decrypt(self):
        username = 'username'
        password = 'password'

        sec = SecurityModule(username, password, self.database)

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

        sec = SecurityModule(username, password, self.database)

        infile = tempfile.TemporaryFile()

        simplecrypt.CHUNKSIZE = 1024
        for i in range(simplecrypt.CHUNKSIZE+10):
            infile.write(b'x')

        infile.seek(0)
        outfile = sec.decrypt(sec.encrypt(infile))

        infile.seek(0)
        assert_equal(infile.read(), outfile.read())
