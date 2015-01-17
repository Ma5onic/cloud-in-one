from log import Logger
import json
import dropboxAccount
import dataset
from fileSystemModule import FileSystemModule

config_file = "config/config.json"


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
        self.config = json.load(open(config_file))
        self.logger.info("Loaded config file")
        self.logger.debug("===== Config contents: ======")
        self.logger.debug(self.config)
        self.logger.debug("===== END Config contents: ======")

        self.database = self.connectDB(self.config["database"])

        self.fileSystemModule = FileSystemModule(self.config["sync_folder_name"])

        #TODO: inicializar los módulos de seguridad y FS
        self.securityModule = None

    def newAccount(self, type, user):
        self.logger.info("Adding new account")
        self.logger.debug("type = %s", type)
        self.logger.debug("user = %s", user)

        newAcc = Create(type, user)
        self.cuentas.append(newAcc)
        self.saveAccount(newAcc)

        #TODO: Do whatever it's needed to add a new account
        return True

    def deleteAccount(self, account):
        self.logger.info("Deleting account")
        self.logger.debug("account = %s", account)

        self.deleteAccountDB(account)
        #TODO: Do things to delete an account
        return True

    def updateLocalSyncFolder(self, folder="/"):
        self.logger.info("Updating sync folder")
        self.logger.debug("Folder = <" + folder + ">")
        for account in self.cuentas:
            deltaDict = account.delta()
            self.logger.debug(deltaDict)
            if deltaDict['reset']:
                pass
                #TODO: get all files & folders from account
                #TODO: remove all files & folders from account
            for filePath, metadata in deltaDict['entries']:
                if metadata["is_dir"]:
                    self.fileSystemModule.createDirectory(metadata["path"])
                else:
                    streamFile = account.getFile(metadata["path"])
                    self.fileSystemModule.createFile(metadata["path"], streamFile)
                    streamFile.close()

    def callDeltas(self):
        self.cuentas[0].delta()

    def saveAccount(self, account):
        accounts_table = self.database['accounts']
        accounts_table.insert(dict(accountType=account.getAccountType(), user=account.user))

    def deleteAccountDB(self, account):
        accounts_table = self.database['accounts']
        accounts_table.delete(dict(accountType=account.getAccountType(), user=account.user))

    def connectDB(self, database):
        return dataset.connect('sqlite:///' + database)


if __name__ == '__main__':
    man = Manager('user', 'password')
    man.newAccount('Dropbox', 'user')
    man.cuentas[0].getUserInfo()
    man.updateLocalSyncFolder()
