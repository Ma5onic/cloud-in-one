import account


class GDriveAccount(account.Account):
    """docstring for GDriveAccount"""
    def __init__(self, arg):
        super(GDriveAccount, self).__init__()
        self.arg = arg
