from io import BytesIO
import hashlib
from log import Logger

from simplecrypt.src import simplecrypt
from exceptions import SecurityError


class SecurityModule():
    """docstring for SecurityModule"""
    def __init__(self, user, password, database):
        super(SecurityModule, self).__init__()

        self.logger = Logger(__name__)
        self.logger.info("Creating SecurityModule")

        self.database = database
        self.user = user

        self.password = self.hashPassword(password)
        del(password)
        if not self.checkLogin(user, self.password):
            raise PermissionError("Wrong user/password")

    def checkLogin(self, user, password):
        self.logger.info("Checking Login")
        user_table = self.database['user']

        users_count = user_table.__len__()

        if users_count == 1:
            user = user_table.find_one(user=user)
            if user:
                stored_hash = user['hash']
                return password == stored_hash
        elif users_count == 0:
            self.logger.debug("There are no users, registering a new one")
            self.register(user, password)
            return True
        else:
            self.__cleanDatabase()
            raise SecurityError("More than one user. Security breach")
        return False

    def register(self, user, password):
        self.logger.info("Registering user")
        self.logger.debug("user = <" + user + ">")

        self.__cleanDatabase()

        user_table = self.database['user']
        user_table.upsert(dict(id=1, user=user, hash=password), ['id'])

    def __cleanDatabase(self):
        self.logger.debug("Cleaning database")
        for i in self.database.tables:
            self.database[i].drop()

    def hashPassword(self, password):
        self.logger.debug("Hashing password")
        # we cannot use a random salt because this should be installed in several computers and give the same password to be able to decrypt...
        return hashlib.sha256(('th¡5iS@sal7' + password).encode('utf-8')).hexdigest()

    def encrypt(self, streamFile):
        self.logger.debug("Encrypting file")
        encrypted = simplecrypt.encrypt_file(self.password, streamFile)
        self.logger.debug("File encrypted successfully. ")
        return encrypted

    def decrypt(self, streamFile):
        self.logger.debug("Decrypting file")
        decrypted = simplecrypt.decrypt_file(self.password, streamFile)
        self.logger.debug("File decrypted successfully. ")
        return decrypted


class SecurityModuleStub(object):
    def __init__(self):
        super(SecurityModuleStub, self).__init__()

    def checkLogin(self, user, password):
        return True

    def hashPassword(self, password):
        self.logger.debug("Hashing password")
        # we cannot use a random salt because this should be installed in several computers and give the same password to be able to decrypt...
        return password

    def encrypt(self, streamFile):
        return streamFile

    def decrypt(self, streamFile):
        return streamFile
