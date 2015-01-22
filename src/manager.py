from log import Logger
import json
import dropboxAccount
import dataset
from fileSystemModule import FileSystemModule

config_file = "config/config.json"


def Create(type, user):
    if type is "dropbox":
        return dropboxAccount.DropboxAccount(user)
    elif type is "dropbox_stub":
        return dropboxAccount.DropboxAccountStub(user)


class Manager():
    """Manager of the Cloud-In-One application.
    It is responsible for the control flow and coordination of components"""
    def __init__(self, user, password):
        self.logger = Logger(__name__)
        self.logger.info("Creating Manager")

        self.user = user
        self.password = password

        self.config = json.load(open(config_file))
        self.logger.info("Loaded config file")
        self.logger.debug("===== Config contents: ======")
        self.logger.debug(self.config)
        self.logger.debug("===== END Config contents: ======")

        self.database = self.connectDB(self.config["database"])

        self.cuentas = self.getAccounts()

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
        for cuenta in self.cuentas:
            cuenta.delta()

    def getAccounts(self):
        accounts_table = self.database['accounts']
        accounts_data = accounts_table.all()
        cuentas_list = []
        for acc in accounts_data:
            if acc["accountType"] == 'dropbox':
                cuentas_list.append(dropboxAccount.DropboxAccount(acc['user'], acc['token'], acc['userid']))

        return cuentas_list

    def saveAccount(self, account):
        accounts_table = self.database['accounts']
        accounts_table.insert(dict(accountType=account.getAccountType(), user=account.user, token=account.access_token, userid=account.user_id))

    def deleteAccountDB(self, account):
        accounts_table = self.database['accounts']
        accounts_table.delete(accountType=account.getAccountType(), user=account.user)

    def saveFile(self, account, metadata, file_hash=None):
        files_table = self.database['files']
        files_table.insert(dict(accountType=account.getAccountType(), user=account.user, path=metadata['path'], hash=file_hash))

    def connectDB(self, database):
        return dataset.connect('sqlite:///' + database)


if __name__ == '__main__':
    man = Manager('user', 'password')
    if not man.cuentas:
        man.newAccount('dropbox_stub', 'user')
    man.cuentas[0].getUserInfo()
    man.updateLocalSyncFolder()
    if len(man.cuentas) > 1:
        for i in range(1, len(man.cuentas)):
            man.deleteAccount(man.cuentas[i])
