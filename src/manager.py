from log import Logger
import json
import dropboxAccount
import dataset
import datetime
from fileSystemModule import FileSystemModule

config_file = "config/config.json"


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

        self.fileSystemModule = FileSystemModule(self.config["sync_folder_name"])

        self.cuentas = self.getAccounts()

        #TODO: inicializar los módulos de seguridad y FS
        self.securityModule = None

    def CreateAccount(self, type, user):
        if type is "dropbox":
            return dropboxAccount.DropboxAccount(self.fileSystemModule, user)
        elif type is "dropbox_stub":
            return dropboxAccount.DropboxAccountStub(self.fileSystemModule, user)

    def newAccount(self, type, user):
        self.logger.info("Adding new account")
        self.logger.debug("type = %s", type)
        self.logger.debug("user = %s", user)

        newAcc = self.CreateAccount(type, user)
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
        localChanges = self.findLocalChanges()
        remoteChanges = self.findRemoteChanges()
        localChanges,remoteChanges = self.fixCollisions(localChanges,remoteChanges)
        self.applyLocalChanges(localChanges)
        # TODO: check collisions with the local!
        self.syncAccounts(localChanges, remoteChanges)

    def syncAccounts(self, localChanges, remoteChanges):
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
                        self.saveFile(account, metadata['path'])
                    else:
                        self.logger.debug('is_dir = False')
                        streamFile = account.getFile(metadata["path"])  # Aquí tendré que encriptar el fichero...
                        fullpath = (self.fileSystemModule.createFile(metadata["path"], streamFile))
                        streamFile.close()
                        file_hash = self.fileSystemModule.md5sum(fullpath)

                        self.saveFile(account, metadata['path'], file_hash)
                else:  # delete path
                    self.remove(filePath, account)

    def findRemoteChanges(self):
        self.logger.info('Getting Remote differences')
        # TODO: get remote changes 
        
        return [{'path': '/test/muerte2.txt', 'hash': '6d9a0ae6be9debf5cfe7a62fafe8553'}]
        # return [{'path': '/test/muerte2.txt', 'hash': None}]
        #return []

    def fixCollisions(self, localChanges, remoteChanges):
        self.logger.info('fixCollisions')
        self.logger.debug('localChanges <' + str(localChanges) + '>')
        self.logger.debug('remoteChanges <' + str(remoteChanges) + '>')
        
        # list of removes to avoid modifying the list we are iterating
        indexesToRemoveLocal = []

        for i,local in enumerate(localChanges):
            collided = next((item for item in remoteChanges if item['path'] == local['path']), None)
            if collided:
                self.logger.debug('Found collision! <' + local['path'] + '>')
                if collided['hash']: # remote created/modified
                    if local['hash']: # AND local created/modified!
                        if local['hash'] == collided['hash']: # same change...
                            self.logger.debug('Both modified in the same way. Keeping local changes')
                            remoteChanges.remove(collided) # we delete it from one of the lists to avoid trying to delete it twice
                        else:
                            date = datetime.date.today()
                            oldpath = local['path']
                            newname = oldpath+'__CONFLICTED_COPY__'+date.isoformat()
                            self.logger.debug('Both modified. New name = <' + newname + '>')
                            localChanges[i]['path'] = newname
                            localChanges[i]['oldpath'] = oldpath
                    else: # local deletion, remote modification, we keep the remote changes.
                        self.logger.debug('Deleted locally, keeping remote changes')
                        indexesToRemoveLocal.append(i)
                else: # in case of remote deletion, we keep the local changes
                    self.logger.debug('Deleted remotely, keeping local changes')
                    remoteChanges.remove(collided) # we delete it from one of the lists to avoid trying to delete it twice

        for i in indexesToRemoveLocal:
            del(localChanges[i])

        self.logger.debug('localChanges <' + str(localChanges) + '>')
        self.logger.debug('remoteChanges <' + str(remoteChanges) + '>')
        return (localChanges, remoteChanges)
        

    def findLocalChanges(self):
        self.logger.info('Getting Local differences')
        fileList = self.fileSystemModule.getFileList()
        toCheck =  []
        for i in self.cuentas:
            toCheck+= self.getFilesPaths(i.getAccountType(),i.user)
        localChanges = []
        for i in toCheck:
            if i in fileList:
                md5 = self.fileSystemModule.md5sum(i)
                if md5 != self.getMD5BD(i):
                    self.logger.debug('The file <' + i + '> has been MODIFIED')
                    localChanges.append(dict(path=i,hash=md5))
                else:
                    self.logger.debug('The file <' + i + '> is the same. Doing nothing')
                fileList.remove(i)
            else:
                self.logger.debug('The file <' + i + '> has been DELETED')
                localChanges.append(dict(path=i,hash=None))

        for i in fileList:
            self.logger.debug('The file <' + i + '> has been CREATED')
            md5 = self.fileSystemModule.md5sum(i)
            localChanges.append(dict(path=i,hash=md5))

        self.logger.debug('localChanges = <' + str(localChanges) + '>')
        return localChanges

    def applyLocalChanges(self, localChanges):
        self.logger.info("Applying local changes")
        # TODO: mark things to upload to remote
        # TODO: it must create the file if it doesn't exist right now
        for element in localChanges:
            if element['hash']: # created or modified, upsert in the db, mark to upload...
                for account in self.cuentas:
                    self.logger.debug("Trying to save file <" + element['path'] + "> in account <" + str(account) + ">")
                    if self.saveFile(account, element['path'], element['hash']):
                        self.logger.debug('Saved')
                        if 'oldpath' in element:
                            self.fileSystemModule.renameFile(element['oldpath'], element['path'])
                        break
            else: # deleted, remove from the db, remove from remote...
                self.logger.debug("Deleting file <" + element['path'] + ">")
                self.deleteFileDB(element['path'])

    def getMD5BD(self, filename):
        files_table = self.database['files']
        row = files_table.find_one(path=filename)
        return row['hash']


    def callDeltas(self):
        for cuenta in self.cuentas:
            cuenta.delta()

    def getAccounts(self):
        accounts_table = self.database['accounts']
        accounts_data = accounts_table.all()
        cuentas_list = []
        for acc in accounts_data:
            if acc["accountType"] == 'dropbox':
                cuentas_list.append(dropboxAccount.DropboxAccount(self.fileSystemModule, acc['user'], acc['token'], acc['userid']))

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

    # NOTE: is account needed here?
    def deleteFileDB(self, path, account=None):
        self.logger.debug('deleting file <' + path + '>')#' from account <' + account.getAccountType() + ',' + account.user + '>')
        files_table = self.database['files']
        files_table.delete(
            # accountType=account.getAccountType(), user=account.user,
            path=path)

    def saveFile(self, account, path, file_hash=None):
        self.logger.debug('saving file <' + path + '> with hash <' + str(file_hash) + '> to account <' + account.getAccountType() + ',' + account.user + '>')
        files_table = self.database['files']
        files_table.upsert(dict(accountType=account.getAccountType(), user=account.user, path=path, hash=file_hash), ['accountType', 'user', 'path'])
        # TODO: check if can be inserted and this...
        return True

    def connectDB(self, database):
        return dataset.connect('sqlite:///' + database)

    def getFilesPaths(self, account, user):
        files_table = self.database['files']
        files = files_table.find(accountType=account, user=user)
        filesPaths = []
        for i in files:
            filesPaths.append(i['path'])
        self.logger.debug('filesPaths for account <' + account + ',' + user + '> = '+ str(filesPaths))
        return filesPaths

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


if __name__ == '__main__':
    man = Manager('user', 'password')
    if not man.cuentas:
        man.newAccount('dropbox_stub', 'user')
    man.cuentas[0].getUserInfo()
    man.updateLocalSyncFolder()
    #if len(man.cuentas) > 1:
        #for i in range(1, len(man.cuentas)):
         #   man.deleteAccount(man.cuentas[i])

    list_files = man.fileSystemModule.getFileList()
    for i in list_files:
        print(i)

    print('======')
    for i in man.getFilesPaths(man.cuentas[0].getAccountType(),man.cuentas[0].user):
        print(i)

