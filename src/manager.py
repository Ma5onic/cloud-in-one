from log import Logger
import json
import dropboxAccount
import dataset
import hashlib
from fileSystemModule import FileSystemModule
from functools import partial

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
        # TODO: get the files changed and check for collisions!
        self.findLocalChanges()
        self.syncAccounts()

    def syncAccounts(self):
        self.logger.info('Syncing accounts')
        for account in self.cuentas:
            self.logger.debug('Account <' + str(account) + '>')
            deltaDict = account.delta()
            self.logger.debug(deltaDict)
            if deltaDict['reset']:
                self.logger.debug('Reset recieved. Resetting account <' + str(account) + '>')
                path_list = [element['path'] for element in self.getFiles(account.getAccountType(), account.user)]
                for path in path_list:
                    self.logger.debug('removing <' + str(path) + '>')
                    self.remove(path, account)

            for filePath, metadata in deltaDict['entries']:
                self.logger.debug('filePath <' + str(filePath) + '> metadata <' + str(metadata) + '>')
                if metadata:  # create/edit path
                    if metadata["is_dir"]:
                        self.logger.debug('is_dir = True')
                        self.fileSystemModule.createDirectory(metadata["path"])
                        self.saveFile(account, metadata)
                    else:
                        self.logger.debug('is_dir = False')
                        streamFile = account.getFile(metadata["path"])  # Aquí tendré que encriptar el fichero...
                        fullpath = (self.fileSystemModule.createFile(metadata["path"], streamFile))
                        streamFile.close()
                        file_hash = self.md5sum(fullpath)

                        self.saveFile(account, metadata, file_hash)
                else:  # delete path
                    self.remove(filePath, account)

    def findLocalChanges(self):
        self.logger.info('Getting Local differences')
        import pdb; pdb.set_trace()  # breakpoint ed20eecf //
        fileList = self.fileSystemModule.getFileList()
        toCheck = self.getToCheckFiles(fileList)

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
        accounts_table.upsert(dict(accountType=account.getAccountType(), user=account.user, token=account.access_token, userid=account.user_id), ['accountType', 'user'])

    def deleteAccountDB(self, account):
        accounts_table = self.database['accounts']
        accounts_table.delete(accountType=account.getAccountType(), user=account.user)

    def remove(self, path, account):
        self.fileSystemModule.remove(path)
        self.deleteFileDB(path, account)

    def deleteFileDB(self, path, account):
        self.logger.debug('deleting file <' + path + '> from account <' + account.getAccountType() + ',' + account.user + '>')
        files_table = self.database['files']
        files_table.delete(accountType=account.getAccountType(), user=account.user,path=path)

    def saveFile(self, account, metadata, file_hash=None):
        self.logger.debug('saving file <' + metadata['path'] + '> with hash <' + str(file_hash) + '> to account <' + account.getAccountType() + ',' + account.user + '>')
        files_table = self.database['files']
        files_table.upsert(dict(accountType=account.getAccountType(), user=account.user, path=metadata['path'], hash=file_hash), ['accountType', 'user', 'path'])

    def connectDB(self, database):
        return dataset.connect('sqlite:///' + database)

    def getFiles(self, account, user):
        files_table = self.database['files']
        files = files_table.find(accountType=account, user=user)
        return files

    def getToCheckFiles(self, file_list):
        files_table = self.database['files']
        iter_files = files_table.find(path=file_list)
        toCheck = []
        for i in iter_files:
            toCheck.append(i['path'])

        self.logger.debug('toCheck <' + str(toCheck) + '>')
        return toCheck

    def md5sum(self, filename):
        with open(filename, mode='rb') as f:
            d = hashlib.md5()
            for buf in iter(partial(f.read, 128), b''):
                d.update(buf)
        return d.hexdigest()


if __name__ == '__main__':
    man = Manager('user', 'password')
    if not man.cuentas:
        man.newAccount('dropbox_stub', 'user')
    man.cuentas[0].getUserInfo()
    man.updateLocalSyncFolder()
    if len(man.cuentas) > 1:
        for i in range(1, len(man.cuentas)):
            man.deleteAccount(man.cuentas[i])

    list_files = man.fileSystemModule.getFileList()
    for i in list_files:
        print(i)
