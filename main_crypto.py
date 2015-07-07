import getpass
import argparse
import shutil

from databaseManager import DatabaseManager
from securityModule import SecurityModule


def processFile(file_in_name, file_out_name, encrypt_flag):
    user = input("CLOUD-IN-ONE Username: ")
    password = getpass.getpass()

    databaseManager = DatabaseManager(':memory:')
    sec = SecurityModule(databaseManager, user, password)

    file_processed = None
    with open(file_in_name, 'rb') as f_in:
        if encrypt_flag:
            file_processed = sec.encrypt(f_in)
        else:
            file_processed = sec.decrypt(f_in)

    with open(file_out_name, 'wb') as f_out:
        file_processed.seek(0)
        shutil.copyfileobj(file_processed, f_out)
        file_processed.close()


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--decrypt", action="store_true")
    group.add_argument("-e", "--encrypt", action="store_true")
    parser.add_argument("file", help="the file to encrypt / decrypt")
    parser.add_argument("file_output", help="name of the destination file")
    args = parser.parse_args()

    encrypt_flag = args.encrypt
    if not encrypt_flag:
        encrypt_flag = not args.decrypt

    processFile(args.file, args.file_output, encrypt_flag)


if __name__ == '__main__':
    main()
