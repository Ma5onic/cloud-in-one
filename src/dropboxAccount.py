import account
import dropbox
import os
from log import *

app_key = os.getenv("APP_KEY")
app_secret = os.getenv("APP_SECRET")
TOKEN_FILE = "config/dropbox_token.txt"


class DropboxAccount(account.Account):
    """docstring for DropboxAccount"""
    def __init__(self, user, access_token=None, user_id=None):
        self.logger = Logger(__name__)
        self.logger.info("Creating Dropbox Account")
        self.user = user
        self.access_token = access_token
        self.user_id = user_id
        self.last_cursor = None
        # You shouldn't use self.__client, call __getDropboxClient() to get it safely
        self.__client = None
        self.__client = self.__getDropboxClient()

    def __startOAuthFlow(self):
        self.logger.info("starting OAuth Flow")
        self.logger.debug("Token not found, asking for one")
        token_file = open(TOKEN_FILE, "w")
        flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
        # Have the user sign in and authorize this token
        authorize_url = flow.start()
        print('1. Go to: ' + authorize_url)
        print('2. Click "Allow" (you might have to log in first)')
        print('3. Copy the authorization code.')
        code = input("Enter the authorization code here: ").strip()
        self.access_token, self.user_id = flow.finish(code)
        token_file.write("%s|%s" % (self.access_token, self.user_id))

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
        user_info = client.account_info()
        self.logger.info(user_info)

    def getMetadata(self, folder):
        client = self.__getDropboxClient()
        self.logger.info("Getting metadata from <" + folder + ">")
        metadata = client.metadata(folder)
        # for now, it will return all what Dropbox sends, but as we move forward we will return a custom metadata dict
        return metadata

    def delta(self, returnDict=dict()):
        client = self.__getDropboxClient()
        self.logger.info("Calling delta")
        self.logger.debug("Last cursor = <" + str(self.last_cursor) + ">")
        returnDict["entries"] = []
        returnDict["reset"] = False

        deltaDict = client.delta(cursor=self.last_cursor)
        self.last_cursor = deltaDict["cursor"]
        self.logger.debug(deltaDict)

        returnDict["entries"] += deltaDict["entries"]
        returnDict["reset"] = deltaDict["reset"]

        if deltaDict["has_more"]:
            delta(returnDict)

        self.logger.debug("returnDict = <" + str(returnDict) + ">")
        return returnDict

    def getFile(self, file_path):
        client = self.__getDropboxClient()
        self.logger.info("Calling getFile")
        self.logger.debug("file_path = <" + file_path + ">")
        outputFile = client.get_file(file_path)
        self.logger.debug("outputFile = <" + str(outputFile) + ">")
        return outputFile

    def getAccountType(self):
        return "dropbox"

    def __repr__(self):
        return self.getAccountType() + ' (' + self.user + ')'


class DropboxAccountStub(DropboxAccount):
    """Stub for testing the DBAccount"""
    def __init__(self, user):
        # super(DropboxAccountStub, self).__init__(user)
        self.logger = Logger(__name__)
        self.logger.info("Creating Dropbox Account")
        self.user = user
        self.access_token = None
        self.user_id = None
        self.last_cursor = None
        # You shouldn't use self.__client, call __getDropboxClient() to get it safely
        self.__client = None

    def getUserInfo(self):
        self.logger.info("Getting User Info")
        self.logger.info("INFO:")
        #self.logger.info(self.client.account_info())

    def getMetadata(self, folder):
        raise NotImplemented()

    def delta(self, returnDict=dict()):
        returnDict["entries"] = []
        returnDict["entries"].append(['/test/muerte.txt', {'is_dir': False, 'path': '/test/muerte.txt'}])
        returnDict["reset"] = False
        return returnDict

    def deltaEmpty(self, returnDict=dict()):
        returnDict["entries"] = []
        returnDict["reset"] = False
        return returnDict

    def getFile(self, file_path):
        f = open('test/muerte.txt', 'rb')
        return f

    def getAccountType(self):
        return "dropbox_stub"



