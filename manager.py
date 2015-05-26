import json
import dataset
import datetime
import threading
from log import Logger
import dropboxAccount
from fileSystemModule import FileSystemModule
from exceptions import RetryException, FullStorageException, APILimitedException, UnknownError


config_file = "config/config.json"


class Manager(threading.Thread):
    """Manager of the Cloud-In-One application.
    It is responsible for the control flow and coordination of components"""
    def __init__(self, user, password, event=None, lock=None, config=None, finish=None):
        threading.Thread.__init__(self)
        self.__initLocks(event, lock, finish)

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

        database_file = self.config["database"]
        from os import makedirs
        import os.path
        database_dir = os.path.dirname(database_file)
        if database_dir and not os.path.isdir(database_dir):
            makedirs(database_dir)
        self.database = self.connectDB(database_file)

        self.fileSystemModule = FileSystemModule(self.config["sync_folder_name"])

        self.cuentas = self.getAccounts()

        #TODO: inicializar los módulos de seguridad y FS
        self.securityModule = None

    def __initLocks(self, event, lock, finish):
        if not event:
            event = threading.Event()
        self.event = event

        if not finish:
            finish = threading.Event()
        self.finish = finish

        if not lock:
            lock = threading.Lock()
        self.lock = lock

    def __CreateAccount(self, type, user):
        if type is "dropbox":
            return dropboxAccount.DropboxAccount(self.fileSystemModule, user)
        elif type is "dropbox_stub":
            return dropboxAccount.DropboxAccountStub(self.fileSystemModule, user)

    def newAccount(self, type, user):
        self.logger.info("Adding new account")
        self.logger.debug("type = %s", type)
        self.logger.debug("user = %s", user)

        try:
            newAcc = self.__CreateAccount(type, user)
            self.cuentas.append(newAcc)
            self.saveAccount(newAcc)

            #TODO: Do whatever it's needed to add a new account
            return True
        except UnknownError as e:
            self.logger.error("Cannot create the new account")
            self.logger.exception(e)
            return False

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

        remoteChanges = self.findRemoteChanges()
        localChanges = self.findLocalChanges()

        changesOnLocal, changesOnDB, changesOnRemote = self.fixCollisions(localChanges, remoteChanges)

        self.syncAccounts(changesOnLocal, changesOnDB, changesOnRemote)
        for i in self.cuentas:
            try:
                i.updateAccountInfo()
                self.saveAccount(i)
            except UnknownError as e:
                self.logger.error("Error updating account information.")
                self.logger.exception(e)

    def syncAccounts(self, changesOnLocal, changesOnDB, changesOnRemote):
        self.applyChangesOnRemote(changesOnRemote)
        self.applyChangesOnLocal(changesOnLocal)
        self.applyChangesOnDB(changesOnDB)

    def findRemoteChanges(self):
        self.logger.info('Getting Remote differences')
        remoteChanges = []

        longpoll = True
        for account in self.cuentas:
            self.logger.debug('Account <' + str(account) + '>')
            deltaDict = None
            try:
                deltaDict = account.delta(longpoll=longpoll)
                self.logger.debug(deltaDict)
            except UnknownError as first:
                self.logger.warn("Error when calling delta. Retrying once")
                try:
                    deltaDict = account.delta(longpoll=longpoll)
                    self.logger.debug(deltaDict)
                except UnknownError:
                    self.logger.error("Error when calling delta for account <" + str(account) + ">")
                    self.logger.exception(first)
                    continue

            if deltaDict:
                longpoll = False

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
                        old_revision = self.getRevisionDB(metadata['path'])
                        if old_revision != metadata['rev'] or deltaDict['reset']:
                            newChange = {'path': metadata['path'], 'hash': 'MISSING', 'account': account, 'revision': metadata['rev'], 'size': metadata['bytes']}

                            old_account = self.getAccountFromFile(metadata['path'])
                            if old_account and old_account != account:
                                self.__remote_conflicted_copy(newChange)

                            remoteChanges.append(newChange)

                else:  # delete path
                    remoteChanges.append({'path': filePath, 'hash': None, 'account': account})

        self.logger.debug(remoteChanges)
        return remoteChanges

    def __fixAutoCollisions(self, changeList):
        self.logger.debug('changeList <' + str(changeList) + '>')

        elementsToDel = []

        for i, change in enumerate(changeList):
            collided_tuple = next(((j, item) for j, item in enumerate(changeList) if item['path'] == change['path'] and i != j), None)
            if collided_tuple:
                collided_i = collided_tuple[0]
                collided = collided_tuple[1]
                self.logger.debug('Found collision! <' + change['path'] + '>')

                if change in elementsToDel or collided in elementsToDel:
                    self.logger.debug('Already going to remove it! <' + change['path'] + '>')
                    continue

                if collided['hash']:  # one created/modified
                    if change['hash']:  # the other too!
                        try:
                            if change['account'] != collided['account']:  # they come from different places
                                self.__remote_conflicted_copy(change)
                            else:  # they come from the same place
                                self.logger.warn("Same file changed twice in the same changelist. That's a bug")
                                elementsToDel.append(collided)
                        except KeyError:  # That should be a bug...
                            self.logger.error("Same file changed twice in a bad way. That's a bug")
                            raise StopIteration('Same file changed twice in a bad way')

                    else:  # change is a deletion
                        self.logger.debug('Deleted and modified, keeping modification')
                        elementsToDel.append(change)
                else:  # collided is a deletion
                    if change['hash']:  # the other is not
                        self.logger.debug('Deleted and modified, keeping modification')
                        elementsToDel.append(collided)
                    else:
                        self.logger.debug('Both deleted, keeping only one')
                        elementsToDel.append(collided)

        self.logger.debug('elementsToDel <' + str(elementsToDel) + '>')

        for i in elementsToDel:
            changeList.remove(i)

        self.logger.debug('changeList <' + str(changeList) + '>')

        return changeList

    def __remote_conflicted_copy(self, change):
        self.logger.debug("CONFLICTED COPY")
        date = datetime.date.today()
        oldpath = change['path']
        newname = oldpath+'__CONFLICTED_COPY__FROM_' + str(change['account']) + '_' + date.isoformat()
        self.logger.debug('Both modified. New name = <' + newname + '>')
        change['path'] = newname
        change['oldpath'] = oldpath
        change['remote_move'] = True
        self.logger.debug(change)

    def __conflicted_copy(self, change_info):
        date = datetime.date.today()
        oldpath = change_info['path']
        newname = oldpath+'__CONFLICTED_COPY__'+date.isoformat()
        i = 1
        while self.existsPathDB(newname):
            newname += '_' + str(i)
            i += 1
        self.logger.debug('Both modified. New name = <' + newname + '>')
        change_info['path'] = newname
        change_info['oldpath'] = oldpath
        self.applyChangesOnLocal([change_info])

    def fixCollisions(self, localChanges, remoteChanges):
        self.logger.info('fixCollisions')
        self.logger.debug('localChanges <' + str(localChanges) + '>')
        self.logger.debug('remoteChanges <' + str(remoteChanges) + '>')

        localChanges = self.__fixAutoCollisions(localChanges)
        remoteChanges = self.__fixAutoCollisions(remoteChanges)

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
                        try:
                            if local['revision'] == collided['revision']:  # same change...
                                self.logger.debug('Both modified in the same way. Keeping local changes')
                                changesOnDB.append(collided)  # TODO: WTF!?
                            else:
                                raise KeyError
                        except(KeyError):
                            self.__conflicted_copy(local)
                            # localChanges.append(local)
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
                self.logger.debug("Didn't collide. <" + local['path'] + ">")
                changesOnDB.append(local)
                changesOnRemote.append(local)

        # remoteChanges that weren't present in localChanges
        changesOnLocal += remoteChanges
        changesOnDB += remoteChanges
        changesOnRemote += [change for change in remoteChanges if 'remote_move' in change]

        self.logger.debug('changesOnLocal <' + str(changesOnLocal) + '>')
        self.logger.debug('changesOnDB <' + str(changesOnDB) + '>')
        self.logger.debug('changesOnRemote <' + str(changesOnRemote) + '>')

        changesOnLocal = self.__fixAutoCollisions(changesOnLocal)
        changesOnDB = self.__fixAutoCollisions(changesOnDB)
        changesOnRemote = self.__fixAutoCollisions(changesOnRemote)
        changesOnLocal = [item for item in changesOnLocal if item['hash'] is None] + [item for item in changesOnLocal if item['hash'] is not None]
        changesOnDB = [item for item in changesOnDB if item['hash'] is None] + [item for item in changesOnDB if item['hash'] is not None]
        changesOnRemote = [item for item in changesOnRemote if item['hash'] is None] + [item for item in changesOnRemote if item['hash'] is not None]

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
                    size = self.fileSystemModule.getFileSize(checking['path'])
                    localChanges.append(dict(path=checking['path'], hash=md5, account=checking['account'], revision=checking['revision'], size=size))

                else:
                    self.logger.debug('The file <' + checking['path'] + '> is the same. Doing nothing')
                fileList.remove(checking['path'])

            else:
                self.logger.debug('The file <' + checking['path'] + '> has been DELETED')
                localChanges.append(dict(path=checking['path'], hash=None, account=checking['account']))

        for element in fileList:
            self.logger.debug('The file <' + element + '> has been CREATED')
            md5 = self.fileSystemModule.md5sum(element)
            size = self.fileSystemModule.getFileSize(element)
            localChanges.append(dict(path=element, hash=md5, size=size))

        self.logger.debug('localChanges = <' + str(localChanges) + '>')
        return localChanges

    def applyChangesOnRemote(self, changesOnRemote):
        self.logger.info("Applying changes on remote")
        for i, element in enumerate(changesOnRemote):
            try:
                if element['hash']:  # created or modified, upload to account
                    if 'account' not in element or not element['account']:  # if newly created
                        fits_account = self.fitToNewAccount(element)
                        if not fits_account:  # doesn't fit! We log it and continue with the others.
                            self.logger.error("The file <" + element['path'] + "> doesn't fit anywhere")
                            element['account'] = None
                            continue

                    revision = None
                    if 'remote_move' in element:  # rename
                        try:
                            self.logger.debug("Renaming file <" + element['oldpath'] + "> to <" + element['path'] + "> in account <" + str(element['account']) + ">")
                            revision = element['account'].renameFile(element['oldpath'], element["path"])  # TODO: Aquí tendré que encriptar el fichero...
                        except FileExistsError:
                            element['path'] += '_2'
                            changesOnRemote.insert(i+1, element)
                            continue
                    else:  # normal upload
                        try:
                            self.logger.debug("Uploading file <" + element['path'] + "> to account <" + str(element['account']) + ">")
                            revision = element['account'].uploadFile(element["path"], element.get('revision'))  # TODO: Aquí tendré que encriptar el fichero...
                        except FullStorageException:  # si no cabe en la cuenta...
                            old_account = self.getAccountFromFile(element['path'])
                            fits_account = self.fitToNewAccount(element)
                            if fits_account:
                                if old_account:
                                    try:
                                        old_account.deleteFile(element['path'])
                                    except FileNotFoundError:
                                        self.logger.warn("File already deleted")
                                    except Exception as e:
                                        self.logger.exception(e)
                                raise RetryException
                            else:
                                element['account'] = None

                    element['revision'] = revision

                else:  # deleted, remove from the remote
                    if element['account']:
                        self.logger.debug("Deleting file <" + element['path'] + ">")
                        element['account'].deleteFile(element['path'])
                    else:
                        self.logger.warn("Trying to remove a file without account")

            except RetryException:
                self.logger.debug("Adding to the current list to retry")
                changesOnRemote.insert(i+1, element)
            except FileNotFoundError as e:
                self.logger.error("File not found in the remote account")
                self.logger.exception(e)
            except UnknownError as unknown:
                self.logger.exception(unknown)
                self.logger.error("Unknown Error. Setting account quota to 0 to prevent new uploads")  # will be reset at the end of the sync
                element['account'].free_quota = 0
                element['account'] = None  # applyDB will ignore it
                self.logger.debug("Adding to the current list to retry")
                changesOnRemote.insert(i+1, element)

    def fitToNewAccount(self, element):
        current_account = element.get('account', None)
        for account in self.cuentas:
            if account is current_account:
                continue

            self.logger.debug("Trying to fit file <" + element['path'] + "> in account <" + str(account) + ">")
            if account.fits(element['size']):
                self.logger.debug("It fits in account <" + str(account) + ">")
                element['account'] = account
                return True
            else:
                self.logger.debug("Doesn't fit! <" + str(element['path']) + ">")

        return False

    def applyChangesOnDB(self, changesOnDB):
        self.logger.info("Applying changes on database")
        self.logger.debug(changesOnDB)
        for element in changesOnDB:
            if 'account' not in element or not element['account']:  # if it doesn't have account, ignore it
                self.logger.warn("The file <" + element['path'] + "> doesn't have account")
                continue

            if element['hash']:  # created or modified, upsert in the db
                if element['hash'] == 'MISSING':
                    element['hash'] = self.fileSystemModule.md5sum(element['path'])
                self.saveFile(element)

            else:  # deleted, remove from the db
                self.deleteFileDB(element['path'], element['account'])

    def applyChangesOnLocal(self, changesOnLocal):
        self.logger.info("Applying changes on local")
        self.logger.debug(changesOnLocal)
        for i, element in enumerate(changesOnLocal):
            if 'oldpath' in element and not 'remote_move' in element:  # rename
                try:
                    self.fileSystemModule.renameFile(element["oldpath"], element["path"])
                except FileExistsError:
                    self.logger.debug("<" + element["path"] + "> Already exists, trying with <" + element["path"] + "_2" + ">")
                    element['path'] = element['path'] + '_2'
                    changesOnLocal.insert(i+1, element)
                    continue

            elif element['hash']:  # created or modified
                try:
                    self.logger.debug("Downloading file <" + element['path'] + ">")
                    streamFile = element['account'].getFile(element["path"])  # TODO: Aquí tendré que DESencriptar el fichero...
                    self.fileSystemModule.createFile(element["path"], streamFile)
                    streamFile.close()
                except FileNotFoundError as e:
                    self.logger.error("File not found in the remote. Deleting it")
                    self.logger.exception(e)
                    element['hash'] = None

            else:  # deleted
                cased_path = self.getCasedPath(element['path'], element['account'])
                if not cased_path:
                    continue
                self.logger.debug("Deleting file <" + cased_path + ">")
                self.fileSystemModule.remove(cased_path)

    def getMD5BD(self, filename):
        files_table = self.database['files']
        row = files_table.find_one(internal_path=filename.lower())
        return row['hash']

    def getRevisionDB(self, filename):
        files_table = self.database['files']
        row = files_table.find_one(internal_path=filename.lower())
        if row:
            return row['revision']
        else:
            return None

    def getCasedPath(self, path, account):
        files_table = self.database['files']
        row = files_table.find_one(internal_path=path.lower(), accountType=account.getAccountType(), user=account.user)
        if row:
            return row['path']
        else:
            return None

    def getFileSizeDB(self, path):
        files_table = self.database['files']
        row = files_table.find_one(internal_path=path.lower())
        if row:
            return row['size']
        else:
            return None

    # TODO: generalize
    def getAccounts(self):
        accounts_table = self.database['accounts']
        accounts_data = accounts_table.all()
        cuentas_list = []
        for acc in accounts_data:
            if acc["accountType"] == 'dropbox':
                cuentas_list.append(dropboxAccount.DropboxAccount(self.fileSystemModule, acc['user'], access_token=acc['token'], user_id=acc['userid'], cursor=acc['cursor'], email=acc['email']))

        return cuentas_list

    def getAccountFromFile(self, path):
        files_table = self.database['files']
        row = files_table.find_one(internal_path=path.lower())
        account = None
        if row:
            account = next((cuenta for cuenta in self.cuentas if cuenta.getAccountType() == row['accountType'] and cuenta.user == row['user']), None)
        return account

    def saveAccount(self, account):
        accounts_table = self.database['accounts']
        accounts_table.upsert(dict(accountType=account.getAccountType(), user=account.user, token=account.access_token, userid=account.user_id, cursor=account.last_cursor, email=account.email), ['accountType', 'user'])

    def deleteAccountDB(self, account):
        accounts_table = self.database['accounts']
        accounts_table.delete(accountType=account.getAccountType(), user=account.user)

    def remove(self, path, account):
        self.fileSystemModule.remove(path)
        self.deleteFileDB(path, account)

    def deleteFileDB(self, path, account=None):
        self.logger.debug('deleting file <' + path + '>')
        files_table = self.database['files']
        if account:
            files_table.delete(internal_path=path.lower(), accountType=account.getAccountType(), user=account.user)
        else:
            files_table.delete(internal_path=path.lower())


    def saveFile(self, element):
        size = element['size']
        account = element['account']
        path = element['path']
        file_hash = element['hash']
        self.logger.debug('saving file <' + path + '> with hash <' + str(file_hash) + '> to account <' + account.getAccountType() + ', ' + account.user + '>')
        files_table = self.database['files']
        files_table.upsert(dict(accountType=account.getAccountType(), user=account.user, path=path, internal_path=path.lower(), hash=file_hash, revision=element['revision'], size=size), ['internal_path'])
        # TODO: check if can be inserted and this...
        return True

    def existsPathDB(self, newname):
        files_table = self.database['files']
        files = files_table.find(internal_path=newname.lower())
        if list(files):
            return True
        else:
            return False

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
        return [{'path': element['path'], 'hash': element['hash'], 'account': account, 'revision': element['revision']} for element in files]

    def listAccounts(self):
        return (str(i) for i in self.cuentas)

    def run(self):
        timeout = 300.0
        while not self.finish.is_set():
            if self.event.is_set():
                self.event.clear()

                self.logger.debug("Acquiring lock")
                self.lock.acquire()
                self.logger.debug("Lock acquired")

                self.updateLocalSyncFolder()

                self.logger.debug("Releasing lock")
                self.lock.release()
                self.logger.debug("Lock released")

            self.logger.debug("Waiting " + str(timeout) + " seconds or until forced by menu")
            self.event.wait(timeout)
            self.event.set()
            self.logger.debug("Awaken")
