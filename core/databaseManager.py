import dataset
from core.log import Logger


class DatabaseManager(object):
    def __init__(self, database_file):
        super(DatabaseManager, self).__init__()

        self.logger = Logger(__name__)
        self.logger.info("Creating databaseManager")
        self.logger.debug("database_file = <" + database_file + ">")

        from os import makedirs
        import os.path
        database_dir = os.path.dirname(database_file)
        if database_dir and not os.path.isdir(database_dir):
            makedirs(database_dir)
        self.database = self.connectDB(database_file)

    def cleanDatabase(self):
        self.logger.debug("Cleaning database")
        for i in self.database.tables:
            self.database[i].drop()

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

    def getCasedPath(self, path, account=None):
        files_table = self.database['files']
        row = None
        if account:
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
        return accounts_table.all()

    def getAccountFromFile(self, path):
        files_table = self.database['files']
        row = files_table.find_one(internal_path=path.lower())
        return row

    def saveAccount(self, account):
        accounts_table = self.database['accounts']
        accounts_table.upsert(dict(accountType=account.getAccountType(), user=account.user, token=account.access_token, userid=account.user_id, cursor=account.last_cursor, email=account.email), ['accountType', 'user'])

    def deleteAccountDB(self, account):
        accounts_table = self.database['accounts']
        accounts_table.delete(accountType=account.getAccountType(), user=account.user)

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
        encryption = element.get('encryption', False)
        self.logger.debug('saving file <' + path + '> with hash <' + str(file_hash) + '> to account <' + account.getAccountType() + ', ' + account.user + '>')
        files_table = self.database['files']
        files_table.upsert(dict(accountType=account.getAccountType(), user=account.user, path=path, internal_path=path.lower(), hash=file_hash, revision=element['revision'], size=size, encryption=encryption), ['internal_path'])
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
        self.logger.debug("getFiles <" + str(account) + ">")
        files_table = self.database['files']
        files = files_table.find(accountType=account.getAccountType(), user=account.user)
        return [{'path': element['path'], 'hash': element['hash'], 'account': account, 'revision': element['revision']} for element in files]

    def getUser(self, username):
        user_table = self.database['user']

        return user_table.find_one(user=username)

    def getUserCount(self):
        user_table = self.database['user']
        return len(user_table)

    def saveUser(self, username, hash):
        user_table = self.database['user']
        user_table.upsert(dict(id=1, user=username, hash=hash), ['id'])

    def _insertUser(self, username, hash):
        user_table = self.database['user']
        user_table.upsert(dict(user=username, hash=hash), ['id'])

    def markEncriptionDB(self, path, encryption):
        self.logger.debug("markEncriptionDB <" + path + "> -> <" + str(encryption) + ">")
        files_table = self.database['files']
        files_table.upsert(dict(internal_path=path.lower(), encryption=encryption), ['internal_path'])

    def shouldEncrypt(self, path):
        self.logger.debug("Calling shouldEncrypt for <" + path + ">")
        files_table = self.database['files']
        row = files_table.find_one(internal_path=path.lower())
        if row and 'encryption' in row:
            self.logger.debug("Returning <" + str(bool(row['encryption'])) + ">")
            return bool(row['encryption'])
        else:
            self.logger.debug("Returning <False>")
            return False
