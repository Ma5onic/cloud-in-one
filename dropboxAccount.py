import account
import dropbox
import os

app_key = os.getenv("APP_KEY")
app_secret = os.getenv("APP_SECRET")


class DropboxAccount(account.Account):
    """docstring for DropboxAccount"""
    def __init__(self, user):
        self.user = user
        self.startOAuthFlow()

    def startOAuthFlow(self):
        flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
        # Have the user sign in and authorize this token
        authorize_url = flow.start()
        print('1. Go to: ' + authorize_url)
        print('2. Click "Allow" (you might have to log in first)')
        print('3. Copy the authorization code.')
        code = input("Enter the authorization code here: ").strip()
        self.access_token, self.user_id = flow.finish(code)
        # TODO: guardar el token y user_id de forma segura
        self.client = dropbox.client.DropboxClient(self.access_token)
