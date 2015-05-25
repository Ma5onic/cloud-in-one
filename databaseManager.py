import dataset
from log import Logger


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
        else:
            row = files_table.find_one(internal_path=path.lower())
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
