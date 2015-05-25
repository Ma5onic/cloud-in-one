import threading
import getpass

from menu import Menu
from manager import Manager


def main():
    event = threading.Event()
    finish_event = threading.Event()
    lock = threading.Lock()
    password = getpass.getpass()
    man = Manager('user', password, event=event, lock=lock, finish=finish_event)
    menu = Menu(man, event=event, lock=lock, finish=finish_event)
    man.start()
    menu.start()


if __name__ == '__main__':
    main()
