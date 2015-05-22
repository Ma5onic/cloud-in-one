class Menu(object):
    """Main menu, with options to start things"""
    def __init__(self, manager, event, lock, finish):
        super(Menu, self).__init__()
        self.manager = manager
        self.event = event
        self.finish = finish
        self.lock = lock

    def _listAccounts(self):
        print("Account list:")
        for i, account in enumerate(self.manager.listAccounts(), 1):
            print(i, account)

    def __newAccountInteractive(self):
        account_type = "dropbox"
        print("Select the account type: ", account_type)
        user = input("Enter a username: ")
        self.manager.newAccount(account_type, user)

    def __deleteAccountInteractive(self):
        self._listAccounts()
        account_to_delete = input("Select the account you want to delete, or 0 to cancel: ")
        account_to_delete = int(account_to_delete) - 1

        if account_to_delete == -1:
            return
        try:
            self.manager.deleteAccount(self.manager.cuentas[account_to_delete])
        except IndexError:
            print("ERROR: invalid account")
            return

    def _forceSync(self):
        self.event.set()

    def _showMenu(self):
        print()
        print("""====================== CLOUD IN ONE ======================
                      MAIN MENU
1. New account
2. List accounts
3. Delete account
4. Force start sync
0. EXIT

        Please select an option: """)
        opt = input()
        print(chr(27) + "[2J")  # clear screen

        return opt

    def start(self):
        try:
            option = None
            while option != '0':
                option = self._showMenu()
                if option in {'1', '2', '3', '4'}:
                    with self.lock:
                        if option == '1':
                            self.__newAccountInteractive()
                        elif option == '2':
                            self._listAccounts()
                        elif option == '3':
                            self.__deleteAccountInteractive()
                        elif option == '4':
                            self._forceSync()
        except:
            raise
        finally:
            self.finish.set()
            self._forceSync()
