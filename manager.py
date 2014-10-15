from log import *
import dropboxAccount


def Create(type, user):
    if type is "Dropbox":
        return dropboxAccount.DropboxAccount(user)


class Manager():
    """Manager of the Cloud-In-One application.
    It is responsible for the control flow and coordination of components"""
    def __init__(self, user, password):
        self.logger = Logger(__name__)
        self.logger.info("Creating Manager")

        self.user = user
        self.password = password
        self.cuentas = []
        #TODO: inicializar los módulos de seguridad y FS
        self.securityModule = None
        self.fileSystemModule = None

    def newAccount(self, type, user):
        self.logger.info("Adding new account")
        self.logger.debug("type = %s", type)
        self.logger.debug("user = %s", user)

        self.cuentas.append(Create(type, user))
        # Do whatever it's needed to add a new account
        return True

    def deleteAccount(self, account):
        self.logger.info("Deleting account")
        self.logger.debug("account = %s", account)
        # Do things to delete an account
        return True
