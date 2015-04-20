def Ignore(fn):
    def ignoreTest(self):
        pass
    return ignoreTest
