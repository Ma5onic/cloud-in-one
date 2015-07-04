import threading

from menu import Menu
from manager import Manager
from log import Logger


def main():
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
    finally:
        input("Press ENTER to quit.")

if __name__ == '__main__':
    main()
