from menu import Menu
from manager import Manager


def main():
    man = Manager('user', 'password')
    menu = Menu(man)
    menu.start()


if __name__ == '__main__':
    main()
