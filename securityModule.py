import hashlib
import simplecrypt


class SecurityModule():
    """docstring for SecurityModule"""
    def __init__(self, password):
        super(SecurityModule, self).__init__()
        # we cannot use a random salt because this should be installed in several computers and give the same password to be able to decrypt...
        self.password = hashlib.sha256(('th¡5iS@sal7' + password).encode('utf-8')).hexdigest()

    def encrypt(self, streamFile):
        encrypted = simplecrypt.encrypt(self.password, streamFile.read())
        return encrypted

    def decrypt(self, streamFile):
        decrypted = simplecrypt.decrypt(self.password, streamFile.read())
        return decrypted
