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
    def __init__(self, user, password, config=None):
        self.logger = Logger(__name__)
        self.logger.info("Creating Manager")

        self.user = user
        self.password = password

        if not config:
            self.config = json.load(open(config_file))
        else:
            self.config = config

        self.logger.info("Loaded config file")
        self.logger.debug("===== Config contents: ======")
        self.logger.debug(self.config)
        self.logger.debug("===== END Config contents: ======")

        self.database = self.connectDB(self.config["database"])

        self.fileSystemModule = FileSystemModule(self.config["sync_folder_name"])

        self.cuentas = self.getAccounts()

        #TODO: inicializar los módulos de seguridad y FS
        self.securityModule = None

    def __CreateAccount__(self, type, user):
        if type is "dropbox":
            return dropboxAccount.DropboxAccount(self.fileSystemModule, user)
        elif type is "dropbox_stub":
            return dropboxAccount.DropboxAccountStub(self.fileSystemModule, user)

    def newAccount(self, type, user):
        self.logger.info("Adding new account")
        self.logger.debug("type = %s", type)
        self.logger.debug("user = %s", user)

        newAcc = self.__CreateAccount__(type, user)
        self.cuentas.append(newAcc)
        self.saveAccount(newAcc)

        #TODO: Do whatever it's needed to add a new account
        return True

    def deleteAccount(self, account):
        self.logger.info("Deleting account")
        self.logger.debug("account = %s", account)

        self.deleteAccountDB(account)
        self.cuentas.remove(account)
        #TODO: Do things to delete an account
        return True

    def updateLocalSyncFolder(self, folder="/"):
        self.logger.info("Updating sync folder")
        self.logger.debug("Folder = <" + folder + ">")

        localChanges = self.findLocalChanges()
        remoteChanges = self.findRemoteChanges()

        changesOnLocal, changesOnDB, changesOnRemote = self.fixCollisions(localChanges, remoteChanges)

        self.syncAccounts(changesOnLocal, changesOnDB, changesOnRemote)

    def syncAccounts(self, changesOnLocal, changesOnDB, changesOnRemote):
        self.applyChangesOnLocal(changesOnLocal)
        self.applyChangesOnRemote(changesOnRemote)
        self.applyChangesOnDB(changesOnDB)

    def findRemoteChanges(self):
        self.logger.info('Getting Remote differences')
        remoteChanges = []
        for account in self.cuentas:
            self.logger.debug('Account <' + str(account) + '>')
            deltaDict = account.delta()
            self.logger.debug(deltaDict)
            if deltaDict['reset']:
                self.logger.debug('Reset recieved. Resetting account <' + str(account) + '>')
                resetChanges = self.getFiles(account)
                for i in resetChanges:
                    i['hash'] = None
                remoteChanges += resetChanges

            for filePath, metadata in deltaDict['entries']:
                self.logger.debug('filePath <' + str(filePath) + '> metadata <' + str(metadata) + '>')
                if metadata:  # create/edit path
                    if metadata["is_dir"]:
                        self.logger.debug('is_dir = True')
                    else:
                        self.logger.debug('is_dir = False')
                        remoteChanges.append({'path': metadata['path'], 'hash': 'MISSING', 'account': account})

                else:  # delete path
                    remoteChanges.append({'path': filePath, 'hash': None, 'account': account})

        self.logger.debug(remoteChanges)
        return remoteChanges

    def __fixAutoCollisions__(self, changeList):
        self.logger.debug('changeList <' + str(changeList) + '>')

        indexesToRemove = []

        for i, change in enumerate(changeList):
            collided_tuple = next(((j, item) for j, item in enumerate(changeList) if item['path'] == change['path'] and i != j), None)
            if collided_tuple:
                collided_i = collided_tuple[0]
                collided = collided_tuple[1]
                self.logger.debug('Found collision! <' + change['path'] + '>')

                if i in indexesToRemove or collided_i in indexesToRemove:
                    self.logger.debug('Already going to remove it! <' + change['path'] + '>')
                    continue

                if collided['hash']:  # one created/modified
                    if change['hash']:  # the other too!
                        if collided['hash'] == change['hash']:  # same change...
                            self.logger.warn("Same change twice in the same changeList. There's a bug there...")
                            indexesToRemove.append(collided_i)
                        else:  # different change...
                            self.logger.error("Same file changed in two different ways in the same changeList.")
                            raise StopIteration("Same file changed in two different ways in the same changeList." + str(change) + " vs " + str(collided))
                    else:  # change is a deletion
                        self.logger.debug('Deleted and modified, keeping modification')
                        indexesToRemove.append(i)
                else:  # collided is a deletion
                    if change['hash']:  # the other is not
                        self.logger.debug('Deleted and modified, keeping modification')
                        indexesToRemove.append(collided_i)
                    else:
                        self.logger.debug('Both deleted, keeping only one')
                        indexesToRemove.append(collided_i)

        self.logger.debug('indexesToRemove <' + str(indexesToRemove) + '>')

        for i in indexesToRemove:
            del(changeList[i])

        self.logger.debug('changeList <' + str(changeList) + '>')

        return changeList

    def fixCollisions(self, localChanges, remoteChanges):
        self.logger.info('fixCollisions')
        self.logger.debug('localChanges <' + str(localChanges) + '>')
        self.logger.debug('remoteChanges <' + str(remoteChanges) + '>')

        localChanges = self.__fixAutoCollisions__(localChanges)
        remoteChanges = self.__fixAutoCollisions__(remoteChanges)

        self.logger.debug('localChanges <' + str(localChanges) + '>')
        self.logger.debug('remoteChanges <' + str(remoteChanges) + '>')

        changesOnLocal = []
        changesOnDB = []
        changesOnRemote = []

        for i, local in enumerate(localChanges):
            collided = next((item for item in remoteChanges if item['path'] == local['path']), None)
            if collided:
                self.logger.debug('Found collision! <' + local['path'] + '>')
                if collided['hash']:  # remote created/modified
                    if local['hash']:  # AND local created/modified!
                        if local['hash'] == collided['hash']:  # same change...
                            self.logger.debug('Both modified in the same way. Keeping local changes')
                            changesOnDB.append(collided)
                        else:
                            date = datetime.date.today()
                            oldpath = local['path']
                            newname = oldpath+'__CONFLICTED_COPY__'+date.isoformat()
                            self.logger.debug('Both modified. New name = <' + newname + '>')
                            local['path'] = newname
                            local['oldpath'] = oldpath

                            changesOnLocal.append(local)
                            changesOnLocal.append(collided)
                            changesOnDB.append(local)
                            changesOnDB.append(collided)
                            changesOnRemote.append(local)

                    else:  # local deletion, remote modification, we keep the remote changes.
                        self.logger.debug('Deleted locally, keeping remote changes')
                        changesOnLocal.append(collided)
                        changesOnDB.append(collided)
                else:  # in case of remote deletion, we keep the local changes
                    if local['hash']:
                        self.logger.debug('Deleted remotely, but modified locally, keeping local changes')
                        changesOnRemote.append(local)
                    changesOnDB.append(local)

                remoteChanges.remove(collided)  # We remove it from the remoteChanges

            else:
                self.logger.debug("Didn't collide. Uploading <" + local['path'] + ">")
                changesOnDB.append(local)
                changesOnRemote.append(local)

        # remoteChanges that weren't present in localChanges
        changesOnLocal += remoteChanges
        changesOnDB += remoteChanges
        


        self.logger.debug('changesOnLocal <' + str(changesOnLocal) + '>')
        self.logger.debug('changesOnDB <' + str(changesOnDB) + '>')
        self.logger.debug('changesOnRemote <' + str(changesOnRemote) + '>')

        changesOnLocal = self.__fixAutoCollisions__(changesOnLocal)
        changesOnDB = self.__fixAutoCollisions__(changesOnDB)
        changesOnRemote = self.__fixAutoCollisions__(changesOnRemote)

        self.logger.debug('changesOnLocal <' + str(changesOnLocal) + '>')
        self.logger.debug('changesOnDB <' + str(changesOnDB) + '>')
        self.logger.debug('changesOnRemote <' + str(changesOnRemote) + '>')

        return (changesOnLocal, changesOnDB, changesOnRemote)

    def findLocalChanges(self):
        self.logger.info('Getting Local differences')
        fileList = self.fileSystemModule.getFileList()

        toCheck = []
        for i in self.cuentas:
            toCheck += self.getFiles(i)

        localChanges = []
        for checking in toCheck:
            if checking['path'] in fileList:
                md5 = self.fileSystemModule.md5sum(checking['path'])
                if md5 != checking['hash']:
                    self.logger.debug('The file <' + checking['path'] + '> has been MODIFIED')
                    localChanges.append(dict(path=checking['path'], hash=md5, account=checking['account']))

                else:
                    self.logger.debug('The file <' + checking['path'] + '> is the same. Doing nothing')
                fileList.remove(checking['path'])

            else:
                self.logger.debug('The file <' + checking['path'] + '> has been DELETED')
                localChanges.append(dict(path=checking['path'], hash=None, account=checking['account']))

        for element in fileList:
            self.logger.debug('The file <' + element + '> has been CREATED')
            md5 = self.fileSystemModule.md5sum(element)
            localChanges.append(dict(path=element, hash=md5))

        self.logger.debug('localChanges = <' + str(localChanges) + '>')
        return localChanges

    def applyChangesOnRemote(self, changesOnRemote):
        self.logger.info("Applying changes on remote")
        for element in changesOnRemote:
            if element['hash']:  # created or modified, upload to account
                if 'account' not in element or not element['account']:  # if newly created
                    for account in self.cuentas:
                        self.logger.debug("Trying to save file <" + element['path'] + "> in account <" + str(account) + ">")
                        if account.fits(element['path']):
                            element['account'] = account

                self.logger.debug("Uploading file <" + element['path'] + "> to account <" + str(element['account']) + ">")
                element['account'].uploadFile(element["path"])  # TODO: Aquí tendré que encriptar el fichero...

            else:  # deleted, remove from the remote
                self.logger.debug("Deleting file <" + element['path'] + ">")
                element['account'].deleteFile(element['path'])

    def applyChangesOnDB(self, changesOnDB):
        self.logger.info("Applying changes on database")
        for element in changesOnDB:
            if element['hash']:  # created or modified, upsert in the db
                md5 = self.fileSystemModule.md5sum(element['path'])
                self.saveFile(element['account'], element['path'], md5)

            else:  # deleted, remove from the db
                self.deleteFileDB(element['path'], element['account'])

    def applyChangesOnLocal(self, changesOnLocal):
        self.logger.info("Applying changes on local")
        for element in changesOnLocal:
            if element['hash']:  # created or modified
                streamFile = element['account'].getFile(element["path"])  # TODO: Aquí tendré que DESencriptar el fichero...
                self.fileSystemModule.createFile(element["path"], streamFile)
                streamFile.close()

            else:  # deleted
                self.logger.debug("Deleting file <" + element['path'] + ">")
                self.fileSystemModule.remove(element['path'])

    def getMD5BD(self, filename):
        files_table = self.database['files']
        row = files_table.find_one(path=filename)
        return row['hash']

    # TODO: generalize
    def getAccounts(self):
        accounts_table = self.database['accounts']
        accounts_data = accounts_table.all()
        cuentas_list = []
        for acc in accounts_data:
            if acc["accountType"] == 'dropbox':
                cuentas_list.append(dropboxAccount.DropboxAccount(self.fileSystemModule, acc['user'], acc['token'], acc['userid']))

        return cuentas_list

    def getAccountFromFile(self, path):
        files_table = self.database['files']
        row = files_table.find_one(path=path)
        account = None
        if row:
            account = next((cuenta for cuenta in self.cuentas if cuenta.getAccountType() == row['accountType'] and cuenta.user == row['user']), None)
        return account

    def saveAccount(self, account):
        accounts_table = self.database['accounts']
        accounts_table.upsert(dict(accountType=account.getAccountType(), user=account.user, token=account.access_token, userid=account.user_id), ['accountType', 'user'])

    def deleteAccountDB(self, account):
        accounts_table = self.database['accounts']
        accounts_table.delete(accountType=account.getAccountType(), user=account.user)

    def remove(self, path, account):
        self.fileSystemModule.remove(path)
        self.deleteFileDB(path, account)

    def deleteFileDB(self, path, account=None):
        self.logger.debug('deleting file <' + path + '>')
        files_table = self.database['files']
        files_table.delete(path=path)

    def saveFile(self, account, path, file_hash=None):
        self.logger.debug('saving file <' + path + '> with hash <' + str(file_hash) + '> to account <' + account.getAccountType() + ', ' + account.user + '>')
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
        self.logger.debug('filesPaths for account <' + account + ', ' + user + '> = ' + str(filesPaths))
        return filesPaths

    def getFiles(self, account):
        files_table = self.database['files']
        files = files_table.find(accountType=account.getAccountType(), user=account.user)
        return [{'path': element['path'], 'hash': element['hash'], 'account': account} for element in files]


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
    for i in man.getFilesPaths(man.cuentas[0].getAccountType(), man.cuentas[0].user):
        print(i)
