#!/usr/bin/env python3

import sys
import threading
import argparse

from core.menu import Menu
from core.manager import Manager
from core.log import Logger
from core.repl import Repl

def uninstall():
    print("")
    print("")
    print("")
    print("")
    print("UNINSTALLING")
    print("Removing all accounts linked to the system")

    man = Manager()
    for i in man.cuentas:
        man.deleteAccount(i)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--uninstall", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--cli", help="Invoke a REPL", action="store_true")
    args = parser.parse_args()

    if args.uninstall:
        uninstall()
    else:
        try:
            if args.cli:
                man = Manager()
                repl = Repl(man)
                repl.start()
            else:
                man = Manager()
                if man.cuentas == []:
                    account_type = "dropbox"
                    print("Select the account type: ", account_type)
                    user = input("Enter a name for the new account: ")
                    man.newAccount(account_type, user)
                man.updateLocalSyncFolder()
        except Exception as e:
            logger = Logger(__name__)
            logger.critical(str(e))
            sys.exit(1)
        finally:
            input("Press ENTER to quit.")

if __name__ == '__main__':
    main()
