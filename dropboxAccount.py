import account


class DropboxAccount(account.Account):
    """docstring for DropboxAccount"""
    def __init__(self, arg):
        super(DropboxAccount, self).__init__()
        self.arg = arg
