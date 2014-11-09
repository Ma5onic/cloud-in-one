import account
import dropbox
import os
from log import *

app_key = os.getenv("APP_KEY")
app_secret = os.getenv("APP_SECRET")
TOKEN_FILE = "config/dropbox_token.txt"


class DropboxAccount(account.Account):
    """docstring for DropboxAccount"""
    def __init__(self, user):
        self.logger = Logger(__name__)
        self.logger.info("Creating Dropbox Account")
        self.user = user
        self.access_token = None
        self.client = None
        self.access_token = self.user_id = None

        self.__startOAuthFlow()

    def __startOAuthFlow(self):
        self.logger.info("starting OAuth Flow")
        if(os.path.isfile(TOKEN_FILE)):
            self.logger.debug("Found existing token")
            token_file = open(TOKEN_FILE, "r")
            self.access_token, self.user_id = token_file.read().split('|')
            token_file.close()
        else:
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

        self.logger.debug("Creating Client. Token = <" + self.access_token + "> user_id = <" + self.user_id + ">")
        self.client = dropbox.client.DropboxClient(self.access_token)

    def getUserInfo(self):
        self.logger.info("Getting User Info")
        self.logger.info("INFO:")
        self.logger.info(self.client.account_info())

    def getMetadata(self, folder):
        self.logger.info("Getting metadata from <" + folder + ">")
        metadata = self.client.metadata(folder)
        # for now, it will return all what Dropbox sends, but as we move forward we will return a custom metadata dict
        return metadata


class DropboxAccountStub(DropboxAccount):
    """Stub for testing the DBAccount"""
    def __init__(self, user):
        self.user = user
