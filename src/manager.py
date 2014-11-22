from log import Logger
import json
import dropboxAccount
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

        self.fileSystemModule = FileSystemModule()
        self.sync_folder = self.fileSystemModule.createDirectory(self.config["sync_folder_name"])

        #TODO: inicializar los módulos de seguridad y FS
        self.securityModule = None

    def newAccount(self, type, user):
        self.logger.info("Adding new account")
        self.logger.debug("type = %s", type)
        self.logger.debug("user = %s", user)

        self.cuentas.append(Create(type, user))
        #TODO: Do whatever it's needed to add a new account
        return True

    def deleteAccount(self, account):
        self.logger.info("Deleting account")
        self.logger.debug("account = %s", account)
        #TODO: Do things to delete an account
        return True

    def updateLocalSyncFolder(self, folder="/"):
        self.logger.info("Updating sync folder")
        self.logger.debug("Folder = <" + folder + ">")
        for account in self.cuentas:
            metadataDict = account.getMetadata(folder)
            self.logger.debug(metadataDict)
            for element in metadataDict['contents']:
                if element["is_dir"]:
                    dirname = element['path']
                    self.fileSystemModule.createDirectory(dirname, path=self.sync_folder)
                    self.updateLocalSyncFolder(dirname)
                else:
                    #TODO: download and save file
                    self.logger.debug("no folder!" + element['path'])

if __name__ == '__main__':
    man = Manager('user', 'password')
    man.newAccount('Dropbox', 'user')
    man.cuentas[0].getUserInfo()
    man.updateLocalSyncFolder()
