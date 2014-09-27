class Account():
    """ Base class for the hierarchy responsible of connecting
     with a remote account in a cloud storage service"""
    def __init__(self, user, password):
        self.user = user
        self.password = password
