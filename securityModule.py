from io import BytesIO
import hashlib
import getpass

from log import Logger

import simplecrypt
from exceptions import SecurityError


class SecurityModule():
    """docstring for SecurityModule"""
    def __init__(self, databaseManager, user='', password=''):
        super(SecurityModule, self).__init__()

        self.logger = Logger(__name__)
        self.logger.info("Creating SecurityModule")

        self.databaseManager = databaseManager
        self.user, self.password = self.getCredentials(user, password)

        if not self.checkLogin(self.user, self.password):
            raise PermissionError("Wrong user/password")

    def getCredentials(self, user='', passw=''):

        users_count = self.databaseManager.getUserCount()

        if users_count == 1:
            if user:
                password = self.hashPassword(user, passw)
            else:
                user = input("CLOUD-IN-ONE Username: ")
                password = self.hashPassword(user, getpass.getpass())
        elif users_count == 0:
            self.logger.debug("There are no users, registering a new one")
            if user:
                password = self.hashPassword(user, passw)
            else:
                user = input("Register a new username. This will be used to encrypt your files and authenticate you in the application:\n")
                password = self.hashPassword(user, getpass.getpass())
            self.register(user, password)
        else:
            self.databaseManager.cleanDatabase()
            raise SecurityError("More than one user. Security breach")
        return (user, password)

    def checkLogin(self, username, password):
        self.logger.info("Checking Login")
        user = self.databaseManager.getUser(username)

        if user:
            stored_hash = user['hash']
            self.logger.info("Logged in")
            return password == stored_hash

        return False

    def register(self, user, password):
        self.logger.info("Registering user")
        self.logger.debug("user = <" + user + ">")

        self.databaseManager.cleanDatabase()

        self.databaseManager.saveUser(user, password)

    def hashPassword(self, username, password):
        self.logger.debug("Hashing password")
        # we cannot use a random salt because this should be installed in several computers and give the same password to be able to decrypt...
        return hashlib.sha256(('th¡5iS@sal7' + username + '||' + password).encode('utf-8')).hexdigest()

    def encrypt(self, streamFile):
        if hasattr(streamFile, 'read'):
            self.logger.debug("Encrypting file")
            encrypted = simplecrypt.encrypt_file(self.password, streamFile)
            self.logger.debug("File encrypted successfully. ")
        else:
            self.logger.debug("Encrypting bytes")
            encrypted = simplecrypt.encrypt(self.password, streamFile)
            self.logger.debug("Encrypted successfully. ")
        return encrypted

    def decrypt(self, streamFile):
        if hasattr(streamFile, 'read'):
            self.logger.debug("Decrypting file")
            decrypted = simplecrypt.decrypt_file(self.password, streamFile)
            self.logger.debug("File decrypted successfully. ")
        else:
            self.logger.debug("Decrypting bytes")
            decrypted = simplecrypt.decrypt(self.password, streamFile)
            self.logger.debug("Decrypted successfully. ")
        return decrypted


class SecurityModuleStub(object):
    def __init__(self):
        super(SecurityModuleStub, self).__init__()

    def checkLogin(self, user, password):
        return True

    def hashPassword(self, password):
        self.logger.debug("Hashing password")
        # we cannot use a random salt because this should be installed in several computers and give the same password to be able to decrypt...
        return 'hashed' + password

    def encrypt(self, streamFile):
        return streamFile

    def decrypt(self, streamFile):
        return streamFile
