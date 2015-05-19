import account
import dropbox
import os
from log import *
from fileSystemModule import FileSystemModule
from dropbox.rest import ErrorResponse

app_key = os.getenv("APP_KEY")
app_secret = os.getenv("APP_SECRET")
TOKEN_FILE = "config/dropbox_token.txt"


class DropboxAccount(account.Account):
    """docstring for DropboxAccount"""
    def __init__(self, fileSystemModule, user, cursor=None, access_token=None, user_id=None):
        self.logger = Logger(__name__)
        self.logger.info("Creating Dropbox Account")
        self.fileSystemModule = fileSystemModule
        self.user = user
        self.access_token = access_token
        self.user_id = user_id
        self.last_cursor = cursor
        self.email = ''
        self.free_quota = 0
        # You shouldn't use self.__client, call __getDropboxClient() to get it safely
        self.__client = None
        self.__client = self.__getDropboxClient()
        self.getFreeSpace()

    def __startOAuthFlow(self):
        self.logger.info("starting OAuth Flow")
        self.logger.debug("Token not found, asking for one")
        flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
        # Have the user sign in and authorize this token
        authorize_url = flow.start()
        print('1. Go to: ' + authorize_url)
        print('2. Click "Allow" (you might have to log in first)')
        print('3. Copy the authorization code.')
        code = input("Enter the authorization code here: ").strip()
        self.access_token, self.user_id = flow.finish(code)
        self.updateAccountInfo()

    def __getDropboxClient(self):
        self.logger.info("Getting Dropbox Client")
        self.logger.debug("__client <" + str(self.__client) + ">")
        if self.__client is None:
            self.logger.debug("access_token =<" + str(self.access_token) + ">, user_id =<" + str(self.user_id) + ">")
            if self.access_token is None or self.user_id is None:
                self.__startOAuthFlow()
            self.logger.debug("Creating Client. Token = <" + str(self.access_token) + "> user_id = <" + str(self.user_id) + ">")
            self.__client = dropbox.client.DropboxClient(self.access_token)

        return self.__client

    def getUserInfo(self):
        client = self.__getDropboxClient()
        self.logger.info("Getting User Info")
        self.logger.info("INFO:")
        try:
            user_info = client.account_info()
            self.logger.info(user_info)
        except ErrorResponse:
            raise RuntimeError()

    def updateAccountInfo(self):
        client = self.__getDropboxClient()
        self.logger.info("Getting account information")
        try:
            account_info = client.account_info()

            quota_info = account_info['quota_info']
            self.free_quota = quota_info['quota'] - quota_info['normal'] - quota_info['shared']
            self.logger.debug("Remaining space = <" + str(self.free_quota) + "> bytes")

            self.email = account_info['email']
            self.logger.debug("Email = <" + str(self.email) + ">")
        except ErrorResponse:
            raise RuntimeError()

    def getFreeSpace(self):
        client = self.__getDropboxClient()
        self.logger.info("Getting remaining space")
        try:
            quota_info = client.account_info()['quota_info']
            quota = quota_info['quota']
            normal_used = quota_info['normal']
            shared_used = quota_info['shared']

            self.free_quota = quota - normal_used - shared_used
            self.logger.debug("Remaining space = <" + str(self.free_quota) + "> bytes")
        except ErrorResponse:
            raise RuntimeError()

    def getMetadata(self, folder):
        client = self.__getDropboxClient()
        self.logger.info("Getting metadata from <" + folder + ">")
        try:
            metadata = client.metadata(folder)
            # for now, it will return all what Dropbox sends, but as we move forward we will return a custom metadata dict
            return metadata
        except ErrorResponse:
            raise RuntimeError()

    def delta(self, returnDict=None):
        client = self.__getDropboxClient()
        self.logger.info("Calling delta")
        self.logger.debug("Last cursor = <" + str(self.last_cursor) + ">")
        if not returnDict:
            returnDict = dict()
            returnDict["entries"] = []
            returnDict["reset"] = False

        try:
            deltaDict = client.delta(cursor=self.last_cursor)
            self.last_cursor = deltaDict["cursor"]
            self.logger.debug(deltaDict)

            returnDict["entries"] += deltaDict["entries"]
            returnDict["reset"] = deltaDict["reset"]

            if deltaDict["has_more"]:
                delta(returnDict)

            self.logger.debug("returnDict = <" + str(returnDict) + ">")
            return returnDict
        except ErrorResponse:
            raise RuntimeError()

    def getFile(self, file_path):
        client = self.__getDropboxClient()
        self.logger.info("Calling getFile")
        self.logger.debug("file_path = <" + file_path + ">")
        try:
            outputFile = client.get_file(file_path)
            self.logger.debug("outputFile = <" + str(outputFile) + ">")
            return outputFile
        except ErrorResponse:
            raise RuntimeError()

    def getAccountType(self):
        return "dropbox"

    def uploadFile(self, file_path, rev):
        client = self.__getDropboxClient()
        self.logger.info("Calling uploadFile")
        self.logger.debug("file_path = <" + file_path + ">")

        stream = self.fileSystemModule.openFile(file_path)
        try:
            response = client.put_file(file_path, stream, parent_rev=rev)
            self.logger.debug("Response = <" + str(response) + ">")
            self.fileSystemModule.closeFile(file_path, stream)
            return response['rev']
        except ErrorResponse:
            raise RuntimeError()

    def renameFile(self, oldpath, newpath):
        client = self.__getDropboxClient()
        self.logger.info("Calling renameFile")
        self.logger.debug("renaming <" + oldpath + "> to <" + newpath + ">")

        try:
            response = client.file_move(oldpath, newpath)
            self.logger.debug("Response = <" + str(response) + ">")
            return response['rev']
        except ErrorResponse:
            raise RuntimeError()

    def deleteFile(self, file_path):
        client = self.__getDropboxClient()
        self.logger.info("Calling deleteFile")
        self.logger.debug("file_path = <" + file_path + ">")

        try:
            response = client.file_delete(file_path)
            return True
        except ErrorResponse:
            raise RuntimeError()

    def fits(self, file_size):
        return file_size <= self.free_quota

    def __repr__(self):
        return self.getAccountType() + '-' + self.user + ''


class DropboxAccountStub(DropboxAccount):
    """Stub for testing the DBAccount"""
    def __init__(self, fileSystemModule, user):
        # super(DropboxAccountStub, self).__init__(user)
        self.logger = Logger(__name__)
        self.logger.info("Creating Dropbox Account")
        self.fileSystemModule = fileSystemModule
        self.user = user
        self.email = user + '@mail.com'
        self.access_token = None
        self.user_id = None
        self.last_cursor = None

        # You shouldn't use self.__client, call __getDropboxClient() to get it safely
        self.__client = None

        self.free_quota = 100
        self.__file_list__ = []
        self.__delta_acum__ = []
        self._delta_reset_ = False

    def __getDropboxClient(self):
        return None

    def getUserInfo(self):
        self.logger.info("Getting User Info")
        self.logger.info("INFO:")
        #self.logger.info(self.client.account_info())

    def getMetadata(self, folder):
        raise NotImplemented()

    def delta(self, returnDict=dict()):
        returnDict["entries"] = self.__delta_acum__
        self.resetChanges()

        returnDict["reset"] = self._delta_reset_
        return returnDict

    def deltaEmpty(self, returnDict=dict()):
        returnDict["entries"] = []
        returnDict["reset"] = False
        return returnDict

    def getFile(self, file_path):
        for i in self.__file_list__:
            if i == file_path:
                f = open('test/muerte.txt', 'rb')
                return f
        return None

    def getAccountType(self):
        return "dropbox_stub"

    def uploadFile(self, file_path, rev=None):
        if rev:
            size = self.fileSystemModule.getFileSize(file_path)
            if not self.fits(size):
                raise RuntimeError()
        if file_path not in self.__file_list__:
            self.__file_list__.append(file_path)

        if not rev:
            rev = 'revision_number'
        else:
            rev = rev + '1'
        deltaItem = [file_path.lower(), {'is_dir': False, 'path': file_path, 'rev': rev, 'bytes': len(file_path)}]
        if deltaItem not in self.__delta_acum__:
            self.__delta_acum__.append(deltaItem)

        return deltaItem[1]['rev']

    def renameFile(self, oldpath, newpath):
        index = self.__file_list__.index(oldpath)
        self.__file_list__[index] = newpath
        deltaItem = [oldpath.lower(), None]
        self.__delta_acum__.append(deltaItem)
        deltaItem = [newpath.lower(), {'is_dir': False, 'path': newpath, 'rev': 'renamed', 'bytes': len(newpath)}]
        self.__delta_acum__.append(deltaItem)
        return deltaItem[1]['rev']

    def deleteFile(self, file_path):
        if file_path in self.__file_list__:
            self.__file_list__.remove(file_path)
            self.__delta_acum__.append([file_path.lower(), None])
            return True
        return False

    def getFileList(self):
        return self.__file_list__

    def resetChanges(self):
        self.__delta_acum__ = []

    def updateAccountInfo(self):
        pass
