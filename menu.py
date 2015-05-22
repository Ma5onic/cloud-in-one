class Menu(object):
    """Main menu, with options to start things"""
    def __init__(self, manager):
        super(Menu, self).__init__()
        self.manager = manager

    def _listAccounts(self):
        print("Account list:")
        for i, account in enumerate(self.manager.listAccounts(),1):
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

    def _showMenu(self):
        print()
        print("====================== CLOUD IN ONE ======================")
        print("                        MAIN MENU                         ")
        print("1. New account")
        print("2. List accounts")
        print("3. Delete account")
        print("4. Force start sync")
        print("0. EXIT")
        print("")
        opt = input("Please select an option: ")
        print(chr(27) + "[2J")  # clear screen

        return opt

    def start(self):
        option = None
        while option != '0':
            option = self._showMenu()
            if option == '1':
                self.__newAccountInteractive()
            elif option == '2':
                self._listAccounts()
            elif option == '3':
                self.__deleteAccountInteractive()
            elif option == '4':
                print("force sync")
