import sys
import threading
import argparse

from menu import Menu
from manager import Manager
from log import Logger


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
    args = parser.parse_args()

    if args.uninstall:
        uninstall()
    else:
        try:
            event = threading.Event()
            finish_event = threading.Event()
            lock = threading.Lock()
            event_menu = threading.Event()

            man = Manager(event=event, lock=lock, finish=finish_event, event_menu=event_menu)
            menu = Menu(man, event=event, lock=lock, finish=finish_event, event_menu=event_menu)
            man.start()
            menu.start()
        except Exception as e:
            logger = Logger(__name__)
            logger.critical(str(e))
            sys.exit(1)
        finally:
            input("Press ENTER to quit.")

if __name__ == '__main__':
    main()
