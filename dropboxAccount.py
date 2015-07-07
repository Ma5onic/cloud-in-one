import os
import webbrowser
import dropbox
import tempfile
from dropbox.rest import ErrorResponse

from log import *
import account
from exceptions import RetryException, FullStorageException, APILimitedException, UnknownError
from fileSystemModule import FileSystemModule

app_key = os.getenv("APP_KEY")
app_secret = os.getenv("APP_SECRET")
TOKEN_FILE = "config/dropbox_token.txt"


class DropboxAccount(account.Account):
    """docstring for DropboxAccount"""
    def __init__(self, fileSystemModule, user, cursor=None, access_token=None, user_id=None, email=None):
        self.logger = Logger(__name__)
        self.logger.info("Creating Dropbox Account")
        self.fileSystemModule = fileSystemModule
        self.user = user
        self.access_token = access_token
        self.user_id = user_id
        self.last_cursor = cursor
        self.timeout = 30
        self.email = email
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
        webbrowser.open_new(authorize_url)
        print('2. Click "Allow" (you might have to log in first)')
        print('3. Copy the authorization code.')
        code = input("Enter the authorization code here: ").strip()
        self.access_token, self.user_id = flow.finish(code)
        self.updateAccountInfo()

    def __getDropboxClient(self):
        self.logger.info("Getting Dropbox Client")
        self.logger.debug("__client <" + str(self.__client) + ">")
        try:
            if not self.__client:
                self.logger.debug("access_token =<" + str(self.access_token) + ">, user_id =<" + str(self.user_id) + ">")
                if not self.access_token or not self.user_id:
                    self.__startOAuthFlow()
                self.logger.debug("Creating Client. Token = <" + str(self.access_token) + "> user_id = <" + str(self.user_id) + ">")
                self.__client = dropbox.client.DropboxClient(self.access_token)
        except ErrorResponse as error:
            self.__manageException(error)

        return self.__client

    def __manageException(self, error):
        self.logger.error(error)
        if error.status == 401:
            self.access_token = None
            self.__getDropboxClient()
            raise RetryException(error.reason) from error
        elif error.status == 507:
            self.updateAccountInfo()
            raise FullStorageException(error.reason) from error
        elif error.status == 429 or error.status == 503:
            # TODO: wait until API rate gets unlimited
            import time
            time.sleep(60)  # for now, sleep one minute and retry
            raise RetryException(error.reason) from error
            # raise APILimitedException(error.reason) from error
        elif error.status == 403:  # You keep using that status. I do not think it means what you think it means.
            raise FileExistsError(error.reason) from error
        elif error.status == 404:
            raise FileNotFoundError(error.reason) from error
        else:
            raise UnknownError('Other error happened') from error

    def getUserInfo(self):
        client = self.__getDropboxClient()
        self.logger.info("Getting User Info")
        self.logger.info("INFO:")
        try:
            user_info = client.account_info()
            self.logger.info(user_info)
        except ErrorResponse as error:
            self.__manageException(error)

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
        except ErrorResponse as error:
            self.__manageException(error)

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
        except ErrorResponse as error:
            self.__manageException(error)

    def getMetadata(self, folder):
        client = self.__getDropboxClient()
        self.logger.info("Getting metadata from <" + folder + ">")
        try:
            metadata = client.metadata(folder)
            # for now, it will return all what Dropbox sends, but as we move forward we will return a custom metadata dict
            return metadata
        except ErrorResponse as error:
            self.__manageException(error)

    def delta(self, returnDict=None, longpoll=False):
        client = self.__getDropboxClient()
        self.logger.info("Calling delta")
        self.logger.debug("Last cursor = <" + str(self.last_cursor) + ">")
        if not returnDict:
            returnDict = dict()
            returnDict["entries"] = []
            returnDict["reset"] = False

        try:
            if longpoll and self.last_cursor:
                self.logger.info("Waiting for changes in the remote")
                self.logger.debug("Calling longpoll_delta")
                longpoll_dict = client.longpoll_delta(cursor=self.last_cursor, timeout=self.timeout)
                self.logger.debug("longpoll_dict = <" + str(longpoll_dict) + ">")
                if not longpoll_dict['changes']:
                    self.logger.debug("No changes")
                    return returnDict

            self.logger.debug("Calling delta")
            deltaDict = client.delta(cursor=self.last_cursor)
            self.last_cursor = deltaDict["cursor"]
            self.logger.debug(deltaDict)

            returnDict["entries"] += deltaDict["entries"]
            returnDict["reset"] = deltaDict["reset"]

            if deltaDict["has_more"]:
                delta(returnDict)

            self.logger.debug("returnDict = <" + str(returnDict) + ">")
            return returnDict
        except ErrorResponse as error:
            self.__manageException(error)

    def getFile(self, file_path):
        client = self.__getDropboxClient()
        self.logger.info("Calling getFile")
        self.logger.debug("file_path = <" + file_path + ">")
        try:
            outputFile = client.get_file(file_path)
            self.logger.debug("outputFile = <" + str(outputFile) + ">")
            return outputFile
        except ErrorResponse as error:
            self.__manageException(error)

    def getAccountType(self):
        return "dropbox"

    def uploadFile(self, file_path, rev, stream):
        client = self.__getDropboxClient()
        self.logger.info("Calling uploadFile")
        self.logger.debug("file_path = <" + file_path + ">")

        if not stream:
            stream = self.fileSystemModule.openFile(file_path)
        try:
            response = client.put_file(file_path, stream, parent_rev=rev)
            self.logger.debug("Response = <" + str(response) + ">")
            self.fileSystemModule.closeFile(file_path, stream)
            return response['rev']
        except ErrorResponse as error:
            self.__manageException(error)

    def renameFile(self, oldpath, newpath):
        client = self.__getDropboxClient()
        self.logger.info("Calling renameFile")
        self.logger.debug("renaming <" + oldpath + "> to <" + newpath + ">")

        try:
            response = client.file_move(oldpath, newpath)
            self.logger.debug("Response = <" + str(response) + ">")
            return response['rev']
        except ErrorResponse as error:
            self.__manageException(error)

    def deleteFile(self, file_path):
        client = self.__getDropboxClient()
        self.logger.info("Calling deleteFile")
        self.logger.debug("file_path = <" + file_path + ">")

        try:
            response = client.file_delete(file_path)
            return True
        except ErrorResponse as error:
            self.__manageException(error)

    def fits(self, file_size):
        return file_size <= self.free_quota

    def getFileList(self, folder='/'):
        client = self.__getDropboxClient()
        self.logger.info("Getting file list from <" + str(self) + ">")
        fileList = []

        try:
            self.logger.info("Getting metadata from <" + str(folder) + ">")
            metadata = client.metadata(folder)
            contents = metadata['contents']
            for element in contents:
                if element['is_dir']:
                    fileList += self.getFileList(element['path'])
                else:
                    fileList.append({'account': self, 'path': element['path']})

            return fileList

        except ErrorResponse as error:
            self.__manageException(error)

    def __repr__(self):
        return self.getAccountType() + '-' + self.user + '-' + self.email

    def summarize(self):
        return {'name': self.user, 'token': self.access_token, 'id': self.user_id, 'type': self.getAccountType()}


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
        self.__file_list = []
        self.__delta_acum = []
        self._delta_reset = False

    def __getDropboxClient(self):
        return None

    def getUserInfo(self):
        self.logger.info("Getting User Info")
        self.logger.info("INFO:")
        #self.logger.info(self.client.account_info())

    def getMetadata(self, folder):
        raise NotImplemented()

    def delta(self, returnDict=None, longpoll=False):
        if not returnDict:
            returnDict = dict()
        returnDict["entries"] = self.__delta_acum
        self.resetChanges()

        returnDict["reset"] = self._delta_reset
        return returnDict

    def deltaEmpty(self, returnDict=dict()):
        returnDict["entries"] = []
        returnDict["reset"] = False
        return returnDict

    def getFile(self, file_path):
        fileStream = next((i['stream'] for i in self.__file_list if i['path'] == file_path.lower()), None)
        if fileStream:
            fileStream.seek(0)
            return fileStream
        else:
            raise FileNotFoundError(file_path)

    def getAccountType(self):
        return "dropbox_stub"

    def uploadFile(self, file_path, rev=None, stream=None):
        if not stream:
            stream = tempfile.TemporaryFile()
        else:
            import shutil
            oldStream = stream
            newFileObj = tempfile.TemporaryFile()
            shutil.copyfileobj(oldStream, newFileObj)
            stream = newFileObj
        stream.seek(0)

        if rev:
            size = self.fileSystemModule.getFileSize(file_path)
            if not self.fits(size):
                raise FullStorageException(file_path)

        index = next((i for i, element in enumerate(self.__file_list) if element['path'] == file_path.lower()), -1)
        if index >= 0:
            self.__file_list[index] = {'path': file_path.lower(), 'original_path': file_path, 'stream': stream}
        else:
            self.__file_list.append({'path': file_path.lower(), 'original_path': file_path, 'stream': stream})

        if not rev:
            rev = 'revision_number'
        else:
            rev = rev + '1'
        deltaItem = [file_path.lower(), {'is_dir': False, 'path': file_path, 'rev': rev, 'bytes': len(file_path)}]
        if deltaItem not in self.__delta_acum:
            self.__delta_acum.append(deltaItem)

        return deltaItem[1]['rev']

    def renameFile(self, oldpath, newpath):
        try:
            index = next((i for i, element in enumerate(self.__file_list) if element['path'] == oldpath.lower()))

            self.__file_list[index]['path'] = newpath.lower()
            self.__file_list[index]['original_path'] = newpath
            deltaItem = [oldpath.lower(), None]
            self.__delta_acum.append(deltaItem)
            deltaItem2 = [newpath.lower(), {'is_dir': False, 'path': newpath, 'rev': 'renamed', 'bytes': len(newpath)}]
            self.__delta_acum.append(deltaItem2)
            return deltaItem2[1]['rev']

        except StopIteration as e:
            raise FileNotFoundError from e

    def deleteFile(self, file_path):
        try:
            element = next((i for i in self.__file_list if i['path'] == file_path.lower()))
            self.__file_list.remove(element)
            self.__delta_acum.append([file_path.lower(), None])
            return True
        except StopIteration as e:
            raise FileNotFoundError(file_path)

    def getFileList(self):
        return [i['original_path'] for i in self.__file_list]

    def resetChanges(self):
        self.__delta_acum = []

    def updateAccountInfo(self):
        pass
