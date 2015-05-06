def Ignore(fn):
    def ignoreTest(self):
        pass
    return ignoreTest


def returnFalse(*args, **kwargs):
    ''' This function ignores all arguments, and always returns false '''
    return False
